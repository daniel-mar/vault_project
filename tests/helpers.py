# tests/helpers.py
import oqs
import pytest
from tests.constants import USER_REGULAR_1, USER_REGULAR_2, USER__REGULAR_3, USER_ADMIN_1, USER_ADMIN_2, USER_ADMIN_3, BOOK_A, BOOK_B, BOOK_A_UPDATE

def establish_kyber_session(api_client) -> str:
    """Helper to perform the PQC handshake and return a valid session_id."""
    # 1. Init
    init_res = api_client.post("/api/v1/auth/pqc-handshake")
    data = init_res.json()
    server_pub_key = bytes.fromhex(data["server_public_key_hex"])
    session_id = data["session_id"]
    
    # 2. Encap
    with oqs.KeyEncapsulation("Kyber768") as client_kem:
        ciphertext, _ = client_kem.encap_secret(server_pub_key)
        
    # 3. Complete
    api_client.post("/api/v1/auth/pqc-complete", json={
        "session_id": session_id,
        "ciphertext_hex": ciphertext.hex()
    })
    
    return session_id


@pytest.fixture
def auth_client_user(client):
    """
    Flow: Quantum Tunnel -> Register -> Login -> Attach Token
    """
    # Establish PQC
    session_id = establish_kyber_session(client)

    # Register a user
    register_user_payload = USER_REGULAR_1.copy()
    register_user_payload["session_id"] = session_id

    client.post("/api/v1/users/register", json=register_user_payload)

    # Login with said user
    login_user_payload = {
        "username": USER_REGULAR_1["username"],
        "password": USER_REGULAR_1["password"],
        "session_id": session_id
    }
    # Generate Token
    token = client.post("/api/v1/users/login", data=login_user_payload).json()["access_token"]

    # Attach Token for subsequent requests
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return client

@pytest.fixture
def auth_client_admin(client):
    session_id = establish_kyber_session(client)

    register_admin_payload = USER_ADMIN_1.copy()
    register_admin_payload["session_id"] = session_id

    client.post("/api/v1/users/register", json=register_admin_payload)

    login_admin_payload = {
        "username": USER_ADMIN_1["username"],
        "password": USER_ADMIN_1["password"],
        "session_id": session_id
    }
    token = client.post("/api/v1/users/login", data=login_admin_payload).json()["access_token"]

    client .headers.update({"Authorization": f"Bearer {token}"})
    return client