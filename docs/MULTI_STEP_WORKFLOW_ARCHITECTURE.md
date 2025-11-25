# Multi-Step Workflow Architecture for All Jasper Conversations

## Overview

The meal plan workflow pattern (ask question → collect answer → generate response) should be **generalized** to support **all multi-step conversations** across all subjects Jasper handles.

---

## 🎯 Core Pattern

### Generic Multi-Step Workflow

```
1. User Request → Backend detects missing required info
2. Backend returns early (NO API CALL) with question
3. User provides answer
4. Backend combines request + answer
5. API Call → Generate final response
```

### Key Principles

1. **Early Return Pattern**: When required info is missing, return immediately with a question (no API call)
2. **Metadata Storage**: Store pending request in assistant message metadata
3. **Answer Detection**: Detect when user provides required information
4. **Message Combination**: Combine original request + collected answers
5. **Proceed Reminder**: Inject explicit instructions to prevent acknowledgment

---

## 📋 Multi-Step Workflows by Subject

### 1. Meal Plans ✅ (Already Implemented)

**Required Information:**
- Original meal plan request
- Allergy/dietary restrictions

**Workflow:**
```
Request → Allergy question → Answer → Meal plan
```

**Status:** ✅ Fully implemented

---

### 2. Workout Plans 🔄 (Needs Implementation)

**Required Information:**
- Original workout request
- Fitness level (beginner/intermediate/advanced)
- Available equipment
- Injury/limitation restrictions
- Training goals (strength/endurance/hybrid)

**Potential Workflow:**
```
Request → Fitness level question → Answer
       → Equipment question → Answer
       → Injury/limitation question → Answer
       → Workout plan
```

**Or Single Question:**
```
Request → "What's your fitness level, available equipment, and any injuries?" → Answer → Workout plan
```

**Implementation Needed:**
- `detect_workout_request()` - Check if workout plan requested
- `check_workout_info()` - Verify fitness level, equipment, injuries exist
- `store_pending_workout_request()` - Store in metadata
- `detect_workout_answer()` - Detect fitness level/equipment/injury answers
- `combine_workout_request()` - Merge request + collected info

---

### 3. Lesson Plans 🔄 (Needs Implementation)

**Required Information:**
- Original lesson plan request
- Grade level
- Subject/topic
- Standards alignment
- Duration (single lesson vs. unit)
- Student needs/adaptations

**Potential Workflow:**
```
Request → Grade level question → Answer
       → Subject/topic question → Answer
       → Standards question → Answer
       → Lesson plan
```

**Or Single Question:**
```
Request → "What grade level, subject, and standards?" → Answer → Lesson plan
```

**Implementation Needed:**
- `detect_lesson_plan_request()` - Check if lesson plan requested
- `check_lesson_plan_info()` - Verify grade, subject, standards exist
- `store_pending_lesson_plan_request()` - Store in metadata
- `detect_lesson_plan_answer()` - Detect grade/subject/standards answers
- `combine_lesson_plan_request()` - Merge request + collected info

---

### 4. Skill Assessments 🔄 (Needs Implementation)

**Required Information:**
- Original assessment request
- Student name/ID
- Skill being assessed
- Current skill level
- Assessment type (formative/summative)

**Potential Workflow:**
```
Request → Student question → Answer
       → Skill question → Answer
       → Assessment
```

**Implementation Needed:**
- `detect_assessment_request()` - Check if assessment requested
- `check_assessment_info()` - Verify student, skill, level exist
- `store_pending_assessment_request()` - Store in metadata
- `detect_assessment_answer()` - Detect student/skill/level answers
- `combine_assessment_request()` - Merge request + collected info

---

### 5. Student Profiles 🔄 (Needs Implementation)

**Required Information:**
- Original profile creation request
- Student name
- Grade level
- Health conditions
- Fitness goals
- Parent contact info

**Potential Workflow:**
```
Request → Student name question → Answer
       → Grade level question → Answer
       → Health conditions question → Answer
       → Profile created
```

---

## 🏗️ Generic Architecture

### Core Service Methods (To Be Created)

```python
class MultiStepWorkflowService:
    """Generic multi-step workflow handler for all Jasper conversations."""
    
    def detect_multi_step_request(self, message: str, workflow_type: str) -> bool:
        """Detect if message requires multi-step workflow."""
        pass
    
    def check_required_info(self, conversation_id: str, workflow_type: str) -> Dict[str, Any]:
        """Check if all required information is collected."""
        return {
            "has_all_info": bool,
            "missing_fields": List[str],
            "collected_info": Dict[str, Any]
        }
    
    def store_pending_request(
        self, 
        conversation_id: str, 
        workflow_type: str,
        original_request: str,
        required_fields: List[str]
    ) -> AIAssistantMessage:
        """Store pending request with metadata."""
        pass
    
    def detect_answer(
        self, 
        message: str, 
        workflow_type: str,
        expected_fields: List[str]
    ) -> Dict[str, Any]:
        """Detect if message answers required questions."""
        return {
            "is_answer": bool,
            "detected_fields": Dict[str, str],
            "confidence": float
        }
    
    def combine_request_with_answers(
        self,
        original_request: str,
        collected_answers: Dict[str, str]
    ) -> str:
        """Combine original request with collected answers."""
        pass
    
    def build_proceed_reminder(
        self,
        workflow_type: str,
        combined_request: str
    ) -> str:
        """Build proceed reminder message for workflow type."""
        pass
```

---

## 📐 Workflow Configuration

