from pydantic import BaseModel

class HandshakeInitResponse(BaseModel):
    server_public_key_hex: str
    session_id: str

class HandshakeCompleteRequest(BaseModel):
    session_id: str
    ciphertext_hex: str

class HandshakeCompleteResponse(BaseModel):
    status: str