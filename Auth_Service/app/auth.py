"""
Authentication utilities: JWT tokens and password hashing.

This module handles:
1. Password hashing and verification (bcrypt)
2. JWT token creation and validation
3. User authentication logic
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings


# Password hashing context
# Why bcrypt:
# - Industry standard for password hashing
# - Adaptive: can increase rounds as computers get faster
# - Salted: same password produces different hashes
# - Slow by design: makes brute-force attacks impractical
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Process:
    1. Generate random salt (automatic)
    2. Combine password + salt
    3. Hash multiple rounds (default: 12 rounds)
    4. Return hash string

    Example:
        plain = "MyPassword123"
        hashed = hash_password(plain)
        # Result: "$2b$12$KIXvZ8..."

        # Same password, different hash (due to random salt):
        hash1 = hash_password("test")  # $2b$12$abc...
        hash2 = hash_password("test")  # $2b$12$xyz...

    Args:
        password: Plain-text password

    Returns:
        Bcrypt hash string (60 characters)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    Process:
    1. Extract salt from hash
    2. Hash plain_password with same salt
    3. Compare results (constant-time comparison)
    Example:
        stored_hash = "$2b$12$KIXvZ8..."

        verify_password("correct", stored_hash)  # True
        verify_password("wrong", stored_hash)    # False

    Args:
        plain_password: User-provided password
        hashed_password: Stored bcrypt hash

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    JWT Structure:
        Header.Payload.Signature
        Header:     {"alg": "HS256", "typ": "JWT"}
        Payload:    {"sub": "user@example.com", "exp": 1234567890}
        Signature:  HMAC-SHA256(header + payload, SECRET_KEY)

    Why JWT:
    - Stateless: No database lookup needed to verify token
    - Self-contained: All user info in the token
    - Portable: Works across services (microservices)
    - Standard: OAuth2, OpenID Connect use JWT

    Security considerations:
    - Don't store sensitive data in payload (it's base64, not encrypted)
    - Keep SECRET_KEY secret (anyone with it can create valid tokens)
    - Use HTTPS (tokens can be intercepted)
    - Set reasonable expiration (30 minutes typical)

    Example:
        token = create_access_token(
            data={"sub": "user@example.com"},
            expires_delta=timedelta(minutes=30)
        )
        # Result: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    Args:
        data: Dictionary to encode in token (usually {"sub": email})
        expires_delta: Token lifetime (default: from settings)

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiration to payload
    to_encode.update({"exp": expire})

    # Create and return JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Process:
    1. Decode header and payload
    2. Verify signature using SECRET_KEY
    3. Check expiration time
    4. Return payload if valid

    Common failure reasons:
    - Invalid signature (wrong SECRET_KEY or tampered token)
    - Expired token (exp < current time)
    - Malformed token (not valid JWT format)

    Example:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        payload = verify_token(token)
        if payload:
            email = payload.get("sub")
            print(f"Valid token for {email}")
        else:
            print("Invalid or expired token")

    Args:
        token: JWT token string
    Returns:
        Decoded payload dict if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Token is invalid, expired, or malformed
        return None


def get_password_hash(password: str) -> str:
    """
    Alias for hash_password for consistency with FastAPI examples.
    """
    return hash_password(password)