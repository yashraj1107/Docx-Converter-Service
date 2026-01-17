from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.storage import storage_service 
from app.models.job import Job, JobStatusEnum
from app.tasks import process_conversion
import uuid
import os
from fastapi.responses import FileResponse

router = APIRouter()

# --- 1. SUBMIT JOB ---
@router.post("/", response_model=dict, status_code=202)
async def submit_job(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files accepted")

    job_id = str(uuid.uuid4())
    
    # 1. Use the imported storage_service instance
    saved_path = storage_service.save_upload(job_id, file)
    
    # 2. Get output path for DB
    output_dir = storage_service.get_output_path(job_id)

    # 3. Save to DB
    new_job = Job(id=job_id, status=JobStatusEnum.PENDING, input_path=saved_path, output_path=output_dir)
    db.add(new_job)
    db.commit()

    # 4. Trigger Worker
    process_conversion.delay(job_id)

    return {"job_id": job_id, "status": "PENDING"}

# --- 2. GET STATUS ---
@router.get("/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job.id, "status": job.status.value}

# --- 3. DOWNLOAD ---
@router.get("/{job_id}/download")
async def download_result(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or job.status != JobStatusEnum.COMPLETED:
        raise HTTPException(status_code=404, detail="File not ready or found")
    
    zip_path = os.path.join(job.output_path, "converted.zip")
    
    if not os.path.exists(zip_path):
         raise HTTPException(status_code=500, detail="Output file missing from disk")
         
    return FileResponse(
        path=zip_path, 
        filename="converted_files.zip", 
        media_type='application/zip'
    )