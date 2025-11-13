# LMS Integration Prerequisites Checklist

**Date:** November 13, 2025  
**Status:** Pre-Implementation  
**Purpose:** Complete checklist of everything needed before starting LMS integration

---

## ✅ Already Configured

- [x] **OpenAI API Key** - Already set in `run.sh` and `docker-compose.yml`
- [x] **OpenAI Service** - `app/services/ai/openai_service.py` is implemented and working
- [x] **Token Encryption Service** - `app/services/integration/token_encryption.py` exists (used for Microsoft integration)
- [x] **Database Infrastructure** - PostgreSQL database is set up and running
- [x] **Test Suite** - All 1405 tests passing, ready for new integration tests

---

## 🔴 Required Before Starting

### 1. Canvas Integration

**API Credentials:**
- [ ] Canvas API Key (Access Token)
- [ ] Canvas Instance URL (e.g., `https://your-school.instructure.com`)
- [ ] OAuth Client ID (if using OAuth)
- [ ] OAuth Client Secret (if using OAuth)

**Where to Get:**
- Canvas Admin → Settings → Integrations → API
- Or: Account → Settings → New Access Token

**OAuth Setup:**
- [ ] Register application in Canvas Developer Keys
- [ ] Set Redirect URI: `https://faraday-ai.com/api/v1/integration/lms/canvas/callback`
- [ ] Configure OAuth scopes (read/write courses, assignments, grades)

**Test Instance:**
- [ ] Access to Canvas test/sandbox instance (or production with test account)
- [ ] Test teacher account
- [ ] Test student account
- [ ] Test course with assignments

---

### 2. Blackboard Integration

**API Credentials:**
- [ ] Blackboard Application Key
- [ ] Blackboard Application Secret
- [ ] Blackboard Instance URL (e.g., `https://your-school.blackboard.com`)
- [ ] Blackboard Learn REST API Key (if using REST API)

**Where to Get:**
- Blackboard Admin → System Admin → Integrations → REST API Integrations
- Create new REST API integration

**OAuth Setup:**
- [ ] Register application in Blackboard Developer Portal
- [ ] Set Redirect URI: `https://faraday-ai.com/api/v1/integration/lms/blackboard/callback`
- [ ] Configure OAuth scopes (read/write courses, assignments, grades)

**Test Instance:**
- [ ] Access to Blackboard test instance
- [ ] Test teacher account
- [ ] Test student account
- [ ] Test course with assignments

---

### 3. Moodle Integration

**API Credentials:**
- [ ] Moodle Web Service Token
- [ ] Moodle Instance URL (e.g., `https://your-school.moodle.com`)
- [ ] Moodle Site Administrator access (to create web service token)

**Where to Get:**
- Moodle Admin → Site Administration → Server → Web Services → Manage Tokens
- Create token for a user with appropriate permissions

**Authentication:**
- Moodle uses Web Service Token (not OAuth)
- Token is user-specific and has permissions based on user role

**Test Instance:**
- [ ] Access to Moodle test instance
- [ ] Test teacher account (with web service token)
- [ ] Test student account
- [ ] Test course with assignments

---

### 4. PowerSchool Integration

**API Credentials:**
- [ ] PowerSchool API Client ID
- [ ] PowerSchool API Client Secret
- [ ] PowerSchool Instance URL (e.g., `https://your-school.powerschool.com`)
- [ ] PowerSchool OAuth 2.0 credentials

**Where to Get:**
- PowerSchool Admin → System → System Settings → API Settings
- Create OAuth 2.0 application

**OAuth Setup:**
- [ ] Register OAuth 2.0 application in PowerSchool
- [ ] Set Redirect URI: `https://faraday-ai.com/api/v1/integration/lms/powerschool/callback`
- [ ] Configure OAuth scopes (read/write students, courses, grades)

**Test Instance:**
- [ ] Access to PowerSchool test instance
- [ ] Test teacher account
- [ ] Test student account
- [ ] Test course with assignments

**Note:** PowerSchool has PowerBuddy AI (Azure OpenAI), but we'll add direct OpenAI integration for additional features.

---

### 5. Schoology Integration

**API Credentials:**
- [ ] Schoology API Key
- [ ] Schoology API Secret
- [ ] Schoology Instance URL (e.g., `https://your-school.schoology.com`)

**Where to Get:**
- Schoology Admin → Integrations → API Access
- Create new API application

**OAuth Setup:**
- [ ] Register application in Schoology Developer Portal
- [ ] Set Redirect URI: `https://faraday-ai.com/api/v1/integration/lms/schoology/callback`
- [ ] Configure OAuth scopes (read/write courses, assignments, grades)

**Test Instance:**
- [ ] Access to Schoology test instance
- [ ] Test teacher account
- [ ] Test student account
- [ ] Test course with assignments

**Note:** Schoology has PowerBuddy AI (Azure OpenAI) available, but we'll add direct OpenAI integration for additional features.

---

### 6. Google Classroom Integration

**API Credentials:**
- [ ] Google Cloud Project with Classroom API enabled
- [ ] OAuth 2.0 Client ID
- [ ] OAuth 2.0 Client Secret
- [ ] Google Cloud Console access

**Where to Get:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable Google Classroom API
4. Create OAuth 2.0 credentials (Web Application)
5. Set authorized redirect URIs

**OAuth Setup:**
- [ ] Enable Google Classroom API in Google Cloud Console
- [ ] Create OAuth 2.0 Client ID (Web Application)
- [ ] Set Redirect URI: `https://faraday-ai.com/api/v1/integration/lms/google-classroom/callback`
- [ ] Configure OAuth consent screen
- [ ] Add scopes: `https://www.googleapis.com/auth/classroom.courses.readonly`, `https://www.googleapis.com/auth/classroom.rosters.readonly`, `https://www.googleapis.com/auth/classroom.profile.emails`, `https://www.googleapis.com/auth/classroom.coursework.me`, `https://www.googleapis.com/auth/classroom.grades`

