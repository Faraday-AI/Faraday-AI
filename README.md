# Faraday AI

A specialized AI-powered educational platform designed to support teachers with AI assistance while maintaining FERPA/HIPAA compliance through a no-student-data approach.

## Current Features
- Custom AI interface for educational support
- Secure teacher-only access
- No student data storage (FERPA/HIPAA compliant)
- Educational optimizations
- Usage analytics tracking
- Real-time collaboration capabilities with WebSocket support
- Movement analysis features for physical activities
- Video processing capabilities for movement tracking
- Document sharing and version control
- Advanced analytics dashboard
- Custom landing page with responsive design
- Cross-platform compatibility (mobile and desktop)
- Cache-busting for static assets
- Safari-specific optimizations
- Mobile-first design approach
- Dynamic image cropping system
- Visual debugging tools for layout refinement
- PostgreSQL database implementation
- Redis caching system
- MinIO file storage

## Development Status
Currently in development, preparing for beta testing:
- Core AI integration complete
- Teacher interface implemented
- Analytics collection active
- Deployment infrastructure ready
- Movement analysis features in development
- Video processing capabilities in development
- Real-time collaboration features deployed
- Document sharing system active
- Landing page responsive design implemented
- Cross-platform compatibility achieved
- Static asset optimization complete
- Safari-specific optimizations implemented
- Mobile-first design approach established
- Dynamic image cropping system deployed
- Visual debugging tools integrated
- Database system implemented and operational
- Caching system active and optimized
- File storage system configured

## Technical Stack
- Frontend: Modern web interface with real-time updates
- Backend: FastAPI with WebSocket support
- AI: OpenAI API integration
- Database: PostgreSQL for persistent storage
- Cache: Redis for real-time features
- Storage: MinIO for file storage
- Analytics: Prometheus metrics
- Security: JWT authentication
- Monitoring: Grafana dashboards
- CI/CD: GitHub Actions
- CSS: Modern responsive design with vendor prefixes
- JavaScript: Cross-browser compatible
- Image Optimization: Cache-busting implementation
- Layout Tools: Visual debugging system
- Browser Support: Safari-specific optimizations
- Design Approach: Mobile-first methodology

## Running the Application

### Local Development
```bash
# Clone the repository
git clone https://github.com/your-username/Faraday-AI.git
cd Faraday-AI

# Create and activate virtual environment with Python 3.10
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start required services
brew services start postgresql@14
brew services start redis
brew services start minio

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual commands
docker build -t faraday-ai .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key faraday-ai
```

### Production Deployment

#### Render Deployment
1. Fork the repository to your GitHub account
2. Connect your Render account to GitHub
3. Create a new Web Service in Render
4. Select the repository
5. Configure environment variables:
   - OPENAI_API_KEY
   - ENVIRONMENT=production
   - DATABASE_URL
   - REDIS_URL
   - MINIO_URL
   - Other necessary variables
6. Deploy the service

Render will automatically build and deploy updates when you push to the main branch.

#### Docker Production Deployment
1. Pull the latest image:
   ```bash
   docker pull ghcr.io/your-username/faraday-ai:latest
   ```

2. Run with production settings:
   ```bash
   docker run -d \
     -p 80:8000 \
     -e OPENAI_API_KEY=your-key \
     -e ENVIRONMENT=production \
     -e DATABASE_URL=your-db-url \
     -e REDIS_URL=your-redis-url \
     -e MINIO_URL=your-minio-url \
     ghcr.io/your-username/faraday-ai:latest
   ```

### Repository Structure
```
Faraday-AI/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   │   ├── endpoints/     # Specific endpoint handlers
│   │   └── v1/           # API version 1
│   ├── core/             # Core functionality
│   │   ├── auth.py       # Authentication
│   │   ├── config.py     # Configuration
│   │   └── database.py   # Database setup
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   └── scripts/          # Utility scripts
├── config/               # Configuration files
├── docker/              # Docker configuration
├── static/              # Static files
│   └── images/         # Image assets
├── tests/               # Test suite
├── .env.example         # Environment template
├── docker-compose.yml   # Docker Compose config
├── Dockerfile          # Docker build file
└── prometheus.yml      # Prometheus configuration
```

