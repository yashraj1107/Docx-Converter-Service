import time
import os
from fastapi import FastAPI, Request, Security, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyHeader
from sqlalchemy.exc import OperationalError
from app.core.database import engine, Base
from app.api.v1 import jobs

# --- Database Connection Retry Logic ---
MAX_RETRIES = 10
for i in range(MAX_RETRIES):
    try:
        Base.metadata.create_all(bind=engine)
        print("--- Database Connected & Tables Created ---")
        break
    except OperationalError:
        print(f"Database unavailable... retrying ({i+1}/{MAX_RETRIES})")
        time.sleep(2)

app = FastAPI(title="Docx Converter Service")

# --- 1. SECURITY CONFIGURATION ---
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    
    env_keys = os.getenv("API_KEYS", "").split(",")
    
    if api_key_header and api_key_header in env_keys:
        return api_key_header
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or Missing API Key. Contact the owner for access."
    )

# --- 2. TEMPLATES & STATIC FILES ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# --- 3. ROOT ROUTE ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    public_key = os.getenv("PUBLIC_API_KEY", "")
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "api_key_variable": public_key 
    })

app.include_router(
    jobs.router, 
    prefix="/api/v1/jobs", 
    tags=["Jobs"],
    dependencies=[Depends(get_api_key)]
)