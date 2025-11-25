# Saved Lesson Plans - Remaining Tasks

**Date Created:** November 20, 2025  
**Status:** Backend Implementation Complete, Frontend & Database Migration Pending

---

## Overview

This document tracks the remaining tasks needed to complete the saved lesson plan functionality. The backend logic is implemented, but database migration and frontend integration are still needed.

---

## ✅ Completed

1. **Database Model Updates** (`app/models/lesson_plan/models.py`)
   - ✅ Added `topic` field (String, indexed) for searchable topics
   - ✅ Added `lesson_name` field (String, indexed) for user-friendly names
   - ✅ Added `full_lesson_data` field (JSON) for complete lesson content
   - ✅ Added `is_saved_template` field (Boolean) to mark saved plans
   - ✅ Updated Pydantic models (Create, Update, Response)

2. **Service Methods** (`app/services/pe/ai_assistant_service.py`)
   - ✅ `_extract_topic_from_message()` - Extracts topic from user messages
   - ✅ `find_saved_lesson_plan()` - Finds saved lesson plans by topic/name
   - ✅ `save_lesson_plan()` - Saves new or updates existing lesson plans
   - ✅ Integrated saved lesson check before OpenAI API calls
   - ✅ Automatic saving of new lesson plans after generation

3. **AI Assistant Logic**
   - ✅ Checks for saved lesson plans BEFORE calling OpenAI (saves tokens/time)
   - ✅ Returns saved lesson immediately if found
   - ✅ Creates and saves new lesson plans if not found
   - ✅ Skips worksheet/rubric generation for saved lessons

4. **API Endpoints** (`app/api/v1/endpoints/ai_assistant.py`)
   - ✅ `GET /api/v1/ai-assistant/saved-lesson-plans` - List all saved lesson plans
   - ✅ `GET /api/v1/ai-assistant/saved-lesson-plans/{id}` - Get specific lesson plan
   - ✅ `PUT /api/v1/ai-assistant/saved-lesson-plans/{id}` - Update saved lesson plan

5. **System Prompt Updates** (`app/core/ai_system_prompts.py`)
   - ✅ Added instructions for Jasper to check for saved lesson plans first
   - ✅ Informs Jasper about save/retrieve/edit functionality

---

## 🔲 TODO: Database Migration

### Priority: HIGH

**Task:** Create database migration to add new columns to `pe_lesson_plans` table

**Required Changes:**
```sql
ALTER TABLE pe_lesson_plans
ADD COLUMN topic VARCHAR(200),
ADD COLUMN lesson_name VARCHAR(200),
ADD COLUMN full_lesson_data JSON,
ADD COLUMN is_saved_template BOOLEAN DEFAULT FALSE;

-- Add indexes for faster searches
CREATE INDEX idx_pe_lesson_plans_topic ON pe_lesson_plans(topic);
CREATE INDEX idx_pe_lesson_plans_lesson_name ON pe_lesson_plans(lesson_name);
CREATE INDEX idx_pe_lesson_plans_teacher_saved ON pe_lesson_plans(teacher_id, is_saved_template) WHERE is_saved_template = TRUE;
```

**Files to Create:**
- `alembic/versions/XXXX_add_saved_lesson_plan_fields.py` (or equivalent migration file)

**Notes:**
- Migration should be backward compatible (existing lesson plans will have `is_saved_template = FALSE`)
- Consider data migration for existing lesson plans if needed
- Test migration on development database first

---

## 🔲 TODO: Frontend Integration

### Priority: HIGH

### 1. **Display Saved Lesson Plans List**

**Location:** `static/js/dashboard.js` or new component

**Features Needed:**
- UI to view all saved lesson plans for the current teacher
- Filter/search by topic or name
- Display lesson plan title, topic, grade level, last updated date
- Click to load/view a specific saved lesson plan

**API Integration:**
- Call `GET /api/v1/ai-assistant/saved-lesson-plans` to fetch list
- Display results in a modal or sidebar panel

### 2. **Edit Saved Lesson Plans**

**Location:** `static/js/dashboard.js`

**Features Needed:**
- Ability to edit lesson plan content directly in the widget
- "Save Changes" button to update the saved lesson plan
- "Save As New" option to create a copy
- Confirmation dialog before overwriting existing saved lesson

