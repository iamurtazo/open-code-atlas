from fastapi import APIRouter, Depends, HTTPException
from typing import List


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

# @router.get()
