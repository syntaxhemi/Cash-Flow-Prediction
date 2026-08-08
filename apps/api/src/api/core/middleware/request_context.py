import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = 'X-Request-ID'
logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        """Attach request IDs and log completed requests.

        Args:
            request: Incoming HTTP request.
            call_next: Downstream ASGI handler.

        Returns:
            Response with a propagated request ID header.
        """
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
        request.state.request_id = request_id
        started_at = perf_counter()
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            'Request completed.',
            extra={
                'request_id': request_id,
                'request_method': request.method,
                'request_path': request.url.path,
                'response_status_code': response.status_code,
                'duration_ms': round((perf_counter() - started_at) * 1000, 2),
            },
        )
        return response


def add_request_context_middleware(app: FastAPI) -> None:
    """Register request context middleware.

    Args:
        app: FastAPI application receiving the middleware.
    """
    app.add_middleware(RequestContextMiddleware)