**Service Account (Optional):**
- [ ] Service Account JSON key (for domain-wide delegation, if needed)
- [ ] Domain-wide delegation enabled (if using service account)

**Test Instance:**
- [ ] Google Workspace for Education account (or personal Google account for testing)
- [ ] Test teacher account
- [ ] Test student account
- [ ] Test course with assignments

**Note:** Google Classroom has native Gemini AI, but we'll integrate OpenAI API for additional features.

---

## 📋 General Requirements

### Environment Variables

Add to `run.sh` and `docker-compose.yml`:

```bash
# Canvas
CANVAS_API_KEY=
CANVAS_BASE_URL=
CANVAS_CLIENT_ID=
CANVAS_CLIENT_SECRET=
CANVAS_REDIRECT_URI=https://faraday-ai.com/api/v1/integration/lms/canvas/callback

# Blackboard
BLACKBOARD_API_KEY=
BLACKBOARD_API_SECRET=
BLACKBOARD_BASE_URL=
BLACKBOARD_REDIRECT_URI=https://faraday-ai.com/api/v1/integration/lms/blackboard/callback

# Moodle
MOODLE_API_TOKEN=
MOODLE_BASE_URL=

# PowerSchool
POWERSCHOOL_CLIENT_ID=
POWERSCHOOL_CLIENT_SECRET=
POWERSCHOOL_BASE_URL=
POWERSCHOOL_REDIRECT_URI=https://faraday-ai.com/api/v1/integration/lms/powerschool/callback

# Schoology
SCHOOLOGY_API_KEY=
SCHOOLOGY_API_SECRET=
SCHOOLOGY_BASE_URL=
SCHOOLOGY_REDIRECT_URI=https://faraday-ai.com/api/v1/integration/lms/schoology/callback

# Google Classroom
GOOGLE_CLASSROOM_CLIENT_ID=
GOOGLE_CLASSROOM_CLIENT_SECRET=
GOOGLE_CLASSROOM_REDIRECT_URI=https://faraday-ai.com/api/v1/integration/lms/google-classroom/callback
GOOGLE_CLASSROOM_SERVICE_ACCOUNT_KEY=  # Optional, for domain-wide delegation
```

### Redirect URIs to Configure

For each LMS system that uses OAuth, you'll need to register these redirect URIs:

1. **Canvas:** `https://faraday-ai.com/api/v1/integration/lms/canvas/callback`
2. **Blackboard:** `https://faraday-ai.com/api/v1/integration/lms/blackboard/callback`
3. **PowerSchool:** `https://faraday-ai.com/api/v1/integration/lms/powerschool/callback`
4. **Schoology:** `https://faraday-ai.com/api/v1/integration/lms/schoology/callback`
5. **Google Classroom:** `https://faraday-ai.com/api/v1/integration/lms/google-classroom/callback`

**Note:** Moodle uses Web Service Token, not OAuth, so no redirect URI needed.

### Test Data Requirements

For each LMS system, you'll need:

- [ ] **Test Teacher Account** - With permissions to:
  - Create/manage courses
  - Create/manage assignments
  - View student grades
  - Sync rosters

- [ ] **Test Student Account** - To test:
  - Student roster sync
  - Grade passback
  - Assignment submission viewing

- [ ] **Test Course** - With:
  - At least 2-3 assignments
  - Student enrollments
  - Some completed assignments with grades

---

## 🎯 Priority Order Recommendation

Based on typical usage and complexity:

1. **Canvas** - Most common, well-documented API
2. **Google Classroom** - Very common, good API documentation
3. **Moodle** - Open-source, flexible
4. **PowerSchool** - K-12 focused, important for schools
5. **Schoology** - K-12 focused, part of PowerSchool ecosystem
6. **Blackboard** - Higher education focused, more complex API

**Note:** You can start with Phase 1 (Base Infrastructure) while gathering credentials for specific systems.

---

## 📚 Documentation to Review

Before starting, review API documentation for each system:

- [ ] [Canvas API Documentation](https://canvas.instructure.com/doc/api/)
- [ ] [Blackboard API Documentation](https://developer.blackboard.com/)
- [ ] [Moodle Web Services API](https://docs.moodle.org/dev/Web_services_API)
- [ ] [PowerSchool API Documentation](https://support.powerschool.com/developer/)
- [ ] [Schoology API Documentation](https://developers.schoology.com/)
- [ ] [Google Classroom API Documentation](https://developers.google.com/classroom)

---

## ✅ Ready to Start When

You can begin **Phase 1: Base Infrastructure** as soon as you have:
- [x] OpenAI API key (✅ Already have)
- [ ] At least ONE LMS system's credentials (to test the base infrastructure)

You can begin **Phase 2+ (Specific LMS Integration)** when you have:
- [ ] That LMS system's API credentials
- [ ] OAuth redirect URI configured (if using OAuth)
- [ ] Test instance access
- [ ] Test accounts (teacher and student)

---

## 🚀 Next Steps

1. **Gather credentials** for at least one LMS system (recommend Canvas or Google Classroom first)
2. **Set up OAuth redirect URIs** in each LMS system's developer portal
3. **Get test instance access** and create test accounts
4. **Review API documentation** for the first LMS system you'll integrate
5. **Begin Phase 1: Base Infrastructure** (can start while gathering credentials)

---

**Status:** Waiting for LMS API credentials and test instance access

