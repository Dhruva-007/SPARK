"""
SPARK — User Domain Models
Internal Pydantic models for user profile and settings.
These represent the Firestore document structure exactly.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class UserSettings(BaseModel):
    """User configuration and integration settings."""

    timezone: str = Field(default="UTC")
    workingHoursStart: str = Field(default="09:00")
    workingHoursEnd: str = Field(default="17:00")
    workingDays: list[int] = Field(default=[1, 2, 3, 4, 5])
    notificationsEnabled: bool = Field(default=True)
    calendarConnected: bool = Field(default=False)
    gmailConnected: bool = Field(default=False)


class UserProfile(BaseModel):
    """
    Complete user profile as stored in Firestore /users/{userId}.
    """

    uid: str
    email: str = Field(default="")
    displayName: str = Field(default="")
    photoURL: Optional[str] = Field(default=None)
    createdAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    lastActiveAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    onboardingComplete: bool = Field(default=False)
    settings: UserSettings = Field(default_factory=UserSettings)

    @classmethod
    def create_new(
        cls,
        uid: str,
        email: str,
        display_name: str,
        photo_url: Optional[str] = None,
    ) -> "UserProfile":
        """Factory method for creating a new user on first sign-in."""
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            uid=uid,
            email=email,
            displayName=display_name,
            photoURL=photo_url,
            createdAt=now,
            lastActiveAt=now,
            onboardingComplete=False,
            settings=UserSettings(),
        )

    def to_firestore(self) -> dict:
        """Serializes to Firestore-compatible dict."""
        return self.model_dump()


class UpdateUserSettingsRequest(BaseModel):
    """Validated request for updating user settings."""

    timezone: Optional[str] = None
    workingHoursStart: Optional[str] = None
    workingHoursEnd: Optional[str] = None
    workingDays: Optional[list[int]] = None
    notificationsEnabled: Optional[bool] = None
    calendarConnected: Optional[bool] = None
    gmailConnected: Optional[bool] = None