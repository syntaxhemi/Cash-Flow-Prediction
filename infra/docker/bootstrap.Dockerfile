FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/shared/database/src:/app/shared/domain/src:/app/shared/schemas/src"

RUN pip install --no-cache-dir \
    alembic==1.19.0 \
    asyncpg==0.31.0 \
    pydantic==2.13.4 \
    pydantic-settings==2.15.0 \
    sqlalchemy==2.0.51

COPY shared/database/src shared/database/src
COPY shared/domain/src shared/domain/src
COPY shared/schemas/src shared/schemas/src
COPY infra/migrations infra/migrations
COPY infra/seed infra/seed

CMD ["alembic", "-c", "infra/migrations/alembic.ini", "upgrade", "head"]
