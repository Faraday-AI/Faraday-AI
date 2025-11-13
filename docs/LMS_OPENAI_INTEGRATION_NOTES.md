# LMS + OpenAI Integration Notes

**Date:** November 13, 2025  
**Status:** Planning Phase

---

## Overview

**All LMS systems can integrate with OpenAI API** for AI-powered features. We will leverage the existing OpenAI API key and service implementation when integrating all LMS systems. Native support varies by platform:

- **Canvas & Moodle**: Direct OpenAI API integration support
- **PowerSchool & Schoology**: Native OpenAI integration via Microsoft Azure OpenAI Service (PowerBuddy AI assistant)
- **Google Classroom**: API-based integration possible (Google also has native Gemini AI)
- **Blackboard**: API-based integration possible

---

## Existing OpenAI Infrastructure

### Current Implementation

**Service:** `app/services/ai/openai_service.py`
- `OpenAIService` class with `generate_text()` method
- Already configured with `OPENAI_API_KEY` environment variable
- Cached singleton instance via `get_openai_service()`
- Supports structured JSON output
- Error handling and retry logic

**Environment Variable:**
- `OPENAI_API_KEY` - Already set in `run.sh` and `docker-compose.yml`

---

## OpenAI Integration by LMS System

### ✅ Canvas - Direct OpenAI Integration
- Native support for OpenAI API integration
- Use OpenAI for assignment feedback, content suggestions, grading assistance

### ✅ Moodle - Direct OpenAI Integration
- Native support for OpenAI API integration
- Use OpenAI for quiz generation, forum enhancement, rubric creation

### ✅ PowerSchool - Native OpenAI Integration
- **PowerBuddy AI Assistant** - Already uses Microsoft Azure OpenAI Service
- Can integrate our OpenAI API for additional features
- Personalized learning pathways and AI-generated assessments
- Use OpenAI for: student progress analysis, assignment feedback, content generation

### ✅ Schoology - Native OpenAI Integration
- **PowerBuddy AI Assistant** - Available in Schoology Learning (part of PowerSchool ecosystem)
- Can integrate our OpenAI API for additional features
- Lesson plan generation, quiz creation, personalized learning activities
- Use OpenAI for: automated content creation, student engagement analysis

### ✅ Google Classroom - API-Based Integration
- Google has native Gemini AI tools
- Can integrate OpenAI API via Google Classroom API
- Third-party integrations possible (e.g., MagicSchool AI)
- Use OpenAI for: assignment feedback, automated responses, content suggestions

### ✅ Blackboard - API-Based Integration
- Blackboard Learn API supports external integrations
- Can integrate OpenAI API for AI-powered features
- Use OpenAI for: course content generation, student analytics, automated grading assistance

---

## Canvas + OpenAI Integration

### Use Cases

1. **Assignment Feedback Generation**
   - Generate AI-powered feedback for student submissions
   - Integrate with Canvas assignment grading workflow
   - Provide suggestions for improvement

2. **Content Suggestions**
   - Suggest course content based on student performance
   - Recommend resources and activities
   - Generate discussion prompts

3. **Automated Grading Assistance**
   - Assist with rubric-based grading
   - Generate grade justifications
   - Identify common errors and patterns

4. **Student Progress Analysis**
   - Analyze student performance trends
   - Generate personalized learning recommendations
   - Identify at-risk students

### Implementation Approach

```python
# In canvas_service.py
from app.services.ai.openai_service import get_openai_service

class CanvasService(BaseLMSService):
    def __init__(self, ...):
        super().__init__(...)
        self.openai_service = get_openai_service()
    
    async def generate_assignment_feedback(self, submission_id: str, rubric: dict):
        """Generate AI-powered feedback for a Canvas assignment submission."""
        # Fetch submission from Canvas
        submission = await self.get_submission(submission_id)
        
        # Generate feedback using OpenAI
        prompt = f"Generate feedback for this submission based on the rubric: {rubric}"
        result = await self.openai_service.generate_text(prompt)
        
        # Post feedback back to Canvas
        await self.post_feedback(submission_id, result['content'])
        
        return result
```

---

## Moodle + OpenAI Integration

### Use Cases

1. **Quiz Question Generation**
   - Generate quiz questions based on course content
   - Create multiple choice, short answer, and essay questions
   - Adapt difficulty based on student level

2. **Forum Discussion Enhancement**
   - Generate discussion prompts
   - Summarize forum discussions
   - Identify key themes and insights

3. **Assignment Rubric Generation**
   - Create detailed rubrics for assignments
   - Generate grading criteria
   - Suggest assessment methods

4. **Learning Path Recommendations**
   - Recommend next steps for students
   - Generate personalized learning paths
   - Suggest resources based on progress

