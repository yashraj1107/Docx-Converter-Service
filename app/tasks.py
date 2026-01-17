import os
import zipfile
import subprocess
from celery import Celery
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.job import Job
from app.schemas.job import JobStatusEnum

celery = Celery(__name__, broker=settings.CELERY_BROKER_URL)

@celery.task
def process_conversion(job_id):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job: 
        return

    try:
        job.status = JobStatusEnum.PROCESSING
        db.commit()

        input_zip = job.input_path
        extract_dir = os.path.dirname(input_zip)
        output_dir = job.output_path
        
        # 1. Unzip
        with zipfile.ZipFile(input_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # 2. Convert
        file_status = {}
        converted_files = []
        
        for filename in os.listdir(extract_dir):
            if filename.endswith(".docx"):
                file_path = os.path.join(extract_dir, filename)
                cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, file_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    file_status[filename] = "COMPLETED"
                    converted_files.append(filename.replace(".docx", ".pdf"))
                else:
                    file_status[filename] = "FAILED"

        # 3. Zip Output
        output_zip_path = os.path.join(output_dir, "converted.zip")
        with zipfile.ZipFile(output_zip_path, 'w') as zipf:
            for pdf in converted_files:
                pdf_path = os.path.join(output_dir, pdf)
                if os.path.exists(pdf_path):
                    zipf.write(pdf_path, arcname=pdf)

        job.file_details = file_status
        job.status = JobStatusEnum.COMPLETED
        db.commit()

    except Exception as e:
        job.status = JobStatusEnum.FAILED
        job.file_details = {"error": str(e)}
        db.commit()
    finally:
        db.close()