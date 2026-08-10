FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY . .
RUN uv sync --frozen --no-dev

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY apps/worker/src apps/worker/src
COPY shared/domain/src shared/domain/src
COPY shared/schemas/src shared/schemas/src
COPY shared/database/src shared/database/src
COPY shared/ml/src shared/ml/src
COPY shared/integrations/src shared/integrations/src
COPY shared/event_broker/src shared/event_broker/src

CMD ["python", "-m", "worker.main"]
