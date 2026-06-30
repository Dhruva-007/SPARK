"""
SPARK — Security Utilities
Token verification, user extraction, and security helpers.
All authentication logic flows through this module.
"""

from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_bearer_token(authorization_header: str | None) -> str | None:
    """
    Extract Bearer token from Authorization header.
    Returns None if header is missing or malformed.
    
    Expected format: "Bearer <token>"
    """
    if not authorization_header:
        return None

    parts = authorization_header.split(" ", maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Malformed Authorization header received")
        return None

    token = parts[1].strip()
    if not token:
        return None

    return token


def sanitize_user_id(user_id: str) -> str:
    """
    Sanitize user ID to prevent injection attacks.
    Firebase UIDs contain only alphanumeric characters and some symbols.
    """
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "-_"
    )
    sanitized = "".join(c for c in user_id if c in allowed_chars)

    if sanitized != user_id:
        logger.warning(
            "User ID contained unexpected characters — sanitized",
            original_length=len(user_id),
            sanitized_length=len(sanitized),
        )

    return sanitized