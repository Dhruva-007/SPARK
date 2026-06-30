"""
SPARK — Firebase Admin SDK Initialization
Initializes the Firebase Admin SDK once at application startup.
Provides access to Firebase Auth and Firestore clients.

Design decisions:
- Single initialization via module-level state
- Lazy initialization pattern with is_initialized guard
- Separate functions for auth and firestore to keep concerns isolated
- Graceful handling when credentials file is missing (development)
"""

import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore import Client as FirestoreClient

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level state — initialized once per process
_firebase_app: Optional[firebase_admin.App] = None
_firestore_client: Optional[FirestoreClient] = None


def initialize_firebase() -> None:
    """
    Initialize Firebase Admin SDK.
    Called once during application startup in events.py.
    Safe to call multiple times — subsequent calls are no-ops.

    Initialization strategy:
    1. Try service account file (local development)
    2. Try Application Default Credentials (Cloud Run — automatic)
    3. Log warning and continue with limited functionality if neither works
    """
    global _firebase_app, _firestore_client

    if _firebase_app is not None:
        logger.debug("Firebase already initialized — skipping")
        return

    settings = get_settings()

    try:
        # Strategy 1: Service account JSON file (local dev)
        service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            _firebase_app = firebase_admin.initialize_app(
                cred,
                {"projectId": settings.FIREBASE_PROJECT_ID},
            )
            logger.info(
                "Firebase initialized with service account file",
                path=service_account_path,
                project=settings.FIREBASE_PROJECT_ID,
            )

        # Strategy 2: Application Default Credentials (Cloud Run)
        else:
            _firebase_app = firebase_admin.initialize_app(
                options={"projectId": settings.FIREBASE_PROJECT_ID}
            )
            logger.info(
                "Firebase initialized with Application Default Credentials",
                project=settings.FIREBASE_PROJECT_ID,
            )

        # Initialize Firestore client
        _firestore_client = firestore.client()
        logger.info("Firestore client initialized successfully")

    except Exception as exc:
        logger.error(
            "Firebase initialization failed",
            error=str(exc),
            hint="Ensure firebase-service-account.json exists or ADC is configured",
        )
        # Do not raise — allow app to start with degraded Firebase support
        # Individual operations will fail gracefully with ServiceUnavailableError


def get_firestore() -> FirestoreClient:
    """
    Returns the initialized Firestore client.
    Raises ServiceUnavailableError if Firebase is not initialized.

    Usage in repositories:
        db = get_firestore()
        doc = db.collection("tasks").document(task_id).get()
    """
    if _firestore_client is None:
        from app.core.exceptions import ServiceUnavailableError
        raise ServiceUnavailableError("Firestore")
    return _firestore_client


def verify_firebase_token(token: str) -> dict:
    """
    Verifies a Firebase ID token and returns the decoded claims.
    Raises AuthenticationError if the token is invalid or expired.

    Args:
        token: Firebase ID token from the client Authorization header

    Returns:
        Decoded token dict with uid, email, name, picture, etc.
    """
    if _firebase_app is None:
        from app.core.exceptions import ServiceUnavailableError
        raise ServiceUnavailableError("Firebase Auth")

    return auth.verify_id_token(token)


def is_firebase_initialized() -> bool:
    """Returns True if Firebase Admin SDK has been successfully initialized."""
    return _firebase_app is not None


def is_firestore_available() -> bool:
    """Returns True if Firestore client is available."""
    return _firestore_client is not None