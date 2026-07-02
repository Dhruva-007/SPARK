"""
SPARK — User Repository
All Firestore operations for user profiles.
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.user import UserProfile, UpdateUserSettingsRequest
from app.repositories.base_repository import BaseRepository

logger = get_logger(__name__)

_COLLECTION = "users"


class UserRepository(BaseRepository):
    """Repository for user profile Firestore operations."""

    def create(self, user: UserProfile) -> UserProfile:
        """Creates a new user document on first sign-in."""
        self._set_document(_COLLECTION, user.uid, user.to_firestore())
        logger.info("User document created", uid=user.uid)
        return user

    def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        """
        Fetches a user profile by UID.
        Returns None if user document does not exist yet.
        """
        try:
            data = self._get_document(_COLLECTION, user_id, "User")
            return UserProfile.model_validate(data)
        except Exception:
            return None

    def upsert(self, user: UserProfile) -> UserProfile:
        """
        Creates or updates a user document.
        Used on sign-in to ensure user document always exists.
        """
        self._set_document(
            _COLLECTION,
            user.uid,
            user.to_firestore(),
            merge=True,
        )
        return user

    def update_last_active(self, user_id: str) -> None:
        """Updates the lastActiveAt timestamp."""
        self._update_document(
            _COLLECTION,
            user_id,
            {"lastActiveAt": datetime.now(timezone.utc).isoformat()},
        )

    def update_settings(
        self,
        user_id: str,
        request: UpdateUserSettingsRequest,
    ) -> None:
        """
        Updates only the provided settings fields.
        Uses dot notation for nested Firestore updates.
        """
        updates: dict = {}

        if request.timezone is not None:
            updates["settings.timezone"] = request.timezone
        if request.workingHoursStart is not None:
            updates["settings.workingHoursStart"] = request.workingHoursStart
        if request.workingHoursEnd is not None:
            updates["settings.workingHoursEnd"] = request.workingHoursEnd
        if request.workingDays is not None:
            updates["settings.workingDays"] = request.workingDays
        if request.notificationsEnabled is not None:
            updates["settings.notificationsEnabled"] = request.notificationsEnabled
        if request.calendarConnected is not None:
            updates["settings.calendarConnected"] = request.calendarConnected
        if request.gmailConnected is not None:
            updates["settings.gmailConnected"] = request.gmailConnected

        if updates:
            updates["updatedAt"] = datetime.now(timezone.utc).isoformat()
            self._update_document(_COLLECTION, user_id, updates)

    def mark_onboarding_complete(self, user_id: str) -> None:
        """Marks the user's onboarding as complete."""
        self._update_document(
            _COLLECTION,
            user_id,
            {
                "onboardingComplete": True,
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            },
        )