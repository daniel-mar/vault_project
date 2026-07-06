# tests/test_auth.py
import pytest
import logging
from tests.constants import USER_REGULAR_1, USER_ADMIN_1
from tests.helpers import establish_kyber_session

logger = logging.getLogger(__name__)

def test_pqc_handshake_flow_success(client):
    init_response = client.post("/api/v1/auth/pqc-handshake")
    assert init_response.status_code == 200
    
    data = init_response.json()
    server_pub_key = bytes.fromhex(data["server_public_key_hex"])
    session_id = data["session_id"]
    
    import oqs
    with oqs.KeyEncapsulation("Kyber768") as client_kem:
        ciphertext, _ = client_kem.encap_secret(server_pub_key)
    
    complete_response = client.post("/api/v1/auth/pqc-complete", json={
        "session_id": session_id,
        "ciphertext_hex": ciphertext.hex()
    })
    
    assert complete_response.status_code == 200
    logger.info("Handshake flow success.")


def test_handshake_invalid_ciphertext_length(client):
    init_response = client.post("/api/v1/auth/pqc-handshake")
    session_id = init_response.json()["session_id"]
    
    payload = {
        "session_id": session_id,
        "ciphertext_hex": "deadbeef" 
    }
    response = client.post("/api/v1/auth/pqc-complete", json=payload)
    
    assert response.status_code == 400
    assert "Invalid ciphertext length" in response.json()["detail"]
    logger.info("Invalid Ciphertext Length test passed! Short payload rejected.")


def test_handshake_invalid_session_id(client):
    response = client.post("/api/v1/auth/pqc-complete", json={
        "session_id": "fake_123", "ciphertext_hex": "A1B2" * 200
    })
    assert response.status_code == 404
    logger.info("Invalid session ID test passed.")


def test_create_and_login_regular_user(client):

    # Establish Quantum Tunnel first before sending data
    session_id = establish_kyber_session(client)
    logger.info("=== PQC Tunnel Established ===")

    # Attempt to create a user
    client.post("/api/v1/users/register", json=USER_REGULAR_1)
    logger.info("=== Created a new user ===")

    # Attempt to login with newly created user
    res = client.post("/api/v1/users/login", data={
        "username": USER_REGULAR_1["username"],
        "password": USER_REGULAR_1["password"],
        "session_id": session_id
    })
    print(res.json())
    logger.info("=== Successfully logged in user w. Qauntum Tunnel ===")

    assert res.status_code == 200