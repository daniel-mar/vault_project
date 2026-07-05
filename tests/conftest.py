# tests/conftest.py
import pytest
import logging
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import SESSIONS, USERS, BLACKLIST

# Configure standard Python logging for the test suite
logging.basicConfig(
    level=logging.INFO,
    format="\n[%(levelname)s] %(message)s"
)

@pytest.fixture(scope="module")
def client():
    """Provides a global TestClient instance."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    """Automatically resets in-memory data before every test."""
    USERS.clear()
    BLACKLIST.clear()
    # SESSIONS.clear() # Uncomment if you want sessions wiped between tests too