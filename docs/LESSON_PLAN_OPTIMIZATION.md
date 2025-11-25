# Lesson Plan Workflow Optimization

## Overview
This document describes the optimizations applied to make the lesson plan workflow as robust as the meal plan workflow.

## Issues Identified

### 1. Widget Data Extraction Problems
- **Curriculum Standards**: Duplicated text ("Aligned with state standards, students will be able to: Aligned with state standards, students will be able to: II. Activities:")
- **Danielson Framework Alignment**: Duplicated headers ("VIII. Alignment: VIII. Danielson Framework Alignment:")
- **Costa's Levels of Questioning**: Duplicated headers ("VII. Costa's Levels of Questioning: VII. Costa's Levels of Questioning:")
- Extraction was picking up section headers (like "VIII. Alignment:") instead of just the content

### 2. Missing Robustness Features
- No validation logic for lesson plan responses
- No top-priority instructions for comprehensive lesson plan requests
- Weak system prompt compared to meal plan module
- Extraction regex patterns didn't handle roman numeral headers properly

## Optimizations Applied

### 1. Strengthened Lesson Plan System Prompt
**File**: `app/core/prompts/module_lesson_plan.txt`

**Changes**:
- Added explicit workflow rules (similar to meal plan)
- Listed all 14 required components with detailed descriptions
- Added formatting requirements
- Added critical instructions for comprehensive lesson plans
- Clarified worksheet/rubric generation process

**Key Sections**:
- RULE A: Complete list of required components
- RULE B: Formatting requirements
- RULE C: Comprehensive lesson plan handling
- RULE D: Worksheets and rubrics

### 2. Fixed Extraction Regex Patterns
**File**: `app/services/pe/ai_assistant_service.py`

**Fixed Sections**:
- **Curriculum Standards** (line ~1375):
  - Removed roman numeral headers (e.g., "I.", "II.", "VIII.")
  - Added check to skip activity markers
  - Added validation for actual standard codes
  - Added duplication prevention check

- **Danielson Framework** (line ~1352):
  - Removed roman numeral headers (e.g., "VIII. Alignment:")
  - Added check to skip header-only content
  - Added validation for actual domain content
  - Added duplication prevention check

- **Costa's Levels of Questioning** (line ~1364):
  - Removed roman numeral headers (e.g., "VII. Costa's Levels of Questioning:")
  - Added check to skip header-only content
  - Added validation for actual level content
  - Added duplication prevention check

**Key Improvements**:
- Removes section headers before extraction
- Validates content is not just a header
- Prevents duplication by checking if content already exists
- Filters out activity markers that get incorrectly picked up

### 3. Added Top-Priority Instructions
**File**: `app/services/pe/ai_assistant_service.py` (line ~2378)

**Implementation**:
- Detects comprehensive lesson plan requests
- Adds top-priority system message with all 14 required components
- Inserts at the beginning of the first system message
- Ensures AI follows comprehensive requirements

**Detection Keywords**:
- "comprehensive lesson plan"
- "detailed learning objectives"
- "danielson framework"
- "costa's levels"
- "state standards"
- "assessment rubrics"
- "differentiation strategies"

### 4. Added Validation Logic
**File**: `app/services/pe/ai_assistant_service.py` (line ~2667)

**Validation Checks**:
- **Required Components**: Checks for all 14 required components
- **Standards Codes**: Validates actual standard codes are present (not just "aligned with state standards")
- **Danielson Domains**: Ensures all 4 domains are included
- **Costa's Levels**: Ensures all 3 levels are included
- **Time Allocations**: Validates activities include time allocations

**Behavior**:
- Logs validation errors (unlike meal plans, doesn't force correction)
- Lesson plans are more flexible than meal plans (no safety-critical requirements)
- Extraction logic handles missing components gracefully

### 5. Safe Message Builders
**Status**: Already applied (from meal plan patches)

**Location**: `app/services/pe/ai_assistant_service.py` (line ~2386)

**Functionality**:
- Prevents `NoneType.strip()` crashes
- Ensures all message content is a string
- Applied to all messages before OpenAI API calls

## Comparison with Meal Plan Workflow

| Feature | Meal Plan | Lesson Plan |
|---------|-----------|-------------|
| System Prompt Strength | ✅ Strong | ✅ Strong (now) |
| Validation Logic | ✅ Strict (forces correction) | ✅ Logs errors (flexible) |
| Top-Priority Instructions | ✅ Yes | ✅ Yes (now) |
| Extraction Fixes | ✅ Yes | ✅ Yes (now) |
| Safe Message Builders | ✅ Yes | ✅ Yes (already) |
| Duplication Prevention | ✅ Yes | ✅ Yes (now) |

## Testing Recommendations

1. **Test Comprehensive Lesson Plan Request**:
   ```
   "Create a comprehensive lesson plan for a 10th grade basketball unit that includes detailed learning objectives aligned with state standards, step-by-step activities for a 45-minute class, assessment rubrics, differentiation strategies for students with varying skill levels, safety considerations, and homework assignments. Also include Costa's Levels of Questioning examples and Danielson Framework alignment."
   ```

2. **Verify Widget Data Extraction**:
   - Check that Curriculum Standards shows actual standard codes (not duplicated headers)
   - Check that Danielson Framework shows all 4 domains (not duplicated headers)
   - Check that Costa's Levels shows all 3 levels (not duplicated headers)

3. **Verify Response Quality**:
   - All 14 required components are present
   - Activities include time allocations
   - Standards include codes and descriptions
   - No duplicated section headers in widget data

## Files Modified

1. `app/core/prompts/module_lesson_plan.txt` - Strengthened system prompt
2. `app/services/pe/ai_assistant_service.py` - Fixed extraction, added validation, added top-priority instructions

## Next Steps

1. Test the comprehensive lesson plan request on live site
2. Verify widget data extraction shows clean, non-duplicated content
3. Monitor response quality and adjust validation thresholds if needed
4. Consider adding forced correction for critical missing components (similar to meal plans)

