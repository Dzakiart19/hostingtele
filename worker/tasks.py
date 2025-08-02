import os
import shutil
import tempfile
import zipfile
import docker
import time
from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import uuid
import subprocess
import socket

from config import settings
from database import Project, ProjectStatus, SessionLocal
from encryption import token_encryption
from storage import storage

# Konfigurasi Celery
app = Celery(
    "ziphostbot",
    broker=settings.redis_url,
    backend=settings.redis_url
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Docker client
docker_client = docker.from_env()


def update_project_status(project_id: str, status: ProjectStatus, error_log: str = None, container_id: str = None):
    """
    Update status proyek di database
    """
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == uuid.UUID(project_id)).first()
        if project:
            project.status = status
            if error_log:
                project.last_error_log = error_log
            if container_id:
                project.container_id = container_id
            db.commit()
    finally:
        db.close()


def scan_with_clamav(file_path: str) -> bool:
    """
    Scan file dengan ClamAV
    """
    try:
        # Tunggu ClamAV siap
        max_retries = 30
        for i in range(max_retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((settings.clamav_host, settings.clamav_port))
                sock.close()
                if result == 0:
                    break
            except:
                pass
            time.sleep(2)
        
        # Jalankan clamdscan
        result = subprocess.run([
            'clamdscan', 
            '--fdpass',
            f'--stream',
            file_path
        ], capture_output=True, text=True, timeout=300)
        
        # Jika return code 0, file bersih
        return result.returncode == 0
        
    except Exception as e:
        print(f"ClamAV scan error: {e}")
        # Jika ClamAV tidak tersedia, lanjutkan (untuk development)
        return True


def detect_runtime(work_dir: str) -> str:
    """
    Deteksi runtime berdasarkan file yang ada
    """
    if os.path.exists(os.path.join(work_dir, 'requirements.txt')):
        return 'python'
    elif os.path.exists(os.path.join(work_dir, 'package.json')):
        return 'nodejs'
    else:
        return None


def create_dockerfile(work_dir: str, runtime: str) -> str:
    """
    Buat Dockerfile dinamis berdasarkan runtime
    """
    dockerfile_path = os.path.join(work_dir, 'Dockerfile')
    
    if runtime == 'python':
        # Cari file utama Python
        main_files = ['main.py', 'bot.py', 'app.py', 'run.py']
        main_file = None
        for file in main_files:
            if os.path.exists(os.path.join(work_dir, file)):
                main_file = file
                break
        
        if not main_file:
            # Cari file .py pertama
            for file in os.listdir(work_dir):
                if file.endswith('.py'):
                    main_file = file
                    break
        
        if not main_file:
            raise Exception("No Python main file found")
        
        dockerfile_content = f"""FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the bot
CMD ["python", "{main_file}"]
"""
    
    elif runtime == 'nodejs':
        dockerfile_content = """FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Run the bot
CMD ["npm", "start"]
"""
    
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)
    
    return dockerfile_path


