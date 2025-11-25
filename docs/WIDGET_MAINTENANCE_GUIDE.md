# Widget Architecture Maintenance & Expansion Guide

## Quick Reference

### Current Architecture Status: ✅ Production Ready

- **Hybrid Service Pattern:** Each service owns prompt, model, extraction
- **Model Tiering:** Optimized for speed (gpt-4o-mini) and quality (gpt-4o)
- **Service Routing:** ModelRouter with intelligent fallbacks
- **Widget Handling:** Custom handlers + shared extraction helpers
- **Documentation:** Complete architecture guide available

---

## Adding New Widgets: Step-by-Step Checklist

### 1. Create Specialized Service
- [ ] Create `app/services/pe/specialized_services/new_widget_service.py`
- [ ] Inherit from `BaseWidgetService` and `BaseSpecializedService`
- [ ] Set `prompt_file` to specialized prompt
- [ ] Set `model` based on quality needs (gpt-4o-mini or gpt-4o)
- [ ] Set `widget_type` identifier

### 2. Implement Required Methods
- [ ] `get_system_prompt()` - Load focused prompt
- [ ] `get_supported_intents()` - List intents this service handles
- [ ] `get_model()` - Return model name
- [ ] `extract_widget_data()` - Extract widget data from response
  - [ ] Option A: Use shared extraction function (if response-based)
  - [ ] Option B: Custom logic (if GPT function calling)

### 3. Create Specialized Prompt
- [ ] Create `app/core/prompts/specialized_new_widget.txt`
- [ ] Keep prompt focused (~200-500 tokens)
- [ ] Include JSON widget format instructions if applicable
- [ ] Emphasize speed and clarity

### 4. Add Shared Extraction Function (if needed)
- [ ] If response-based parsing needed, add to `widget_handler.py`
- [ ] Function name: `_extract_new_widget_data(response_text)`
- [ ] Handle multiple response formats
- [ ] Return structured dict with `type` and `data` keys

### 5. Register in ServiceRegistry
- [ ] Import new service in `service_registry.py`
- [ ] Add to `register_defaults()` method
- [ ] Map primary intent to service class

### 6. Update Intent Classification (if needed)
- [ ] Add keywords to `widget_handler.py::classify_intent()`
- [ ] Test intent classification with new keywords
- [ ] Ensure proper routing to new service

### 7. Testing
- [ ] Add test case to `tests/test_hybrid_architecture.py`
- [ ] Test service registration
- [ ] Test intent routing
- [ ] Test widget data extraction
- [ ] Test end-to-end flow

---

## Model Tiering Guidelines

### Use `gpt-4o-mini` for:
- ✅ Simple data queries (attendance, analytics)
- ✅ GPT function calling widgets
- ✅ General responses and advice
- ✅ Fast, low-cost operations
- ✅ High-volume requests

### Use `gpt-4o` for:
- ✅ Lesson plans (educational quality critical)
- ✅ Meal plans (nutrition accuracy critical)
- ✅ Workout plans (safety and detail critical)
- ✅ Complex structured outputs
- ✅ Quality-sensitive content

### Use `gpt-4-turbo` for:
- ✅ Complex analysis requiring advanced reasoning
- ✅ Very large context windows
- ✅ Multi-step problem solving
- ✅ Fallback for complex queries

---

## Monitoring & Performance

### Metrics to Track

1. **Token Usage**
   - Track tokens per service
   - Monitor cost per widget type
   - Identify optimization opportunities

2. **Response Times**
   - Measure latency per service
   - Identify bottlenecks
   - Optimize slow services

3. **Widget Extraction Success Rate**
   - Track extraction failures
   - Monitor empty widget_data returns
   - Improve extraction patterns

4. **Model Performance**
   - Compare gpt-4o-mini vs gpt-4o quality
   - Adjust model tiering if needed
   - Monitor cost vs quality trade-offs

### Optimization Strategies

- **Prompt Optimization:** Reduce token count while maintaining quality
- **Caching:** Cache frequent widget responses if appropriate
- **Parallel Processing:** Consider async extraction for multiple widgets
- **Model Selection:** Adjust model tier based on actual usage patterns

---

## Testing Checklist

### Integration Tests
- [ ] Service registry routing
- [ ] Model router fallback
- [ ] Intent classification accuracy
- [ ] Widget data extraction
- [ ] End-to-end request flow

