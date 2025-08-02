from minio import Minio
from minio.error import S3Error
import io
from typing import Optional
import uuid
from config import settings


class MinIOStorage:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """
        Pastikan bucket ada, jika tidak buat bucket baru
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def upload_file(self, file_data: bytes, filename: str) -> str:
        """
        Upload file ke MinIO dan return path
        """
        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            
            # Upload file
            self.client.put_object(
                self.bucket_name,
                unique_filename,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type='application/zip'
            )
            
            return unique_filename
        except S3Error as e:
            raise Exception(f"Failed to upload file: {e}")
    
    def download_file(self, file_path: str) -> bytes:
        """
        Download file dari MinIO
        """
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            return response.read()
        except S3Error as e:
            raise Exception(f"Failed to download file: {e}")
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()
    
    def delete_file(self, file_path: str) -> bool:
        """
        Hapus file dari MinIO
        """
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False


# Instance global
storage = MinIOStorage()