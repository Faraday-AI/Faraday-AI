# Jasper Meal Plan Workflow - Complete End-to-End Flow

## Overview

This document describes the complete end-to-end flow for Jasper's meal plan generation with allergy handling, showing how the frontend and backend interact using a persistent `conversation_id`.

## Flow Diagram

```mermaid
flowchart TD
    %% User sends initial request
    A[User sends: "I need a 7-day meal plan..."] --> B[Frontend attaches conversation_id (persistent)]
    
    %% Backend checks for pending allergy info
    B --> C[Backend checks last messages in conversation_id for pending_meal_plan_request]
    C -->|No allergy info| D[Backend returns hardcoded message: "Do you have any food allergies?"]
    D --> E[Message saved as assistant message with pending_meal_plan_request metadata]
    E --> F[User sees allergy question immediately (<100ms)]
    
    %% User answers allergy question
    F --> G[User sends allergy answer: "The student is allergic to tree nuts"]
    G --> H[Frontend sends message with same conversation_id]
    
    %% Backend retrieves pending request
    H --> I[Backend queries messages in conversation_id, finds assistant message with pending request]
    I --> J[Combine original meal plan request + allergy info, inject proceed reminder]
    
    %% Jasper generates meal plan
    J --> K[Jasper API call #1 (OpenAI) generates full 7-day meal plan avoiding tree nuts]
    K --> L[Backend saves AI response in DB, clears pending flag]
    
    %% User receives final meal plan
    L --> M[User sees complete 7-day meal plan immediately, starts with Day 1]
    
    %% Styling for clarity
    classDef userAction fill:#e1f5ff,stroke:#333,stroke-width:1px;
    classDef backendAction fill:#fff3cd,stroke:#333,stroke-width:1px;
    classDef apiCall fill:#d1f2eb,stroke:#333,stroke-width:2px;
    
    class A,F,G userAction;
    class B,C,D,E,H,I,J,L backendAction;
    class K apiCall;
```

## Implementation Details

### Frontend (static/js/dashboard.js)

**Lines 1357-1359**: Get conversation_id from sessionStorage
```javascript
let currentConversationId = sessionStorage.getItem('jasper_conversation_id') || null;
```

**Line 1372**: Send conversation_id with request
```javascript
conversation_id: currentConversationId, // Use persisted conversation ID
```

**Lines 1507-1512**: Save conversation_id from response
```javascript
if (result.conversation_id) {
    sessionStorage.setItem('jasper_conversation_id', result.conversation_id);
}
```

### Backend (app/services/pe/ai_assistant_service.py)

**Lines 1765-1772**: Query messages BEFORE saving user message
- Ensures we can find the assistant message with `pending_meal_plan_request`

**Lines 1815-1845**: Find pending meal plan request in metadata
- Searches assistant messages for `conversation_metadata.pending_meal_plan_request`

**Lines 1897-1902**: Detect allergy answer via intent classifier
- Uses `detect_allergy_answer()` utility function
- Intent classifier returns `"allergy_answer"` when detected

**Lines 1904-1907**: Force meal_plan intent when allergy answer + pending request
- Sets `user_intent = "meal_plan"` to load correct module

**Lines 2002-2022**: Fallback search in conversation history
- If metadata lookup fails, searches user messages for meal plan keywords

**Lines 2025-2094**: Combine original request + allergy info
- Creates `combined_message` with natural language formatting
- Extracts allergen for system prompt instruction

**Lines 2096-2110**: Inject proceed reminder
- Adds explicit instructions to create meal plan immediately
- Forbids acknowledgment, requires starting with "Day 1"

**Lines 2220-2235**: Hardcoded allergy question (no API call)
- Returns immediately without calling OpenAI
- Saves `pending_meal_plan_request` in `conversation_metadata`

**Lines 2237-2300**: Build messages array and call OpenAI
- Includes system prompts, conversation history, combined request
- Calls OpenAI API to generate meal plan

## Key Implementation Points

### 1. Persistent conversation_id
- **Critical**: Frontend must send the same `conversation_id` for both requests
- Stored in `sessionStorage` to persist across page reloads
- Backend uses it to find pending requests in the same conversation

