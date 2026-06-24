from fastapi import APIRouter, Depends, HTTPException
import oqs


from app.api.dependencies import verify_signature_dependency
from app.core.exceptions import CryptographicError


# Create router for 'verification' domain
router = APIRouter(prefix="/verify", tags=["Document Verification"])

@router.post("/document")
def verify_document_signature(valid_data: dict = Depends(verify_signature_dependency)):
    # Dependency (depends) has handled regex and hex conversion
    with oqs.Signature("ML-DSA-65") as verifier:
        try:
            is_valid = verifier.verify(valid_data["msg"], valid_data["sig"], valid_data["key"])
        except Exception as e:
            raise CryptographicError(
                message="Verification processing failed",
                internal_error=str(e)
            )
        
        if is_valid:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=401, detail="Signature mismatch.")


# Debugging Route - Triggers a verification error
@router.post("/debug/force-crash", include_in_schema=False)
def force_crash():
    """Forced a CryptographicError to test logging"""
    raise CryptographicError(
        message="Verification processing failed",
        internal_error="Forced test error"
    )