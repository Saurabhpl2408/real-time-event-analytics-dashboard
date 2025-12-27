from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import hashlib
import secrets
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    
    full_name = Column(String(200))
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    api_key = Column(String(64), unique=True, index=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True))
    
    def generate_api_key(self):
        """Generate a unique API key"""
        self.api_key = secrets.token_urlsafe(32)
        return self.api_key
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return self.hashed_password == self.hash_password(password)
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "role": self.role.value,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data["api_key"] = self.api_key
        
        return data