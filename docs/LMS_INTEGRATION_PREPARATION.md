# LMS Integration Preparation Guide

**Date:** November 13, 2025  
**Status:** Ready to Begin  
**Estimated Time:** 20-30 hours

---

## Overview

LMS (Learning Management System) integration will allow the Faraday AI platform to sync with external learning management systems:

- **Canvas** - Instructure Canvas LMS
- **Blackboard** - Blackboard Learn
- **Moodle** - Open-source LMS
- **PowerSchool** - K-12 student information system
- **Schoology** - K-12 learning management platform
- **Google Classroom** - Google's learning management platform

---

## Prerequisites

Before starting LMS integration, you'll need:

### 1. LMS API Credentials

**Canvas:**
- [ ] Canvas API Key and Secret
- [ ] Canvas Instance URL
- [ ] OAuth credentials

**Blackboard:**
- [ ] Blackboard API Key and Secret
- [ ] Blackboard Instance URL
- [ ] Application Key and Secret

**Moodle:**
- [ ] Moodle API Key (Web Service Token)
- [ ] Moodle Instance URL

**PowerSchool:**
- [ ] PowerSchool API Client ID and Secret
- [ ] PowerSchool Instance URL
- [ ] OAuth 2.0 credentials

**Schoology:**
- [ ] Schoology API Key and Secret
- [ ] Schoology Instance URL
- [ ] OAuth credentials

**Google Classroom:**
- [ ] Google Cloud Project with Classroom API enabled
- [ ] OAuth 2.0 Client ID and Secret
- [ ] Service Account credentials (optional, for domain-wide delegation)

### 2. LMS API Documentation
- [ ] Canvas API documentation: https://canvas.instructure.com/doc/api/
- [ ] Blackboard API documentation: https://developer.blackboard.com/
- [ ] Moodle API documentation: https://docs.moodle.org/dev/Web_services_API
- [ ] PowerSchool API documentation: https://support.powerschool.com/developer/
- [ ] Schoology API documentation: https://developers.schoology.com/
- [ ] Google Classroom API documentation: https://developers.google.com/classroom

### 3. Test LMS Instance
- [ ] Access to a test/sandbox LMS instance for each system
- [ ] Test user accounts (teacher and student roles)
- [ ] Test courses/classes
- [ ] Test assignments and grades

---

## Integration Scope

### Core Features to Implement

1. **Authentication & Authorization**
   - OAuth 2.0 flow for LMS
   - Token storage and refresh
   - User mapping (LMS user ↔ Faraday user)

2. **Course/Class Synchronization**
   - Fetch courses from LMS
   - Sync course rosters
   - Map LMS courses to Faraday classes

3. **Assignment Synchronization**
   - Fetch assignments from LMS
   - Create assignments in LMS
   - Sync assignment grades

4. **Grade Passback**
   - Send grades from Faraday to LMS
   - Handle grade updates
   - Grade history tracking

5. **Student Roster Sync**
   - Import students from LMS
   - Sync student enrollments
   - Handle student updates

---

## Implementation Plan

### Phase 1: Base Infrastructure (4-6 hours)
- [ ] Create LMS service abstraction layer (`BaseLMSService`)
- [ ] Create database models for LMS tokens/connections
- [ ] Create API endpoints for LMS authentication
- [ ] Implement token storage and encryption
- [ ] Create LMS factory pattern for service selection

### Phase 2: Canvas Integration (8-10 hours)
- [ ] Canvas API client implementation
- [ ] Canvas OAuth flow
- [ ] Canvas course/assignment sync
- [ ] Canvas grade passback
- [ ] Canvas student roster sync
- [ ] **Canvas + OpenAI Integration** - Use existing OpenAI API key for Canvas AI features

### Phase 3: Blackboard Integration (6-8 hours)
- [ ] Blackboard API client implementation
- [ ] Blackboard OAuth flow
- [ ] Blackboard course/assignment sync
- [ ] Blackboard grade passback
- [ ] Blackboard student roster sync
- [ ] **Blackboard + OpenAI Integration** - Use existing OpenAI API key for Blackboard AI features

### Phase 4: Moodle Integration (6-8 hours)
- [ ] Moodle API client implementation
- [ ] Moodle Web Service Token authentication
- [ ] Moodle course/assignment sync
- [ ] Moodle grade passback
- [ ] Moodle student roster sync
- [ ] **Moodle + OpenAI Integration** - Use existing OpenAI API key for Moodle AI features

### Phase 5: PowerSchool Integration (8-10 hours)
- [ ] PowerSchool API client implementation
- [ ] PowerSchool OAuth 2.0 flow
- [ ] PowerSchool course/assignment sync
- [ ] PowerSchool grade passback
- [ ] PowerSchool student roster sync
- [ ] **PowerSchool + OpenAI Integration** - Use existing OpenAI API key (PowerBuddy already uses Azure OpenAI, we can add direct OpenAI integration)

