import pytest
from fastapi.testclient import TestClient
import oqs

# Import the app from your new modular structure
from app.main import app

client = TestClient(app)

# ==========================================
# --- SUCCESS TESTS (Happy Paths) ---
# ==========================================

def test_pqc_handshake_flow_success():
    """
    Tests the complete, successful Kyber768 handshake lifecycle.
    """
    # 1. Init Handshake (Get Server Public Key)
    init_response = client.post("/api/v1/auth/pqc-handshake")
    assert init_response.status_code == 200
    
    data = init_response.json()
    server_pub_key = bytes.fromhex(data["server_public_key_hex"])
    session_id = data["session_id"]
    
    # 2. Client performs Key Encapsulation Mechanism (KEM)
    with oqs.KeyEncapsulation("Kyber768") as client_kem:
        ciphertext, shared_secret = client_kem.encap_secret(server_pub_key)
    
    # 3. Complete Handshake
    payload = {
        "session_id": session_id,
        "ciphertext_hex": ciphertext.hex()
    }
    complete_response = client.post("/api/v1/auth/pqc-complete", json=payload)
    
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "Secure Channel Established"


def test_verify_signature_success():
    """
    Tests successful ML-DSA-65 document verification.
    """
    message = "Classified Vault Data"
    
    # Signer generates keys and signs the document
    with oqs.Signature("ML-DSA-65") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(message.encode('utf-8'))
        
    payload = {
        "message": message,
        "public_key_hex": public_key.hex(),
        "signature_hex": signature.hex()
    }
    
    response = client.post("/api/v1/verify/document", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"


# ==========================================
# --- FAILURE TESTS (Edge Cases) ---
# ==========================================

def test_handshake_invalid_session_id():
    """
    Tests that completing a handshake with a fake session ID fails properly.
    """
    payload = {
        "session_id": "fake_session_12345",
        "ciphertext_hex": "A1B2C3D4" * 200 # Arbitrary valid hex
    }
    
    response = client.post("/api/v1/auth/pqc-complete", json=payload)
    
    # Should be caught by the `get_session_data` dependency
    assert response.status_code == 404
    assert "Session expired or invalid" in response.json()["detail"]


def test_handshake_invalid_ciphertext_length():
    """
    Tests that sending ciphertext that isn't exactly 1088 bytes is rejected.
    """
    # Create a valid session first
    init_response = client.post("/api/v1/auth/pqc-handshake")
    session_id = init_response.json()["session_id"]
    
    payload = {
        "session_id": session_id,
        "ciphertext_hex": "deadbeef" # Valid hex, but way too short
    }
    
    response = client.post("/api/v1/auth/pqc-complete", json=payload)
    
    # Should be caught by our manual length check in the route
    assert response.status_code == 400
    assert "Invalid ciphertext length" in response.json()["detail"]


def test_verify_signature_tampered_document():
    """
    Tests that altering the message after it was signed results in a 401 Unauthorized.
    """
    original_message = "Approve $10"
    tampered_message = "Approve $10,000,000"
    
    with oqs.Signature("ML-DSA-65") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(original_message.encode('utf-8'))
        
    # We send the tampered text, but the original signature
    payload = {
        "message": tampered_message, 
        "public_key_hex": public_key.hex(),
        "signature_hex": signature.hex()
    }
    
    response = client.post("/api/v1/verify/document", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Signature mismatch."


def test_cryptographic_error_handler():
    """
    Tests our global exception handler for internal crypto crashes.
    """
    response = client.post("/api/v1/verify/debug/force-crash")
    
    # Even though it's an internal crash (500-level issue), 
    # our handler safely sanitizes it to a 400 to prevent data leakage.
    assert response.status_code == 400
    assert response.json()["detail"] == "Verification processing failed"