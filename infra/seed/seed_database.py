"""Load the deterministic 2026 demo dataset into PostgreSQL."""

import argparse
import asyncio
import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from database.config import get_database_settings
from database.models import (
    CounterpartyModel,
    CounterpartyMonthlyReceivableModel,
    EnterpriseModel,
    FinancialTransactionModel,
    ForecastRunModel,
    ForecastRunPeriodModel,
    IngestionRunModel,
    IngestionSourceCredentialModel,
    IngestionSourceModel,
    MitigationRecommendationModel,
    MonthlyCashflowAggregateModel,
    ReceivablesRankingModel,
    SimulationRunModel,
    SimulationScenarioModel,
    StaticFinancialSnapshotModel,
)
from database.session import (
    AsyncDatabaseConfig,
    create_database_engine,
    create_session_factory,
)
from domain.enterprise import CounterpartyType
from domain.financial import (
    EntryMode,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
)
from domain.forecasting import ForecastRunType, ForecastStatus
from domain.ingestion import (
    CredentialStatus,
    CredentialType,
    IngestionRunType,
    IngestionStatus,
)
from domain.simulation import (
    RecommendationActionType,
    SimulationStatus,
    SimulationType,
)
from sqlalchemy.ext.asyncio import AsyncSession

SEED_DIR = Path(__file__).resolve().parent


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _stable_id(enterprise_id: UUID, kind: str, key: str) -> UUID:
    return uuid5(NAMESPACE_URL, f'cash-flow-seed:2026:{enterprise_id}:{kind}:{key}')


def _parse_date(value: str) -> date:
    parsed = date.fromisoformat(value)
    if parsed.year != 2026:
        raise ValueError(f'Seed date must be in 2026: {value}')
    return parsed


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.year != 2026:
        raise ValueError(f'Seed timestamp must be in 2026: {value}')
    return parsed


def _decimal(value: str | float) -> Decimal:
    return Decimal(str(value))


def _payload_hash(source_record_id: str) -> str:
    return hashlib.sha256(source_record_id.encode('utf-8')).hexdigest()


async def _ensure_by_id(
    session: AsyncSession,
    model_class: Any,
    model_id: UUID,
    values: dict[str, Any],
) -> Any:
    existing = await session.get(model_class, model_id)
    if existing is not None:
        return existing
    model = model_class(id=model_id, **values)  # type: ignore[call-arg]
    session.add(model)
    await session.flush()
    return model


async def _seed_credentials(
    session: AsyncSession,
    state: dict[str, str],
    api_seed: dict[str, Any],
) -> None:
    credential_id = UUID(state['erpnext_credential_id'])
    if await session.get(IngestionSourceCredentialModel, credential_id) is not None:
        return

    payload = api_seed['erpnext_credential']
    session.add(
        IngestionSourceCredentialModel(
            id=credential_id,
            enterprise_id=UUID(state['enterprise_id']),
            ingestion_source_id=UUID(state['erpnext_source_id']),
            credential_type=CredentialType(payload['credential_type']),
            status=CredentialStatus.ACTIVE,
            config_json=payload['config_json'],
            secret_ref=payload['secret_ref'],
            last_rotated_at=_parse_datetime('2026-08-01T09:00:00+05:30'),
        )
    )
    await session.flush()


async def _seed_ingestion_runs(
    session: AsyncSession,
    enterprise_id: UUID,
    source_ids: dict[str, UUID],
    records: list[dict[str, Any]],
) -> dict[str, IngestionRunModel]:
    runs: dict[str, IngestionRunModel] = {}
    for item in records:
        run = await _ensure_by_id(
            session,
            IngestionRunModel,
            _stable_id(enterprise_id, 'ingestion-run', item['key']),
            {
                'enterprise_id': enterprise_id,
                'ingestion_source_id': source_ids[item['source_key']],
                'run_type': IngestionRunType(item['run_type']),
                'status': IngestionStatus(item['status']),
                'started_at': _parse_datetime(item['started_at']),
                'finished_at': _parse_datetime(item['finished_at']),
                'records_received': item['records_received'],
                'records_processed': item['records_processed'],
                'records_failed': item['records_failed'],
                'error_summary': item.get('error_summary'),
                'created_at': _parse_datetime(item['created_at']),
            },
        )
        runs[item['key']] = run
    return runs


async def _seed_counterparties(
    session: AsyncSession,
    enterprise_id: UUID,
    records: list[dict[str, Any]],
) -> dict[str, CounterpartyModel]:
    counterparties: dict[str, CounterpartyModel] = {}
    for item in records:
        counterparty = await _ensure_by_id(
            session,
            CounterpartyModel,
            _stable_id(enterprise_id, 'counterparty', item['key']),
            {
                'enterprise_id': enterprise_id,
                'external_key': item['external_key'],
                'name': item['name'],
                'counterparty_type': CounterpartyType(item['counterparty_type']),
                'is_active': item['is_active'],
            },
        )
        counterparties[item['key']] = counterparty
    return counterparties


