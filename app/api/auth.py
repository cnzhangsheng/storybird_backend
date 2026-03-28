"""API routes for authentication."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.exceptions import AuthenticationException
from app.models.schemas import (
    SendCodeRequest,
    VerifyCodeRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.services import get_auth_service
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """Get current user from JWT token."""
    user_id = auth_service.validate_token(credentials.credentials)
    return auth_service.get_current_user(user_id)


@router.post("/send-code", response_model=MessageResponse)
async def send_verification_code(
    request: SendCodeRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Send verification code to phone number."""
    message = auth_service.send_verification_code(request.phone)
    return MessageResponse(message=message)


@router.post("/verify", response_model=TokenResponse)
async def verify_code_and_login(
    request: VerifyCodeRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Verify code and login/register user."""
    return auth_service.verify_code(request.phone, request.code)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get current user information."""
    return UserResponse(**current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout user (client should discard token)."""
    return MessageResponse(message="已退出登录")