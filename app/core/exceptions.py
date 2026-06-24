from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("vault-api")

class CryptographicError(Exception):
    """Raised on internal cryptographic library failure (OQS library)."""
    def __init__(self, message: str, internal_error: str = None):
        self.message = message
        self.internal_error = internal_error
        super().__init__(self.message)


async def crypto_exception_handler(request: Request, exc: CryptographicError):
    """Global handler that intercepts CryptographicErrors and logs them safely."""
    # Handle IP for logging
    client_ip = request.client.host if request.client else "Unknown/TestClient"

    logger.error(
        f"CRITICAL_CRYPTO_LIB_FAILRUE | Endpoint: {request.url.path} | "
        f"IP: {client_ip} | Internal Error: {exc.internal_error}"
    )
    return JSONResponse(status_code=400, content={"detail": exc.message})