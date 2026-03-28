"""API routes for user settings."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.models.schemas import (
    UserResponse,
    UserUpdate,
    UserSettingsResponse,
    UserSettingsUpdate,
    UserStatsResponse,
)
from app.services import get_user_service
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    current_user: Annotated[dict, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Get current user profile."""
    return UserResponse(**current_user)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Update current user profile."""
    user = user_service.update_user(current_user["id"], update_data)
    return UserResponse(**user)


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: Annotated[dict, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Get user settings."""
    settings = user_service.get_user_settings(current_user["id"])
    return UserSettingsResponse(**settings)


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    update_data: UserSettingsUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Update user settings."""
    settings = user_service.update_user_settings(current_user["id"], update_data)
    return UserSettingsResponse(**settings)


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: Annotated[dict, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Get user statistics."""
    return user_service.get_user_stats(current_user["id"])