async def _seed_transactions(
    session: AsyncSession,
    enterprise_id: UUID,
    source_id: UUID,
    run_id: UUID,
    counterparties: dict[str, CounterpartyModel],
    records: list[dict[str, Any]],
) -> None:
    for item in records:
        transaction_date = _parse_date(item['transaction_date'])
        due_date = _parse_date(item['due_date']) if item.get('due_date') else None
        settlement_date = (
            _parse_date(item['settlement_date'])
            if item.get('settlement_date')
            else None
        )
        if due_date is not None and due_date < transaction_date:
            raise ValueError(f'Due date precedes transaction date: {item["key"]}')
        if settlement_date is not None and settlement_date < transaction_date:
            raise ValueError(
                f'Settlement date precedes transaction date: {item["key"]}'
            )

        await _ensure_by_id(
            session,
            FinancialTransactionModel,
            _stable_id(enterprise_id, 'transaction', item['key']),
            {
                'enterprise_id': enterprise_id,
                'ingestion_source_id': source_id,
                'ingestion_run_id': run_id,
                'counterparty_id': (
                    counterparties[item['counterparty_key']].id
                    if item.get('counterparty_key')
                    else None
                ),
                'transaction_type': TransactionType(item['transaction_type']),
                'transaction_date': transaction_date,
                'due_date': due_date,
                'settlement_date': settlement_date,
                'amount': _decimal(item['amount']),
                'currency_code': item['currency_code'],
                'direction': TransactionDirection(item['direction']),
                'status': TransactionStatus(item['status']),
                'reference_number': item.get('reference_number'),
                'description': item.get('description'),
                'source_record_id': item['source_record_id'],
                'source_payload_hash': _payload_hash(item['source_record_id']),
            },
        )


async def _seed_aggregates(
    session: AsyncSession,
    enterprise_id: UUID,
    runs: dict[str, IngestionRunModel],
    records: list[dict[str, Any]],
) -> dict[str, MonthlyCashflowAggregateModel]:
    aggregates: dict[str, MonthlyCashflowAggregateModel] = {}
    for item in records:
        aggregate = await _ensure_by_id(
            session,
            MonthlyCashflowAggregateModel,
            _stable_id(enterprise_id, 'monthly-aggregate', item['key']),
            {
                'enterprise_id': enterprise_id,
                'period_start': _parse_date(item['period_start']),
                'period_end': _parse_date(item['period_end']),
                'total_invoice_amount': _decimal(item['total_invoice_amount']),
                'total_inflows': _decimal(item['total_inflows']),
                'total_outflows': _decimal(item['total_outflows']),
                'monthly_repayment': _decimal(item['monthly_repayment']),
                'total_payment_delay_days': _decimal(item['total_payment_delay_days']),
                'invoice_count': item['invoice_count'],
                'payment_count': item['payment_count'],
                'derived_from_run_id': runs[item['run_key']].id,
            },
        )
        aggregates[item['key']] = aggregate
    return aggregates


async def _seed_receivables(
    session: AsyncSession,
    enterprise_id: UUID,
    counterparties: dict[str, CounterpartyModel],
    records: list[dict[str, Any]],
) -> None:
    for item in records:
        await _ensure_by_id(
            session,
            CounterpartyMonthlyReceivableModel,
            _stable_id(enterprise_id, 'counterparty-receivable', item['key']),
            {
                'enterprise_id': enterprise_id,
                'counterparty_id': counterparties[item['counterparty_key']].id,
                'period_start': _parse_date(item['period_start']),
                'period_end': _parse_date(item['period_end']),
                'invoice_total': _decimal(item['invoice_total']),
                'amount_paid': _decimal(item['amount_paid']),
                'outstanding_amount': _decimal(item['outstanding_amount']),
                'average_payment_delay_days': (
                    _decimal(item['average_payment_delay_days'])
                    if item.get('average_payment_delay_days') is not None
                    else None
                ),
                'late_invoice_count': item['late_invoice_count'],
            },
        )