### Phase 6: Schoology Integration (6-8 hours)
- [ ] Schoology API client implementation
- [ ] Schoology OAuth flow
- [ ] Schoology course/assignment sync
- [ ] Schoology grade passback
- [ ] Schoology student roster sync
- [ ] **Schoology + OpenAI Integration** - Use existing OpenAI API key (PowerBuddy available, we can add direct OpenAI integration)

### Phase 7: Google Classroom Integration (8-10 hours)
- [ ] Google Classroom API client implementation
- [ ] Google OAuth 2.0 flow
- [ ] Google Classroom course/assignment sync
- [ ] Google Classroom grade passback
- [ ] Google Classroom student roster sync
- [ ] **Google Classroom + OpenAI Integration** - Use existing OpenAI API key for AI features (Google has native Gemini, but OpenAI can be integrated via API)

### Phase 8: Testing & Documentation (4-6 hours)
- [ ] Integration tests for all LMS systems
- [ ] API documentation
- [ ] User guide
- [ ] Deployment guide
- [ ] LMS-specific configuration guides

---

## Database Schema

### Tables Needed

1. **lms_connections**
   - `id` (UUID, primary key)
   - `user_id` (UUID, foreign key to users)
   - `lms_type` (enum: canvas, blackboard, moodle, powerschool, schoology, google_classroom)
   - `access_token` (encrypted)
   - `refresh_token` (encrypted, nullable)
   - `expires_at` (timestamp, nullable)
   - `lms_user_id` (string)
   - `lms_base_url` (string)
   - `lms_instance_id` (string, nullable - for multi-tenant systems)
   - `additional_config` (JSONB, nullable - for LMS-specific settings)
   - `created_at`, `updated_at` (timestamps)

2. **lms_course_mappings**
   - `id` (UUID, primary key)
   - `lms_connection_id` (UUID, foreign key)
   - `lms_course_id` (string)
   - `faraday_class_id` (UUID, foreign key to classes)
   - `sync_enabled` (boolean)
   - `created_at`, `updated_at` (timestamps)

3. **lms_assignment_sync**
   - `id` (UUID, primary key)
   - `lms_course_mapping_id` (UUID, foreign key)
   - `lms_assignment_id` (string)
   - `faraday_assignment_id` (UUID, foreign key)
   - `last_synced_at` (timestamp)
   - `sync_direction` (enum: lms_to_faraday, faraday_to_lms, bidirectional)
   - `created_at`, `updated_at` (timestamps)

4. **lms_grade_sync**
   - `id` (UUID, primary key)
   - `lms_assignment_sync_id` (UUID, foreign key)
   - `student_id` (UUID, foreign key)
   - `lms_grade` (decimal)
   - `faraday_grade` (decimal)
   - `last_synced_at` (timestamp)
   - `sync_status` (enum: pending, synced, failed)
   - `created_at`, `updated_at` (timestamps)

---

## API Endpoints to Create

### Authentication
- `POST /api/v1/integration/lms/{lms_type}/auth` - Initiate OAuth flow
- `GET /api/v1/integration/lms/{lms_type}/callback` - OAuth callback
- `GET /api/v1/integration/lms/connections` - List user's LMS connections
- `DELETE /api/v1/integration/lms/connections/{connection_id}` - Disconnect LMS

### Course Sync
- `GET /api/v1/integration/lms/{lms_type}/courses` - Fetch courses from LMS
- `POST /api/v1/integration/lms/course-mappings` - Create course mapping
- `GET /api/v1/integration/lms/course-mappings` - List course mappings
- `PUT /api/v1/integration/lms/course-mappings/{mapping_id}` - Update mapping
- `POST /api/v1/integration/lms/course-mappings/{mapping_id}/sync` - Manual sync

### Assignment Sync
- `GET /api/v1/integration/lms/course-mappings/{mapping_id}/assignments` - List assignments
- `POST /api/v1/integration/lms/assignment-sync` - Create assignment sync
- `POST /api/v1/integration/lms/assignment-sync/{sync_id}/sync` - Manual sync

### Grade Sync
- `POST /api/v1/integration/lms/grade-sync` - Sync grades
- `GET /api/v1/integration/lms/grade-sync/{sync_id}/status` - Check sync status

---

## Service Architecture

### Service Layer Structure

```
app/services/integration/
├── lms/
│   ├── __init__.py
│   ├── base_lms_service.py          # Abstract base class
│   ├── canvas_service.py            # Canvas implementation (with OpenAI integration)
│   ├── blackboard_service.py        # Blackboard implementation
│   ├── moodle_service.py            # Moodle implementation (with OpenAI integration)
│   ├── powerschool_service.py       # PowerSchool implementation
│   ├── schoology_service.py         # Schoology implementation
│   ├── google_classroom_service.py  # Google Classroom implementation
│   └── lms_factory.py               # Factory to get correct service
```

### OpenAI Integration