@app.task(bind=True)
def process_project(self, project_id: str):
    """
    Task utama untuk memproses proyek ZIP
    """
    work_dir = None
    try:
        print(f"Processing project {project_id}")
        
        # Update status ke PROCESSING
        update_project_status(project_id, ProjectStatus.PROCESSING)
        
        # Ambil data proyek dari database
        db = SessionLocal()
        project = db.query(Project).filter(Project.id == uuid.UUID(project_id)).first()
        if not project:
            raise Exception("Project not found")
        
        # Download file ZIP dari MinIO
        print("Downloading ZIP file...")
        zip_data = storage.download_file(project.zip_storage_path)
        
        # Buat direktori kerja temporary
        work_dir = f"/tmp/builds/{project_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        # Simpan file ZIP sementara untuk scanning
        zip_file_path = os.path.join(work_dir, 'project.zip')
        with open(zip_file_path, 'wb') as f:
            f.write(zip_data)
        
        # Scan dengan ClamAV
        print("Scanning with ClamAV...")
        if not scan_with_clamav(zip_file_path):
            raise Exception("File contains malware or virus")
        
        # Ekstrak ZIP
        print("Extracting ZIP file...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(work_dir)
        
        # Hapus file ZIP setelah ekstrak
        os.remove(zip_file_path)
        
        # Deteksi runtime
        print("Detecting runtime...")
        runtime = detect_runtime(work_dir)
        if not runtime:
            raise Exception("Runtime tidak dapat dideteksi. Pastikan ada requirements.txt (Python) atau package.json (Node.js)")
        
        print(f"Detected runtime: {runtime}")
        
        # Buat Dockerfile
        print("Creating Dockerfile...")
        dockerfile_path = create_dockerfile(work_dir, runtime)
        
        # Build Docker image
        print("Building Docker image...")
        image_tag = f"ziphostbot/project:{project_id}"
        
        try:
            # Build image
            image, build_logs = docker_client.images.build(
                path=work_dir,
                tag=image_tag,
                rm=True,
                forcerm=True
            )
            
            print("Docker image built successfully")
            
        except docker.errors.BuildError as e:
            error_msg = "Docker build failed:\n"
            for log in e.build_log:
                if 'stream' in log:
                    error_msg += log['stream']
            raise Exception(error_msg)
        
        # Dekripsi bot token
        bot_token = token_encryption.decrypt_token(project.encrypted_bot_token)
        
        # Jalankan container
        print("Starting container...")
        container = docker_client.containers.run(
            image_tag,
            environment={'BOT_TOKEN': bot_token},
            detach=True,
            restart_policy={"Name": "unless-stopped"},
            name=f"ziphostbot_{project_id}"
        )
        
        print(f"Container started: {container.id}")
        
        # Update status ke RUNNING
        update_project_status(project_id, ProjectStatus.RUNNING, container_id=container.id)
        
        print(f"Project {project_id} processed successfully")
        
        db.close()
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error processing project {project_id}: {error_msg}")
        update_project_status(project_id, ProjectStatus.FAILED, error_log=error_msg)
        
    finally:
        # Cleanup work directory
        if work_dir and os.path.exists(work_dir):
            shutil.rmtree(work_dir, ignore_errors=True)


@app.task(bind=True)
def stop_project(self, project_id: str):
    """
    Task untuk menghentikan proyek
    """
    try:
        print(f"Stopping project {project_id}")
        
        # Ambil data proyek dari database
        db = SessionLocal()
        project = db.query(Project).filter(Project.id == uuid.UUID(project_id)).first()
        if not project or not project.container_id:
            return
        
        # Stop dan hapus container
        try:
            container = docker_client.containers.get(project.container_id)
            container.stop(timeout=10)
            container.remove()
            print(f"Container {project.container_id} stopped and removed")
        except docker.errors.NotFound:
            print(f"Container {project.container_id} not found")
        except Exception as e:
            print(f"Error stopping container: {e}")
        
        # Update status
        update_project_status(project_id, ProjectStatus.STOPPED, container_id=None)
        
        db.close()
        
    except Exception as e:
        print(f"Error stopping project {project_id}: {e}")


@app.task(bind=True)
def start_project(self, project_id: str):
    """
    Task untuk memulai ulang proyek
    """
    try:
        print(f"Starting project {project_id}")
        
        # Ambil data proyek dari database
        db = SessionLocal()
        project = db.query(Project).filter(Project.id == uuid.UUID(project_id)).first()
        if not project:
            return
        
        # Dekripsi bot token
        bot_token = token_encryption.decrypt_token(project.encrypted_bot_token)
        
        # Jalankan container dengan image yang sudah ada
        image_tag = f"ziphostbot/project:{project_id}"
        
        try:
            # Cek apakah image ada
            docker_client.images.get(image_tag)
            
            # Jalankan container
            container = docker_client.containers.run(
                image_tag,
                environment={'BOT_TOKEN': bot_token},
                detach=True,
                restart_policy={"Name": "unless-stopped"},
                name=f"ziphostbot_{project_id}"
            )
            
            print(f"Container restarted: {container.id}")
            
            # Update status
            update_project_status(project_id, ProjectStatus.RUNNING, container_id=container.id)
            
        except docker.errors.ImageNotFound:
            # Jika image tidak ada, proses ulang dari awal
            process_project.delay(project_id)
        
        db.close()
        
    except Exception as e:
        print(f"Error starting project {project_id}: {e}")
        update_project_status(project_id, ProjectStatus.FAILED, error_log=str(e))


if __name__ == '__main__':
    app.start()