**API Integration:**
- Call `PUT /api/v1/ai-assistant/saved-lesson-plans/{id}` to update
- Include full lesson data in the request body

### 3. **Widget UI Updates**

**Location:** `static/js/dashboard.js` - `formatWidgetData()` function

**Features Needed:**
- Add "Edit" button to lesson plan widgets (for saved lessons)
- Add "Save" button when editing
- Add "Save As New" button
- Visual indicator showing if a lesson plan is saved (e.g., "💾 Saved" badge)
- Display topic/lesson name in widget header

**Code Changes:**
- Update `formatWidgetData()` to add edit/save buttons for lesson-planning widgets
- Add event handlers for edit/save actions
- Update widget display to show saved status

### 4. **Chat Interface Updates**

**Location:** `static/js/dashboard.js` - `handleChatResponse()`

**Features Needed:**
- When Jasper finds a saved lesson, display a message like: "I found your saved lesson plan on [topic]"
- When a new lesson is created and saved, display: "I've saved this lesson plan as '[topic] lesson' for future use"
- Add UI hint/button to view all saved lesson plans

**Code Changes:**
- Update chat message display to show save status
- Add "View Saved Lessons" button/link in chat interface

### 5. **Settings/Management Panel**

**Location:** Settings modal or new "My Lesson Plans" section

**Features Needed:**
- List all saved lesson plans
- Delete saved lesson plans
- Rename lesson plans
- View/edit lesson plan details
- Export lesson plans (PDF, Word, etc.)

**API Integration:**
- `GET /api/v1/ai-assistant/saved-lesson-plans` - List all
- `DELETE /api/v1/ai-assistant/saved-lesson-plans/{id}` - Delete (needs to be created)
- `PUT /api/v1/ai-assistant/saved-lesson-plans/{id}` - Update

---

## 🔲 TODO: Additional API Endpoints

### Priority: MEDIUM

### 1. **Delete Saved Lesson Plan**

**Endpoint:** `DELETE /api/v1/ai-assistant/saved-lesson-plans/{lesson_plan_id}`

**Location:** `app/api/v1/endpoints/ai_assistant.py`

**Implementation:**
```python
@router.delete("/saved-lesson-plans/{lesson_plan_id}", response_model=Dict[str, Any])
async def delete_saved_lesson_plan(
    lesson_plan_id: int,
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Delete a saved lesson plan"""
    # Verify ownership, delete, return success
```

### 2. **Search Saved Lesson Plans**

**Endpoint:** `GET /api/v1/ai-assistant/saved-lesson-plans?search={query}`

**Enhancement:** Add search parameter to existing GET endpoint

**Features:**
- Search by topic, lesson name, or title
- Case-insensitive search
- Return matching results

---

## 🔲 TODO: Enhanced Features (Future)

### Priority: LOW

### 1. **Lesson Plan Versioning**
- Track versions of saved lesson plans
- Allow reverting to previous versions
- Show edit history

### 2. **Lesson Plan Sharing**
- Share saved lesson plans with other teachers
- Make lesson plans public/private
- Collaboration features

### 3. **Lesson Plan Templates**
- Convert saved lesson plans to reusable templates
- Apply templates to create new lesson plans quickly
- Template library/catalog

### 4. **Bulk Operations**
- Export multiple lesson plans
- Delete multiple lesson plans
- Duplicate lesson plans

### 5. **Advanced Search & Filtering**
- Filter by grade level, subject, date created
- Sort by various criteria (date, title, topic)
- Tag system for better organization

### 6. **Lesson Plan Analytics**
- Track usage of saved lesson plans
- Show which lessons are used most frequently
- Usage statistics and insights

---

## 🔲 TODO: Testing

### Priority: HIGH

### 1. **Backend Testing**
- Test `find_saved_lesson_plan()` with various topic formats
- Test `save_lesson_plan()` for new and existing lessons
- Test `_extract_topic_from_message()` with various message formats
- Test API endpoints (GET, PUT, DELETE)
- Test error handling (lesson not found, unauthorized access, etc.)

### 2. **Integration Testing**
- Test full flow: create → save → retrieve → edit → re-save
- Test with multiple teachers (ensure isolation)
- Test topic extraction accuracy
- Test saved lesson retrieval when requesting by different phrasings

### 3. **Frontend Testing**
- Test UI for viewing saved lesson plans
- Test edit functionality
- Test save/update operations
- Test error handling in UI

