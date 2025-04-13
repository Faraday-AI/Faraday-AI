# Project Context

## Overview
Faraday AI is an AI-powered personal education assistant and school management platform designed to enhance educational experiences through advanced tracking, security features, and AI-driven insights. The system combines personalized AI assistance with comprehensive tools for collaboration, resource management, and analytics to support educators and students in their educational journey.

## Current Development
- FastAPI backend service deployed on Render (https://faraday-ai.com)
- Real-time collaboration features with WebSocket support
- Document sharing and version control system
- Custom landing page with static assets
- Integration with ChatGPT's API for AI assistance
- In-memory storage (SQL database in development)

### Development Phases
1. Beta Version (Current):
   - Focused implementation for K-12 PE, Health, and Driver's Ed teachers in Elizabeth Public Schools (EPS)
   - Custom GPT integration:
     * Specialized ChatGPT model trained for educational content
     * Direct integration with Faraday-AI's codebase
     * AI-powered assistance for curriculum development
   - Data Management (In Development):
     * SQL database implementation planned for beta launch
     * Migration from in-memory to persistent storage
     * Secure data handling for educational content
   - Testing and Feedback:
     * Core features and real-time collaboration testing
     * User feedback collection through integrated systems
     * Usage pattern analysis for optimization
     * Performance metrics tracking

2. Full Application (Planned):
   - Option A: Pilot program implementation in selected school districts
   - Option B: Private launch on Faraday-AI.com as a standalone service
   - Complete feature set including all planned enhancements
   - Scalable infrastructure for multiple institutions
   - Enhanced AI capabilities and database optimization

## Original Features & Recent Changes
1. Added new endpoints:
   - `/test` (POST) - Simple health check endpoint
   - `/generate-document` (POST) - Simplified document generation
2. Added CORS support
3. Simplified document generation logic
4. Restored `TextRequest` class definition after deployment error

## New Collaboration Features
1. Session Management:
   - Create collaboration sessions
   - Track session participants
   - Maintain session status and metadata

2. Document Collaboration:
   - Share documents within sessions
   - Lock/unlock documents for editing
   - Track document version history
   - Prevent concurrent edits through locking mechanism

3. Real-time Updates:
   - WebSocket connections for live updates
   - Broadcast changes to all session participants
   - Track participant status

## API Endpoints

### Original Endpoints
- POST `/test` - Health check endpoint
- POST `/generate-document` - Document generation
- POST `/auth/login` - Authentication endpoint

### Session Management
- POST `/api/collaboration/create`
  - Create new collaboration session
  - Parameters: session_id, user_id

- GET `/api/collaboration/status`
  - Get session status
  - Parameters: session_id

### Document Management
- POST `/api/collaboration/share_document`
  - Share document in session
  - Parameters: session_id, user_id, document_id, document_type

- POST `/api/collaboration/lock`
  - Lock document for editing
  - Parameters: session_id, user_id, document_id

- POST `/api/collaboration/unlock`
  - Release document lock
  - Parameters: session_id, user_id, document_id

- POST `/api/collaboration/edit_document`
  - Edit document (requires lock)
  - Parameters: session_id, user_id, document_id, document_content

- GET `/api/collaboration/document/{document_id}`
  - Get document details and history
  - Parameters: session_id

### WebSocket
- WS `/ws/{user_id}`
  - Real-time updates connection
  - Receives session and document updates

## Current Implementation Details
1. In-Memory Storage:
   - Sessions stored in RealtimeCollaborationService
   - Document content and history maintained in memory
   - Lock status tracked per session/document
   - Note: Data is lost on server restart

2. Locking Mechanism:
   - Single-user lock system
   - Must acquire lock before editing
   - Automatic lock validation on edit attempts
   - Lock release functionality

3. Version Control:
   - Document versions tracked
   - History maintained with timestamps
   - User attribution for changes

## Deployment Status
1. Latest deployment includes static landing page with custom image
2. Code has been pushed to GitHub and deployed to Render
3. Service is live at https://faraday-ai.com
4. Landing page accessible and displaying custom image
5. Real-time collaboration features ready for local development and testing

## Latest Updates and Changes

### Deployment Configuration
1. Render Configuration:
   - Service Name: faraday-ai
   - Environment: Python
   - Region: Oregon
   - Plan: Free
   - Build Command: 
     ```bash
     pip install -r requirements.txt
     mkdir -p /tmp/faraday-ai/logs
     chmod -R 777 /tmp/faraday-ai/logs
     mkdir -p static/images
     chmod -R 755 static
     ```
   - Start Command: `gunicorn --config gunicorn.conf.py main:app`

2. Environment Variables:
   - PYTHON_VERSION: 3.11.0
   - PYTHONPATH: .
   - APP_ENVIRONMENT: production
   - PORT: 8000
   - LOG_LEVEL: info
   - LOG_DIR: /tmp/faraday-ai/logs
   - VERSION: 0.1.0
   - WORKERS: 4
   - ALLOWED_HOSTS: faraday-ai.onrender.com,localhost,127.0.0.1,faraday-ai.com,www.faraday-ai.com
   - CORS_ORIGINS: https://faraday-ai.com,https://www.faraday-ai.com
   - RATELIMIT_STORAGE_URL: memory://
   - RATELIMIT_DEFAULT: "100/minute"
   - RATELIMIT_STRATEGY: fixed-window

3. Security Headers:
   - X-Frame-Options: DENY
   - X-Content-Type-Options: nosniff
   - Strict-Transport-Security: max-age=31536000; includeSubDomains
   - Content-Security-Policy: "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline';"

### Development Workflow
1. Local Development:
   - Use Docker for local testing and development
   - Docker setup for consistent development environment
   - Local testing of all features before deployment

2. Deployment Process:
   - Push changes directly from Cursor to GitHub
   - Render automatically deploys from GitHub repository
   - No direct Docker deployment to Render
   - Automatic deployment on main branch updates

3. Static Assets:
   - Static files stored in `static/` directory
   - Images stored in `static/images/`
   - Proper permissions set during build process
   - Automatic handling of static file updates

### Testing and Verification
1. Local Testing:
   ```bash
   # Test local deployment
   docker-compose up
   
   # Verify application
   curl http://localhost:8000/test
   ```

2. Production Verification:
   ```bash
   # Check production health
   curl https://faraday-ai.com/test
   
   # Verify static assets
   curl https://faraday-ai.com/static/index.html
   ```

### Monitoring and Maintenance
1. Log Management:
   - Logs stored in `/tmp/faraday-ai/logs`
   - Proper permissions for log writing
   - Log rotation and cleanup

2. Performance Monitoring:
   - Memory usage tracking
   - CPU usage monitoring
   - Request rate limiting
   - Health check endpoint

3. Security Measures:
   - CORS protection
   - Rate limiting
   - Security headers
   - Input validation

## Setup Instructions

### Prerequisites
1. Python 3.x
2. Virtual environment (venv)
3. Git (for version control)
4. Terminal/Command Prompt
5. Code editor (VS Code recommended)

### Installation Steps
1. Open Terminal/Command Prompt

2. Navigate to your projects directory:
   ```bash
   # On macOS/Linux
   cd ~/Projects/New\ Faraday\ Cursor/Faraday-AI
   
   # On Windows
   cd "C:\Path\To\Projects\New Faraday Cursor\Faraday-AI"
   ```

3. Clone the repository (if not already done):
   ```bash
   git clone https://github.com/Faraday-AI/Faraday-AI.git
   cd Faraday-AI
   ```

4. Create and activate virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server
1. Ensure you're in the project root directory:
   ```bash
   # Check current directory
   pwd  # On macOS/Linux
   cd   # On Windows
   
   # Should show: /Path/to/Faraday-AI
   ```

2. Ensure virtual environment is activated:
   ```bash
   # Should show (venv) at start of prompt
   # If not, activate it using step 4 from Installation
   ```

3. Start the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. Server access points:
   - Main URL: http://127.0.0.1:8000
   - API documentation: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc
   - Landing page: http://127.0.0.1:8000/static/index.html

5. To stop the server:
   - Press CTRL+C in the terminal
   - Server will gracefully shut down

### Troubleshooting
1. If "command not found":
   - Ensure you're in the correct directory
   - Verify virtual environment is activated
   - Try reinstalling dependencies

2. If port is in use:
   - Change port: `python -m uvicorn app.main:app --reload --port 8001`
   - Or find and stop the process using port 8000

3. If modules not found:
   - Verify you're in project root directory
   - Confirm all dependencies are installed
   - Try deactivating and reactivating virtual environment

## Testing the System

### Original Endpoints
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

### Collaboration Features Testing

#### Create a Session
```bash
curl -X POST "http://127.0.0.1:8000/api/collaboration/create?session_id=test-session&user_id=user1"
```

#### Share a Document
```bash
curl -X POST "http://127.0.0.1:8000/api/collaboration/share_document?session_id=test-session&user_id=user1&document_id=doc1&document_type=text"
```

#### Lock a Document
```bash
curl -X POST "http://127.0.0.1:8000/api/collaboration/lock?session_id=test-session&user_id=user1&document_id=doc1"
```

#### Edit a Document
```bash
curl -X POST "http://127.0.0.1:8000/api/collaboration/edit_document?session_id=test-session&user_id=user1&document_id=doc1" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated document content"}'
```

#### Check Document Status
```bash
curl "http://127.0.0.1:8000/api/collaboration/document/doc1?session_id=test-session"
```

## Recent Testing Progress

### Session Management Testing
1. Session Creation and Joining:
   - Successfully created multiple test sessions (test-session-6 through test-session-12)
   - Successfully joined sessions with different users (user1, user2, user3)
   - Successfully left sessions with proper cleanup
   - Proper error handling for:
     * Attempting to join non-existent sessions
     * Attempting to join already joined sessions
     * Attempting to leave non-existent sessions
     * Attempting to leave already left sessions

2. Session Status:
   - Successfully retrieved session status
   - Proper handling of session cleanup when empty
   - Accurate participant tracking
   - Correct metadata maintenance

### Document Management Testing
1. Document Operations:
   - Successfully shared documents in sessions
   - Successfully created documents with different types
   - Successfully deleted documents with proper authorization
   - Proper error handling for:
     * Attempting to delete non-existent documents
     * Attempting to delete documents in non-existent sessions
     * Attempting to delete documents without proper authorization

2. Document Locking System:
   - Successfully implemented lock acquisition
   - Successfully implemented lock release
   - Proper lock status checking
   - Lock timeout functionality working
   - Error handling for:
     * Attempting to edit without a lock
     * Attempting to acquire lock when already locked
     * Attempting to unlock without authorization

3. Document Editing:
   - Successful edits when proper lock was acquired
   - Failed edits when no lock was present
   - Version tracking working correctly
   - History tracking maintained

4. Document Approval System:
   - Successfully tested approval workflow
   - Document status changes to "approved" after approval
   - Proper tracking of who approved and when

### History Tracking
- Successfully tracked document version history
- Maintained user attribution for changes
- Timestamp tracking working correctly
- History retrieval working properly

### Current Test Session (test-session-12)
- Successfully created and managed
- Multiple users participated
- Document operations tested
- Lock mechanism verified
- History tracking confirmed

### Next Testing Steps
1. Test concurrent editing scenarios
2. Test WebSocket real-time updates
3. Test session persistence
4. Test edge cases in document locking
5. Test session timeout functionality

## Important Files
1. `app/main.py` - Contains all endpoints and core logic
2. `app/services/realtime_collaboration_service.py` - Collaboration service implementation
3. `render.yaml` - Deployment configuration
4. `.env` - Environment variables
5. `requirements.txt` - Project dependencies

## Important Notes
1. Server restarts clear all data (in-memory storage)
2. Document locks must be acquired before editing
3. Only one user can hold a document lock at a time
4. WebSocket connections provide real-time updates
5. Environment variables must be set in Render's dashboard for deployment

## Current Limitations
1. No persistent storage (data lost on restart)
2. No authentication system
3. Basic error handling
4. No conflict resolution for concurrent edits
5. Deployment issues with some endpoints

## Next Steps
1. Implement persistent storage (database)
2. Add user authentication
3. Enhance error handling
4. Add conflict resolution
5. Implement document diff tracking
6. Add user presence indicators
7. Fix deployment issues on Render
8. Verify all routes are loading properly
9. Add more comprehensive logging

## Dependencies
Key dependencies from requirements.txt:
- fastapi
- uvicorn
- websockets
- python-multipart
- typing-extensions
- pydantic
- gunicorn (for deployment)

## Recent Testing Progress (Added March 2024)

### Session Management Testing
1. Session Creation and Joining:
   - Successfully created multiple test sessions (test-session-6 through test-session-12)
   - Successfully joined sessions with different users (user1, user2, user3)
   - Successfully left sessions with proper cleanup
   - Proper error handling for:
     * Attempting to join non-existent sessions
     * Attempting to join already joined sessions
     * Attempting to leave non-existent sessions
     * Attempting to leave already left sessions

2. Session Status:
   - Successfully retrieved session status
   - Proper handling of session cleanup when empty
   - Accurate participant tracking
   - Correct metadata maintenance

### Document Management Testing
1. Document Operations:
   - Successfully shared documents in sessions
   - Successfully created documents with different types
   - Successfully deleted documents with proper authorization
   - Proper error handling for:
     * Attempting to delete non-existent documents
     * Attempting to delete documents in non-existent sessions
     * Attempting to delete documents without proper authorization

2. Document Locking System:
   - Successfully implemented lock acquisition
   - Successfully implemented lock release
   - Proper lock status checking
   - Lock timeout functionality working
   - Error handling for:
     * Attempting to edit without a lock
     * Attempting to acquire lock when already locked
     * Attempting to unlock without authorization

3. Document Editing:
   - Successful edits when proper lock was acquired
   - Failed edits when no lock was present
   - Version tracking working correctly
   - History tracking maintained

4. Document Approval System:
   - Successfully tested approval workflow
   - Document status changes to "approved" after approval
   - Proper tracking of who approved and when

### History Tracking
- Successfully tracked document version history
- Maintained user attribution for changes
- Timestamp tracking working correctly
- History retrieval working properly

### Current Test Session (test-session-12)
- Successfully created and managed
- Multiple users participated
- Document operations tested
- Lock mechanism verified
- History tracking confirmed

### Next Testing Steps
1. Test concurrent editing scenarios
2. Test WebSocket real-time updates
3. Test session persistence
4. Test edge cases in document locking
5. Test session timeout functionality