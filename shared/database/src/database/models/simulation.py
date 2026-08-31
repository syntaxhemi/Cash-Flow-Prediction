from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from domain.simulation import RecommendationActionType, SimulationStatus, SimulationType
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type

if TYPE_CHECKING:
    from database.models.enterprise import EnterpriseModel
    from database.models.financial import CounterpartyModel
    from database.models.forecasting import ForecastRunModel


class SimulationRunModel(Base):
    __tablename__ = 'simulation_runs'
    __table_args__ = (
        Index(
            'ix_simulation_runs_enterprise_id_created_at', 'enterprise_id', 'created_at'
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    forecast_run_id: Mapped[UUID] = mapped_column(
        ForeignKey('forecast_runs.id'), nullable=False
    )
    simulation_type: Mapped[SimulationType] = mapped_column(
        enum_type(SimulationType, name='simulation_type'), nullable=False
    )
    status: Mapped[SimulationStatus] = mapped_column(
        enum_type(SimulationStatus, name='simulation_status'), nullable=False
    )
    summary_result: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    requested_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    enterprise: Mapped['EnterpriseModel'] = relationship()
    forecast_run: Mapped['ForecastRunModel'] = relationship(
        back_populates='simulation_runs'
    )
    scenarios: Mapped[list['SimulationScenarioModel']] = relationship(
        back_populates='simulation_run'
    )
    receivables_rankings: Mapped[list['ReceivablesRankingModel']] = relationship(
        back_populates='simulation_run'
    )
    mitigation_recommendations: Mapped[list['MitigationRecommendationModel']] = (
        relationship(back_populates='simulation_run')
    )


class SimulationScenarioModel(Base):
    __tablename__ = 'simulation_scenarios'
    __table_args__ = (UniqueConstraint('simulation_run_id', 'scenario_index'),)

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    simulation_run_id: Mapped[UUID] = mapped_column(
        ForeignKey('simulation_runs.id'), nullable=False
    )
    scenario_index: Mapped[int] = mapped_column(Integer, nullable=False)
    scenario_label: Mapped[str] = mapped_column(String(255), nullable=False)
    input_patch_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    predicted_net_cashflow: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False
    )
    delta_from_baseline: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    meets_buffer: Mapped[bool] = mapped_column(Boolean, nullable=False)
    health_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    health_score_delta: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    health_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    simulation_run: Mapped[SimulationRunModel] = relationship(
        back_populates='scenarios'
    )


class ReceivablesRankingModel(Base):
    __tablename__ = 'receivables_rankings'
    __table_args__ = (UniqueConstraint('simulation_run_id', 'counterparty_id'),)

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    simulation_run_id: Mapped[UUID] = mapped_column(
        ForeignKey('simulation_runs.id'), nullable=False
    )
    counterparty_id: Mapped[UUID] = mapped_column(
        ForeignKey('counterparties.id'), nullable=False
    )
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    baseline_outstanding_amount: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False
    )
    simulated_cashflow_delta: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    simulation_run: Mapped[SimulationRunModel] = relationship(
        back_populates='receivables_rankings'
    )
    counterparty: Mapped['CounterpartyModel'] = relationship()


class MitigationRecommendationModel(Base):
    __tablename__ = 'mitigation_recommendations'
    __table_args__ = (UniqueConstraint('simulation_run_id', 'priority_rank'),)

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    simulation_run_id: Mapped[UUID] = mapped_column(
        ForeignKey('simulation_runs.id'), nullable=False
    )
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[RecommendationActionType] = mapped_column(
        enum_type(RecommendationActionType, name='recommendation_action_type'),
        nullable=False,
    )
    parameter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    recommended_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    expected_cashflow_delta: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False
    )
    expected_post_action_cashflow: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False
    )
    meets_buffer: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    simulation_run: Mapped[SimulationRunModel] = relationship(
        back_populates='mitigation_recommendations'
    )
