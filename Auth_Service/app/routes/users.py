"""
User authentication routes.

Endpoints:
- POST /auth/register: Create new user account
- POST /auth/login: Login and get JWT token
- GET /auth/me: Get current user info (protected)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Token
from ..auth import hash_password, verify_password, create_access_token, verify_token


# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# OAuth2 scheme for JWT
# tokenUrl: Tells Swagger UI where to get tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    Process:
    1. Check if email already exists
    2. Hash the password
    3. Create user in database
    4. Return user info (without password)

    Security:
    - Password is hashed before storage
    - Duplicate emails are rejected
    - Response doesn't include password

    Example Request:
        POST /auth/register
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe"
        }

    Example Response (201):
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "John Doe",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }

    Errors:
        400: Email already registered
        422: Validation error (invalid email, password too short)
    """

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.full_name
    )

    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Reload from DB to get generated fields (id, created_at)

    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Login and receive JWT access token.

    OAuth2PasswordRequestForm provides:
    - username: In our case, this is the email
    - password: Plain-text password
    - scope: Optional permissions (not used here)

    Process:
    1. Find user by email
    2. Verify password
    3. Create JWT token
    4. Return token

    Security:
    - Generic error message (don't reveal if email exists)
    - Password verified using constant-time comparison
    - Token expires after configured time

    Example Request:
        POST /auth/login
        Content-Type: application/x-www-form-urlencoded

        username=user@example.com&password=SecurePass123!

    Example Response (200):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }

    Usage:
        Include token in subsequent requests:
        Authorization: Bearer <access_token>

    Errors:
        401: Invalid email or password
        422: Validation error
    """

    # Find user (username field contains email)
    user = db.query(User).filter(User.email == form_data.username).first()

    # Verify credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Generic error (don't reveal if email exists)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current user from JWT token.

    This is a FastAPI dependency used to protect routes.

    Process:
    1. Extract token from Authorization header
    2. Verify and decode token
    3. Get user from database
    4. Return user object

    Usage in routes:
        @router.get("/protected")
        async def protected_route(
            current_user: User = Depends(get_current_user)
        ):
            return {"message": f"Hello {current_user.email}"}

    How it works:
    - oauth2_scheme extracts "Bearer <token>" from header
    - verify_token checks signature and expiration
    - Query database for user
    - Return user or raise 401

    Errors:
        401: Invalid token, expired token, or user not found
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify and decode token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    # Extract email from token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current authenticated user's information.

    This is a protected route - requires valid JWT token.

    Example Request:
        GET /auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200):
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "John Doe",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
    Errors:
        401: No token provided, invalid token, or expired token
    """
    return current_user


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Used by:
    - Load balancers
    - Monitoring systems
    - Container orchestration (Kubernetes, ECS)

    Returns:
        200: Service is healthy
    """
    return {"status": "healthy", "service": "auth"}