#!/usr/bin/env python3
"""
Main FastAPI application for ZipHostBot - Local Version
Simplified version for running without Docker
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import uvicorn

# Import local modules
try:
    from database import get_db, User, Project, ProjectStatus, engine, Base
    from auth import verify_telegram_auth, create_access_token, get_current_user, verify_telegram_bot_token
    from encryption import token_encryption
    from config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the correct directory")
    sys.exit(1)

# Create tables
print("🗄️ Creating database tables...")
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ZipHostBot API - Local", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "ZipHostBot API is running (Local Mode)",
        "version": "1.0.0",
        "mode": "local",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "local"}

@app.post("/auth/telegram")
async def telegram_auth(auth_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Endpoint untuk otentikasi menggunakan Telegram Login Widget
    """
    # Verifikasi data otentikasi Telegram
    if not verify_telegram_auth(auth_data.copy()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication"
        )
    
    telegram_id = int(auth_data["id"])
    first_name = auth_data["first_name"]
    username = auth_data.get("username")
    
    # Cari atau buat user
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user info jika ada perubahan
        user.first_name = first_name
        user.username = username
        db.commit()
    
    # Buat JWT token
    access_token = create_access_token(data={"telegram_id": telegram_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "username": user.username
        }
    }

@app.get("/projects")
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mendapatkan daftar proyek milik user
    """
    projects = db.query(Project).filter(Project.owner_id == current_user.telegram_id).all()
    
    return {
        "projects": [
            {
                "id": str(project.id),
                "name": project.name,
                "status": project.status.value,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "last_error_log": project.last_error_log
            }
            for project in projects
        ]
    }

@app.post("/projects")
async def create_project(
    name: str = Form(...),
    bot_token: str = Form(...),
    zip_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Membuat proyek baru dengan upload file ZIP (Simplified untuk local mode)
    """
    # Validasi file
    if not zip_file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a ZIP archive"
        )
    
    # Validasi ukuran file
    file_content = await zip_file.read()
    if len(file_content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum limit of 50MB"
        )
    
    # Validasi bot token
    if not await verify_telegram_bot_token(bot_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bot token"
        )
    
    try:
        # Simpan file ZIP ke local storage (simplified)
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        zip_path = upload_dir / f"{uuid.uuid4()}.zip"
        with open(zip_path, "wb") as f:
            f.write(file_content)
        
        # Enkripsi bot token
        encrypted_token = token_encryption.encrypt_token(bot_token)
        
        # Buat project di database
        project = Project(
            owner_id=current_user.telegram_id,
            name=name,
            zip_storage_path=str(zip_path),
            encrypted_bot_token=encrypted_token,
            status=ProjectStatus.PENDING
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return {
            "message": "Project created successfully (Local Mode - Manual processing required)",
            "project_id": str(project.id),
            "status": "PENDING",
            "note": "In local mode, you need to manually process the bot deployment"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

if __name__ == "__main__":
    print("🚀 Starting ZipHostBot Backend (Local Mode)...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "main_local:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )