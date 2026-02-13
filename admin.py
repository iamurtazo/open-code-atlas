"""
SQLAdmin configuration — ModelView classes and authentication backend.
Provides a Django-like admin panel at /admin.
"""

from __future__ import annotations

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from core.security import hash_password, verify_password
from config import settings
from database import AsyncSessionLocal
from models import User, Course, Enrollment

from sqlalchemy import select


# ── Authentication Backend ──────────────────────────────────────────────


class AdminAuth(AuthenticationBackend):
    """Session-based admin authentication.

    Validates credentials against the User table using
    Argon2id password verification from core.security.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()

        if user is None or not verify_password(password, user.hashed_password):
            return False

        # Store minimal info in session
        request.session.update({"admin_user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin_user_id"))


# ── Model Views ─────────────────────────────────────────────────────────


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    # List page
    column_list = [
        User.id,
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.created_at,
    ]

    # Detail page — show everything except the hash
    column_details_exclude_list = [User.hashed_password]

    # Search / sort / filter
    column_searchable_list = [User.username, User.email, User.first_name, User.last_name]
    column_sortable_list = [User.id, User.username, User.email, User.created_at]
    column_default_sort = ("created_at", True)  # newest first

    # Export
    column_export_list = [
        User.id,
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.created_at,
    ]
    export_types = ["csv", "json"]
    export_max_rows = 0  # unlimited

    # Forms — never expose hashed_password directly
    form_excluded_columns = [
        User.hashed_password,
        User.created_at,
        User.updated_at,
        User.enrollments,
    ]

    # Create form will have a plain "password" field added via form_overrides
    form_include_pk = False

    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100]

    # Labels
    column_labels = {
        User.id: "ID",
        User.username: "Username",
        User.email: "Email",
        User.first_name: "First Name",
        User.last_name: "Last Name",
        User.created_at: "Created",
        User.updated_at: "Updated",
    }

    async def on_model_change(self, data: dict, model: User, is_created: bool, request: Request) -> None:
        """Hash the password when creating / editing a user through the admin panel."""
        if "password" in data and data["password"]:
            model.hashed_password = hash_password(data["password"])
        elif is_created:
            # Creating a user without a password — set a random unusable one
            model.hashed_password = hash_password("changeme")


class CourseAdmin(ModelView, model=Course):
    name = "Course"
    name_plural = "Courses"
    icon = "fa-solid fa-book"

    # List page
    column_list = [
        Course.id,
        Course.title,
        Course.description,
        Course.created_at,
    ]

    # Search / sort
    column_searchable_list = [Course.title, Course.description]
    column_sortable_list = [Course.id, Course.title, Course.created_at]
    column_default_sort = ("created_at", True)

    # Export
    column_export_list = [
        Course.id,
        Course.title,
        Course.description,
        Course.created_at,
    ]
    export_types = ["csv", "json"]
    export_max_rows = 0

    # Forms
    form_excluded_columns = [Course.created_at, Course.updated_at, Course.enrollments]
    form_include_pk = False

    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100]

    # Labels
    column_labels = {
        Course.id: "ID",
        Course.title: "Title",
        Course.description: "Description",
        Course.created_at: "Created",
        Course.updated_at: "Updated",
    }


class EnrollmentAdmin(ModelView, model=Enrollment):
    name = "Enrollment"
    name_plural = "Enrollments"
    icon = "fa-solid fa-graduation-cap"

    # List page
    column_list = [
        Enrollment.id,
        Enrollment.user,
        Enrollment.course,
        Enrollment.enrolled_at,
    ]

    # Search / sort
    column_searchable_list = [Enrollment.id]
    column_sortable_list = [Enrollment.id, Enrollment.enrolled_at]
    column_default_sort = ("enrolled_at", True)

    # Export
    column_export_list = [
        Enrollment.id,
        Enrollment.user_id,
        Enrollment.course_id,
        Enrollment.enrolled_at,
    ]
    export_types = ["csv", "json"]
    export_max_rows = 0

    # Forms
    form_excluded_columns = [Enrollment.enrolled_at]
    form_include_pk = False

    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100]

    # Labels
    column_labels = {
        Enrollment.id: "ID",
        Enrollment.user: "User",
        Enrollment.course: "Course",
        Enrollment.user_id: "User ID",
        Enrollment.course_id: "Course ID",
        Enrollment.enrolled_at: "Enrolled At",
    }


# ── Factory ──────────────────────────────────────────────────────────────


def create_admin(app, engine) -> Admin:
    """Create and configure the SQLAdmin instance."""
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

    admin = Admin(
        app=app,
        engine=engine,
        title="CodeAtlas Admin",
        authentication_backend=authentication_backend,
    )

    admin.add_view(UserAdmin)
    admin.add_view(CourseAdmin)
    admin.add_view(EnrollmentAdmin)

    return admin
