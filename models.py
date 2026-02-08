from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    # Auto-generated fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC), 
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Required fields
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # Optional fields
    first_name: Mapped[str] = mapped_column(String(70), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)

    enrollments: Mapped[list[Enrollment]] = relationship(
        "Enrollment", 
        back_populates="user"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

 
class Course(Base):
    __tablename__ = "courses"
    
    # Auto-generated
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC), 
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Required fields
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    
    enrollments: Mapped[list[Enrollment]] = relationship(
        "Enrollment", 
        back_populates="course"
    ) 
    
    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}')>"
    

class Enrollment(Base):
    __tablename__ = "enrollments"

    # auto-generated
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"), 
        nullable=False
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC), 
        nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="enrollments")
    course: Mapped[Course] = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<Enrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id})>"