async def _seed_snapshot(
    session: AsyncSession,
    enterprise_id: UUID,
    source_ids: dict[str, UUID],
    records: list[dict[str, Any]],
) -> dict[str, StaticFinancialSnapshotModel]:
    snapshots: dict[str, StaticFinancialSnapshotModel] = {}
    for item in records:
        snapshot = await _ensure_by_id(
            session,
            StaticFinancialSnapshotModel,
            _stable_id(enterprise_id, 'snapshot', item['key']),
            {
                'enterprise_id': enterprise_id,
                'ingestion_source_id': source_ids[item['source_key']],
                'snapshot_date': _parse_date(item['snapshot_date']),
                'entry_mode': EntryMode(item['entry_mode']),
                'credit_score': _decimal(item['credit_score']),
                'failure_score': _decimal(item['failure_score']),
                'debt_to_revenue_ratio': _decimal(item['debt_to_revenue_ratio']),
                'current_assets': _decimal(item['current_assets']),
                'current_liabilities': _decimal(item['current_liabilities']),
                'fixed_assets': _decimal(item['fixed_assets']),
                'long_term_liabilities': _decimal(item['long_term_liabilities']),
                'capex': _decimal(item['capex']),
                'cogs': _decimal(item['cogs']),
                'missed_payments_number': item['missed_payments_number'],
            },
        )
        snapshots[item['key']] = snapshot
    return snapshots


async def _seed_forecasts(
    session: AsyncSession,
    enterprise_id: UUID,
    snapshots: dict[str, StaticFinancialSnapshotModel],
    aggregates: dict[str, MonthlyCashflowAggregateModel],
    records: list[dict[str, Any]],
) -> dict[str, ForecastRunModel]:
    forecasts: dict[str, ForecastRunModel] = {}
    for item in records:
        forecast = await _ensure_by_id(
            session,
            ForecastRunModel,
            _stable_id(enterprise_id, 'forecast', item['key']),
            {
                'enterprise_id': enterprise_id,
                'run_type': ForecastRunType(item['run_type']),
                'target_period_start': _parse_date(item['target_period_start']),
                'target_period_end': _parse_date(item['target_period_end']),
                'sequence_window_months': item['sequence_window_months'],
                'static_snapshot_id': snapshots[item['snapshot_key']].id,
                'model_version': item['model_version'],
                'artifact_version': item['artifact_version'],
                'predicted_net_cashflow': _decimal(item['predicted_net_cashflow']),
                'solvency_buffer': _decimal(item['solvency_buffer']),
                'buffer_gap': _decimal(item['buffer_gap']),
                'status': ForecastStatus(item['status']),
                'requested_at': _parse_datetime(item['requested_at']),
                'completed_at': _parse_datetime(item['completed_at']),
                'created_at': _parse_datetime(item['created_at']),
            },
        )
        for sequence_index, aggregate_key in enumerate(item['aggregate_keys']):
            await _ensure_by_id(
                session,
                ForecastRunPeriodModel,
                _stable_id(
                    enterprise_id,
                    'forecast-period',
                    f'{item["key"]}:{sequence_index}',
                ),
                {
                    'forecast_run_id': forecast.id,
                    'monthly_cashflow_aggregate_id': aggregates[aggregate_key].id,
                    'sequence_index': sequence_index,
                },
            )
        forecasts[item['key']] = forecast
    return forecasts


async def _seed_simulations(
    session: AsyncSession,
    enterprise_id: UUID,
    forecasts: dict[str, ForecastRunModel],
    counterparties: dict[str, CounterpartyModel],
    records: dict[str, list[dict[str, Any]]],
) -> None:
    simulations: dict[str, SimulationRunModel] = {}
    for item in records['simulation_runs']:
        simulation = await _ensure_by_id(
            session,
            SimulationRunModel,
            _stable_id(enterprise_id, 'simulation', item['key']),
            {
                'enterprise_id': enterprise_id,
                'forecast_run_id': forecasts[item['forecast_key']].id,
                'simulation_type': SimulationType(item['simulation_type']),
                'status': SimulationStatus(item['status']),
                'summary_result': item['summary_result'],
                'requested_at': _parse_datetime(item['requested_at']),
                'completed_at': _parse_datetime(item['completed_at']),
                'created_at': _parse_datetime(item['created_at']),
            },
        )
        simulations[item['key']] = simulation

    for item in records['simulation_scenarios']:
        await _ensure_by_id(
            session,
            SimulationScenarioModel,
            _stable_id(enterprise_id, 'simulation-scenario', item['key']),
            {
                'simulation_run_id': simulations[item['simulation_key']].id,
                'scenario_index': item['scenario_index'],
                'scenario_label': item['scenario_label'],
                'input_patch_json': item['input_patch_json'],
                'predicted_net_cashflow': _decimal(item['predicted_net_cashflow']),
                'delta_from_baseline': _decimal(item['delta_from_baseline']),
                'meets_buffer': item['meets_buffer'],
            },
        )

    for item in records['receivables_rankings']:
        await _ensure_by_id(
            session,
            ReceivablesRankingModel,
            _stable_id(enterprise_id, 'receivables-ranking', item['key']),
            {
                'simulation_run_id': simulations[item['simulation_key']].id,
                'counterparty_id': counterparties[item['counterparty_key']].id,
                'rank_position': item['rank_position'],
                'baseline_outstanding_amount': _decimal(
                    item['baseline_outstanding_amount']
                ),
                'simulated_cashflow_delta': _decimal(item['simulated_cashflow_delta']),
            },
        )

    for item in records['mitigation_recommendations']:
        await _ensure_by_id(
            session,
            MitigationRecommendationModel,
            _stable_id(enterprise_id, 'mitigation-recommendation', item['key']),
            {
                'simulation_run_id': simulations[item['simulation_key']].id,
                'priority_rank': item['priority_rank'],
                'action_type': RecommendationActionType(item['action_type']),
                'parameter_name': item['parameter_name'],
                'original_value': _decimal(item['original_value']),
                'recommended_value': _decimal(item['recommended_value']),
                'expected_cashflow_delta': _decimal(item['expected_cashflow_delta']),
                'expected_post_action_cashflow': _decimal(
                    item['expected_post_action_cashflow']
                ),
                'meets_buffer': item['meets_buffer'],
            },
        )


