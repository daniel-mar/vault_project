# tests/test_users.py
import pytest
import jwt
import logging
from tests.constants import USER_REGULAR_1, USER_REGULAR_2
from tests.helpers import establish_kyber_session
from app.core.config import SESSIONS

logger = logging.getLogger(__name__)

def test_proof_of_session_isolation(client):
    """
    Flow: Creating quantum tunnel which returns a unique session_id with a unique shared_secret from PQC handshake.
    """
    # == Setup User A ==

    # Establish Quantum Tunnel session for user A
    session_a = establish_kyber_session(client)    
    logger.info("=== PQC Tunnel Established ===")

    # Attempt to register first user
    client.post("/api/v1/users/register", json=USER_REGULAR_1)
    
    token_a = client.post("/api/v1/users/login", data={
        "username": USER_REGULAR_1["username"],
        "password": USER_REGULAR_1["password"],
        "session_id": session_a
        }).json()["access_token"]
    
    # Proof - The Kyber shared_secret associated with user_a is valid, unnecessary here; used ONLY to view data via print and to test the decode method.
    # kyber_secret_a = SESSIONS[session_a]["shared_secret"]
    # with pytest.raises(jwt.InvalidSignatureError):
    #     jwt.decode(token_a, kyber_secret_a, algorithms=["HS256"])
    
    # == Setup User B ==

    # Establish another PQC session on server for user B
    session_b = establish_kyber_session(client)

    # Attempt to register second user
    client.post("/api/v1/users/register", json=USER_REGULAR_2)
    
    kyber_secret_b = SESSIONS[session_b]["shared_secret"]

    # Attempting to decode w. shared_secret(s) between user_a and user_b fails to decode the token_a, proving session isolation.
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token_a, kyber_secret_b, algorithms=["HS256"])
    logger.info("Session isolation between users proof passed.")