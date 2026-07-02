"""
SPARK — FastAPI Dependencies
Reusable dependencies injected into route handlers via Depends().

Authentication flow:
1. Extract Bearer token from Authorization header
2. Verify with Firebase Admin SDK
3. Return AuthenticatedUser with decoded claims
4. All route handlers receive a verified, typed user object
"""

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthenticationError, ServiceUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)

# auto_error=False — we handle auth errors ourselves for better messages
_bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    """
    Represents a verified Firebase user.
    Constructed from decoded JWT claims on every authenticated request.
    """

    def __init__(self, decoded_token: dict) -> None:
        self.uid: str = decoded_token["uid"]
        self.email: str | None = decoded_token.get("email")
        self.name: str | None = decoded_token.get("name")
        self.picture: str | None = decoded_token.get("picture")
        self.email_verified: bool = decoded_token.get("email_verified", False)

    def __repr__(self) -> str:
        return f"AuthenticatedUser(uid={self.uid}, email={self.email})"


async def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ] = None,
) -> AuthenticatedUser:
    """
    FastAPI dependency that verifies Firebase JWT.
    Returns an AuthenticatedUser with verified claims.

    Development mode (no Firebase configured):
    - Returns a dev user so routes can be tested without Firebase

    Production mode (Firebase configured):
    - Verifies the JWT with Firebase Admin SDK
    - Raises AuthenticationError for any invalid token
    """
    from app.core.config import get_settings
    from app.core.firebase import is_firebase_initialized, verify_firebase_token

    settings = get_settings()

    # Development bypass — when Firebase project ID is not configured
    if settings.is_development and settings.APP_ENV == "development":
        logger.warning(
            "Firebase not configured — development auth bypass active",
            hint="Set FIREBASE_PROJECT_ID in .env to enable real authentication",
        )
        return AuthenticatedUser(
            {
                "uid": "dev-user-001",
                "email": "dev@spark.local",
                "name": "Development User",
                "picture": None,
                "email_verified": True,
            }
        )

    # Real authentication path
    if credentials is None:
        raise AuthenticationError("No authorization token provided")

    token = credentials.credentials
    if not token:
        raise AuthenticationError("Empty authorization token")

    if not is_firebase_initialized():
        raise ServiceUnavailableError("Firebase Auth")

    try:
        decoded_token = verify_firebase_token(token)
        user = AuthenticatedUser(decoded_token)
        logger.debug("Token verified", uid=user.uid)
        return user

    except AuthenticationError:
        raise
    except ServiceUnavailableError:
        raise
    except Exception as exc:
        logger.warning("Token verification failed", error=str(exc))
        raise AuthenticationError("Invalid or expired token") from exc


# Type alias for clean route handler signatures
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]