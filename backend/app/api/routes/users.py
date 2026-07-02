"""
SPARK — User Routes
Now wired to real UserService.
"""

from typing import Any

from fastapi import APIRouter, Body

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response
from app.models.user import UpdateUserSettingsRequest
from app.services.user_service import UserService

router = APIRouter()
logger = get_logger(__name__)

_user_service = UserService()


@router.get("/users/me", summary="Get current user profile")
async def get_me(user: CurrentUser) -> dict[str, Any]:
    """Returns or creates the authenticated user's profile."""
    profile = _user_service.get_or_create_user(
        uid=user.uid,
        email=user.email or "",
        display_name=user.name or "",
        photo_url=user.picture,
    )
    return success_response(data=profile.model_dump())


@router.put("/users/me", summary="Update user settings")
async def update_me(
    user: CurrentUser,
    request: UpdateUserSettingsRequest = Body(...),
) -> dict[str, Any]:
    """Updates the authenticated user's settings."""
    _user_service.update_settings(user.uid, request)
    profile = _user_service.get_profile(user.uid)
    return success_response(
        data=profile.model_dump() if profile else {"uid": user.uid}
    )


@router.post("/users/me/onboard", summary="Complete onboarding")
async def complete_onboarding(user: CurrentUser) -> dict[str, Any]:
    """Marks onboarding as complete."""
    _user_service.complete_onboarding(user.uid)
    return success_response(data={"onboardingComplete": True})