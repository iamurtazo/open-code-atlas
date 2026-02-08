from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import select

from database import AsyncSessionLocal
from models import User


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Reads 'user_id' cookie on every request.
    If valid, attaches User object to request.state.user.
    Templates can then use {% if user %} conditionals.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.user = None

        user_id = request.cookies.get("user_id")
        if user_id:
            try:
                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(User).where(User.id == int(user_id))
                    )
                    request.state.user = result.scalars().first()
            except (ValueError, Exception):
                pass

        response = await call_next(request)
        return response
