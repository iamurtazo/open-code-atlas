from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import User

from schemas import *


router = APIRouter(
    prefix="/api/admin",
    tags=["admin - users"]
)

DB = Annotated[AsyncSession, Depends(get_db)]


# ── GET /api/admin/users ──
@router.get("/users", response_model=list[UserAdmin])
async def list_users(
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    load_enrollments: bool = Query(default=False),
):
    """List all users with pagination."""
    stmt = select(User).offset(skip).limit(limit)

    if load_enrollments:
        stmt = stmt.options(selectinload(User.enrollments))

    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


# ── POST /api/admin/users ──
@router.post("/users", response_model=UserAdmin, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserBase,
    db: DB
):
    """Create a new user."""
    stmt = await db.execute(
        select(User).where(
            (func.lower(User.username) == user.username.lower()) |
            (func.lower(User.email) == user.email.lower())
        )
    )
    existing_user = stmt.scalars().first()

    if existing_user:
        if existing_user.username.lower() == user.username.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user.username}' already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user.email}' already exists"
            )
    
    new_user = User(
        username=user.username,
        email=user.email.lower(),
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# ── GET /api/admin/users/{user_id} ──
@router.get("/users/{user_id}", response_model=UserAdmin)
async def get_user(
    user_id: int,
    db: DB,
    load_enrollments: bool = Query(default=False)
):
    
    stmt = select(User).where(User.id == user_id)
    if load_enrollments:
        stmt = stmt.options(selectinload(User.enrollments))

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


# ── GET /api/admin/users/{username} ──
@router.get("/users/{username}", response_model=UserAdmin)
async def get_user(
    username: str,
    db: DB,
    load_enrollments: bool = Query(default=False)
):
    
    stmt = select(User).where(User.username == username)
    if load_enrollments:
        stmt = stmt.options(selectinload(User.enrollments))

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found"
        )
    return user


# ── GET /api/admin/users/{email} ──
@router.get("/users/{email}", response_model=UserAdmin)
async def get_user(
    email: str,
    db: DB,
    load_enrollments: bool = Query(default=False)
):
    
    stmt = select(User).where(User.email == email)
    if load_enrollments:
        stmt = stmt.options(selectinload(User.enrollments))

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    return user


# ── PATCH /api/admin/users/{user_id} ──
@router.patch("/users/{user_id}", response_model=UserAdmin)
async def update_user(user_id: int, user_in: UserUpdate, db: DB):
    """Partially update a user. Only provided fields are changed."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )

    # Only get fields that were actually provided
    update_data = user_in.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    if "username" in update_data:
        result = await db.execute(
            select(User).where(
                func.lower(User.username) == update_data["username"].lower(),
                User.id != user_id,
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{update_data['username']}' is already taken",
            )


    if "email" in update_data:
        update_data["email"] = update_data["email"].lower()
        
        result = await db.execute(
            select(User).where(
                func.lower(User.email) == update_data["email"],
                User.id != user_id,
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{update_data['email']}' is already registered",
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


# ── DELETE /api/admin/users/{user_id} ──
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DB):
    """Delete a user by ID."""
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    await db.delete(user)
    await db.commit()
    return None