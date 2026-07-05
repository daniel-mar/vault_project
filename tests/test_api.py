# # tests/test_api.py
# import pytest
# import oqs
# import jwt
# import logging

# # Import from your new modular test files
# from tests.constants import USER_REGULAR, USER_ADMIN, USER_A, USER_B, VALID_MESSAGE
# from tests.helpers import establish_kyber_session

# # Import application state for the proof test
# from app.core.config import SESSIONS

# # Grab the logger configured in conftest.py
# logger = logging.getLogger(__name__)

# # ==========================================
# # --- SUCCESS TESTS (Happy Paths) ---
# # ==========================================

# def test_pqc_handshake_flow_success(client):
#     init_response = client.post("/api/v1/auth/pqc-handshake")
#     assert init_response.status_code == 200
    
#     data = init_response.json()
#     server_pub_key = bytes.fromhex(data["server_public_key_hex"])
#     session_id = data["session_id"]
    
#     with oqs.KeyEncapsulation("Kyber768") as client_kem:
#         ciphertext, shared_secret = client_kem.encap_secret(server_pub_key)
    
#     payload = {
#         "session_id": session_id,
#         "ciphertext_hex": ciphertext.hex()
#     }
#     complete_response = client.post("/api/v1/auth/pqc-complete", json=payload)
    
#     assert complete_response.status_code == 200
#     assert complete_response.json()["status"] == "Secure Channel Established"
#     logger.info(f"Handshake Flow test passed! Secure channel established for session: {session_id[:8]}...")


# def test_verify_signature_success(client):
#     with oqs.Signature("ML-DSA-65") as signer:
#         public_key = signer.generate_keypair()
#         signature = signer.sign(VALID_MESSAGE.encode('utf-8'))
        
#     payload = {
#         "message": VALID_MESSAGE,
#         "public_key_hex": public_key.hex(),
#         "signature_hex": signature.hex()
#     }
    
#     response = client.post("/api/v1/verify/document", json=payload)
    
#     assert response.status_code == 200
#     assert response.json()["status"] == "success"
#     logger.info("Signature Verification test passed! ML-DSA-65 validated successfully.")


# # ==========================================
# # --- FAILURE TESTS (Edge Cases) ---
# # ==========================================

# def test_handshake_invalid_session_id(client):
#     payload = {
#         "session_id": "fake_session_12345",
#         "ciphertext_hex": "A1B2C3D4" * 200
#     }
#     response = client.post("/api/v1/auth/pqc-complete", json=payload)
    
#     assert response.status_code == 404
#     assert "Session expired or invalid" in response.json()["detail"]
#     logger.info("Invalid Session ID test passed! Fake session properly rejected.")


# def test_handshake_invalid_ciphertext_length(client):
#     init_response = client.post("/api/v1/auth/pqc-handshake")
#     session_id = init_response.json()["session_id"]
    
#     payload = {
#         "session_id": session_id,
#         "ciphertext_hex": "deadbeef" 
#     }
#     response = client.post("/api/v1/auth/pqc-complete", json=payload)
    
#     assert response.status_code == 400
#     assert "Invalid ciphertext length" in response.json()["detail"]
#     logger.info("Invalid Ciphertext Length test passed! Short payload rejected.")


# def test_verify_signature_tampered_document(client):
#     tampered_message = "Approve $10,000,000"
    
#     with oqs.Signature("ML-DSA-65") as signer:
#         public_key = signer.generate_keypair()
#         signature = signer.sign(b"Approve $10")
        
#     payload = {
#         "message": tampered_message, 
#         "public_key_hex": public_key.hex(),
#         "signature_hex": signature.hex()
#     }
#     response = client.post("/api/v1/verify/document", json=payload)
    
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Signature mismatch."
#     logger.info("Tampered Document test passed! Forgery detected and rejected.")


# def test_cryptographic_error_handler(client):
#     response = client.post("/api/v1/verify/debug/force-crash")
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Verification processing failed"
#     logger.info("Crypto Error Handler test passed! Internal crash safely masked.")


# # ==========================================
# # --- USER & ADMIN TESTS ---
# # ==========================================

# def test_create_and_login_regular_user(client):
#     res_reg = client.post("/api/v1/users/register", json=USER_REGULAR)
#     assert res_reg.status_code == 200
    
#     session_id = establish_kyber_session(client)
    
#     res_login = client.post("/api/v1/users/login", data={
#         "username": USER_REGULAR["username"], 
#         "password": USER_REGULAR["password"],
#         "session_id": session_id
#     })
    
#     assert res_login.status_code == 200
#     assert "access_token" in res_login.json()
#     logger.info(f"Regular User Login test passed! Logged in as: {USER_REGULAR['username']}")


# def test_create_and_login_admin_user(client):
#     res_reg = client.post("/api/v1/users/register", json=USER_ADMIN)
#     assert res_reg.status_code == 200
#     assert res_reg.json()["role"] == "admin"
    
#     session_id = establish_kyber_session(client)
    
#     res_login = client.post("/api/v1/users/login", data={
#         "username": USER_ADMIN["username"], 
#         "password": USER_ADMIN["password"],
#         "session_id": session_id
#     })
    
#     assert res_login.status_code == 200
#     assert "access_token" in res_login.json()
#     logger.info(f"Admin User Login test passed! Elevated privileges confirmed for: {USER_ADMIN['username']}")


# # ==========================================
# # --- THE ARCHITECTURE PROOF TEST ---
# # ==========================================

# def test_proof_of_session_isolation(client):
#     # 1. Set up User A
#     assert client.post("/api/v1/users/register", json=USER_A).status_code == 200
#     session_a = establish_kyber_session(client)
#     token_a = client.post("/api/v1/users/login", data={"username": USER_A["username"], "password": USER_A["password"], "session_id": session_a}).json()["access_token"]
    
#     # 2. Set up User B
#     assert client.post("/api/v1/users/register", json=USER_B).status_code == 200
#     session_b = establish_kyber_session(client)
#     token_b = client.post("/api/v1/users/login", data={"username": USER_B["username"], "password": USER_B["password"], "session_id": session_b}).json()["access_token"]
    
#     # 3. Get User B's unique Kyber Secret
#     kyber_secret_b = SESSIONS[session_b]["shared_secret"]
    
#     # 4. THE PROOF
#     try:
#         jwt.decode(token_a, kyber_secret_b, algorithms=["HS256"])
#         assert False, "CRITICAL VULNERABILITY: Token A was validated using Token B's secret!"
#     except jwt.InvalidSignatureError:
#         logger.info("Session Isolation Proof passed! Token A is mathematically incompatible with Session B.")