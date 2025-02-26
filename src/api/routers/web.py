# src/api/routers/web.py
from fastapi import APIRouter, Request, Depends, HTTPException, Form, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List, Dict, Any
import os
import logging
from pathlib import Path
from datetime import datetime

from src.core.config import settings
from src.api.models.auth import authenticate_user, create_access_token, get_current_active_user, User
from src.rag.vector_store import VectorStoreManager
from src.api.dependencies import get_vector_store, get_current_user_optional

logger = logging.getLogger(__name__)

# Setup templates
templates_path = Path(__file__).parent.parent.parent.parent / "frontend" / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter()

# Home page
@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request, 
    access_token: Optional[str] = Cookie(None),
    user: Optional[User] = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )

# Login page
@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request, 
    access_token: Optional[str] = Cookie(None),
    user: Optional[User] = Depends(get_current_user_optional)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user": None}
    )

# Login form submission
@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    if not settings.auth.enabled:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "messages": [{"type": "danger", "text": "Invalid username or password"}]
            }
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.auth.token_expire_minutes * 60,
        samesite="lax"
    )
    
    return response

# Logout
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

# Documents page
@router.get("/documents", response_class=HTMLResponse)
async def documents_page(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    user: Optional[User] = Depends(get_current_user_optional),
    vector_store: VectorStoreManager = Depends(get_vector_store)
):
    if settings.auth.enabled and not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "documents.html",
        {"request": request, "user": user}
    )

# Chat page
@router.get("/chat", response_class=HTMLResponse)
async def chat_page(
    request: Request,
    doc_id: Optional[str] = None,
    access_token: Optional[str] = Cookie(None),
    user: Optional[User] = Depends(get_current_user_optional)
):
    if settings.auth.enabled and not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "user": user, "doc_id": doc_id}
    )

# Stats page
@router.get("/stats", response_class=HTMLResponse)
async def stats_page(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    user: Optional[User] = Depends(get_current_user_optional),
    vector_store: VectorStoreManager = Depends(get_vector_store)
):
    if settings.auth.enabled and not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        stats = {
            "vector_store": vector_store.get_collection_stats(),
            "uploads_dir": Path(settings.uploads_dir),
            "chat_histories_dir": Path(settings.chat_histories_dir)
        }
        
        # Count files in uploads directory
        uploads_count = len(list(Path(settings.uploads_dir).glob("*")))
        
        # Count files in chat_histories directory
        chat_histories_count = len(list(Path(settings.chat_histories_dir).glob("*.json")))
        
        return templates.TemplateResponse(
            "stats.html",
            {
                "request": request, 
                "user": user, 
                "stats": stats,
                "uploads_count": uploads_count,
                "chat_histories_count": chat_histories_count
            }
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "user": user,
                "error": "Error retrieving system statistics"
            }
        )