### 4. **Edge Cases**
- What happens if topic extraction fails?
- What happens if multiple lessons exist with same topic?
- What happens if lesson plan data is corrupted?
- What happens if database connection fails during save?

---

## 🔲 TODO: Documentation

### Priority: MEDIUM

### 1. **User Documentation**
- How to create and save lesson plans
- How to retrieve saved lesson plans
- How to edit and update saved lesson plans
- How to delete saved lesson plans
- Best practices for naming topics

### 2. **Developer Documentation**
- API endpoint documentation
- Database schema updates
- Service method documentation
- Code examples for frontend integration

---

## 🔲 TODO: Error Handling & Edge Cases

### Priority: MEDIUM

### 1. **Topic Extraction Improvements**
- Handle edge cases in topic extraction (e.g., "create a lesson plan on basketball fundamentals")
- Support multiple topic formats
- Handle special characters in topics
- Normalize topic names (e.g., "CPR" vs "cpr" vs "C.P.R.")

### 2. **Duplicate Handling**
- What if teacher creates "CPR lesson" and "CPR" - should they be merged?
- Handle case-insensitive topic matching
- Suggest similar topics if exact match not found

### 3. **Data Validation**
- Validate lesson plan data before saving
- Ensure required fields are present
- Handle malformed JSON in `full_lesson_data`
- Validate topic/lesson_name length and format

---

## Implementation Notes

### Current Behavior

1. **When teacher requests lesson plan:**
   - System extracts topic from message (e.g., "CPR" from "create a lesson plan on CPR")
   - Checks database for existing lesson plan with that topic
   - If found: Returns saved lesson immediately (skips OpenAI call)
   - If not found: Creates new lesson plan via OpenAI, then saves it automatically

2. **Saving:**
   - Lesson plans are automatically saved when created
   - Topic is extracted from the user's message
   - Lesson name is auto-generated as "{topic} lesson"
   - Full lesson data (including worksheets/rubrics) is stored in `full_lesson_data` JSON field

3. **Retrieval:**
   - Teacher can request lesson by topic name (e.g., "show me the CPR lesson")
   - System searches by topic, lesson_name, or title
   - Returns complete lesson plan data including all sections

### Database Schema

```sql
-- New columns in pe_lesson_plans table
topic VARCHAR(200) NULL INDEX
lesson_name VARCHAR(200) NULL INDEX  
full_lesson_data JSON NULL
is_saved_template BOOLEAN DEFAULT FALSE
```

### API Endpoints Summary

- `GET /api/v1/ai-assistant/saved-lesson-plans` - List all saved lesson plans
- `GET /api/v1/ai-assistant/saved-lesson-plans/{id}` - Get specific lesson plan
- `PUT /api/v1/ai-assistant/saved-lesson-plans/{id}` - Update saved lesson plan
- `DELETE /api/v1/ai-assistant/saved-lesson-plans/{id}` - Delete (TODO)

---

## Questions to Resolve

1. **Should we allow multiple lesson plans with the same topic?**
   - Current implementation: Updates existing if topic matches
   - Alternative: Allow multiple, use most recent or let user choose

2. **How should we handle topic extraction failures?**
   - Current: Falls back to creating new lesson without topic
   - Alternative: Ask user to clarify topic name

3. **Should saved lesson plans be editable directly in the widget?**
   - Current: Widget displays lesson plan, but editing not implemented
   - Need: Edit UI in widget or separate edit page

4. **Should we support lesson plan categories/tags?**
   - Current: Only topic-based organization
   - Future: Add tags, categories, folders

---

## Estimated Time

- **Database Migration:** 1-2 hours
- **Frontend Integration (Basic):** 4-6 hours
- **Frontend Integration (Full with Edit):** 8-12 hours
- **Testing:** 4-6 hours
- **Documentation:** 2-3 hours

**Total Estimated Time:** 19-29 hours

---

## Priority Order

1. **Database Migration** (Required for system to work)
2. **Basic Frontend - View Saved Lessons** (Core functionality)
3. **Frontend - Edit & Save** (Essential feature)
4. **Testing** (Ensure reliability)
5. **Delete Endpoint** (Complete CRUD operations)
6. **Enhanced Features** (Nice to have)

---

**Last Updated:** November 20, 2025

