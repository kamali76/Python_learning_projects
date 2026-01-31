"""
SQLAlchemy database models.

Models define the structure of database tables and relationships.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """
    User model representing the 'users' table in PostgreSQL.

    Table structure:
    - id: Auto-incrementing primary key
    - email: Unique, indexed for fast lookups during login
    - hashed_password: Bcrypt hash (NEVER store plain passwords!)
    - full_name: Optional display name
    - is_active: Soft delete / account disable flag
    - created_at: Automatic timestamp (set by database)

    Why these design choices:

    1. Email as unique identifier:
       - Users login with email
       - Index speeds up WHERE email = '...' queries
       - Unique constraint prevents duplicate accounts

    2. hashed_password instead of password:
       - Security best practice
       - Even if database is compromised, passwords are safe
       - Uses bcrypt (slow hashing = resistant to brute force)

    3. is_active flag:
       - Soft delete (preserve data, disable access)
       - Can reactivate accounts
       - Useful for compliance (GDPR, data retention)

    4. created_at with server_default:
       - Database sets timestamp (consistent across timezones)
       - func.now() uses PostgreSQL's CURRENT_TIMESTAMP
       - Automatically set, no manual code needed
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Auto-incrementing user ID"
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User's email address (used for login)"
    )

    hashed_password = Column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password"
    )

    full_name = Column(
        String(255),
        nullable=True,
        comment="User's full name (optional)"
    )

    is_active = Column(
        Boolean,
        default=True,
        comment="Account status (False = disabled/deleted)"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Account creation timestamp"
    )

    def __repr__(self):
        """String representation for debugging"""
        return f"<User(id={self.id}, email='{self.email}')>"

    def __str__(self):
        """Human-readable string"""
        return self.email