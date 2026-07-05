# tests/test_users.py
import pytest
import jwt
import logging
from tests.constants import USER_A, USER_B
from tests.helpers import establish_kyber_session
from app.core.config import SESSIONS

logger = logging.getLogger(__name__)

def test_proof_of_session_isolation(client):
    # Setup User A
    client.post("/api/v1/users/register", json=USER_A)
    session_a = establish_kyber_session(client)
    token_a = client.post("/api/v1/users/login", data={"username": USER_A["username"], "password": USER_A["password"], "session_id": session_a}).json()["access_token"]
    
    # Setup User B
    client.post("/api/v1/users/register", json=USER_B)
    session_b = establish_kyber_session(client)
    
    kyber_secret_b = SESSIONS[session_b]["shared_secret"]
    
    # Proof
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token_a, kyber_secret_b, algorithms=["HS256"])
    
    logger.info("Session isolation proof passed.")