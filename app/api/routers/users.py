from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Form
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.users_schemas import UserCreate, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.core.config import USERS, BLACKLIST, SESSIONS
import token


router = APIRouter(prefix="/users", tags=["Users & Authentication"])

@router.post("/register", response_model=UserResponse)
def create_user(user: UserCreate):
    """
    Create a new user.
    """
    if user.username in USERS:
        raise HTTPException(status_code=400, detail="Username already registered")

    USERS[user.username] = {
        "password_hash": get_password_hash(user.password),
        "role": user.role
    }

    return UserResponse(username=user.username, role=user.role)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session_id: str = Form(...)):
    user_dict = USERS.get(form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    
    if session_id not in SESSIONS:
        raise HTTPException(status_code=400, detail="Invalid or expired session.")

    # Get Kyber768 shared secret from session
    kyber_secret = SESSIONS[session_id]["shared_secret"]

    # Session_id IN JWT payload for look-up later. Passes the dynamic key
    access_token = create_access_token(
        data={"sub": form_data.username, "role": user_dict["role"], "sid": session_id},
        signing_key=kyber_secret
    )
    return {"access_token": access_token, "token_type": "bearer"}
    
@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    # ******** Revisit this, possibly return logout message and delete session. ********
    BLACKLIST.add(current_user["token"])  # Add the token to the blacklist
    return {"detail": "Successfully logged out"}