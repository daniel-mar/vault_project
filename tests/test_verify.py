# tests/test_verify.py
import pytest
import oqs
import logging
from tests.constants import VALID_MESSAGE

logger = logging.getLogger(__name__)

def test_verify_signature_success(client):
    with oqs.Signature("ML-DSA-65") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(VALID_MESSAGE.encode('utf-8'))
        
    response = client.post("/api/v1/verify/document", json={
        "message": VALID_MESSAGE,
        "public_key_hex": public_key.hex(),
        "signature_hex": signature.hex()
    })
    assert response.status_code == 200
    logger.info("Signature verification success.")

def test_verify_signature_tampered_document(client):
    with oqs.Signature("ML-DSA-65") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(b"Original")
        
    response = client.post("/api/v1/verify/document", json={
        "message": "Tampered", 
        "public_key_hex": public_key.hex(),
        "signature_hex": signature.hex()
    })
    assert response.status_code == 401
    logger.info("Tamper detection test passed.")