### Implementation Approach

```python
# In moodle_service.py
from app.services.ai.openai_service import get_openai_service

class MoodleService(BaseLMSService):
    def __init__(self, ...):
        super().__init__(...)
        self.openai_service = get_openai_service()
    
    async def generate_quiz_questions(self, course_id: str, topic: str, count: int = 5):
        """Generate quiz questions using OpenAI."""
        prompt = f"Generate {count} quiz questions about {topic} for a Moodle course."
        result = await self.openai_service.generate_text(
            prompt,
            structured_output=True  # Get JSON format for questions
        )
        
        # Parse and create questions in Moodle
        questions = json.loads(result['content'])
        await self.create_quiz_questions(course_id, questions)
        
        return result
```

---

## PowerSchool + OpenAI Integration

### Use Cases

1. **Personalized Learning Pathways**
   - Generate AI-powered learning paths based on student performance
   - Create adaptive assessments
   - Recommend next steps for students

2. **Assignment Feedback Generation**
   - Generate AI-powered feedback for student submissions
   - Provide personalized improvement suggestions
   - Analyze student work patterns

3. **Content Generation**
   - Generate course content and materials
   - Create assessment items
   - Develop personalized learning activities

### Implementation Approach

```python
# In powerschool_service.py
from app.services.ai.openai_service import get_openai_service

class PowerSchoolService(BaseLMSService):
    def __init__(self, ...):
        super().__init__(...)
        self.openai_service = get_openai_service()
    
    async def generate_personalized_pathway(self, student_id: str, performance_data: dict):
        """Generate personalized learning pathway using OpenAI."""
        prompt = f"Create a personalized learning pathway for a student with this performance: {performance_data}"
        result = await self.openai_service.generate_text(prompt, structured_output=True)
        
        # Create pathway in PowerSchool
        pathway = json.loads(result['content'])
        await self.create_learning_pathway(student_id, pathway)
        
        return result
```

**Note:** PowerSchool already has PowerBuddy AI (Azure OpenAI), but we can add direct OpenAI integration for additional features.

---

## Schoology + OpenAI Integration

### Use Cases

1. **Lesson Plan Generation**
   - Generate complete lesson plans with objectives, activities, and assessments
   - Create lesson variations for different student levels
   - Suggest engaging activities and resources

2. **Quiz Creation**
   - Generate quiz questions based on course content
   - Create multiple question types (multiple choice, short answer, essay)
   - Adapt difficulty levels

3. **Personalized Learning Activities**
   - Generate activities tailored to individual student needs
   - Create differentiated instruction materials
   - Develop engagement strategies

### Implementation Approach

```python
# In schoology_service.py
from app.services.ai.openai_service import get_openai_service

class SchoologyService(BaseLMSService):
    def __init__(self, ...):
        super().__init__(...)
        self.openai_service = get_openai_service()
    
    async def generate_lesson_plan(self, course_id: str, topic: str, duration: int = 60):
        """Generate a lesson plan using OpenAI."""
        prompt = f"Create a {duration}-minute lesson plan about {topic} for a Schoology course."
        result = await self.openai_service.generate_text(prompt, structured_output=True)
        
        # Create lesson plan in Schoology
        lesson_plan = json.loads(result['content'])
        await self.create_lesson_plan(course_id, lesson_plan)
        
        return result
```

**Note:** Schoology has PowerBuddy AI (Azure OpenAI) available, but we can add direct OpenAI integration for additional features.

---

## Google Classroom + OpenAI Integration

### Use Cases

1. **Assignment Feedback**
   - Generate AI-powered feedback for student submissions
   - Provide detailed improvement suggestions
   - Analyze student work quality

2. **Automated Responses**
   - Generate responses to student questions
   - Create announcement content
   - Provide automated support

3. **Content Suggestions**
   - Suggest course content based on student needs
   - Recommend resources and activities
   - Generate discussion prompts

### Implementation Approach

```python
# In google_classroom_service.py
from app.services.ai.openai_service import get_openai_service

class GoogleClassroomService(BaseLMSService):
    def __init__(self, ...):
        super().__init__(...)
        self.openai_service = get_openai_service()
    
    async def generate_assignment_feedback(self, course_id: str, submission_id: str):
        """Generate AI-powered feedback for a Google Classroom assignment."""
        # Fetch submission from Google Classroom
        submission = await self.get_submission(course_id, submission_id)
        
        # Generate feedback using OpenAI
        prompt = f"Generate constructive feedback for this submission: {submission['content']}"
        result = await self.openai_service.generate_text(prompt)
        
        # Post feedback back to Google Classroom
        await self.post_feedback(course_id, submission_id, result['content'])
        
        return result
```

