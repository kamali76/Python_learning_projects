"""
Pydantic schemas for request/response validation.

Schemas vs Models:
- Pydantic schemas: API layer (validation, serialization)
- SQLAlchemy models: Database layer (persistence)

Why separate schemas:
- Different requirements (API vs Database)
- Security (don't expose password in responses)
- Flexibility (API can differ from database structure)
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Base user schema with common fields.

    Other schemas inherit from this to avoid repetition.
    """
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for user registration (POST /auth/register).

    Validations:
    - email: Must be valid email format (handled by EmailStr)
    - password: Minimum 8 characters
    - full_name: Optional

    Example valid request:
    {
        "email": "user@example.com",
        "password": "SecurePass123!",
        "full_name": "John Doe"
    }

    Example invalid requests:
    {
        "email": "not-an-email",  # ❌ Invalid email format
        "password": "short"        # ❌ Too short (< 8 chars)
    }
    """
    password: str = Field(
        ...,  # Required field
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }
    )


class UserLogin(BaseModel):
    """
    Schema for login request (POST /auth/login).

    Note: FastAPI's OAuth2PasswordRequestForm is used instead
    in actual endpoint (for OAuth2 compatibility), but this
    schema documents the expected fields.
    """
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class UserResponse(UserBase):
    """
    Schema for user data in responses (GET /auth/me, POST /auth/register).

    SECURITY: Notice password is NOT included!
    Never send passwords (even hashed) in API responses.

    from_attributes: Allows Pydantic to read from SQLAlchemy model:
        db_user = User(email="...", ...)
        user_response = UserResponse.from_orm(db_user)
    """
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class Token(BaseModel):
    """
    Schema for JWT token response (POST /auth/login).

    OAuth2 standard requires:
    - access_token: The JWT token string
    - token_type: Always "bearer" for JWT

    Client usage:
        Authorization: Bearer <access_token>
    """
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    """
    Schema for decoded JWT token payload.

    Used internally to validate token contents.
    Not exposed in API responses.

    JWT payload contains:
    - sub: Subject (user email in our case)
    - exp: Expiration timestamp (set automatically)
    """
    email: Optional[str] = None