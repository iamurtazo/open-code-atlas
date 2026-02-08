from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Course

from schemas import *


router = APIRouter(
    prefix="/api/admin",
    tags=["admin - courses"]
)

DB = Annotated[AsyncSession, Depends(get_db)]


# ── GET /api/admin/courses ──
@router.get("/courses", response_model=list[CourseResponse])
async def list_courses(
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    """List all courses with pagination."""
    stmt = select(Course).offset(skip).limit(limit)

    result = await db.execute(stmt)
    courses = result.scalars().all()
    return courses


# ── POST /api/admin/courses ──
@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: DB,
):
    """Create a new course."""
    # Check for duplicate title (case-insensitive)
    result = await db.execute(
        select(Course).where(
            func.lower(Course.title) == course.title.lower()
        )
    )
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with title '{course.title}' already exists",
        )

    new_course = Course(
        title=course.title,
        description=course.description,
    )

    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)
    return new_course


# ── GET /api/admin/courses/{course_id} ──
@router.get("/courses/{course_id}", response_model=CourseResponse | CourseWithUsers)
async def get_course(
    course_id: int,
    db: DB,
    load_enrollments: bool = Query(default=False),
):
    """Get a single course by ID. Optionally load enrollments."""
    stmt = select(Course).where(Course.id == course_id)

    if load_enrollments:
        stmt = stmt.options(selectinload(Course.enrollments))

    result = await db.execute(stmt)
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found",
        )
    return course


# ── PATCH /api/admin/courses/{course_id} ──
@router.patch("/courses/{course_id}", response_model=CourseResponse)
async def update_course(course_id: int, course_in: CourseUpdate, db: DB):
    """Partially update a course. Only provided fields are changed."""

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found",
        )

    update_data = course_in.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    # Check title uniqueness if being updated
    if "title" in update_data:
        result = await db.execute(
            select(Course).where(
                func.lower(Course.title) == update_data["title"].lower(),
                Course.id != course_id,
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Course with title '{update_data['title']}' already exists",
            )

    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)
    return course


# ── DELETE /api/admin/courses/{course_id} ──
@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, db: DB):
    """Delete a course by ID."""
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found",
        )

    await db.delete(course)
    await db.commit()
    return None
