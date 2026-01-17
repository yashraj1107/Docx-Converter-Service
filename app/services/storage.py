import os
import shutil
from abc import ABC, abstractmethod
from fastapi import UploadFile
from app.core.config import settings

class StorageStrategy(ABC):
    """Abstract Base Class for file storage."""
    
    @abstractmethod
    def save_upload(self, job_id: str, file: UploadFile) -> str:
        pass

    @abstractmethod
    def get_output_path(self, job_id: str) -> str:
        pass

class LocalStorageStrategy(StorageStrategy):
    """Implementation for Local Docker Volumes."""
    
    def _get_job_dir(self, job_id: str) -> str:
        return os.path.join(settings.SHARED_DIR, job_id)

    def save_upload(self, job_id: str, file: UploadFile) -> str:
        job_dir = self._get_job_dir(job_id)
        input_dir = os.path.join(job_dir, "source")
        os.makedirs(input_dir, exist_ok=True)
        
        file_path = os.path.join(input_dir, "upload.zip")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path

    def get_output_path(self, job_id: str) -> str:
        output_dir = os.path.join(self._get_job_dir(job_id), "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

storage_service = LocalStorageStrategy()