import os
import httpx
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWKS_URL = os.environ.get("CLERK_JWKS_URL", "")
AUD = os.environ.get("CLERK_AUD", "")  # e.g., "atom-api"
HMAC_SECRET = os.environ.get("CLERK_SECRET_KEY", "")
SCHEME = HTTPBearer()

_jwk_client = None

async def verify_jwt(creds: HTTPAuthorizationCredentials = Depends(SCHEME)):
    token = creds.credentials
    # Prefer JWKS (RS256); fallback to HMAC if configured
    if JWKS_URL and AUD:
        global _jwk_client
        if _jwk_client is None:
            _jwk_client = PyJWKClient(JWKS_URL)
        try:
            signing_key = _jwk_client.get_signing_key_from_jwt(token)
            decoded = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience=AUD)
            return decoded
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    elif HMAC_SECRET:
        try:
            decoded = jwt.decode(token, HMAC_SECRET, algorithms=["HS256"])  # audience optional in HMAC mode
            return decoded
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="auth not configured") 