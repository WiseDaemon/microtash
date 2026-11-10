from fastapi import APIRouter, HTTPException, Depends, Response, status
from typing import Dict, Any
from app.models import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    UserProfileResponse
)
from app import database
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/auth", tags=["User Authentication & Sessions"])

@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserRegisterRequest, response: Response):
    """
    Registers a new user account, creates a secure session, and returns an access token.
    """
    email = payload.email.strip().lower()
    username = payload.username.strip().lower()

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email address is required.")
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    try:
        user = database.create_user(
            email=email,
            username=username,
            password=payload.password,
            full_name=payload.full_name or ""
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token, expires_at = create_access_token(user["id"], user["username"], user["email"])
    database.create_user_session(user["id"], token, expires_at)

    response.set_cookie(
        key="microstash_session",
        value=token,
        httponly=True,
        samesite="lax",
        expires=int(expires_at.timestamp())
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_at=expires_at.isoformat(),
        user=UserResponse(**user)
    )

@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, response: Response):
    """
    Authenticates user with username or email, issues a JWT token, and registers an active session.
    """
    login_id = payload.login.strip().lower()
    user = database.get_user_by_email_or_username(login_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password."
        )

    if not verify_password(payload.password, user["password_hash"], user["salt"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password."
        )

    token, expires_at = create_access_token(user["id"], user["username"], user["email"])
    database.create_user_session(user["id"], token, expires_at)

    response.set_cookie(
        key="microstash_session",
        value=token,
        httponly=True,
        samesite="lax",
        expires=int(expires_at.timestamp())
    )

    clean_user = {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "created_at": user["created_at"],
        "is_active": bool(user["is_active"])
    }

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_at=expires_at.isoformat(),
        user=UserResponse(**clean_user)
    )

@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns current authenticated user profile, active streak, and progress metrics.
    """
    clean_user = {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "created_at": user["created_at"],
        "is_active": bool(user["is_active"])
    }
    progress = database.get_user_progress()
    return UserProfileResponse(
        user=UserResponse(**clean_user),
        progress=progress
    )

@router.post("/logout")
def logout_user(response: Response, user: Dict[str, Any] = Depends(get_current_user)):
    """
    Terminates current session token in database and clears session cookies.
    """
    token = user.get("token")
    if token:
        database.delete_user_session(token)

    response.delete_cookie(key="microstash_session")
    return {"status": "ok", "message": "Successfully logged out."}

@router.post("/refresh", response_model=TokenResponse)
def refresh_session_token(response: Response, user: Dict[str, Any] = Depends(get_current_user)):
    """
    Refreshes session token with a renewed 30-day expiration window.
    """
    old_token = user.get("token")
    if old_token:
        database.delete_user_session(old_token)

    token, expires_at = create_access_token(user["id"], user["username"], user["email"])
    database.create_user_session(user["id"], token, expires_at)

    response.set_cookie(
        key="microstash_session",
        value=token,
        httponly=True,
        samesite="lax",
        expires=int(expires_at.timestamp())
    )

    clean_user = {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "created_at": user["created_at"],
        "is_active": bool(user["is_active"])
    }

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_at=expires_at.isoformat(),
        user=UserResponse(**clean_user)
    )
