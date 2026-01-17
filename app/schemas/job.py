from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class JobStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobResponse(BaseModel):
    job_id: str = Field(validation_alias="id")
    status: JobStatusEnum
    created_at: datetime
    files: Optional[Dict[str, str]] = Field(default=None, validation_alias="file_details")
    download_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)