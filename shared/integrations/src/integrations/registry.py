from collections.abc import Mapping

from domain.exceptions import (
    IntegrationAdapterAlreadyRegisteredError,
    IntegrationAdapterNotFoundError,
)

from integrations.interfaces import IIngestionAdapter


class IngestionAdapterRegistry:
    """Resolve ingestion adapters by stable source key."""

    def __init__(self, adapters: Mapping[str, IIngestionAdapter] | None = None) -> None:
        """Initialize the ingestion adapter registry.

        Args:
            adapters: Optional initial adapter mapping registered during startup.

        Raises:
            IntegrationAdapterAlreadyRegisteredError: If initial keys collide.
        """
        self._adapters: dict[str, IIngestionAdapter] = {}
        for source_key, adapter in (adapters or {}).items():
            self.register(source_key, adapter)

    def register(self, source_key: str, adapter: IIngestionAdapter) -> None:
        """Register an ingestion adapter under a stable source key.

        Args:
            source_key: Stable key persisted on an ingestion source.
            adapter: Adapter implementation resolved for the key.

        Raises:
            ValueError: If the source key is empty.
            IntegrationAdapterAlreadyRegisteredError: If the key is already used.
        """
        normalized_key = source_key.strip()

        if not normalized_key:
            raise ValueError('Integration adapter source key must not be empty.')

        if normalized_key in self._adapters:
            raise IntegrationAdapterAlreadyRegisteredError(
                f'Integration adapter for source key "{normalized_key}" '
                'is already registered.'
            )

        self._adapters[normalized_key] = adapter

    def get_adapter(self, source_key: str) -> IIngestionAdapter:
        """Return the adapter registered for a source key.

        Args:
            source_key: Stable source key to resolve.

        Returns:
            The registered ingestion adapter.

        Raises:
            IntegrationAdapterNotFoundError: If no adapter is registered.
        """
        adapter = self._adapters.get(source_key)
        if adapter is None:
            raise IntegrationAdapterNotFoundError(
                f'No ingestion adapter is registered for source key "{source_key}".'
            )
        return adapter

    def has_adapter(self, source_key: str) -> bool:
        """Return whether an adapter is registered for a source key.

        Args:
            source_key: Stable source key to check.

        Returns:
            ``True`` when an adapter is registered, otherwise ``False``.
        """
        return source_key in self._adapters