async def _seed_database(seed: dict[str, Any], state: dict[str, str]) -> None:
    required_state = {
        'enterprise_id',
        'erpnext_source_id',
        'csv_source_id',
        'erpnext_credential_id',
    }
    missing = required_state - state.keys()
    if missing:
        names = ', '.join(sorted(missing))
        raise RuntimeError(
            f'Missing seed state values: {names}. Run seed_api.py first.'
        )

    enterprise_id = UUID(state['enterprise_id'])
    source_ids = {
        'erpnext': UUID(state['erpnext_source_id']),
        'csv': UUID(state['csv_source_id']),
    }
    settings = get_database_settings()
    engine = create_database_engine(AsyncDatabaseConfig.from_settings(settings))
    session_factory = create_session_factory(engine)

    try:
        async with session_factory() as session:
            enterprise = await session.get(EnterpriseModel, enterprise_id)
            if enterprise is None:
                raise RuntimeError(f'Enterprise {enterprise_id} was not found.')
            for source_id in source_ids.values():
                if await session.get(IngestionSourceModel, source_id) is None:
                    raise RuntimeError(f'Ingestion source {source_id} was not found.')

            await _seed_credentials(session, state, seed['api'])
            runs = await _seed_ingestion_runs(
                session,
                enterprise_id,
                source_ids,
                seed['database']['ingestion_runs'],
            )
            counterparties = await _seed_counterparties(
                session, enterprise_id, seed['database']['counterparties']
            )
            await _seed_transactions(
                session,
                enterprise_id,
                source_ids['erpnext'],
                runs['erpnext-full-2026-07-31'].id,
                counterparties,
                seed['database']['financial_transactions'],
            )
            aggregates = await _seed_aggregates(
                session,
                enterprise_id,
                runs,
                seed['database']['monthly_cashflow_aggregates'],
            )
            await _seed_receivables(
                session,
                enterprise_id,
                counterparties,
                seed['database']['counterparty_monthly_receivables'],
            )
            snapshots = await _seed_snapshot(
                session,
                enterprise_id,
                source_ids,
                seed['database']['static_financial_snapshots'],
            )
            forecasts = await _seed_forecasts(
                session,
                enterprise_id,
                snapshots,
                aggregates,
                seed['database']['forecast_runs'],
            )
            await _seed_simulations(
                session,
                enterprise_id,
                forecasts,
                counterparties,
                seed['database'],
            )

            latest_sync = _parse_datetime('2026-08-29T10:15:22+05:30')
            for source_id in source_ids.values():
                source = await session.get(IngestionSourceModel, source_id)
                if source is not None:
                    source.last_synced_at = latest_sync
            await session.commit()
            print(f'Seeded the 2026 demo dataset for enterprise {enterprise_id}.')
    finally:
        await engine.dispose()


def main() -> None:
    """Load the JSON fixture into the configured PostgreSQL database."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed-file', type=Path, default=SEED_DIR / 'seed-data.json')
    parser.add_argument('--state-file', type=Path, default=SEED_DIR / 'seed-state.json')
    args = parser.parse_args()
    if not args.state_file.exists():
        raise RuntimeError('Seed state file is missing. Run seed_api.py first.')
    asyncio.run(_seed_database(_load_json(args.seed_file), _load_json(args.state_file)))


if __name__ == '__main__':
    main()
