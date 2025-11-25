# Meal Plan Flow Validation Checklist

## ✅ Step-by-Step Log Validation

After rebuilding Docker and testing, check your logs for these exact messages in order:

---

## Step 1: Initial Meal Plan Request

**User sends:** "I need a 7 day meal plan..."

**Look for:**
```
🔍 Pre-checking X recent messages for allergy question...
🚨 Meal plan requested but allergies not asked - forcing allergy question first
💾 DEBUG: Saving metadata with pending_meal_plan_request: i have student who is a 16 year old...
💾 DEBUG: Full metadata to save: {'model': 'gpt-4', 'temperature': 0.7, 'max_tokens': 2000, 'forced_allergy_question': True, 'pending_meal_plan_request': '...'}
✅ DEBUG: Verified saved metadata: {'model': 'gpt-4', 'forced_allergy_question': True, 'pending_meal_plan_request': '...'}
✅ DEBUG: Has pending_meal_plan_request: True
```

**Jasper responds:** "Before I create your meal plan, do you have any food allergies..."

---

## Step 2: User Provides Allergy Info

**User sends:** "the student is allergic to tree nuts"

**Look for (in order):**

### 2a. Metadata Retrieval
```
🔍 Pre-checking X recent messages for allergy question...
✅ Found allergy question in previous message: Before I create your meal plan...
🔍 DEBUG: Raw conversation_metadata type: <class 'dict'>, value: {...}
🔍 DEBUG: Processed metadata type: <class 'dict'>, keys: ['model', 'temperature', 'max_tokens', 'forced_allergy_question', 'pending_meal_plan_request']
✅ Found pending meal plan request in metadata: i have student who is a 16 year old...
🔍 DEBUG: Full metadata: {'model': 'gpt-4', 'forced_allergy_question': True, 'pending_meal_plan_request': '...'}
```

**OR if it fails:**
```
⚠️ DEBUG: No pending_meal_plan_request found. Metadata keys: [...]
```

### 2b. Allergy Answer Detection
```
✅ PRE-DETECTED allergy answer: 'the student is allergic to tree nuts'
✅ Marked as meal plan request based on allergy answer + pending request
🎯 Forced intent to 'meal_plan' because allergy answer detected with pending meal plan request
```

### 2c. Message Combination
```
🔄 Detected allergy answer with pending meal plan request - combining
🔍 DEBUG: Original request: i have student who is a 16 year old high school wrestler...
🔍 DEBUG: Allergy answer: the student is allergic to tree nuts
✅ Combined message: i have student who is a 16 year old high school wrestler in season wrestling 2 hours a day 5 days a week and an additional 8 hours combed strength and cardio training outside of practice, I need a 7 day meal plan for him to maintain 172 pounds without going over or under while maintaining strength and stamina for his workouts and daily activities. the student is allergic to tree nuts.
🔍 DEBUG: Message combination complete. is_meal_plan_request=True, is_allergy_answer=True
```

### 2d. System Prompt Enhancement
```
✅ Added top priority instruction at the very beginning of system prompt
```

### 2e. Proceed Reminder Injection
```
✅ Added combined request as user message: i have student who is a 16 year old...
✅ Added proceed reminder message to conversation
```

### 2f. API Call
```
🔍 DEBUG: About to call OpenAI API with X messages
🔍 DEBUG: First system message starts with: 🚨🚨🚨 ABSOLUTE TOP PRIORITY...
🔍 DEBUG: Last user message: I have provided my complete meal plan request above...
🔍 DEBUG: Combined request: i have student who is a 16 year old...
```

### 2g. Response Validation
```
🔍 DEBUG: OpenAI response received (XXXX chars)
🔍 DEBUG: Response starts with: Day 1, Breakfast:...
🔍 DEBUG: Starts with Day 1: True, Contains acknowledgment: False
🔍 Validating meal plan response (length: XXXX chars)
```

**OR if acknowledgment detected:**
```
🚨 VALIDATION FAILED: Response starts with acknowledgment after allergy answer
🔄 Requesting corrected meal plan response...
```

---

## ✅ Success Indicators

### All Steps Present:
1. ✅ Metadata saved with `pending_meal_plan_request`
2. ✅ Metadata retrieved correctly (not None, not empty)
3. ✅ Allergy answer detected
4. ✅ Pending request found
5. ✅ Messages combined
6. ✅ System prompt enhanced
7. ✅ Proceed reminder injected
8. ✅ API called with combined request
9. ✅ Response starts with "Day 1" (not "Understood")

---

## ❌ Failure Indicators

### If Metadata Not Saved:
```
⚠️ DEBUG: conversation_metadata is None, using empty dict
⚠️ DEBUG: No pending_meal_plan_request found. Metadata keys: []
```
**Fix:** Check that `conversation_metadata=` is used (not `metadata=`)

### If Metadata Not Retrieved:
```
⚠️ DEBUG: Raw conversation_metadata type: <class 'NoneType'>, value: None
```
**Fix:** Check that `msg.conversation_metadata` is used (not `msg.metadata`)

### If Allergy Answer Not Detected:
```
⚠️ Not detected as allergy answer: 'the student is allergic to tree nuts'
```
**Fix:** Check allergy detection keywords/phrases

### If Combination Fails:
```
⚠️ Detected allergy answer but no pending meal plan request found in metadata or conversation history
```
**Fix:** Check metadata retrieval logic

### If Acknowledgment Still Appears:
```
🔍 DEBUG: Response starts with: Understood, Joe. I have updated...
🔍 DEBUG: Starts with Day 1: False, Contains acknowledgment: True
🚨 VALIDATION FAILED: Response starts with acknowledgment after allergy answer
```
**Fix:** Check system prompt enhancement and proceed reminder injection

---

## 📋 Quick Test Sequence

1. **Send meal plan request** → Check for metadata save logs
2. **Send allergy answer** → Check for metadata retrieval logs
3. **Check response** → Should start with "Day 1" not "Understood"

---

## 🔍 Log Search Commands

### Find metadata save:
```bash
grep "💾 DEBUG: Saving metadata" logs/app.log
```

### Find metadata retrieval:
```bash
grep "🔍 DEBUG: Raw conversation_metadata" logs/app.log
```

### Find combination:
```bash
grep "🔄 Detected allergy answer with pending meal plan request" logs/app.log
```

### Find validation:
```bash
grep "🔍 DEBUG: Response starts with" logs/app.log
```

---

## 🎯 Expected Final Result

**Jasper's response should start with:**
```
Day 1, Breakfast:
```

**NOT:**
```
Understood, Joe. I have updated...
```

If you see the acknowledgment, check the validation logs to see if it was caught and corrected.

