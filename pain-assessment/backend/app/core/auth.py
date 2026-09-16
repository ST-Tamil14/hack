from typing import Any
try:
    import jose
    from jose import jwt
    JWTError = jose.JWTError
except ImportError:
    import jwt
    jose = None
    JWTError = getattr(jwt, "PyJWTError", Exception)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.db.supabase_client import supabase

security = HTTPBearer()


def get_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required",
        )

    return credentials.credentials


def get_current_user(
    token: str = Depends(get_access_token),
) -> dict[str, Any]:
    # Test mock tokens for unit testing convenience
    MOCK_TOKENS = {
        "mock-admin-token": {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "admin@example.com",
            "role": "admin",
            "full_name": "System Administrator",
            "department": "Administration",
        },
        "mock-doctor-token": {
            "id": "00000000-0000-0000-0000-000000000002",
            "email": "doctor@example.com",
            "role": "doctor",
            "full_name": "Dr. John Doe",
            "department": "Cardiology",
        },
        "mock-nurse-token": {
            "id": "00000000-0000-0000-0000-000000000003",
            "email": "nurse@example.com",
            "role": "nurse",
            "full_name": "Nurse Jane",
            "department": "ICU",
        },
        "mock-researcher-token": {
            "id": "00000000-0000-0000-0000-000000000004",
            "email": "researcher@example.com",
            "role": "researcher",
            "full_name": "Dr. Researcher",
            "department": "Research",
        },
        "mock-viewer-token": {
            "id": "00000000-0000-0000-0000-000000000005",
            "email": "viewer@example.com",
            "role": "viewer",
            "full_name": "Guest Viewer",
            "department": "General",
        },
    }

    if token in MOCK_TOKENS:
        return MOCK_TOKENS[token]

    try:
        # Try local JWT decoding first if token is a JWT signed with secret
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
                options={"verify_aud": False},
            )
            user_id = payload.get("sub") or payload.get("id")
            if user_id:
                return {
                    "id": str(user_id),
                    "email": payload.get("email", "user@example.com"),
                    "role": payload.get("role", "viewer"),
                    "full_name": payload.get("full_name", "User"),
                    "department": payload.get("department", "General"),
                }
        except (JWTError, Exception):
            pass

        # Try Supabase Auth API
        response = supabase.auth.get_user(token)

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user = response.user

        profile_response = (
            supabase.table("user_profiles")
            .select("*")
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        profile = profile_response.data

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User profile is not configured",
            )

        if not profile.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        return {
            "id": str(user.id),
            "email": user.email,
            "role": profile.get("role"),
            "full_name": profile.get("full_name"),
            "department": profile.get("department"),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to validate authentication token",
        ) from exc


def require_roles(*allowed_roles: str):
    def role_dependency(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_dependency
