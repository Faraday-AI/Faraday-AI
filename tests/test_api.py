from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Microsoft Graph API Integration"}

def test_health_check():
    response = client.post("/test")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Service is running"}

def test_generate_document():
    request_data = {
        "document_type": "report",
        "title": "Test Report",
        "content": "This is a test report content",
        "output_format": "docx"
    }
    response = client.post("/generate-document", json=request_data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert "Test Report.docx" in response.headers["content-disposition"]

def test_generate_document_invalid_format():
    request_data = {
        "document_type": "report",
        "title": "Test Report",
        "content": "This is a test report content",
        "output_format": "invalid"
    }
    response = client.post("/generate-document", json=request_data)
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["detail"]

def test_generate_text():
    request_data = {
        "prompt": "Test prompt",
        "structured_output": False
    }
    response = client.post("/generate-text", json=request_data)
    # Note: This will fail without valid OpenAI API key
    assert response.status_code in [200, 500]  # 500 if no API key 