# Frontend Testing Guide - Modular Prompt System

## 🎯 Overview

Test the modular prompt system from your **local frontend**. The system is entirely backend - no frontend code changes needed. You'll automatically see faster responses and better behavior.

---

## ✅ Prerequisites

1. **Backend Running:**
   - Docker: `docker-compose up`
   - Or local server running

2. **Frontend Access:**
   - Open `static/dashboard.html` in browser
   - Or access via your local server URL

3. **Browser DevTools:**
   - Press `F12` to open
   - Keep Console and Network tabs open

---

## 🧪 Critical Test: Meal Plan Workflow

### Test Flow

**Step 1: Request Meal Plan**
```
Type: "I need a 7 day meal plan for a wrestler"
```

**Expected:**
- ✅ Jasper asks: "Before I create your meal plan, do you have any allergies, dietary restrictions, or foods to avoid?"
- ✅ Response appears in chat
- ✅ Check Network tab: Response time should be 1-2 seconds (faster than before)

**Step 2: Provide Allergy Info**
```
Type: "I'm allergic to tree nuts"
```

**Expected:**
- ✅ Jasper **immediately** creates meal plan (no acknowledgment message)
- ✅ Meal plan includes **all 7 days** (scroll through entire response)
- ✅ Every food item shows calories: `Food name (amount: XXX calories)`
- ✅ **Zero tree nuts** in entire meal plan
- ✅ Widget appears with meal plan data
- ✅ Response time: 1-3 seconds

**What to Check:**
- [ ] Allergy question appeared first
- [ ] Meal plan generated immediately after allergy answer
- [ ] All 7 days included (no "repeat" or "same structure" text)
- [ ] Every food has calories
- [ ] No allergens present
- [ ] Widget data extracted correctly

---

## 🧪 Additional Tests

### Test 2: Workout Plan
```
Type: "Create a wrestling workout plan"
```

**Check:**
- ✅ Includes "Strength Training" section
- ✅ Includes "Cardio / Conditioning" section
- ✅ Mentions wrestler-specific guidance (5-6 days/week)

### Test 3: Lesson Plan
```
Type: "Create a PE lesson plan for wrestling"
```

**Check:**
- ✅ Includes Lesson Description
- ✅ Includes Danielson Framework
- ✅ Includes Costa's Levels of Questions

### Test 4: Widget Query
```
Type: "What can you do?"
```

**Check:**
- ✅ Lists 39 widgets
- ✅ Fast response

### Test 5: General Chat
```
Type: "Hello"
```

**Check:**
- ✅ Natural response
- ✅ Uses your name "Joe"
- ✅ Fast response

---

## 🔍 Monitoring in Browser

### Console Tab (F12 → Console)

**Look for:**
- ✅ `✅ Chat response received`
- ✅ `📊 Widget data: {...}`
- ✅ No red error messages
- ✅ API response times logged

**Example:**
```
✅ Chat response received
📊 Widget data: {type: "meal_plan", ...}
🔊 Auto-speak: Starting audio fetch...
```

### Network Tab (F12 → Network)

**Filter by:** `ai-assistant` or `chat`

**Check:**
- ✅ Status: `200 OK`
- ✅ Response time: Should be 1-2 seconds (was 3-5 seconds before)
- ✅ Response size: Should be smaller
- ✅ No 500 errors

**Click on request → Response tab:**
- Verify response structure
- Check for error messages

---

## 📊 Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Response Time | 3-5 sec | 1-2 sec | 50-60% faster |
| Token Usage | ~20,000 | 865-1,723 | 85-95% reduction |
| Accuracy | Variable | Better | Improved adherence |

---

## ⚠️ Red Flags (Should NOT Happen)

### ❌ Jasper doesn't ask about allergies
- **Symptom:** Meal plan request generates meal plan immediately
- **Action:** Check backend logs for intent classification

### ❌ Jasper forgets original request
- **Symptom:** After allergy answer, Jasper gives general info instead of meal plan
- **Action:** Check conversation history retrieval

### ❌ Placeholder text in meal plans
- **Symptom:** "Repeat these meals for remaining days" or "Same structure can be followed"
- **Action:** Report - this should not happen with new system

### ❌ Missing calories
- **Symptom:** Food items without calorie information
- **Action:** Check widget extraction

### ❌ Slow responses (>5 seconds)
- **Symptom:** Response takes too long
- **Action:** Check backend logs, verify modules loading

---

## ✅ Success Checklist

After testing, verify all:

- [ ] Meal plan workflow works end-to-end
- [ ] Allergy question appears before meal plan
- [ ] Meal plan generated immediately after allergy answer
- [ ] All requested days included (no placeholders)
- [ ] Calories included for every food item
- [ ] Allergens completely avoided
- [ ] Response times are faster (1-2 seconds)
- [ ] No errors in browser console
- [ ] No errors in network tab
- [ ] Widgets extract correctly
- [ ] Workout plans include both sections
- [ ] Lesson plans include all components

---

## 🐛 Troubleshooting

### Issue: No Response
**Check:**
- Backend server running? (`docker ps` or check server status)
- Browser console for JavaScript errors
- Network tab for failed requests (status 500, 502, etc.)

### Issue: Slow Response
**Check:**
- Backend logs for errors
- Database connection working
- Network tab for request timing

### Issue: Wrong Behavior
**Check:**
- Backend logs for intent classification
- Verify prompt modules loading (check backend logs)
- Conversation history retrieval (check backend logs)

### Issue: Missing Widget Data
**Check:**
- Browser console for widget extraction errors
- Network response contains widget data
- Widget rendering in chat

---

## 📝 Quick Test Script

Copy-paste this into browser console to test:

```javascript
// Test meal plan workflow
async function testMealPlan() {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) {
        console.error('Chat input not found');
        return;
    }
    
    // Step 1: Request meal plan
    chatInput.value = "I need a 7 day meal plan for a wrestler";
    document.querySelector('button[onclick="sendMessage()"]')?.click();
    
    // Wait for response, then test allergy answer
    setTimeout(() => {
        chatInput.value = "I'm allergic to tree nuts";
        document.querySelector('button[onclick="sendMessage()"]')?.click();
    }, 5000);
}

// Run test
testMealPlan();
```

---

## 🎯 Key Points

1. **No Frontend Changes:** System is entirely backend - frontend works automatically
2. **Faster Responses:** 50-60% improvement in response time
3. **Better Accuracy:** Improved instruction adherence
4. **Test Meal Plan First:** Most critical workflow to verify
5. **Monitor DevTools:** Use Console and Network tabs to track performance

---

## 📞 Need Help?

If something doesn't work:
1. Check browser console for errors
2. Check network tab for failed requests
3. Check backend logs for intent classification
4. Verify all prompt files exist in Docker: `docker exec <container> ls -la /app/app/core/prompts/`

