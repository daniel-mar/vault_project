# tests/helpers.py
import oqs

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