from collections.abc import Mapping, Sequence
from typing import Protocol

from redis.asyncio import Redis

type StreamFieldValue = str | bytes | memoryview | int | float
type StreamFields = Mapping[str, StreamFieldValue]
type StreamMessage = tuple[str, dict[str, str]]
type StreamReadResult = list[tuple[str, list[StreamMessage]]]


class IEventBrokerManager(Protocol):
    async def initialize(self) -> None:
        """Initialize the underlying event broker client."""
        ...

    async def check_connection(self) -> None:
        """Verify that the event broker backend is reachable."""
        ...

    def get_client(self) -> Redis:
        """Return the initialized async event broker client."""
        ...

    async def publish(
        self,
        stream_name: str,
        fields: StreamFields,
        *,
        maxlen: int | None = None,
        approximate: bool = True,
    ) -> str:
        """Publish a message to the given Redis Stream."""
        ...

    async def create_consumer_group(
        self,
        stream_name: str,
        group_name: str,
        *,
        start_id: str = '$',
        mkstream: bool = False,
    ) -> None:
        """Create a consumer group for the given Redis Stream."""
        ...

    async def read_group(
        self,
        group_name: str,
        consumer_name: str,
        streams: Mapping[str, str],
        *,
        count: int | None = None,
        block_ms: int | None = None,
    ) -> StreamReadResult:
        """Read messages for a consumer group from one or more streams."""
        ...

    async def acknowledge(
        self,
        stream_name: str,
        group_name: str,
        message_ids: Sequence[str],
    ) -> int:
        """Acknowledge one or more messages for the given consumer group."""
        ...

    async def delete_messages(
        self, stream_name: str, message_ids: Sequence[str]
    ) -> int:
        """Delete one or more messages from the given stream."""
        ...

    async def dispose(self) -> None:
        """Dispose the underlying event broker resources."""
        ...
