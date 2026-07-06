from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt, token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.users_schemas import UserInDB
from app.core.config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, USERS, SESSIONS


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, signing_key: bytes):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Signing with Kyber bytes
    encoded_jwt = jwt.encode(to_encode, signing_key, algorithm=ALGORITHM)
    return encoded_jwt

# -- Dependencies --
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        session_id = unverified_payload.get("sid")

        if session_id not in SESSIONS:
            raise HTTPException(status_code=401, detail="Invalid or expired session.")
        
        # Get secret for this session
        kyber_secret = SESSIONS[session_id]["shared_secret"]
        
        # Verify signature
        payload = jwt.decode(token, kyber_secret, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")

        if username is None or username not in USERS:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        return UserInDB(
             username=username,
             role=role
        )
    
    except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")