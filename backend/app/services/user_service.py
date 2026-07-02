"""
SPARK — User Service
Business logic for user profile management.
Handles first sign-in, settings updates, and onboarding.
"""

from typing import Optional

from app.core.logging import get_logger
from app.models.user import UserProfile, UpdateUserSettingsRequest
from app.repositories.user_repository import UserRepository
from app.repositories.genome_repository import GenomeRepository

logger = get_logger(__name__)


class UserService:
    """Manages user lifecycle — from first sign-in to settings management."""

    def __init__(self) -> None:
        self._user_repo = UserRepository()
        self._genome_repo = GenomeRepository()

    def get_or_create_user(
        self,
        uid: str,
        email: str,
        display_name: str,
        photo_url: Optional[str] = None,
    ) -> UserProfile:
        """
        Called on every sign-in via GET /users/me.
        Returns existing user or creates a new one on first sign-in.
        Also ensures the Completion Genome exists.
        """
        existing = self._user_repo.get_by_id(uid)

        if existing is not None:
            # Update last active timestamp
            self._user_repo.update_last_active(uid)
            return existing

        # First sign-in — create user and default genome
        logger.info("First sign-in detected — creating user", uid=uid, email=email)

        user = UserProfile.create_new(
            uid=uid,
            email=email,
            display_name=display_name,
            photo_url=photo_url,
        )
        self._user_repo.create(user)

        # Initialize default Completion Genome
        self._genome_repo.get_or_create_default(uid)
        logger.info("Default genome initialized for new user", uid=uid)

        return user

    def get_profile(self, uid: str) -> Optional[UserProfile]:
        """Returns the user profile, or None if not found."""
        return self._user_repo.get_by_id(uid)

    def update_settings(
        self,
        uid: str,
        request: UpdateUserSettingsRequest,
    ) -> None:
        """Updates user settings with validation."""
        if request.workingDays is not None:
            for day in request.workingDays:
                if day < 0 or day > 6:
                    from app.core.exceptions import ValidationError
                    raise ValidationError(
                        "workingDays must contain values 0-6 (Sunday=0)"
                    )

        self._user_repo.update_settings(uid, request)
        logger.info("User settings updated", uid=uid)

    def complete_onboarding(self, uid: str) -> None:
        """
        Marks onboarding as complete.
        The genome already exists from first sign-in.
        """
        self._user_repo.mark_onboarding_complete(uid)
        logger.info("Onboarding completed", uid=uid)