### 2. Query Before Save
- **Critical**: Backend queries messages BEFORE saving the user message
- This ensures the assistant message with `pending_meal_plan_request` is found
- If query happens after save, the new user message hides the assistant message

### 3. Metadata Storage
- `pending_meal_plan_request` is stored in the **assistant message** metadata
- Not in the user message (user message is the allergy answer)
- Stored in `conversation_metadata` field (not `metadata`)

### 4. Allergy Detection
- Uses shared utility function `detect_allergy_answer()` from `app/core/allergy_detection.py`
- Detects keywords, phrases, and short answers
- Intent classifier also detects and returns `"allergy_answer"` intent

### 5. Request Combination
- Combines original request + allergy info into single message
- Handles first-person and third-person formats naturally
- Extracts allergen for explicit system prompt instruction

### 6. Proceed Reminder
- Injects explicit instructions to create meal plan immediately
- Forbids acknowledgment phrases ("Understood", "I will", etc.)
- Requires response to start with "Day 1" or "**DAY 1:**"

## Expected Log Output

### Step 1: Initial Meal Plan Request
```
🔥 DEBUG: Querying messages for conversation_id: <id>
🔥 DEBUG: Found X messages in conversation
🚨 Meal plan requested but allergies not asked - forcing allergy question first
💾 DEBUG: Saving metadata with pending_meal_plan_request: I have student who is a 16 year old...
✅ DEBUG: Verified saved metadata: {'pending_meal_plan_request': '...'}
```

### Step 2: Allergy Answer
```
🔥 DEBUG: Querying messages for conversation_id: <same-id>
🔥 DEBUG: Found X messages in conversation
✅ Found allergy question in previous message
✅✅✅ FOUND pending_meal_plan_request in assistant message #2: I have student who is a 16 year old...
🎯 FORCED intent to 'meal_plan' because allergy_answer intent detected with pending meal plan request
🔄🔄🔄 CRITICAL: Detected allergy answer with pending meal plan request - COMBINING NOW
✅ Combined message: I have student who is a 16 year old... The student is allergic to tree nuts.
🔍 DEBUG: About to call OpenAI API with X messages
```

### Step 3: Meal Plan Generation
```
🔍 DEBUG: OpenAI response received (XXXX chars)
🔍 DEBUG: Response starts with: Day 1, Breakfast:...
🔍 DEBUG: Starts with Day 1: True, Contains acknowledgment: False
✅ Meal plan generated successfully
```

## Testing Checklist

- [ ] User sends meal plan request → Jasper asks allergy question immediately
- [ ] User sends allergy answer → Same conversation_id is used
- [ ] Backend finds pending request in metadata
- [ ] Backend combines request + allergy info
- [ ] Jasper generates meal plan immediately (starts with "Day 1")
- [ ] No acknowledgment phrases in response
- [ ] All 7 days listed separately
- [ ] All allergens avoided in meal plan
- [ ] Conversation_id persists across page reload

## Troubleshooting

### Issue: "No pending meal plan request found"
**Cause**: conversation_id changed between requests
**Fix**: Ensure frontend sends same conversation_id (check sessionStorage)

### Issue: "Response starts with acknowledgment"
**Cause**: System prompt instructions not strong enough
**Fix**: Check that proceed reminder is injected (lines 2096-2110)

### Issue: "Metadata not found"
**Cause**: Query happens after saving user message
**Fix**: Ensure query happens before save (line 1765)

### Issue: "Intent classified as 'general'"
**Cause**: Allergy detection not working
**Fix**: Check `detect_allergy_answer()` function and intent classifier

## Related Files

- **Frontend**: `static/js/dashboard.js` (lines 1357-1513)
- **Backend**: `app/services/pe/ai_assistant_service.py` (lines 1765-2300)
- **Allergy Detection**: `app/core/allergy_detection.py`
- **Intent Classification**: `app/core/prompt_loader.py`
- **Meal Plan Module**: `app/core/prompts/module_meal_plan.txt`

