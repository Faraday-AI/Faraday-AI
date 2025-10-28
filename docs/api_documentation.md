# PE AI Assistant Beta - API Documentation

## Overview

The PE AI Assistant Beta provides a comprehensive API for physical education teachers to create lesson plans, assessments, manage resources, and interact with AI assistants. This documentation covers all available endpoints, authentication, and usage examples.

## Base URL

```
https://api.pe-ai-assistant.com/v1
```

## Authentication

All API requests require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

1. Register for a teacher account
2. Verify your email
3. Login to get your JWT token

```http
POST /auth/login
Content-Type: application/json

{
  "email": "teacher@example.com",
  "password": "your_password"
}
```

## Rate Limits

- **Free Tier**: 100 requests per hour
- **Beta Tier**: 500 requests per hour
- **Premium Tier**: 2000 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### Common Error Codes

- `UNAUTHORIZED` (401): Invalid or missing authentication
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `VALIDATION_ERROR` (422): Invalid input data
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

## Core Endpoints

### Teacher Authentication

#### Register Teacher
```http
POST /auth/register
Content-Type: application/json

{
  "email": "teacher@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "school_name": "Example Elementary",
  "subject_areas": ["PE", "Health"],
  "grade_levels": ["K-5", "6-8"]
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "teacher@example.com",
  "password": "secure_password"
}
```

#### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <your_jwt_token>
```

#### Logout
```http
POST /auth/logout
Authorization: Bearer <your_jwt_token>
```

### Lesson Plan Builder

#### Create Lesson Plan Template
```http
POST /lesson-plan-builder/templates
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Basketball Fundamentals",
  "description": "Basic basketball skills and techniques",
  "subject": "PE",
  "grade_level": "6-8",
  "duration_minutes": 45,
  "learning_objectives": ["Dribbling", "Shooting", "Passing"],
  "materials_needed": ["Basketballs", "Cones", "Whistle"],
  "safety_considerations": ["Proper warm-up", "Safe spacing"],
  "assessment_methods": ["Skill demonstration", "Peer observation"],
  "template_type": "standard",
  "difficulty_level": "intermediate",
  "equipment_required": ["Basketballs", "Cones"],
  "space_requirements": "Gymnasium",
  "weather_dependent": false,
  "is_public": true
}
```

#### Get Lesson Plan Templates
```http
GET /lesson-plan-builder/templates?subject=PE&grade_level=6-8&limit=20&offset=0
Authorization: Bearer <your_jwt_token>
```

#### Update Lesson Plan Template
```http
PUT /lesson-plan-builder/templates/{template_id}
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Updated Basketball Fundamentals",
  "description": "Enhanced basketball skills lesson"
}
```

#### Delete Lesson Plan Template
```http
DELETE /lesson-plan-builder/templates/{template_id}
Authorization: Bearer <your_jwt_token>
```

#### Generate AI Lesson Plan
```http
POST /lesson-plan-builder/ai-generate
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "subject": "PE",
  "grade_level": "6-8",
  "duration_minutes": 45,
  "focus_area": "Cardiovascular Fitness",
  "equipment_available": ["Cones", "Stopwatch", "Music"],
  "space_type": "Gymnasium",
  "weather_conditions": "Indoor"
}
```

### Assessment Tools

#### Create Assessment Template
```http
POST /assessment-tools/templates
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Basketball Skills Assessment",
  "description": "Comprehensive basketball skills evaluation",
  "subject": "PE",
  "grade_level": "6-8",
  "assessment_type": "summative",
  "duration_minutes": 30,
  "total_points": 100,
  "instructions": "Complete all skill stations and demonstrate proper technique",
  "materials_needed": ["Basketballs", "Cones", "Stopwatch"],
  "safety_considerations": ["Proper warm-up", "Safe spacing"],
  "difficulty_level": "intermediate",
  "equipment_required": ["Basketballs", "Cones"],
  "space_requirements": "Gymnasium",
  "weather_dependent": false,
  "is_public": true
}
```

#### Get Assessment Templates
```http
GET /assessment-tools/templates?subject=PE&assessment_type=summative&limit=20&offset=0
Authorization: Bearer <your_jwt_token>
```

#### Generate Assessment Rubric
```http
POST /assessment-tools/generate-rubric
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "template_id": "template_uuid",
  "criteria": [
    {
      "criterion_name": "Skill Execution",
      "criterion_description": "Proper technique and form",
      "max_points": 40,
      "weight_percentage": 40.0
    }
  ]
}
```

#### Align with Standards
```http
POST /assessment-tools/align-standards
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "template_id": "template_uuid",
  "standards": ["SHAPE_AMERICA_GRADE_6", "STATE_STANDARD_PE_1"]
}
```

### Resource Management

#### Upload Resource
```http
POST /resource-management/resources
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data

