import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, JSON
from datetime import datetime
from app.core.database import Base
from app.schemas.job import JobStatusEnum

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_details = Column(JSON, default={}) 
    input_path = Column(String)
    output_path = Column(String)