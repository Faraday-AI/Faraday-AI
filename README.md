# Faraday AI Platform

## Overview
This is a FastAPI application that integrates OpenAI for text generation and Microsoft Graph API for authentication and email/pptx/docx/pandas functionality. These APIs are specifically designed to power a Custom GPT that serves K-12 Physical Education, Health, and Driver's Education teachers in Elizabeth Public Schools (EPS), New Jersey.

## 🎯 Purpose
This API suite enables a specialized Custom GPT to assist educators by:
- Generating structured lesson plans aligned with New Jersey state standards
- Creating assessments following Bloom's Taxonomy
- Producing materials that align with Danielson's Framework for Teaching
- Managing and distributing educational content through Microsoft Office integration

## 🚀 Core Features
✅ **Authentication:** Uses Microsoft Graph API for secure user authentication  
✅ **OpenAI Integration:** Supports intelligent text generation with GPT-4 for lesson planning and content creation  
✅ **Document Generation:** Creates PowerPoint presentations, Word documents (including EPS Lesson Plan templates), and Excel files dynamically  
✅ **Email Integration:** Facilitates direct sharing of educational materials through Microsoft Graph API  
✅ **FERPA Compliance:** Ensures secure handling of educational data  
✅ **REST API:** Built with FastAPI and deployed on Render
✅ **Twilio Integration:** Supports voice and messaging capabilities
✅ **Google Cloud Translation:** Enables multilingual support

## 🌐 Deployment & Access
- **Main URL:** https://faraday-ai.com
- **API Documentation:** https://faraday-ai.com/docs
- **Development URL:** https://faraday-ai.onrender.com

## 🔒 Security & Compliance
- End-to-end encryption with SSL/TLS
- Microsoft 365 OAuth2 authentication
- Cloudflare DDoS protection
- FERPA-compliant data handling
- Secure credential management via Render environment variables

## 🎓 Key Capabilities

### 1. Lesson Planning & Assessment Generation
- Creates structured lesson plans using EPS templates
- Generates differentiated content for ELL, Special Education, 504, and Gifted students
- Produces assessments aligned with state standards

### 2. Document Management
- Automated creation of educational materials
- Secure storage in OneDrive
- Easy retrieval and sharing capabilities

### 3. Educational Enhancement
- AI-powered activity suggestions
- Differentiation strategy recommendations
- Higher-order thinking questions based on Bloom's Taxonomy

## 📦 Dependencies
Key dependencies and their versions:
```txt
fastapi==0.104.1
openai==1.3.7
numpy==1.24.3
pandas==2.0.3
twilio==9.5.0
python-jose[cryptography]==3.4.0
google-cloud-translate==3.15.0
```
For a complete list, see `requirements.txt`.

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Faraday-AI/Faraday-AI.git
cd Faraday-AI
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file with the following:
```env
# Microsoft Graph API Settings
MSCLIENTID=your_client_id
MSCLIENTSECRET=your_client_secret
MSTENANTID=your_tenant_id
REDIRECT_URI=https://faraday-ai.com/auth/callback

# OpenAI Settings
OPENAI_API_KEY=your_openai_key

# Optional Integrations
ENABLE_TWILIO=true
ENABLE_GOOGLE_CLOUD=true

# Twilio Settings (if enabled)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=your_twilio_number
TWILIO_VOICE_URL=https://faraday-ai.com/voice
TWILIO_WEBHOOK_URL=https://faraday-ai.com/api/v1/twilio/webhook
TWILIO_STATUS_CALLBACK=https://faraday-ai.com/api/v1/twilio/status
```

### 4. Development
Start the development server:
```bash
uvicorn app.main:app --reload
```

Access the API documentation:
- OpenAPI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚀 Deployment
The application is deployed on Render with the following configuration:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app`

DNS Configuration:
- Primary Domain: `faraday-ai.com`
- Development URL: `faraday-ai.onrender.com`
- SSL/TLS: Enabled with automatic certificate management
- CDN & Security: Cloudflare integration with Full SSL mode

## Contributing
Faraday AI is in active development. For contribution guidelines, please contact the development team.

## License
Proprietary software. All rights reserved.

## Contact
For more information about Faraday AI, please contact [Contact Information]. 