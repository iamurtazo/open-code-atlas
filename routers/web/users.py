from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password
from database import get_db
from models import User

router = APIRouter(
    include_in_schema=False,
    tags=["Web Auth"]
)

templates = Jinja2Templates(directory="templates")

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/login", name="login")
async def login_page(request: Request):
    """Display login page"""
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@router.get("/signup", name="signup")
async def signup_page(request: Request):
    """Display registration page"""
    return templates.TemplateResponse(
        request,
        "signup.html",
        {"title": "Sign Up"},
    )


@router.post("/signup")
async def signup_user(
    db: DB,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
):
    """Handle signup form submission."""
    # Check username uniqueness (case-insensitive)
    result = await db.execute(
        select(User)
        .where(func.lower(User.username) == username.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{username}' already exists"
        )

    # Check email uniqueness (case-insensitive)
    result = await db.execute(
        select(User)
        .where(func.lower(User.email) == email.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{email}' already exists"
        )

    new_user = User(
        username=username,
        email=email.lower(),
        hashed_password=hash_password(password),
        first_name=first_name or None,
        last_name=last_name or None,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    response = JSONResponse(
        content={
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        },
        status_code=status.HTTP_201_CREATED,
    )
    response.set_cookie(key="user_id", value=str(new_user.id), httponly=True)
    return response


@router.post("/login")
async def login_user(
    db: DB,
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle login form submission."""
    result = await db.execute(
        select(User)
        .where(func.lower(User.username) == username.lower())
    )
    user = result.scalars().first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    response = JSONResponse(
        content={
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    )
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response


@router.get("/signout", name="signout")
async def signout_user():
    """Clear session cookie and redirect to home."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="user_id")
    return response


@router.get("/account", name="account")
async def account_page(request: Request):
    """Display account page"""
    if not request.state.user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account", "user": request.state.user},
    )