**All LMS Systems Support OpenAI Integration:**
- **Canvas & Moodle**: Direct OpenAI API integration support
- **PowerSchool & Schoology**: Native PowerBuddy AI (Azure OpenAI), plus direct OpenAI API integration possible
- **Google Classroom**: API-based OpenAI integration (Google also has native Gemini AI)
- **Blackboard**: API-based OpenAI integration

**Implementation:**
- Use existing `OpenAIService` from `app/services/ai/openai_service.py`
- Reuse `OPENAI_API_KEY` environment variable (already configured)
- Integrate AI features such as:
  - Assignment feedback generation (all systems)
  - Content suggestions (all systems)
  - Automated grading assistance (all systems)
  - Student progress analysis (all systems)
  - Quiz question generation (Moodle, Schoology)
  - Forum discussion enhancement (Moodle)
  - Lesson plan generation (Schoology, PowerSchool)
  - Personalized learning pathways (PowerSchool, Schoology)

### Models

```
app/models/integration/
├── lms_connection.py
├── lms_course_mapping.py
├── lms_assignment_sync.py
└── lms_grade_sync.py
```

### API Endpoints

```
app/api/v1/endpoints/
├── lms_auth.py          # Authentication endpoints
├── lms_courses.py       # Course sync endpoints
├── lms_assignments.py   # Assignment sync endpoints
└── lms_grades.py        # Grade sync endpoints
```

---

## Security Considerations

1. **Token Encryption**
   - Use existing `TokenEncryptionService` for storing LMS tokens
   - Encrypt access tokens and refresh tokens at rest

2. **OAuth Security**
   - Validate state parameter
   - Use PKCE for OAuth flows
   - Implement token refresh automatically

3. **Rate Limiting**
   - Apply rate limiting to LMS API calls
   - Respect LMS API rate limits

4. **Error Handling**
   - Handle token expiration gracefully
   - Log security events
   - Implement retry logic with exponential backoff

---

## Testing Strategy

### Unit Tests
- [ ] Test LMS service methods
- [ ] Test token encryption/decryption
- [ ] Test OAuth flow
- [ ] Test course/assignment mapping

### Integration Tests
- [ ] Test Canvas integration end-to-end
- [ ] Test Canvas + OpenAI integration
- [ ] Test Blackboard integration end-to-end
- [ ] Test Blackboard + OpenAI integration
- [ ] Test Moodle integration end-to-end
- [ ] Test Moodle + OpenAI integration
- [ ] Test PowerSchool integration end-to-end
- [ ] Test PowerSchool + OpenAI integration
- [ ] Test Schoology integration end-to-end
- [ ] Test Schoology + OpenAI integration
- [ ] Test Google Classroom integration end-to-end
- [ ] Test Google Classroom + OpenAI integration
- [ ] Test grade passback
- [ ] Test error handling

### Mock LMS API
- [ ] Create mock LMS API server for testing
- [ ] Test without real LMS credentials

---

## Next Steps

1. **Wait for full test suite to pass** ✅
2. **Gather LMS API credentials** (Canvas, Blackboard, Moodle)
3. **Review LMS API documentation**
4. **Set up test LMS instance**
5. **Begin Phase 1: Base Infrastructure**

---

## Questions to Answer Before Starting

1. ✅ Which LMS systems do you need to support? 
   - **Answer:** Canvas, Blackboard, Moodle, PowerSchool, Schoology, Google Classroom
2. Do you have API credentials for the LMS systems?
3. Do you have access to a test/sandbox LMS instance?
4. What's the priority order? (Canvas first, then others?)
5. Do you need bidirectional sync or one-way only?
6. ✅ OpenAI Integration:
   - **Answer:** Use existing OpenAI API key for **ALL LMS systems** (Canvas, Moodle, Blackboard, PowerSchool, Schoology, Google Classroom)
   - OpenAI service already configured and available
   - PowerSchool & Schoology have native PowerBuddy AI (Azure OpenAI), but we can add direct OpenAI integration
   - Google Classroom has native Gemini AI, but OpenAI can be integrated via API
   - See `docs/LMS_OPENAI_INTEGRATION_NOTES.md` for details

---

## References

- Canvas API: https://canvas.instructure.com/doc/api/
- Canvas + OpenAI Integration: https://canvas.instructure.com/doc/api/ (check for AI features)
- Blackboard API: https://developer.blackboard.com/
- Moodle API: https://docs.moodle.org/dev/Web_services_API
- Moodle + OpenAI Integration: https://docs.moodle.org/dev/Web_services_API (check for AI plugins)
- PowerSchool API: https://support.powerschool.com/developer/
- Schoology API: https://developers.schoology.com/
- Google Classroom API: https://developers.google.com/classroom
- OpenAI API (already integrated): Using existing `OpenAIService` from `app/services/ai/openai_service.py`

---

**Status:** Ready to begin once full test suite passes ✅

