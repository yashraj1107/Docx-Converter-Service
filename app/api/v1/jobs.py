from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobStatusEnum
from app.services.storage import storage_service
from app.tasks import process_conversion
import uuid
import os

router = APIRouter()

@router.post("/", response_model=dict, status_code=202)
async def submit_job(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files accepted")

    job_id = str(uuid.uuid4())
    
    # 1. Use Service to handle file storage
    saved_path = storage_service.save_upload(job_id, file)
    output_dir = storage_service.get_output_path(job_id)

    # 2. Save to DB
    new_job = Job(id=job_id, status=JobStatusEnum.PENDING, input_path=saved_path, output_path=output_dir)
    db.add(new_job)
    db.commit()

    # 3. Trigger Worker
    process_conversion.delay(job_id)

    return {"job_id": job_id, "status": "PENDING"}

@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Construct response
    response = JobResponse.model_validate(job)
    if job.status == JobStatusEnum.COMPLETED:
        response.download_url = f"/api/v1/jobs/{job_id}/download"
    
    return response

@router.get("/{job_id}/download")
def download_result(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job or job.status != JobStatusEnum.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not ready")
        
    result_zip = os.path.join(job.output_path, "converted.zip")
    if not os.path.exists(result_zip):
        raise HTTPException(status_code=404, detail="File lost")
        
    return FileResponse(result_zip, media_type='application/zip', filename=f"job_{job_id}.zip")