# Docker Testing Instructions for Modular Prompt System

## Testing in Docker Only

**IMPORTANT:** All testing must be done inside the Docker container, NOT locally.

## Quick Start

### 1. Find Your Container Name
```bash
docker ps
# Look for container name (usually "faraday-ai-app-1" or similar)
```

### 2. Verify Module Files Are in Container
```bash
docker exec <container-name> ls -la /app/app/core/prompts/
```

Expected output:
```
-rw-r--r-- 1 appuser appuser  3474 Jan 21 12:00 root_system_prompt.txt
-rw-r--r-- 1 appuser appuser  1345 Jan 21 12:00 module_meal_plan.txt
-rw-r--r-- 1 appuser appuser   472 Jan 21 12:00 module_workout.txt
-rw-r--r-- 1 appuser appuser   630 Jan 21 12:00 module_lesson_plan.txt
-rw-r--r-- 1 appuser appuser  3432 Jan 21 12:00 module_widgets.txt
```

### 3. Run Test Script Inside Docker
```bash
docker exec <container-name> python3 /app/test_modular_prompts.py
```

### 4. Expected Test Output
You should see:
```
✅ ALL TESTS PASSED - System is ready for deployment
```

## Detailed Testing Steps

### Step 1: Build/Start Container
```bash
# If using docker-compose
docker-compose up -d

# Or if using docker directly
docker build -t faraday-ai .
docker run -d --name faraday-test faraday-ai
```

### Step 2: Verify Files Exist
```bash
docker exec <container-name> test -f /app/app/core/prompts/root_system_prompt.txt && echo "✅ Root prompt exists" || echo "❌ Root prompt missing"
docker exec <container-name> test -f /app/app/core/prompts/module_meal_plan.txt && echo "✅ Meal plan module exists" || echo "❌ Meal plan module missing"
```

### Step 3: Test Import
```bash
docker exec <container-name> python3 -c "from app.core.prompt_loader import classify_intent, load_prompt_modules; print('✅ Imports work')"
```

### Step 4: Run Full Test Suite
```bash
docker exec <container-name> python3 /app/test_modular_prompts.py
```

### Step 5: Test Intent Classification
```bash
docker exec <container-name> python3 -c "
from app.core.prompt_loader import classify_intent
print('Meal plan:', classify_intent('I need a meal plan'))
print('Workout:', classify_intent('create a workout'))
print('Lesson plan:', classify_intent('lesson plan for basketball'))
print('Widget:', classify_intent('what can you do'))
print('General:', classify_intent('hello'))
"
```

### Step 6: Test Module Loading
```bash
docker exec <container-name> python3 -c "
from app.core.prompt_loader import load_prompt_modules
for intent in ['meal_plan', 'workout', 'lesson_plan', 'widget', 'general']:
    msgs = load_prompt_modules(intent)
    print(f'{intent}: {len(msgs)} message(s) loaded')
"
```

## Verify File Paths Work in Docker

The prompt loader uses relative paths:
```python
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
```

This works in Docker because:
- Files are copied to `/app/app/core/prompts/` via `COPY . .` in Dockerfile
- Python path includes `/app` (WORKDIR /app)
- `__file__` resolves correctly in Docker

## Common Issues & Solutions

### Issue: Module files not found
**Check:** Files exist in container
```bash
docker exec <container-name> ls -la /app/app/core/prompts/
```

**Solution:** Rebuild Docker image
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Import errors
**Check:** Python path
```bash
docker exec <container-name> python3 -c "import sys; print(sys.path)"
```

**Solution:** Should include `/app`

### Issue: Permission errors
**Solution:** Files should be readable (644)
```bash
docker exec <container-name> ls -la /app/app/core/prompts/
```

## Testing Checklist for Docker

- [ ] Container is running
- [ ] All 5 prompt files exist in `/app/app/core/prompts/`
- [ ] `test_modular_prompts.py` runs successfully
- [ ] All tests pass (Intent Classification, Module Loading, etc.)
- [ ] No import errors
- [ ] No file permission errors

