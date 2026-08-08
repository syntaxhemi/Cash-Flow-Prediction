import logging

from domain.exceptions import DomainError
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.core.errors.mapping import get_domain_error_mapping

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register structured application exception handlers.

    Args:
        app: FastAPI application receiving the handlers.
    """

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        """Convert a domain error into a JSON response."""
        _ = request
        mapping = get_domain_error_mapping(exc)
        return JSONResponse(
            status_code=mapping.status_code,
            content={'error': {'code': mapping.error_code, 'message': str(exc)}},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Convert request validation failures into a JSON response."""
        _ = request
        return JSONResponse(
            status_code=422,
            content={
                'error': {
                    'code': 'request_validation_error',
                    'message': 'Request validation failed.',
                    'details': exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        """Log unexpected failures and return a generic error response."""
        logger.exception(
            'Unhandled exception.',
            extra={'request_method': request.method, 'request_path': request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={
                'error': {
                    'code': 'internal_server_error',
                    'message': 'An unexpected error occurred.',
                }
            },
        )
