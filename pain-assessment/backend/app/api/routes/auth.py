from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.auth import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]


@router.post("/token", response_model=TokenResponse)
@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    email = form_data.username
    role = "clinician"
    if "admin" in email.lower():
        role = "admin"
    elif "doctor" in email.lower():
        role = "doctor"
    elif "nurse" in email.lower():
        role = "nurse"
    elif "researcher" in email.lower():
        role = "researcher"

    user_info = {
        "id": "u-101",
        "email": email,
        "full_name": email.split("@")[0].replace(".", " ").title(),
        "role": role,
        "department": "Clinical Care",
    }

    return {
        "access_token": f"mock-token-{role}",
        "token_type": "bearer",
        "user": user_info,
    }


@router.get("/me")
def read_users_me(
    current_user: dict = Depends(get_current_user),
):
    return current_user
