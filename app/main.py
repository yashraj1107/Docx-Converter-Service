import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import OperationalError
from app.core.database import engine, Base
from app.api.v1 import jobs

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

# 1. Mount the static directory for the UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 2. Add the Root Route to serve the HTML UI
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("app/static/index.html", "r") as f:
        return f.read()

# 3. Include the API Router
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])