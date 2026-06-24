from fastapi import FastAPI
import logging

# Import routers and handlers
from app.api.routers import auth, verify
from app.core.exceptions import CryptographicError, crypto_exception_handler

# Configure global logger (instead of printing)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vault-api")

# Initialize App
app = FastAPI(title="Post-Quantum Secure Vault API", version="2.0.0")

# Register Custom Exception Handlers
app.add_exception_handler(CryptographicError, crypto_exception_handler)

# Include Routers (Mounts them to the main app)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(verify.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)