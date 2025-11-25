# How to Check Metadata for Allergy Question Message

## Expected Metadata Structure

When Jasper asks the allergy question, the metadata should be saved as:

```json
{
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000,
  "forced_allergy_question": true,
  "pending_meal_plan_request": "i have student who is a 16 year old high school wrestler in season wrestling 2 hours a day 5 days a week and an additional 8 hours combed strength and cardio training outside of practice, I need a 7 day meal plan for him to maintain 172 pounds without going over or under while maintaining strength and stamina for his workouts and daily activities"
}
```

## How to Query It

### Option 1: Direct SQL Query (PostgreSQL)

```sql
SELECT 
    id,
    message_type,
    content,
    conversation_metadata,
    created_at
FROM ai_assistant_messages
WHERE message_type = 'assistant'
  AND content LIKE '%Before I create your meal plan%'
  AND conversation_metadata IS NOT NULL
ORDER BY created_at DESC
LIMIT 1;
```

### Option 2: Using Python/Django Shell

```python
from app.models.ai_assistant import AIAssistantMessage
from sqlalchemy import desc

# Get the most recent allergy question message
allergy_question = (
    db.query(AIAssistantMessage)
    .filter(AIAssistantMessage.message_type == "assistant")
    .filter(AIAssistantMessage.content.like("%Before I create your meal plan%"))
    .order_by(desc(AIAssistantMessage.created_at))
    .first()
)

if allergy_question:
    print("Message ID:", allergy_question.id)
    print("Content:", allergy_question.content)
    print("Metadata:", allergy_question.conversation_metadata)
    print("Metadata Type:", type(allergy_question.conversation_metadata))
    print("Has pending_meal_plan_request:", "pending_meal_plan_request" in (allergy_question.conversation_metadata or {}))
else:
    print("No allergy question message found")
```

### Option 3: Add Debug Endpoint (Temporary)

Add this to your API for quick checking:

```python
@router.get("/debug/allergy-question-metadata")
async def get_allergy_question_metadata(db: Session = Depends(get_db)):
    """Debug endpoint to check allergy question metadata"""
    from app.models.ai_assistant import AIAssistantMessage
    from sqlalchemy import desc
    
    message = (
        db.query(AIAssistantMessage)
        .filter(AIAssistantMessage.message_type == "assistant")
        .filter(AIAssistantMessage.content.like("%Before I create your meal plan%"))
        .order_by(desc(AIAssistantMessage.created_at))
        .first()
    )
    
    if not message:
        return {"error": "No allergy question message found"}
    
    return {
        "message_id": str(message.id),
        "content": message.content,
        "metadata": message.conversation_metadata,
        "metadata_type": str(type(message.conversation_metadata)),
        "has_pending_request": "pending_meal_plan_request" in (message.conversation_metadata or {}),
        "pending_request": message.conversation_metadata.get("pending_meal_plan_request") if message.conversation_metadata else None
    }
```

## What to Look For

✅ **Correct Structure:**
- `conversation_metadata` is a dict (not None, not string)
- `pending_meal_plan_request` key exists
- `pending_meal_plan_request` contains the original user message
- `forced_allergy_question` is `true`

❌ **Incorrect Structure:**
- `conversation_metadata` is `None`
- `conversation_metadata` is a string (should be dict)
- `pending_meal_plan_request` key is missing
- `pending_meal_plan_request` is empty or None

## After the Fix

With the fix applied, the metadata should be saved correctly using `conversation_metadata=` instead of `metadata=`, and it should be readable using `msg.conversation_metadata` instead of `msg.metadata`.