{
  "title": "Basketball Rules Guide",
  "description": "Complete guide to basketball rules for students",
  "resource_type": "document",
  "subject": "PE",
  "grade_level": "6-8",
  "tags": ["basketball", "rules", "sports"],
  "keywords": ["basketball", "rules", "regulations"],
  "difficulty_level": "intermediate",
  "language": "en",
  "license_type": "educational_use",
  "is_public": true,
  "file": <file_data>
}
```

#### Get Resources
```http
GET /resource-management/resources?subject=PE&tags=basketball&limit=20&offset=0
Authorization: Bearer <your_jwt_token>
```

#### Create Resource Collection
```http
POST /resource-management/collections
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "PE Fundamentals Collection",
  "description": "Essential resources for physical education fundamentals",
  "subject": "PE",
  "grade_level": "K-12",
  "collection_type": "curriculum",
  "is_public": true,
  "resource_ids": ["resource_uuid_1", "resource_uuid_2"]
}
```

#### Share Resource
```http
POST /resource-management/resources/{resource_id}/share
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "share_type": "public",
  "share_message": "Check out this great basketball resource!",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### Teacher Dashboard

#### Get Dashboard Layout
```http
GET /teacher-dashboard/layouts/default
Authorization: Bearer <your_jwt_token>
```

#### Create Dashboard Layout
```http
POST /teacher-dashboard/layouts
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "layout_name": "My Custom Layout",
  "layout_description": "Personalized dashboard layout",
  "is_default": true,
  "widget_instances": [
    {
      "widget_id": "widget_uuid",
      "position_x": 0,
      "position_y": 0,
      "width": 4,
      "height": 3,
      "widget_config": {}
    }
  ]
}
```

#### Get Dashboard Analytics
```http
GET /teacher-dashboard/analytics?days=30
Authorization: Bearer <your_jwt_token>
```

#### Get Dashboard Summary
```http
GET /teacher-dashboard/summary
Authorization: Bearer <your_jwt_token>
```

#### Log Activity
```http
POST /teacher-dashboard/activity-log
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "activity_type": "lesson_plan_created",
  "activity_description": "Created new basketball lesson plan",
  "resource_type": "lesson_plan",
  "resource_id": "lesson_plan_uuid",
  "resource_title": "Basketball Fundamentals",
  "metadata": {
    "subject": "PE",
    "grade_level": "6-8"
  }
}
```

### AI Assistant Integration

#### Create AI Assistant Config
```http
POST /ai-assistant/configs
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "config_name": "Lesson Plan Assistant",
  "config_description": "AI assistant for creating lesson plans",
  "assistant_type": "lesson_planning",
  "is_active": true,
  "config_data": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "system_prompt": "You are an expert PE teacher assistant specializing in creating engaging lesson plans."
  }
}
```

#### Start AI Conversation
```http
POST /ai-assistant/conversations
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "config_id": "config_uuid",
  "conversation_title": "Lesson Plan Help",
  "conversation_type": "lesson_planning",
  "metadata": {
    "subject": "PE",
    "grade_level": "6-8"
  }
}
```

#### Send Chat Message
```http
POST /ai-assistant/chat
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "message": "Help me create a basketball lesson plan for 6th graders",
  "conversation_id": "conversation_uuid",
  "conversation_type": "lesson_planning"
}
```

#### Get AI Templates
```http
GET /ai-assistant/templates?template_type=lesson_planning
Authorization: Bearer <your_jwt_token>
```

#### Use AI Template
```http
POST /ai-assistant/templates/{template_id}/use
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "variables": {
    "subject": "PE",
    "grade_level": "6-8",
    "duration_minutes": 45,
    "focus_area": "Basketball Skills"
  }
}
```

#### Submit AI Feedback
```http
POST /ai-assistant/feedback
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "conversation_id": "conversation_uuid",
  "message_id": "message_uuid",
  "feedback_type": "rating",
  "feedback_value": 5,
  "feedback_text": "Very helpful response!",
  "is_helpful": true
}
```

### Beta Testing

#### Enroll in Beta Program
```http
POST /beta-testing/enroll
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "program_id": "program_uuid",
  "testing_phase": "phase_1",
  "assigned_features": ["lesson_plan_builder", "ai_assistant"],
  "testing_goals": ["Test lesson plan creation", "Evaluate AI responses"],
  "contact_preferences": {
    "email": true,
    "phone": false
  },
  "consent_given": true
}
```

