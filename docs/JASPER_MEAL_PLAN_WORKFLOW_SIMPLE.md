# Jasper Meal Plan Workflow - Quick Reference

## Simple Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER SENDS MEAL PLAN REQUEST                 │
│                    "Create 3-day meal plan"                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND: Detect Intent & Check DB                   │
│  • Classify intent: "meal_plan"                                │
│  • Query conversation history (last 50 messages)                 │
│  • Check for existing allergy info                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
    ┌───────────────────┐    ┌──────────────────────┐
    │  NO ALLERGY INFO  │    │  ALLERGY INFO EXISTS │
    └─────────┬─────────┘    └──────────┬───────────┘
              │                         │
              ▼                         ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│ Build Messages Array:   │  │ Build Messages Array:        │
│ • System prompt         │  │ • System prompt + priority    │
│ • Last 50 messages      │  │ • Last 50 messages           │
│ • User request          │  │ • Combined request + allergy │
│ • Allergy reminder      │  │ • Proceed reminder            │
└─────────┬───────────────┘  └──────────┬───────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   API CALL #1           │  │   API CALL #1                 │
│   (Ask about allergies) │  │   (Generate meal plan)        │
└─────────┬───────────────┘  └──────────┬───────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│ Store in DB:            │  │ Store in DB:                 │
│ • Response              │  │ • Response                  │
│ • Set pending flag      │  │ • Clear pending flag        │
└─────────┬───────────────┘  └──────────┬───────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   USER SEES QUESTION    │  │   USER SEES MEAL PLAN        │
└─────────┬───────────────┘  └──────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              USER RESPONDS: "I am allergic to peanuts"           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND: Process Allergy Answer                     │
│  • Detect allergy answer                                        │
│  • Retrieve pending meal plan request from DB                   │
│  • Combine: original request + allergy info                      │
│  • Build messages array with proceed reminder                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API CALL #2                                   │
│  • System prompt + top priority instruction                     │
│  • Last 50 messages                                             │
│  • Combined request                                             │
│  • Proceed reminder: "CREATE THE MEAL PLAN NOW"                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              JASPER GENERATES FULL MEAL PLAN                    │
│  • 3 meals + 3 snacks per day                                   │
│  • Serving sizes + calories for every item                      │
│  • Daily macros (protein, carbs, fat)                            │
│  • Micronutrients                                               │
│  • All allergens avoided                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND: Store Response & Clear Flags              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER RECEIVES MEAL PLAN                      │
│                      Workflow Complete                          │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Database Storage (PostgreSQL)
- **AIAssistantConversation**: Conversation metadata
- **AIAssistantMessage**: All messages with content, metadata, timestamps
- **Metadata Fields**: `pending_meal_plan_request`, `previous_asked_allergies`

### 2. Memory Retrieval
- Last **50 messages** retrieved per conversation
- Messages ordered chronologically
- Full conversation context maintained

### 3. Message Building
- **System Prompts**: Modular, intent-based (meal_plan module)
- **Conversation History**: Last 50 messages
- **Current Request**: User's message (or combined request)
- **Reminders**: Allergy reminder OR proceed reminder

### 4. API Call Structure
```
Messages Array:
├── System Prompt (modular)
│   └── Top Priority Instruction (if allergy answer detected)
├── Conversation History (last 50 messages, chronological)
├── Combined Request (original + allergy info)
└── Proceed Reminder ("CREATE THE MEAL PLAN NOW")
```

## Timing

| Phase | Time | Action |
|-------|------|--------|
| **t0** | Initial | User sends request |
| **t0 + δ** | Processing | Backend checks DB, builds messages |
| **t0 + δ + Δ** | API Response | Jasper responds |
| **t1** | User Response | User provides allergy info |
| **t1 + Δ** | Final Response | Jasper generates meal plan |

## State Management

```
Initial Request
    ↓
Store pending_meal_plan_request in metadata
    ↓
Ask about allergies (if not exists)
    ↓
User provides allergy info
    ↓
Combine request + allergy info
    ↓
Generate meal plan
    ↓
Clear pending flags
```

## Critical Instructions

### System Prompt Enhancement
```
🚨 ABSOLUTE TOP PRIORITY - READ THIS FIRST 🚨
THE USER'S MESSAGE BELOW IS A COMPLETE MEAL PLAN REQUEST WITH ALLERGY INFORMATION.
YOU MUST CREATE THE MEAL PLAN IMMEDIATELY.
DO NOT ACKNOWLEDGE. DO NOT EXPLAIN. DO NOT ASK QUESTIONS.
JUST CREATE THE MEAL PLAN. START WITH THE MEAL PLAN.
```

### Proceed Reminder
```
"I have provided my complete meal plan request above, which includes 
my original request plus my allergy information. CREATE THE MEAL PLAN NOW. 
DO NOT acknowledge the allergy. START YOUR RESPONSE WITH THE MEAL PLAN 
(Day 1, Breakfast:...)."
```

## Benefits

✅ **Persistent Memory**: All conversations stored in PostgreSQL  
✅ **Context Preservation**: Last 50 messages maintain full context  
✅ **Async-Safe**: DB updates prevent race conditions  
✅ **Modular Prompts**: Only necessary modules loaded  
✅ **Clear Workflow**: Allergy check → Meal plan generation  
✅ **Error Prevention**: Validation ensures complete meal plans  