**Note:** Google Classroom has native Gemini AI, but OpenAI can be integrated via API for additional features.

---

## Blackboard + OpenAI Integration

### Use Cases

1. **Course Content Generation**
   - Generate course materials and content
   - Create learning modules
   - Develop instructional resources

2. **Student Analytics**
   - Analyze student performance data
   - Generate insights and recommendations
   - Identify at-risk students

3. **Automated Grading Assistance**
   - Assist with rubric-based grading
   - Generate grade justifications
   - Provide grading suggestions

### Implementation Approach

```python
# In blackboard_service.py
from app.services.ai.openai_service import get_openai_service

class BlackboardService(BaseLMSService):
    def __init__(self, ...):
        super().__init__(...)
        self.openai_service = get_openai_service()
    
    async def generate_course_content(self, course_id: str, topic: str):
        """Generate course content using OpenAI."""
        prompt = f"Create comprehensive course content about {topic} for a Blackboard course."
        result = await self.openai_service.generate_text(prompt, structured_output=True)
        
        # Create content in Blackboard
        content = json.loads(result['content'])
        await self.create_course_content(course_id, content)
        
        return result
```

---

## Shared OpenAI Service Usage

### Best Practices

1. **Reuse Existing Service**
   - Always use `get_openai_service()` to get the cached singleton
   - Don't create new `OpenAIService` instances
   - Leverage existing error handling and retry logic

2. **Rate Limiting**
   - Be aware of OpenAI API rate limits
   - Implement request queuing if needed
   - Cache responses when appropriate

3. **Error Handling**
   - Handle OpenAI API errors gracefully
   - Fall back to non-AI features if OpenAI is unavailable
   - Log errors for monitoring

4. **Cost Management**
   - Monitor OpenAI API usage
   - Use appropriate models (GPT-3.5-turbo for simple tasks, GPT-4 for complex)
   - Implement usage limits per user/tenant

---

## Configuration

### Environment Variables (Already Set)

```bash
OPENAI_API_KEY=sk-proj-...  # Already configured
```

### Service Initialization

```python
# In LMS service constructors
from app.services.ai.openai_service import get_openai_service

class CanvasService(BaseLMSService):
    def __init__(self, connection: LMSConnection):
        super().__init__(connection)
        # Reuse existing OpenAI service
        self.openai = get_openai_service()
```

---

## Testing Strategy

### Unit Tests
- [ ] Test Canvas service with mocked OpenAI service
- [ ] Test Moodle service with mocked OpenAI service
- [ ] Test PowerSchool service with mocked OpenAI service
- [ ] Test Schoology service with mocked OpenAI service
- [ ] Test Google Classroom service with mocked OpenAI service
- [ ] Test Blackboard service with mocked OpenAI service
- [ ] Verify OpenAI service is reused (singleton pattern)

### Integration Tests
- [ ] Test Canvas + OpenAI integration end-to-end
- [ ] Test Moodle + OpenAI integration end-to-end
- [ ] Test PowerSchool + OpenAI integration end-to-end
- [ ] Test Schoology + OpenAI integration end-to-end
- [ ] Test Google Classroom + OpenAI integration end-to-end
- [ ] Test Blackboard + OpenAI integration end-to-end
- [ ] Test error handling when OpenAI is unavailable
- [ ] Test rate limiting and retry logic

### Mock Strategy
- Mock OpenAI API calls in tests
- Use real OpenAI service only in integration tests with valid API key
- Test fallback behavior when OpenAI fails

---

## API Endpoints

### Canvas AI Features
- `POST /api/v1/integration/lms/canvas/assignments/{assignment_id}/generate-feedback`
- `POST /api/v1/integration/lms/canvas/courses/{course_id}/suggest-content`
- `POST /api/v1/integration/lms/canvas/students/{student_id}/analyze-progress`

### Moodle AI Features
- `POST /api/v1/integration/lms/moodle/courses/{course_id}/generate-quiz`
- `POST /api/v1/integration/lms/moodle/forums/{forum_id}/summarize`
- `POST /api/v1/integration/lms/moodle/assignments/{assignment_id}/generate-rubric`

---

## Next Steps

1. ✅ Document OpenAI integration requirements for all LMS systems
2. Implement Canvas service with OpenAI integration
3. Implement Moodle service with OpenAI integration
4. Implement PowerSchool service with OpenAI integration
5. Implement Schoology service with OpenAI integration
6. Implement Google Classroom service with OpenAI integration
7. Implement Blackboard service with OpenAI integration
8. Create API endpoints for AI features across all systems
9. Write integration tests for all LMS + OpenAI integrations
10. Document usage in user guides

---

**Status:** Ready to implement during Canvas and Moodle integration phases ✅

