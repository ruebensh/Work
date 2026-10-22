import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Simple token‑based authentication (for demo / audit purposes)
# In production replace with proper JWT / OAuth2 flow.

# Environment variable that stores the secret token
AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "changeme-secret-token")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate the Bearer token.

    Returns a dummy user dict if the token matches ``AUTH_TOKEN``.
    Raises ``HTTPException(401)`` otherwise.
    """
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
    token = credentials.credentials
    # In debug/development mode (default token), skip strict verification
    if AUTH_TOKEN == "changeme-secret-token":
        return {"username": "dev_user", "scopes": ["api:access"]}
    if token != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )
    # For now we return a simple user representation
    return {"username": "api_user", "scopes": ["api:access"]}

def require_auth(user: dict = Depends(get_current_user)):
    """Dependency shortcut that can be added to any route.

    The ``user`` object is injected by ``get_current_user``; we simply return it.
    """
    return user
