from collections.abc import Mapping, Sequence
from typing import cast

from redis.asyncio import Redis
from redis.exceptions import ResponseError
from redis.typing import EncodableT, KeyT, StreamIdT

from event_broker.config import EventBrokerSettings
from event_broker.interfaces import StreamFields, StreamReadResult


class EventBrokerManager:
    def __init__(self, settings: EventBrokerSettings) -> None:
        """Initialize the event broker manager.

        Args:
            settings: Settings used to build the Redis client.
        """
        self._settings = settings
        self._client: Redis | None = None

    async def initialize(self) -> None:
        """Initialize the async Redis client."""
        if self._client is not None:
            return
        self._client = Redis.from_url(
            self._settings.EVENT_BROKER_URL,
            decode_responses=True,
        )

    async def check_connection(self) -> None:
        """Verify that the event broker backend is reachable.

        Raises:
            RuntimeError: If the event broker has not been initialized.
        """
        await self.get_client().ping()

    def get_client(self) -> Redis:
        """Return the initialized async Redis client.

        Returns:
            The initialized Redis client.

        Raises:
            RuntimeError: If the event broker has not been initialized.
        """
        if self._client is None:
            raise RuntimeError('Event broker manager has not been initialized.')
        return self._client

    async def publish(
        self,
        stream_name: str,
        fields: StreamFields,
        *,
        maxlen: int | None = None,
        approximate: bool = True,
    ) -> str:
        """Publish a message to a Redis Stream.

        Args:
            stream_name: Target Redis Stream name.
            fields: Stream entry fields.
            maxlen: Optional stream length cap.
            approximate: Whether stream trimming may be approximate.

        Returns:
            The Redis Stream entry identifier.
        """
        stream_fields = cast(dict[EncodableT, EncodableT], dict(fields))
        message_id = await self.get_client().xadd(
            name=stream_name,
            fields=stream_fields,
            maxlen=(
                maxlen
                if maxlen is not None
                else self._settings.EVENT_BROKER_DEFAULT_STREAM_MAXLEN
            ),
            approximate=approximate,
        )
        return cast(str, message_id)

    async def create_consumer_group(
        self,
        stream_name: str,
        group_name: str,
        *,
        start_id: str = '$',
        mkstream: bool = False,
    ) -> None:
        """Create a consumer group for a Redis Stream.

        Args:
            stream_name: Target Redis Stream name.
            group_name: Consumer group name.
            start_id: Starting stream identifier.
            mkstream: Whether Redis should create the stream if missing.
        """
        try:
            await self.get_client().xgroup_create(
                name=stream_name,
                groupname=group_name,
                id=start_id,
                mkstream=mkstream,
            )
        except ResponseError as error:
            if 'BUSYGROUP' not in str(error):
                raise

    async def read_group(
        self,
        group_name: str,
        consumer_name: str,
        streams: Mapping[str, str],
        *,
        count: int | None = None,
        block_ms: int | None = None,
    ) -> StreamReadResult:
        """Read messages for a consumer group.

        Args:
            group_name: Consumer group to read from.
            consumer_name: Consumer identity within the group.
            streams: Stream names mapped to their last-delivered IDs.
            count: Optional maximum number of entries.
            block_ms: Optional blocking wait in milliseconds.

        Returns:
            Stream entries returned by `XREADGROUP`.
        """
        stream_map = cast(dict[KeyT, StreamIdT], dict(streams))
        entries = await self.get_client().xreadgroup(
            groupname=group_name,
            consumername=consumer_name,
            streams=stream_map,
            count=count,
            block=block_ms,
        )
        return cast(StreamReadResult, entries)

    async def acknowledge(
        self,
        stream_name: str,
        group_name: str,
        message_ids: Sequence[str],
    ) -> int:
        """Acknowledge messages for a consumer group.

        Args:
            stream_name: Target Redis Stream name.
            group_name: Consumer group that processed the messages.
            message_ids: Stream entry identifiers to acknowledge.

        Returns:
            Number of acknowledged messages.
        """
        return cast(
            int,
            await self.get_client().xack(stream_name, group_name, *message_ids),
        )

    async def delete_messages(
        self, stream_name: str, message_ids: Sequence[str]
    ) -> int:
        """Delete messages from a Redis Stream.

        Args:
            stream_name: Target Redis Stream name.
            message_ids: Stream entry identifiers to delete.

        Returns:
            Number of deleted messages.
        """
        return cast(int, await self.get_client().xdel(stream_name, *message_ids))

    async def dispose(self) -> None:
        """Dispose the async Redis client."""
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None
