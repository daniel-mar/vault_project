from fastapi import HTTPException
import re

from app.schemas.auth_schemas import HandshakeCompleteRequest
from app.schemas.verify_schemas import VerifySignatureRequest
from app.core.config import SESSIONS


def verify_signature_dependency(payload: VerifySignatureRequest) -> dict:
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    if not (hex_pattern.match(payload.signature_hex) and hex_pattern.match(payload.public_key_hex)):
        raise HTTPException(status_code=400, detail="Malformed Input.")
    
    try:
        return {
            "msg": payload.message.encode('utf-8'),
            "sig": bytes.fromhex(payload.signature_hex),
            "key": bytes.fromhex(payload.public_key_hex)
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hex encoding.")
    

def get_session_data(payload: HandshakeCompleteRequest) -> dict:
    session_data = SESSIONS.get(payload.session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session expired or invalid.")
    return session_data