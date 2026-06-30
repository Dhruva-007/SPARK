"""
SPARK — User Routes
User profile management and first-time onboarding.

First sign-in flow:
  1. Firebase Auth verifies the token (handled by dependency)
  2. GET /users/me is called by the frontend after sign-in
  3. If no Firestore user document exists, one is created automatically
  4. The user document seeds all future genome and task operations
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


def _get_user_document(user_id: str) -> dict | None:
    """
    Fetches the user document from Firestore.
    Returns None if the document does not exist.
    Separated for reuse and testability.
    """
    try:
        from app.core.firebase import get_firestore
        db = get_firestore()
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as exc:
        logger.warning("Could not fetch user document", uid=user_id, error=str(exc))
        return None


def _create_user_document(user: CurrentUser) -> dict:  # type: ignore[valid-type]
    """
    Creates the initial user document in Firestore.
    Called only on first sign-in.
    Returns the created document data.
    """
    from app.core.firebase import get_firestore
    from app.core.config import get_settings

    settings = get_settings()
    db = get_firestore()

    now = datetime.now(timezone.utc).isoformat()

    user_data: dict[str, Any] = {
        "uid": user.uid,
        "email": user.email or "",
        "displayName": user.name or "",
        "photoURL": user.picture or None,
        "createdAt": now,
        "lastActiveAt": now,
        "onboardingComplete": False,
        "settings": {
            "timezone": "UTC",
            "workingHoursStart": "09:00",
            "workingHoursEnd": "17:00",
            "workingDays": [1, 2, 3, 4, 5],
            "notificationsEnabled": True,
            "calendarConnected": False,
            "gmailConnected": False,
        },
    }

    db.collection("users").document(user.uid).set(user_data)
    logger.info("User document created", uid=user.uid, email=user.email)

    return user_data


@router.get("/users/me", summary="Get current user profile")
async def get_me(user: CurrentUser) -> dict[str, Any]:
    """
    Returns the authenticated user's profile.
    Creates the user document automatically on first sign-in.
    This is the entry point for new users into the SPARK system.
    """
    from app.core.firebase import is_firestore_available

    logger.info("Get user profile", uid=user.uid)

    # If Firestore is available, fetch or create user document
    if is_firestore_available():
        user_doc = _get_user_document(user.uid)

        if user_doc is None:
            # First sign-in — create user document
            logger.info("First sign-in detected — creating user document", uid=user.uid)
            user_doc = _create_user_document(user)
        else:
            # Update lastActiveAt on every sign-in
            try:
                from app.core.firebase import get_firestore
                db = get_firestore()
                db.collection("users").document(user.uid).update(
                    {"lastActiveAt": datetime.now(timezone.utc).isoformat()}
                )
            except Exception as exc:
                logger.warning(
                    "Could not update lastActiveAt", uid=user.uid, error=str(exc)
                )

        return success_response(data=user_doc)

    # Firestore not available — return data from token only
    return success_response(
        data={
            "uid": user.uid,
            "email": user.email,
            "displayName": user.name,
            "photoURL": user.picture,
            "emailVerified": user.email_verified,
            "onboardingComplete": False,
        }
    )


@router.put("/users/me", summary="Update current user profile")
async def update_me(user: CurrentUser) -> dict[str, Any]:
    """
    Updates the authenticated user's profile settings.
    Full implementation in Phase 6 (repositories).
    """
    logger.info("Update user profile stub", uid=user.uid)
    return success_response(data={"message": "Full implementation in Phase 6"})


@router.post("/users/me/onboard", summary="Complete user onboarding")
async def complete_onboarding(user: CurrentUser) -> dict[str, Any]:
    """
    Marks onboarding complete and initializes the Completion Genome.
    Full implementation in Phase 6 + 11.
    """
    logger.info("Onboarding stub", uid=user.uid)
    return success_response(data={"message": "Full implementation in Phase 6 + 11"})