### Workflow Definitions (JSON/YAML)

```yaml
workflows:
  meal_plan:
    required_fields:
      - allergies
    questions:
      allergies: "Before I create your meal plan, do you have any food allergies, dietary restrictions, or foods you'd like me to avoid?"
    detection_keywords:
      allergies:
        - "allerg"
        - "dietary restriction"
        - "avoid"
        - "tree nuts"
        - "peanuts"
    proceed_reminder: "CREATE THE MEAL PLAN NOW. DO NOT acknowledge the allergy."
    
  workout_plan:
    required_fields:
      - fitness_level
      - equipment
      - injuries
    questions:
      fitness_level: "What's your current fitness level? (beginner/intermediate/advanced)"
      equipment: "What equipment do you have available?"
      injuries: "Do you have any injuries or physical limitations I should know about?"
    detection_keywords:
      fitness_level:
        - "beginner"
        - "intermediate"
        - "advanced"
        - "fitness level"
      equipment:
        - "equipment"
        - "dumbbells"
        - "barbell"
        - "no equipment"
      injuries:
        - "injury"
        - "limitation"
        - "can't"
        - "avoid"
    proceed_reminder: "CREATE THE WORKOUT PLAN NOW. DO NOT acknowledge the information provided."
    
  lesson_plan:
    required_fields:
      - grade_level
      - subject
      - standards
    questions:
      grade_level: "What grade level is this lesson for?"
      subject: "What subject/topic is this lesson about?"
      standards: "Which standards should this lesson align with?"
    detection_keywords:
      grade_level:
        - "grade"
        - "level"
        - "1st"
        - "2nd"
        - "3rd"
      subject:
        - "subject"
        - "topic"
        - "math"
        - "science"
      standards:
        - "standards"
        - "common core"
        - "ngss"
    proceed_reminder: "CREATE THE LESSON PLAN NOW. DO NOT acknowledge the information provided."
```

---

## 🔄 Migration Strategy

### Phase 1: Extract Generic Functions (Current Implementation)

1. **Extract from meal plan code:**
   - `detect_required_info()` → Generic
   - `store_pending_request()` → Generic
   - `detect_answer()` → Generic (with workflow-specific keywords)
   - `combine_request()` → Generic
   - `build_proceed_reminder()` → Generic

2. **Create workflow registry:**
   ```python
   WORKFLOW_REGISTRY = {
       "meal_plan": MealPlanWorkflow(),
       "workout_plan": WorkoutPlanWorkflow(),
       "lesson_plan": LessonPlanWorkflow(),
       "assessment": AssessmentWorkflow(),
   }
   ```

### Phase 2: Implement New Workflows

1. **Workout Plans** - Use meal plan pattern
2. **Lesson Plans** - Use meal plan pattern
3. **Assessments** - Use meal plan pattern

### Phase 3: Unified Handler

```python
def send_chat_message(self, teacher_id: str, chat_request: AIAssistantChatRequest):
    # Detect workflow type
    workflow_type = self.detect_workflow_type(chat_request.message)
    
    # Get workflow handler
    workflow = WORKFLOW_REGISTRY.get(workflow_type)
    
    if workflow:
        # Use workflow-specific handler
        return workflow.handle_request(chat_request, conversation)
    else:
        # Handle general conversation
        return self.handle_general_conversation(chat_request, conversation)
```

---

## 📝 Implementation Checklist

### For Each New Workflow:

- [ ] Define required fields
- [ ] Create detection keywords/phrases
- [ ] Write question templates
- [ ] Implement answer detection
- [ ] Create message combination logic
- [ ] Build proceed reminder
- [ ] Add system prompt enhancements
- [ ] Test early return (no API call)
- [ ] Test answer detection
- [ ] Test message combination
- [ ] Test final API call
- [ ] Add logging
- [ ] Add error handling

---

## 🎯 Benefits of Generic Architecture

1. **Consistency**: All multi-step workflows follow same pattern
2. **Maintainability**: Single codebase for all workflows
3. **Extensibility**: Easy to add new workflows
4. **Testing**: Test pattern once, works for all
5. **Documentation**: One pattern to document
6. **Cost Efficiency**: Early returns save API calls for all workflows

---

## 📊 Current Status

| Workflow | Status | Implementation |
|----------|--------|----------------|
| **Meal Plans** | ✅ Complete | Fully implemented with all edge cases |
| **Workout Plans** | 🔄 Needed | Pattern exists, needs workflow-specific logic |
| **Lesson Plans** | 🔄 Needed | Pattern exists, needs workflow-specific logic |
| **Assessments** | 🔄 Needed | Pattern exists, needs workflow-specific logic |
| **Student Profiles** | 🔄 Needed | Pattern exists, needs workflow-specific logic |

---

## 🚀 Next Steps

1. **Test meal plan workflow** in Docker (validate pattern)
2. **Extract generic functions** from meal plan code
3. **Create workflow registry** and configuration system
4. **Implement workout plan workflow** (first new workflow)
5. **Implement lesson plan workflow** (second new workflow)
6. **Document each workflow** with specific requirements

---

## 💡 Key Takeaway

The **meal plan workflow is the template** for all multi-step conversations. Once we validate it works correctly, we can:

1. Extract the pattern into generic functions
2. Apply it to workout plans, lesson plans, assessments, etc.
3. Create a unified multi-step workflow system
4. Maintain consistency across all Jasper conversations

**The current meal plan implementation is the foundation for all future multi-step workflows.**

