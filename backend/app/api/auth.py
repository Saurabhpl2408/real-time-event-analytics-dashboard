from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta

from app.core.database import get_db
from app.models.users import User, UserRole
from app.schemas_pydantic.auth import (
    UserCreate, UserLogin, UserResponse, TokenResponse, APIKeyResponse
)
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register new user (first user becomes admin)"""
    
    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Check if this is the first user (make them admin)
    result = await db.execute(select(User))
    user_count = len(result.scalars().all())
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=User.hash_password(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.ADMIN if user_count == 0 else UserRole[user_data.role.upper()],
        is_active=True,
        is_verified=True  # Auto-verify for now
    )
    
    # Generate API key
    user.generate_api_key()
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(**user.to_dict())


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    
    # Find user
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value}
    )
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(**user.to_dict())
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(**current_user.to_dict())


@router.post("/api-key", response_model=APIKeyResponse)
async def generate_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate new API key for current user"""
    
    current_user.generate_api_key()
    await db.commit()
    
    return APIKeyResponse(
        api_key=current_user.api_key,
        user_id=str(current_user.id),
        created_at=datetime.now(timezone.utc).isoformat()
    )


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)"""
    
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    return [UserResponse(**user.to_dict()) for user in users]