from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def create_session_factory(
    engine: AsyncEngine,
    *,
    expire_on_commit: bool = False,
) -> async_sessionmaker[AsyncSession]:
    """Create an async SQLAlchemy session factory.

    Args:
        engine: Async engine used by created sessions.
        expire_on_commit: Whether ORM instances expire after commit.

    Returns:
        Configured async session factory.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=expire_on_commit,
    )