## API Documentation
Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Project Overview
Faraday AI is an AI-powered educational platform designed to enhance teaching and learning experiences through advanced AI assistance, real-time collaboration, and comprehensive analytics. The system combines personalized AI support with tools for movement analysis, video processing, and educational resource management to support educators in their teaching journey.

### Current Implementation
- FastAPI backend service deployed on Render (https://faraday-ai.com)
- Real-time collaboration features with WebSocket support
- Document sharing and version control system
- Custom landing page with static assets and responsive design
- Integration with OpenAI's API for AI assistance
- PostgreSQL database for persistent storage
- Redis for caching and real-time features
- MinIO for file storage
- Docker-based deployment with monitoring stack
- ML models for movement analysis and behavior tracking
- Performance monitoring and analytics
- Automated testing and CI/CD pipeline
- Cross-platform compatibility implementation
- Safari-specific optimizations
- Cache-busting for static assets
- Dynamic image cropping system
- Visual debugging tools
- Mobile-first design implementation

### Development Phases
1. Beta Version (Current):
   - Focused implementation for K-12 PE, Health, and Driver's Ed teachers in Elizabeth Public Schools (EPS)
   - Custom GPT integration:
     * Specialized ChatGPT model trained for educational content
     * Direct integration with Faraday-AI's codebase
     * AI-powered assistance for curriculum development
   - Data Management:
     * PostgreSQL database implementation
     * Redis caching for performance
     * MinIO for file storage
     * Secure data handling for educational content
   - Testing and Feedback:
     * Core features and real-time collaboration testing
     * User feedback collection through integrated systems
     * Usage pattern analysis for optimization
     * Performance metrics tracking
   - ML Model Integration:
     * Movement analysis for PE activities
     * Behavior tracking and engagement metrics
     * Performance prediction models
     * Group dynamics analysis
   - Monitoring and Analytics:
     * Prometheus metrics collection
     * Grafana dashboards for visualization
     * Health checks and system monitoring
     * Performance tracking

2. Full Application (Planned):
   - Option A: Pilot program implementation in selected school districts
   - Option B: Private launch on Faraday-AI.com as a standalone service
   - Complete feature set including all planned enhancements
   - Scalable infrastructure for multiple institutions
   - Enhanced AI capabilities and database optimization
   - Advanced monitoring and analytics
   - Performance optimization and scaling

## Setup Instructions

### Prerequisites
1. Python 3.x
2. Virtual environment (venv)
3. Git (for version control)
4. Terminal/Command Prompt
5. Code editor (VS Code recommended)
6. Docker and Docker Compose (for containerized deployment)

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

### Running with Docker
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Access points:
   - Main URL: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - Grafana dashboard: http://localhost:3000
   - Prometheus metrics: http://localhost:9090

### Running Locally
1. Start the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. Access points:
   - Main URL: http://127.0.0.1:8000
   - API documentation: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc
   - Landing page: http://127.0.0.1:8000/static/index.html

## Project Structure
- `app/`: Main application code, including API endpoints and services
  - `app/main.py`: Core FastAPI application and endpoint definitions
  - `app/services/realtime_collaboration_service.py`: Real-time collaboration implementation
  - `app/services/ai_analytics.py`: AI analytics and ML model integration
  - `app/services/ai_vision.py`: Vision-based movement analysis
  - `app/services/ai_voice.py`: Voice analysis for engagement tracking
  - `app/services/ai_emotion.py`: Emotion analysis for student engagement
  - `app/services/ai_group.py`: Group dynamics analysis
- `app/core/`: Core functionalities and configurations
- `app/services/`: Service layer for business logic
- `app/models/`: Data models and schemas
- `app/static/`: Static files and landing page
- `tests/`: Test files for unit and integration testing
- `docs/`: Documentation and guides
- `docker/`: Docker configuration files
  - `docker-compose.yml`: Container orchestration
  - `Dockerfile`: Web service container definition
  - `nginx/`: Nginx configuration
  - `prometheus/`: Prometheus configuration
  - `grafana/`: Grafana configuration

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

4. PE-Specific Features:
   - Movement analysis for form checking
   - Group dynamics monitoring
   - Performance tracking
   - Behavior analysis for classroom management

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

### Analytics and ML Endpoints
- POST `/api/analytics/performance`: Analyze student performance
- POST `/api/analytics/behavior`: Analyze behavior patterns
- POST `/api/vision/movement-analysis`: Analyze movement patterns
- POST `/api/analytics/progress-report`: Generate progress reports

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

4. ML Model Integration:
   - Movement analysis for PE activities
   - Behavior tracking and engagement metrics
   - Performance prediction models
   - Group dynamics analysis
   - Model files stored in app/models directory

5. Monitoring Stack:
   - Prometheus for metrics collection
   - Grafana for visualization
   - Health checks and system monitoring
   - Performance tracking

### Deployment
- Multi-platform deployment:
  1. Render (Production):
     - FastAPI backend service deployed at https://faraday-ai.com
     - Custom landing page with static assets
     - Automatic deployments from main branch
     - Environment variables managed through Render dashboard
     - Gunicorn server with multiple workers
     - Static file serving and caching

  2. Docker (Development/Testing):
     - Containerized deployment with monitoring stack
     - Services:
       - web: FastAPI application
       - redis: Caching and session storage
       - prometheus: Metrics collection
       - grafana: Visualization and monitoring
       - nginx: Reverse proxy
     - Health checks configured
     - Monitoring stack integrated
     - Local development and testing environment

### Deployment Configuration
1. Render Service Settings:
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

2. Docker Configuration:
   - Service Name: faraday-ai
   - Services:
     - web: FastAPI application
     - redis: Caching and session storage
     - prometheus: Metrics collection
     - grafana: Visualization and monitoring
     - nginx: Reverse proxy
   - Health checks configured
   - Monitoring stack integrated

3. Environment Variables:
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

4. Security Configuration:
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

3. Static Assets Management:
   - Static files stored in `static/` directory
   - Images stored in `static/images/`
   - Proper permissions set during build process
   - Automatic handling of static file updates

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

### Comprehensive Testing Guide

#### 1. Collaboration Feature Testing
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

# Get document details
curl -X GET "http://127.0.0.1:8000/api/collaboration/document/doc1"

# Release document lock
curl -X POST "http://127.0.0.1:8000/api/collaboration/unlock?session_id=test-session&user_id=user1&document_id=doc1"
```

#### 2. Analytics and ML Testing
```bash
# Test movement analysis
curl -X POST "http://127.0.0.1:8000/api/vision/movement-analysis" \
  -H "Content-Type: multipart/form-data" \
  -F "video=@test_video.mp4" \
  -F "movement_type=basic_movement"

# Test behavior analysis
curl -X POST "http://127.0.0.1:8000/api/analytics/behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "student_data": {
      "student_id": "test123",
      "grade": "9",
      "class": "PE"
    },
    "classroom_data": {
      "activity_type": "team_sports",
      "duration": 45,
      "group_size": 20
    }
  }'

