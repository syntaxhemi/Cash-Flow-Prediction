"""API dependency providers package."""

from api.dependencies.event_broker import get_event_broker_manager

__all__ = ['get_event_broker_manager']
