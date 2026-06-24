from pydantic import BaseModel

class VerifySignatureRequest(BaseModel):
    message: str
    public_key_hex: str
    signature_hex: str