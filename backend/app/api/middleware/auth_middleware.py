"""
SPARK — Authentication Middleware
Note: We use FastAPI Dependency Injection for auth (not middleware)
because middleware cannot return HTTP responses directly in a clean way
with FastAPI's response model system.

This module provides the reusable auth dependency that route handlers
inject via Depends(). The actual Firebase verification happens in
app/api/dependencies.py.

This file is kept as the auth middleware documentation and
houses the token extraction logic used by the dependency.
"""

from app.core.security import extract_bearer_token

__all__ = ["extract_bearer_token"]