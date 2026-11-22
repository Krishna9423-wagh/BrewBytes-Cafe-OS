import hashlib
import hmac
import base64
import json
import time
from fastapi import HTTPException, Header, Depends
from typing import Optional, List

JWT_SECRET = "brew_bytes_secret_key_2026_cafe_secure"
TOKEN_EXPIRY_SECONDS = 86400 * 7 # 7 days

def hash_password(password: str) -> str:
    salt = "brew_bytes_salt"
    return hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def b64_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding < 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode())

def create_access_token(data: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + TOKEN_EXPIRY_SECONDS

    header_b64 = b64_encode(json.dumps(header).encode())
    payload_b64 = b64_encode(json.dumps(payload).encode())

    message = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(JWT_SECRET.encode(), message, hashlib.sha256).digest()
    sig_b64 = b64_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")

        header_b64, payload_b64, sig_b64 = parts
        message = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(JWT_SECRET.encode(), message, hashlib.sha256).digest()

        if b64_encode(expected_sig) != sig_b64:
            raise HTTPException(status_code=401, detail="Invalid token signature")

        payload = json.loads(b64_decode(payload_b64).decode())
        if payload.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ")[1]
    return decode_access_token(token)

def require_role(allowed_roles: List[str]):
    def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role")
        if user_role not in allowed_roles and user_role != "owner":
            raise HTTPException(status_code=403, detail=f"Permission denied for role: {user_role}")
        return user
    return role_checker

