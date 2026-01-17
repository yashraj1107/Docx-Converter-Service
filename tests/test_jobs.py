import io
import zipfile
import pytest

# --- HELPER ---
def create_dummy_zip():
    """Helper to create a valid zip file in memory"""
    io_bytes = io.BytesIO()
    with zipfile.ZipFile(io_bytes, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("test.docx", "This is just text content, not real XML docx content.")
    io_bytes.seek(0)
    return io_bytes

def _submit_job_helper(client):
    zip_file = create_dummy_zip()
    files = {"file": ("test.zip", zip_file, "application/zip")}
    response = client.post("/api/v1/jobs/", files=files)
    return response

# --- TESTS ---

def test_submit_job_success(client):
    response = _submit_job_helper(client)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"

def test_submit_invalid_file(client):
    files = {"file": ("test.txt", b"plain text", "text/plain")}
    response = client.post("/api/v1/jobs/", files=files)
    assert response.status_code == 400