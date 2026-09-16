from fastapi import APIRouter, Depends

from app.core.auth import get_current_user

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health_check(
    current_user: dict = Depends(get_current_user),
):
    return {
        "status": "healthy",
        "service": "pain-assessment-backend",
        "authenticated_user": current_user["email"],
        "role": current_user["role"],
    }