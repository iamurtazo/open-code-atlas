from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import User

from schemas import *


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

DB = Annotated[AsyncSession, Depends(get_db)]

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



# ===== CRUD Operations =====



# async def get_user_by_id(
#     db: AsyncSession, user_id: int,
#     load_enrollments: bool = False
# ) -> User | None:
#     stmt = select(User).where(User.id == user_id)
    
#     if load_enrollments:
#         stmt = stmt.options(selectinload(User.enrollments))
    
#     result = await db.execute(stmt)
#     return result.scalar_one_or_none()


# async def get_user_by_username(
#     db: AsyncSession, 
#     username: str,
#     load_enrollments: bool = False
# ) -> User | None:
#     stmt = select(User).where(User.username == username)
    
#     if load_enrollments:
#         stmt = stmt.options(selectinload(User.enrollments))
    
#     result = await db.execute(stmt)
#     return result.scalar_one_or_none()


# async def get_user_by_email(
#     db: AsyncSession, 
#     email: str,
#     load_enrollments: bool = False
# ) -> User | None:
#     stmt = select(User).where(User.email == email)
    
#     if load_enrollments:
#         stmt = stmt.options(selectinload(User.enrollments))
    
#     result = await db.execute(stmt)
#     return result.scalar_one_or_none()


# async def get_all_users(
#     db: AsyncSession,
#     skip: int = 0,
#     limit: int = 100,
#     load_enrollments: bool = False
# ) -> Sequence[User]:
    
#     stmt = select(User).offset(skip).limit(limit)
    
#     if load_enrollments:
#         stmt = stmt.options(selectinload(User.enrollments))
    
#     result = await db.execute(stmt)
#     return result.scalars().all()


# async def update_user(
#     db: AsyncSession,
#     user_id: int,
#     username: str | None = None,
#     email: str | None = None,
#     first_name: str | None = None,
#     last_name: str | None = None
# ) -> User | None:
#     user = await get_user_by_id(db, user_id)
#     if not user:
#         return None
    
#     # Check username uniqueness if changing
#     if username and username != user.username:
#         stmt = select(User).where(User.username == username)
#         result = await db.execute(stmt)
#         if result.scalar_one_or_none():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Username already exists"
#             )
#         user.username = username
    
#     # Check email uniqueness if changing
#     if email and email != user.email:
#         stmt = select(User).where(User.email == email)
#         result = await db.execute(stmt)
#         if result.scalar_one_or_none():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already exists"
#             )
#         user.email = email
    
#     # Update optional fields
#     if first_name is not None:
#         user.first_name = first_name
#     if last_name is not None:
#         user.last_name = last_name
    
#     await db.commit()
#     await db.refresh(user)
    
#     return user


# async def delete_user(db: AsyncSession, user_id: int) -> bool:
#     user = await get_user_by_id(db, user_id)
#     if not user:
#         return False
    
#     await db.delete(user)
#     await db.commit()
    
#     return True


# ===== API Endpoints =====

# @router.post("/users", status_code=status.HTTP_201_CREATED)
# async def create_user_endpoint(
#     username: str,
#     email: str,
#     first_name: str | None = None,
#     last_name: str | None = None,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Create a new user."""
#     user = await create_user(
#         db=db,
#         username=username,
#         email=email,
#         first_name=first_name,
#         last_name=last_name
#     )
#     return {
#         "id": user.id,
#         "username": user.username,
#         "email": user.email,
#         "first_name": user.first_name,
#         "last_name": user.last_name,
#         "created_at": user.created_at
#     }


# @router.get("/users/{user_id}")
# async def get_user_endpoint(
#     user_id: int,
#     load_enrollments: bool = False,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get a user by ID."""
#     user = await get_user_by_id(db, user_id, load_enrollments=load_enrollments)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     response = {
#         "id": user.id,
#         "username": user.username,
#         "email": user.email,
#         "first_name": user.first_name,
#         "last_name": user.last_name,
#         "created_at": user.created_at,
#         "updated_at": user.updated_at
#     }
    
#     if load_enrollments:
#         response["enrollments"] = [
#             {"id": e.id, "course_id": e.course_id, "enrolled_at": e.enrolled_at}
#             for e in user.enrollments
#         ]
    
#     return response


# @router.get("/users")
# async def get_all_users_endpoint(
#     skip: int = 0,
#     limit: int = 100,
#     load_enrollments: bool = False,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all users with pagination."""
#     users = await get_all_users(db, skip=skip, limit=limit, load_enrollments=load_enrollments)
    
#     return [
#         {
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "created_at": user.created_at
#         }
#         for user in users
#     ]


# @router.put("/users/{user_id}")
# async def update_user_endpoint(
#     user_id: int,
#     username: str | None = None,
#     email: str | None = None,
#     first_name: str | None = None,
#     last_name: str | None = None,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Update a user's information."""
#     user = await update_user(
#         db=db,
#         user_id=user_id,
#         username=username,
#         email=email,
#         first_name=first_name,
#         last_name=last_name
#     )
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     return {
#         "id": user.id,
#         "username": user.username,
#         "email": user.email,
#         "first_name": user.first_name,
#         "last_name": user.last_name,
#         "updated_at": user.updated_at
#     }


# @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user_endpoint(
#     user_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Delete a user."""
#     deleted = await delete_user(db, user_id)
#     if not deleted:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )

