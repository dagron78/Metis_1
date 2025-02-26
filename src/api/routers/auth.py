# src/api/routers/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.api.models.auth import Token, User, authenticate_user, create_access_token, get_current_active_user
from src.core.config import settings
from src.core.exceptions import AuthenticationError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    if not settings.auth.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication is disabled"
        )
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise AuthenticationError("Incorrect username or password")
    
    access_token_expires = timedelta(minutes=settings.auth.token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"User {form_data.username} successfully logged in")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return current_user

@router.get("/status")
async def auth_status():
    """
    Get authentication status.
    """
    return {
        "enabled": settings.auth.enabled,
        "token_expire_minutes": settings.auth.token_expire_minutes
    }