### Unit Tests
- [ ] Service initialization
- [ ] Prompt loading
- [ ] Model selection
- [ ] Extraction function accuracy
- [ ] Error handling

### Performance Tests
- [ ] Response time benchmarks
- [ ] Token usage validation
- [ ] Concurrent request handling
- [ ] Fallback performance

---

## Maintenance Best Practices

### ✅ DO

1. **Keep Prompts in Standalone Files**
   - Easier to update without code changes
   - Version control friendly
   - Non-developers can review/edit

2. **Use Patch-Style Modifications**
   - Avoid monolithic changes in `ai_assistant_service.py`
   - Make focused, targeted updates
   - Preserve existing logic

3. **Review Fallback Logic**
   - After adding new widgets, verify fallbacks still work
   - Test unmatched intents
   - Ensure graceful degradation

4. **Document Changes**
   - Update architecture docs when adding services
   - Document new extraction patterns
   - Note model tiering decisions

5. **Test Before Deploy**
   - Run full test suite
   - Test new widget end-to-end
   - Verify no regressions

### ❌ DON'T

1. **Don't Create Monolithic Functions**
   - Avoid `extract_all_widgets()` with massive if/else
   - Keep functions focused and small

2. **Don't Skip Service Registration**
   - Always register in ServiceRegistry
   - Update intent classification if needed

3. **Don't Mix Extraction Patterns**
   - Response-based → use shared extraction
   - GPT function → use custom logic
   - Don't force one pattern on all

4. **Don't Overload Shared Functions**
   - Keep `_extract_*_data()` functions focused
   - Add new functions for new patterns
   - Don't add too many edge cases to existing functions

5. **Don't Bypass Model Tiering**
   - Use appropriate model for each service
   - Don't default everything to gpt-4o
   - Consider cost and performance

---

## Troubleshooting Guide

### Widget Data Not Extracted

**Symptoms:** Response generated but `widget_data` is `None`

**Check:**
1. Is `extract_widget_data()` being called?
2. Does extraction function match response format?
3. Are extraction patterns correct for current response style?
4. Check logs for extraction errors

**Fix:**
- Update extraction patterns to match actual response format
- Add logging to extraction functions
- Test extraction with actual API responses

### Wrong Service Routing

**Symptoms:** Request goes to wrong service or fallback

**Check:**
1. Is intent classification correct?
2. Is service registered in ServiceRegistry?
3. Does `should_handle()` return true for intent?
4. Are supported intents correct?

**Fix:**
- Update intent classification keywords
- Register service in ServiceRegistry
- Update `get_supported_intents()` method

### Model Tiering Issues

**Symptoms:** Wrong model used, poor quality, or high cost

**Check:**
1. Is `get_model()` returning correct model?
2. Is environment variable set correctly?
3. Is model tier appropriate for widget type?

**Fix:**
- Update `get_model()` method
- Set `JASPER_MODEL` or `JASPER_MINI_MODEL` env vars
- Adjust model tier based on quality needs

---

## Quick Reference: File Locations

```
app/services/pe/
├── widget_handler.py              # Shared extraction + intent classification
├── model_router.py                 # Routing logic
├── specialized_services/
│   ├── service_registry.py        # Service registration
│   ├── attendance_service.py      # Attendance widget
│   ├── lesson_plan_service.py     # Lesson plan widget
│   ├── meal_plan_service.py       # Meal plan widget
│   ├── workout_service.py         # Workout widget
│   ├── general_widget_service.py  # GPT function widgets
│   └── general_response_service.py # Text response widgets

app/core/prompts/
├── specialized_attendance.txt
├── specialized_lesson_plan.txt
├── specialized_meal_plan.txt
├── specialized_workout.txt
├── specialized_general_widgets.txt
├── specialized_general_response.txt
└── jasper_router.txt              # Fallback router

docs/
├── WIDGET_ARCHITECTURE.md         # Full architecture guide
└── WIDGET_MAINTENANCE_GUIDE.md    # This file
```

---

## Related Documentation

- `docs/WIDGET_ARCHITECTURE.md` - Complete architecture documentation
- `docs/HYBRID_ARCHITECTURE_FLOW.md` - Detailed flow diagrams
- `docs/MODEL_MAPPING_IMPLEMENTATION.md` - Model tiering details
- `docs/TESTING_HYBRID_ARCHITECTURE.md` - Testing guide

---

## Support

For questions or issues:
1. Check architecture documentation
2. Review troubleshooting guide
3. Check test suite for examples
4. Review existing service implementations

