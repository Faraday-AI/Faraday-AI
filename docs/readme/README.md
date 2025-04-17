# Faraday AI Personal Education Assistant and School Management System Platform

## Project Overview
Faraday AI is an AI-powered personal education assistant and school management platform designed to enhance educational experiences through advanced tracking, security features, and AI-driven insights. The system combines personalized AI assistance with comprehensive tools for collaboration, resource management, and analytics to support educators and students in their educational journey.

### Current Implementation
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

## Setup Instructions

### Prerequisites
1. Python 3.x
2. Virtual environment (venv)
3. Git (for version control)
4. Terminal/Command Prompt
5. Code editor (VS Code recommended)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Faraday-AI/Faraday-AI.git
   cd Faraday-AI
   ```

2. Create and activate virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server
1. Start the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. Access points:
   - Main URL: http://127.0.0.1:8000
   - API documentation: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc
   - Landing page: http://127.0.0.1:8000/static/index.html

### Environment Setup

#### Local Development Setup
To set up your local development environment to match production:

1. Run the setup script:
   ```bash
   chmod +x setup_local.sh  # Make the script executable
   ./setup_local.sh         # Run the setup script
   ```

The setup script:
- Sets PYTHONPATH to `/app` to match production
- Creates necessary directories (models, static, logs, exports)
- Sets up symlinks for static files
- Sets appropriate permissions

#### Import Paths
The project uses absolute import paths with `/app/` notation. This is configured to work in both production and local development:

- Production: Configured through Docker and Render settings
- Local: Configured through the setup script

The imports in the codebase use `app.` notation (e.g., `from app.main import app`). This is intentional and matches the production environment.

#### Production Environment
In production (Render):
- PYTHONPATH is set to `/app` in the Dockerfile
- Static files are served from `/static/`
- A symlink is created from `/app/static` to `/static/`

## Project Structure
- `app/`: Main application code, including API endpoints and services
  - `app/main.py`: Core FastAPI application and endpoint definitions
  - `app/services/realtime_collaboration_service.py`: Real-time collaboration implementation
- `app/core/`: Core functionalities and configurations
- `app/services/`: Service layer for business logic
- `app/models/`: Data models and schemas
- `app/static/`: Static files and landing page
- `tests/`: Test files for unit and integration testing
- `docs/`: Documentation and guides

## Features

### Original Features
- **Educational Resources**: Resource recommendation and management
- **Analytics and Metrics**: User engagement tracking and performance metrics
- **Security**: Advanced security features and compliance tools

### Real-time Collaboration Features
1. Session Management:
   - Create and manage collaboration sessions
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

### Collaboration Endpoints
- POST `/api/collaboration/create`: Create new collaboration session
- GET `/api/collaboration/status`: Get session status
- POST `/api/collaboration/share_document`: Share document in session
- POST `/api/collaboration/lock`: Lock document for editing
- POST `/api/collaboration/unlock`: Release document lock
- POST `/api/collaboration/edit_document`: Edit document (requires lock)
- GET `/api/collaboration/document/{document_id}`: Get document details
- WS `/ws/{user_id}`: WebSocket connection for real-time updates

### Resource Management
- `/api/resources/`: Endpoints for resource management
- `/api/metrics/`: Endpoints for accessing analytics data

## Implementation Details

### Current Features
1. In-Memory Storage:
   - Sessions stored in RealtimeCollaborationService
   - Document content and history maintained in memory
   - Lock status tracked per session/document

2. Locking Mechanism:
   - Single-user lock system
   - Must acquire lock before editing
   - Automatic lock validation
   - Lock release functionality

3. Version Control:
   - Document versions tracked
   - History maintained with timestamps
   - User attribution for changes

### Deployment
- Deployed on Render (https://faraday-ai.com)
- Custom landing page with static assets
- Automatic deployments from main branch

## Testing

### Collaboration Feature Testing
```bash
# Create a session
curl -X POST "http://127.0.0.1:8000/api/collaboration/create?session_id=test-session&user_id=user1"

# Share a document
curl -X POST "http://127.0.0.1:8000/api/collaboration/share_document?session_id=test-session&user_id=user1&document_id=doc1&document_type=text"

# Lock and edit document
curl -X POST "http://127.0.0.1:8000/api/collaboration/lock?session_id=test-session&user_id=user1&document_id=doc1"
curl -X POST "http://127.0.0.1:8000/api/collaboration/edit_document?session_id=test-session&user_id=user1&document_id=doc1" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content"}'
```

## Current Limitations
1. In-memory storage (data lost on restart)
2. Basic authentication system
3. Limited error handling
4. No conflict resolution for concurrent edits

## Future Enhancements
1. Persistent storage (database implementation)
2. Enhanced authentication system
3. Improved error handling
4. Conflict resolution system
5. Document diff tracking
6. User presence indicators

## Contributing
Contributions are welcome! Please see the `CONTRIBUTING.md` file for guidelines.

## Contact Information
For support or inquiries, please contact the project maintainers at support@faraday-ai.com.