# Test performance analysis
curl -X POST "http://127.0.0.1:8000/api/analytics/performance" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test123",
    "activity_type": "running",
    "duration": 30,
    "distance": 100,
    "time": 15
  }'

# Generate progress report
curl -X POST "http://127.0.0.1:8000/api/analytics/progress-report" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test123",
    "period": "semester",
    "include_metrics": ["performance", "behavior", "attendance"]
  }'
```

#### 3. WebSocket Testing
```bash
# Using wscat for WebSocket testing
wscat -c ws://localhost:8000/ws/user1

# Send a message
{"type": "join_session", "session_id": "test-session"}
{"type": "document_update", "session_id": "test-session", "document_id": "doc1", "content": "New content"}
```

#### 4. Monitoring Stack Testing
```bash
# Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=up

# Check Grafana dashboard
# Access http://localhost:3000 in browser
# Default credentials: admin/admin

# Check health endpoint
curl http://localhost:8000/health
```

#### 5. Load Testing
```bash
# Using Apache Benchmark (ab)
ab -n 1000 -c 10 http://localhost:8000/test

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/test
```

### Testing Results History

#### March 2024 Testing Results

1. Collaboration System Testing:
   - Session Management:
     * Successfully created and managed multiple test sessions
     * Verified session state persistence
     * Confirmed participant tracking functionality
     * Tested session join/leave scenarios
   - Document Management:
     * Successfully shared documents within sessions
     * Verified document locking mechanism
     * Tested document version history
     * Confirmed document state persistence
   - Real-time Updates:
     * Successfully established WebSocket connections
     * Verified real-time updates for all actions
     * Tested concurrent editing prevention
     * Confirmed proper message broadcasting

2. ML Model Integration:
   - Movement Analysis:
     * Successfully initialized ML models
     * Verified movement analysis functionality
     * Tested form checking features
     * Confirmed real-time analysis capabilities
   - Behavior Tracking:
     * Successfully implemented behavior analysis
     * Verified engagement metrics
     * Tested classroom management features
     * Confirmed data collection accuracy
   - Performance Prediction:
     * Successfully implemented prediction models
     * Verified accuracy of predictions
     * Tested with various student data
     * Confirmed model reliability

3. Monitoring Stack:
   - Prometheus:
     * Successfully configured metrics collection
     * Verified data retention
     * Tested alert rules
     * Confirmed proper scraping
   - Grafana:
     * Successfully set up dashboards
     * Verified data visualization
     * Tested dashboard sharing
     * Confirmed real-time updates
   - Health Checks:
     * Successfully implemented health endpoints
     * Verified monitoring coverage
     * Tested alert notifications
     * Confirmed system reliability

4. Performance Testing:
   - Load Testing:
     * Successfully tested with 1000 concurrent users
     * Verified response times under load
     * Tested resource utilization
     * Confirmed system stability
   - Stress Testing:
     * Successfully tested under heavy load
     * Verified error handling
     * Tested recovery mechanisms
     * Confirmed system resilience

5. Security Testing:
   - Authentication:
     * Successfully tested user authentication
     * Verified session management
     * Tested token validation
     * Confirmed security measures
   - Authorization:
     * Successfully tested access control
     * Verified permission system
     * Tested role-based access
     * Confirmed proper restrictions
   - Data Protection:
     * Successfully tested data encryption
     * Verified secure transmission
     * Tested data validation
     * Confirmed privacy measures

### Test Environment Setup
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install test dependencies
pip install -r requirements-test.txt

# Run test suite
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Continuous Integration Testing
```bash
# GitHub Actions workflow
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest tests/
          pytest --cov=app tests/
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

## Latest Updates and Configuration

### Deployment Configuration
1. Render Service Settings:
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

3. Security Configuration:
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

3. Static Assets Management:
   - Static files stored in `static/` directory
   - Images stored in `static/images/`
   - Proper permissions set during build process
   - Automatic handling of static file updates

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

## Port Configuration

The application uses a dynamic port configuration system that automatically finds available ports for different services. You can configure the ports in two ways:

1. Using environment variables:
   - `API_PORT`: Main API server port (default: 8000)
   - `METRICS_PORT`: Prometheus metrics server port (default: 9090)
   - `WEBSOCKET_PORT`: WebSocket server port (default: 9100)

2. Using the .env file:
   Create a `.env` file in the project root with your desired port configurations:
   ```env
   API_PORT=8000
   METRICS_PORT=9090
   WEBSOCKET_PORT=9100
   ```

The application will automatically find available ports if the configured ports are already in use. This makes it easier to run multiple instances of the application or run it alongside other services without port conflicts.
