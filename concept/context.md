# Current Development Context

## Project Overview
- FastAPI backend service deployed on Render (https://faraday-ai.com)
- Service intended to support a Custom GPT for K-12 PE, Health, and Driver's Ed teachers in Elizabeth Public Schools (EPS)
- Repository: https://github.com/Faraday-AI/Faraday-AI.git

## Recent Changes
1. Added new endpoints:
   - `/test` (POST) - Simple health check endpoint
   - `/generate-document` (POST) - Simplified document generation
2. Added CORS support
3. Simplified document generation logic
4. Restored `TextRequest` class definition after deployment error

## Current Status
1. Code has been pushed to GitHub (latest commit: 0e419fe - "Fix: Restored TextRequest class definition")
2. Manual deployment on Render was triggered
3. Service shows as "live" but endpoints are returning 404s

## Current Issue
Despite successful code push and Render deployment, the new endpoints are not accessible:
```powershell
Invoke-WebRequest -Method POST -Uri "https://faraday-ai.com/test"
# Returns 404 Not Found
```

## Last Actions Taken
1. Fixed `TextRequest` class definition issue
2. Pushed changes to GitHub
3. Triggered manual deployment on Render
4. Attempted to test endpoints (received 404s)

## Next Steps to Try
1. Verify Render deployment logs for any hidden errors
2. Check if the FastAPI application is properly loading all routes
3. Test the original endpoints (e.g., `/auth/login`) to verify basic functionality
4. Consider checking FastAPI's automatic documentation at `/docs` to see available endpoints
5. Verify environment variables are properly set in Render

## Important Files
1. `main.py` - Contains all endpoints and core logic
2. `render.yaml` - Deployment configuration
3. `.env` - Environment variables (make sure these are set in Render's dashboard)

## Repository Status
- Main branch is up to date with origin
- Latest changes are committed and pushed
- GitHub authentication is confirmed working

## Render Configuration
- Service Name: faraday-ai
- Deploy Command: `pip install -r requirements.txt`
- Start Command: `gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app`

## To Continue Development
1. Check Render deployment logs for any errors
2. Verify the application is starting correctly
3. Consider adding more logging to track route registration
4. Test both new and existing endpoints to isolate the issue

## Testing Commands
```powershell
# Test basic endpoint
Invoke-WebRequest -Method POST -Uri "https://faraday-ai.com/test"

# Test document generation
$body = @{
    document_type = "lesson_plan"
    title = "Test Lesson Plan"
    content = "This is a test content."
    output_format = "docx"
} | ConvertTo-Json

Invoke-WebRequest -Method POST -Uri "https://faraday-ai.com/generate-document" -Body $body -ContentType "application/json"
```

## Steps to Run Locally
1. Open a new terminal window
2. Navigate to your project directory:
```bash
cd /Users/joemartucci/Projects:REPOS/Microsoft-Graph
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Start the FastAPI server:
```bash
python3 -m uvicorn main:app --reload
```

Once you run these commands, you should see the server start up. Then you can open your browser and navigate to:
http://127.0.0.1:8000/docs

# Context for Integrating Custom GPT with FastAPI in Cursor

\## Overview

This document provides the necessary context and specifications for integrating the \*\*PE/Health/Driver's Ed Assistant EPS Edition\*\* custom GPT with FastAPI. The goal is to enable seamless communication between FastAPI and the AI model to handle lesson planning, document generation, and email functionalities amongst other things.

\## Custom GPT Capabilities before any more were added into the code by cursor, which will be updated into custom GPT's schema when the final code is complete

\### 1. Lesson Planning & Assessments

\- Generates structured lesson plans using the \*\*EPS Lesson Plan Template\*\*.

\- Ensures alignment with district requirements, New Jersey state standards, Bloom's Taxonomy, and Danielson's Framework for Teaching.

\- Supports differentiation strategies for ELL, Special Education, 504 students, and Gifted & Talented learners.

\### 2. Automated Document Generation

\- Uses a \*\*Flask-based API\*\* hosted at \`<https://faraday-ai.com/\`> to generate Word, PowerPoint, and Excel documents.

\- Provides direct links for users to download generated files.

\### 3. Email Functionality

\- Sends emails with generated documents and lesson plans.

\- Uses Microsoft Graph API (OAuth 2.0 authentication) to send emails via Mail.Send API permission.

\- Ensures proper formatting and professional email communication.

\### 4. Microsoft Graph API Integration

\- Authentication and document handling through Microsoft Graph API.

\- Uploads and manages files in OneDrive.

\- Retrieves user details securely.

\### 5. File Management

\- Supports creation and sharing of Word, PowerPoint, and Excel files within Microsoft 365.

\- Ensures all generated links are functional before sharing.

\### 6. Lesson Plan Template Integration

\- Uses the EPS Lesson Plan Template for structured lesson creation.

\- Includes:

\- Student Learning Standards (SLS)

\- Lesson Objectives (SMART goals)

\- Anticipatory Set (hooking students into the lesson)

\- Direct Instruction (essential content and teaching strategies)

\- Guided Practice/Monitoring

\- Independent Practice

\- Closure (review and evaluation)

\- Differentiation Strategies

\## FastAPI Integration Points

\### 1. API Endpoints

\#### \`POST /generate_lesson_plan\`

\- \*\*Input:\*\* Lesson details (grade, content area, objectives, differentiation strategies, etc.)

\- \*\*Output:\*\* Generated lesson plan (JSON or downloadable document link)

\#### \`POST /generate_document\`

\- \*\*Input:\*\* Document type (Word, PowerPoint, Excel), content details

\- \*\*Output:\*\* Download link for generated document

\#### \`POST /send_email\`

\- \*\*Input:\*\* Recipient email, subject, message body, attachment (if any)

\- \*\*Output:\*\* Confirmation of email sent status

\#### \`GET /lesson_templates\`

\- \*\*Output:\*\* Available lesson plan templates in JSON format

\### 2. Authentication & Security

\- Uses OAuth 2.0 for Microsoft Graph API authentication.

\- Secure document access through OneDrive.

\- Implements role-based access control (RBAC) for API endpoints.

\### 3. Error Handling & Logging

\- Implements structured error responses for invalid inputs.

\- Logs API requests and responses for debugging and analytics.

\- Provides meaningful error messages to users.

\## Deployment Considerations

\- Deploy FastAPI backend on \*\*Azure\*\*, \*\*AWS\*\*, or \*\*Render\*\*.

\- Use \*\*PostgreSQL\*\* or \*\*MongoDB\*\* for storing lesson plans and user interactions.

\- Leverage \*\*Celery\*\* for background task processing (e.g., document generation, email sending).

\## Next Steps

\- Implement API endpoints based on the outlined specifications.

\- Integrate authentication with Microsoft Graph API.

\- Test document generation and email sending functionalities.

\- Deploy and validate FastAPI in a staging environment before production release.