#### Submit Beta Feedback
```http
POST /beta-testing/feedback
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "participant_id": "participant_uuid",
  "feedback_type": "feature_feedback",
  "feature_name": "lesson_plan_builder",
  "feedback_title": "Great lesson plan builder!",
  "feedback_description": "The lesson plan builder is intuitive and easy to use.",
  "severity_level": "low",
  "priority_level": "medium",
  "user_impact": "moderate"
}
```

#### Get Beta Surveys
```http
GET /beta-testing/surveys?participant_id=participant_uuid
Authorization: Bearer <your_jwt_token>
```

#### Submit Survey Response
```http
POST /beta-testing/survey-responses
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "participant_id": "participant_uuid",
  "survey_id": "survey_uuid",
  "response_data": {
    "question_1": "Very satisfied",
    "question_2": "Easy to use",
    "question_3": "Would recommend"
  },
  "completion_percentage": 100.0,
  "time_spent_minutes": 5,
  "is_completed": true
}
```

#### Track Feature Usage
```http
POST /beta-testing/usage-analytics
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "participant_id": "participant_uuid",
  "feature_name": "lesson_plan_builder",
  "session_count": 1,
  "time_minutes": 15,
  "interactions": 5,
  "errors": 0,
  "satisfaction_score": 4.5,
  "performance_metrics": {
    "load_time_ms": 1200,
    "response_time_ms": 800
  }
}
```

## Webhooks

### Available Webhooks

- `lesson_plan.created` - When a lesson plan is created
- `assessment.created` - When an assessment is created
- `resource.uploaded` - When a resource is uploaded
- `ai_conversation.started` - When an AI conversation begins
- `beta_feedback.submitted` - When beta feedback is submitted

### Webhook Payload Example

```json
{
  "event": "lesson_plan.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": "lesson_plan_uuid",
    "title": "Basketball Fundamentals",
    "teacher_id": "teacher_uuid",
    "subject": "PE",
    "grade_level": "6-8"
  }
}
```

## SDKs and Libraries

### Python SDK
```bash
pip install pe-ai-assistant-sdk
```

```python
from pe_ai_assistant import PEAssistantClient

client = PEAssistantClient(api_key="your_api_key")

# Create a lesson plan
lesson_plan = client.lesson_plans.create({
    "title": "Basketball Fundamentals",
    "subject": "PE",
    "grade_level": "6-8",
    "duration_minutes": 45
})

# Generate AI lesson plan
ai_lesson = client.ai_assistant.generate_lesson_plan({
    "subject": "PE",
    "grade_level": "6-8",
    "focus_area": "Basketball Skills"
})
```

### JavaScript SDK
```bash
npm install pe-ai-assistant-sdk
```

```javascript
import { PEAssistantClient } from 'pe-ai-assistant-sdk';

const client = new PEAssistantClient('your_api_key');

// Create a lesson plan
const lessonPlan = await client.lessonPlans.create({
  title: 'Basketball Fundamentals',
  subject: 'PE',
  gradeLevel: '6-8',
  durationMinutes: 45
});

// Generate AI lesson plan
const aiLesson = await client.aiAssistant.generateLessonPlan({
  subject: 'PE',
  gradeLevel: '6-8',
  focusArea: 'Basketball Skills'
});
```

## Best Practices

### Authentication
- Store JWT tokens securely
- Implement token refresh logic
- Handle authentication errors gracefully

### Rate Limiting
- Implement exponential backoff for rate limit errors
- Cache responses when appropriate
- Monitor rate limit headers

### Error Handling
- Always check response status codes
- Parse error messages for user feedback
- Implement retry logic for transient errors

### Data Validation
- Validate input data before sending requests
- Handle validation errors appropriately
- Use appropriate data types and formats

### Performance
- Use pagination for large datasets
- Implement caching where appropriate
- Optimize request payloads

## Support

### Documentation
- API Reference: https://docs.pe-ai-assistant.com/api
- Guides: https://docs.pe-ai-assistant.com/guides
- Examples: https://docs.pe-ai-assistant.com/examples

### Community
- Discord: https://discord.gg/pe-ai-assistant
- GitHub: https://github.com/pe-ai-assistant
- Stack Overflow: Tag `pe-ai-assistant`

### Support Channels
- Email: support@pe-ai-assistant.com
- Chat: Available in the web application
- Phone: +1 (555) 123-4567 (Business hours)

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Teacher authentication system
- Lesson plan builder
- Assessment tools
- Resource management
- Teacher dashboard
- AI assistant integration
- Beta testing infrastructure

### Version 1.1.0 (2024-02-01)
- Enhanced AI assistant capabilities
- Improved resource sharing
- Additional assessment templates
- Performance optimizations

### Version 1.2.0 (2024-02-15)
- Advanced dashboard analytics
- Bulk operations support
- Enhanced error handling
- Additional webhook events
