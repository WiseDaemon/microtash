import hmac
import hashlib
import json
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> Tuple[str, str]:
    """Hashes a password with PBKDF2-HMAC-SHA256 (100,000 rounds) and a cryptographic salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return pwd_hash, salt

def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a plain password against the stored PBKDF2 hash using constant-time comparison."""
    computed_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return hmac.compare_digest(computed_hash, stored_hash)

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64url_decode(s: str) -> bytes:
    padding = '=' * (4 - (len(s) % 4)) if len(s) % 4 != 0 else ''
    return base64.urlsafe_b64decode(s + padding)

def create_access_token(
    user_id: str,
    username: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> Tuple[str, datetime]:
    """Generates an RFC 7519 compliant HMAC-SHA256 JWT access token."""
    now = datetime.utcnow()
    delta = expires_delta or timedelta(days=settings.JWT_EXPIRY_DAYS)
    exp = now + delta

    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user_id,
        "username": username,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }

    header_b64 = _b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')

    signature = hmac.new(settings.JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    token = f"{header_b64}.{payload_b64}.{sig_b64}"
    return token, exp

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Validates signature and expiration of an access token."""
    try:
        parts = token.strip().split('.')
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(settings.JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))

        # Check expiration
        exp_ts = payload.get("exp")
        if not exp_ts or datetime.utcnow().timestamp() > exp_ts:
            return None

        return payload
    except Exception:
        return None

async def get_current_user(
    request: Request,
    auth: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the Bearer token or session cookie.
    Raises 401 if unauthenticated.
    """
    token = None
    if auth and auth.credentials:
        token = auth.credentials
    elif "Authorization" in request.headers:
        auth_hdr = request.headers["Authorization"]
        if auth_hdr.lower().startswith("bearer "):
            token = auth_hdr[7:].strip()
    elif "microstash_session" in request.cookies:
        token = request.cookies["microstash_session"]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate active session against database
    from app import database
    session_user = database.validate_session_token(token)
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been terminated or logged out. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_user["token"] = token
    return session_user

async def get_optional_user(
    request: Request,
    auth: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[Dict[str, Any]]:
    """Graceful auth dependency: returns user dict if valid session, else None."""
    try:
        return await get_current_user(request, auth)
    except HTTPException:
        return None
