from fastapi import APIRouter, Depends, HTTPException
import oqs
import secrets

# Import custom modules
from app.schemas.auth_schemas import HandshakeInitResponse, HandshakeCompleteRequest, HandshakeCompleteResponse
from app.api.dependencies import get_session_data
from app.core.config import SESSIONS, KYBER768_CIPHERTEXT_LENGTH
from app.core.exceptions import logger


# Create router for 'auth' domain
router = APIRouter(prefix="/auth", tags=["Post-Quantum Authentication"])

@router.post("/pqc-handshake", response_model=HandshakeInitResponse)
def init_pqc_handshake():
    try:
        with oqs.KeyEncapsulation("Kyber768") as server_kem:
            public_key = server_kem.generate_keypair()
            secret_key_bytes = server_kem.export_secret_key()
            session_id = secrets.token_urlsafe(32)
        
        SESSIONS[session_id] = {"secret_key": secret_key_bytes}
        return HandshakeInitResponse(
            server_public_key_hex=public_key.hex(),
            session_id=session_id
                                     )

    except Exception as e:
        raise HTTPException(status_code=500, detail="KEM Initialization Failure.")
    

@router.post("/pqc-complete", response_model=HandshakeCompleteResponse)
def complete_pqc_handshake(
    payload: HandshakeCompleteRequest,
    session: dict = Depends(get_session_data)
):
    try:
        ciphertext = bytes.fromhex(payload.ciphertext_hex)
        if len(ciphertext) != KYBER768_CIPHERTEXT_LENGTH:
            raise ValueError(f"Invalid ciphertext length: expected {KYBER768_CIPHERTEXT_LENGTH} bytes.")
        
        # Re-instantiate KEM Object from stored secret key bytes
        with oqs.KeyEncapsulation("Kyber768", secret_key=session["secret_key"]) as server_kem:
            shared_secret = server_kem.decap_secret(ciphertext)

        # Clean session on success
        del SESSIONS[payload.session_id]

        # Todo: use 'shared_secret' to generate a JWT or symmetric session key


        return HandshakeCompleteResponse(status="Secure Channel Established")
    
    except ValueError as ve:
        if payload.session_id in SESSIONS:
            del SESSIONS[payload.session_id]
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        if payload.session_id in SESSIONS:
            del SESSIONS[payload.session_id]
        
        # Using logger instead of print()
        logger.error(f"Decapsulation internal error: {str(e)}")
        raise HTTPException(status_code=400, detail="Decapsulation failed: Cryptographic error.")