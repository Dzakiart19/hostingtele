from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid

from database import get_db, User, Project, ProjectStatus
from auth import verify_telegram_auth, create_access_token, get_current_user, verify_telegram_bot_token
from encryption import token_encryption
from storage import storage
from celery_app import celery_app
from config import settings

app = FastAPI(title="ZipHostBot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "ZipHostBot API is running"}


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
    Membuat proyek baru dengan upload file ZIP
    """
    # Validasi file
    if not zip_file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a ZIP archive"
        )
    
    # Validasi ukuran file
    file_content = await zip_file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.max_file_size // (1024*1024)}MB"
        )
    
    # Validasi bot token
    if not await verify_telegram_bot_token(bot_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bot token"
        )
    
    try:
        # Upload file ke MinIO
        zip_storage_path = storage.upload_file(file_content, zip_file.filename)
        
        # Enkripsi bot token
        encrypted_token = token_encryption.encrypt_token(bot_token)
        
        # Buat project di database
        project = Project(
            owner_id=current_user.telegram_id,
            name=name,
            zip_storage_path=zip_storage_path,
            encrypted_bot_token=encrypted_token,
            status=ProjectStatus.PENDING
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Kirim task ke Celery worker
        celery_app.send_task('process_project', args=[str(project.id)])
        
        return {
            "message": "Project created successfully",
            "project_id": str(project.id),
            "status": "PENDING"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@app.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mendapatkan detail proyek
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.owner_id == current_user.telegram_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return {
        "id": str(project.id),
        "name": project.name,
        "status": project.status.value,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "last_error_log": project.last_error_log,
        "container_id": project.container_id
    }


@app.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Menghapus proyek
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.owner_id == current_user.telegram_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Kirim task untuk stop container dan cleanup
    if project.container_id:
        celery_app.send_task('stop_project', args=[str(project.id)])
    
    # Hapus file dari storage
    if project.zip_storage_path:
        storage.delete_file(project.zip_storage_path)
    
    # Hapus dari database
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}


@app.post("/projects/{project_id}/stop")
async def stop_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Menghentikan proyek yang sedang berjalan
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.owner_id == current_user.telegram_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.status != ProjectStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not running"
        )
    
    # Kirim task untuk stop container
    celery_app.send_task('stop_project', args=[str(project.id)])
    
    return {"message": "Stop request sent"}


@app.post("/projects/{project_id}/start")
async def start_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Memulai ulang proyek yang sudah di-build
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.owner_id == current_user.telegram_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.status not in [ProjectStatus.STOPPED, ProjectStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project cannot be started in current state"
        )
    
    # Kirim task untuk start container
    celery_app.send_task('start_project', args=[str(project.id)])
    
    return {"message": "Start request sent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)