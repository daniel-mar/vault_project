import os

# ================================
# --- Cryptographic Constants ---
# ================================
KYBER768_CIPHERTEXT_LENGTH = 1088

# ================================
#        --- SECURITY ---
# ================================
# In production, ALWAYS load this from environment variables
# SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-quantum-key-for-jwt-signing") # Replaced with Kyber768 shared secret from session
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ================================
#        --- MOCK DATABASE ---
# ================================

SESSIONS = {}           # In memory session storage (this could be Redis)

USERS = {}              # {"username": {"password_hash": "...", "role": "admin|user"}}
BOOKS = {}              # {"book_id": {"title": "...", "author": "..."}}
BLACKLIST = set()       # Revoked JWT tokens