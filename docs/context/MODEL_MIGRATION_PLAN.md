# Faraday-AI Model Consolidation, Migration, and Rebuild Plan

## Overview

This document details the step-by-step process for consolidating, migrating, and rebuilding all model files in the Faraday-AI project. It is designed to serve as a living record of what has been done, what is in progress, and what remains, ensuring clarity and preventing confusion during this complex refactor.

---

## **Directory Inventory**

### 1. Main Consolidated Models Directory
- `app/models/`
  - Contains the unified, canonical models for the project.

### 2. Legacy/Backup Physical Education Models
- `models/physical_education/`
  - [x] `types.py`
  - [x] `base.py`
  - [x] `exercise.py`
  - [x] `safety.py`
  - [x] `class_.py`
  - [x] `assessment.py`

### 3. Service-Specific/Legacy Models
- `app/services/physical_education/models/`
  - [x] `nutrition.py`
  - [x] `workout.py`
  - [x] `student_types.py`
  - [x] `equipment.py`
  - [x] `activity_types.py`
  - [x] `safety.py`
  - [x] `class_.py`
  - [x] `fitness_goals.py`
  - [x] `exercise.py`
  - [x] `health_metrics.py`
  - [x] `routine.py`
  - [x] `generate_models.py`
  - [x] `class_types.py`
  - [x] `routine_performance_models.py`

### 4. Dashboard Models
- `app/dashboard/models/`
  - [ ] `api_key.py`
  - [ ] `security.py`
  - [ ] `user_models.py`
  - [ ] `gpt_models.py`
  - [ ] `dashboard_models.py`
  - [ ] `resource_models.py`
  - [ ] `notification_models.py`
  - [ ] `organization_models.py`
  - [ ] `project.py`
  - [ ] `feedback.py`
  - [ ] `dashboard.py`
  - [ ] `access_control.py`
  - [ ] `user_preferences.py`
  - [ ] `tool_registry.py`
  - [ ] `context.py`
  - [ ] `context_models.py`

---

## **Migration and Merge Plan**

### **Step 1: Identify Duplicates and Redundancies**
- Compare file contents (not just names) between all model directories.
- If a model already exists in `app/models/`, do NOT move the duplicate—archive or delete the old one after verification.
- If a model is unique or contains unique logic, move it to `app/models/` and resolve any naming conflicts.

### **Step 2: Move Unique Models to `app/models/`**
- For each file in the legacy/service/dashboard directories:
  - If not already represented in `app/models/`, move it there.
  - If it is a utility or enum (e.g., `types.py`, `base.py`), merge its contents into the corresponding file in `app/models/`.

### **Step 3: Merge and Refactor as Needed**
- For files with overlapping content (e.g., multiple `class_.py`, `safety.py`, `exercise.py`):
  - Merge class definitions, enums, and utility functions into the canonical file in `app/models/`.
  - Preserve all relationships, constraints, and docstrings.
  - Remove or archive the old file after merging.

### **Step 4: Update Imports Throughout the Project**
- Update all import statements in:
  - Services
  - APIs
  - Tests
  - Seed scripts
- All model imports should now be from `app.models`.

### **Step 5: Verify and Test**
- Ensure all models are imported in `app/models/__init__.py` (for easy import in Alembic and elsewhere).
- Run Alembic autogenerate to verify all tables are detected.
- Run all tests and seed scripts to ensure nothing is broken.

### **Step 6: Archive or Delete Old Files**
- Once all tests and migrations pass, archive or delete the old model files/directories.

---

## **Proposed Move/Merge Actions (by Directory)**

### **A. `models/physical_education/`**
| File         | Action        | Notes/Instructions                                 |
|--------------|--------------|----------------------------------------------------|
| types.py     | Merge         | Merge enums into `app/models/types.py`             |
| base.py      | Merge         | Merge base classes into `app/models/base.py`       |
| exercise.py  | Merge/Review  | Compare with `app/models/exercise.py`, merge unique logic, archive after merge |
| safety.py    | Merge/Review  | Compare with `app/models/safety.py`, merge unique logic, archive after merge |
| class_.py    | Merge/Review  | Compare with `app/models/class_.py`, merge unique logic, archive after merge |
| assessment.py| Merge/Review  | Compare with `app/models/assessment.py`, merge unique logic, archive after merge |
| __init__.py  | Archive       | Archive after merge                                |
| .DS_Store    | Delete        | Not needed                                         |

### **B. `app/services/physical_education/models/`**
| File                        | Action        | Notes/Instructions                                 |
|-----------------------------|--------------|----------------------------------------------------|
| nutrition.py                | Move          | If not in `app/models/`, move it                   |
| workout.py                  | Move          | If not in `app/models/`, move it                   |
| student_types.py            | Merge         | Merge enums/types into `app/models/types.py`        |
| equipment.py                | Merge/Review  | Compare with `app/models/equipment.py`, merge unique logic, archive after merge |
| activity_types.py           | Merge         | Merge enums/types into `app/models/types.py`        |
| safety.py                   | Merge/Review  | Compare with `app/models/safety.py`, merge unique logic, archive after merge |
| class_.py                   | Merge/Review  | Compare with `app/models/class_.py`, merge unique logic, archive after merge |
| fitness_goals.py            | Move          | If not in `app/models/`, move it                   |
| exercise.py                 | Merge/Review  | Compare with `app/models/exercise.py`, merge unique logic, archive after merge |
| health_metrics.py           | Move          | If not in `app/models/`, move it                   |
| routine.py                  | Merge/Review  | Compare with `app/models/routine.py`, merge unique logic, archive after merge |
| generate_models.py          | Review/Archive| If utility, archive or move as needed              |
| class_types.py              | Merge         | Merge enums/types into `app/models/types.py`        |
| routine_performance_models.py| Merge/Review | Compare with `app/models/routine_performance.py`, merge unique logic, archive after merge |
| __init__.py                 | Archive       | Archive after merge                                |
| .DS_Store                   | Delete        | Not needed                                         |

### **C. `app/dashboard/models/`**
| File                | Action        | Notes/Instructions                                 |
|---------------------|--------------|----------------------------------------------------|
| api_key.py          | Move          | If not in `app/models/`, move it                   |
| security.py         | Merge/Review  | Compare with `app/models/security.py`, merge unique logic, archive after merge |
| user_models.py      | Move          | If not in `app/models/`, move it                   |
| gpt_models.py       | Move          | If not in `app/models/`, move it                   |
| dashboard_models.py | Move          | If not in `app/models/`, move it                   |
| resource_models.py  | Move          | If not in `app/models/`, move it                   |
| notification_models.py| Move        | If not in `app/models/`, move it                   |
| organization_models.py| Move        | If not in `app/models/`, move it                   |
| project.py          | Move          | If not in `app/models/`, move it                   |
| feedback.py         | Move          | If not in `app/models/`, move it                   |
| dashboard.py        | Move          | If not in `app/models/`, move it                   |
| access_control.py   | Move          | If not in `app/models/`, move it                   |
| user_preferences.py | Move          | If not in `app/models/`, move it                   |
| tool_registry.py    | Move          | If not in `app/models/`, move it                   |
| context.py          | Move          | If not in `app/models/`, move it                   |
| context_models.py   | Move          | If not in `app/models/`, move it                   |
| __init__.py         | Archive       | Archive after merge                                |
| __pycache__/        | Delete        | Not needed                                         |

---

## **Stepwise Progress Tracking**

### **Completed**
- [x] Merged enums from `models/physical_education/types.py` into `app/models/types.py`
- [x] Updated `app/models/__init__.py` to import all enums
- [x] Created backup and removed legacy `types.py`
- [x] Compared and confirmed `base.py` in `app/models/` is canonical
- [x] Migrated all legacy physical education models
- [x] Migrated all service-specific models except generate_models.py, class_types.py, and routine_performance_models.py

### **In Progress**
- [x] Merged class_types.py into app/models/types.py
- [x] Merged routine_performance_models.py into app/models/routine_performance.py
- [x] Moved generate_models.py to app/models/utils/generate_models.py
- [ ] Review and consolidate dashboard models in app/dashboard/models/

### **Next Steps**
1. **Service-Specific/Legacy Models**
   - [ ] Complete remaining migrations for `generate_models.py`, `class_types.py`, and `routine_performance_models.py`
2. **Dashboard Models**
   - [ ] Move/merge as per table above
3. **Update Imports**
   - [ ] Update all import paths to use `app.models`
4. **Testing and Verification**
   - [ ] Ensure all models are imported in `app/models/__init__.py`
   - [ ] Run Alembic autogenerate and all tests
5. **Archive/Delete Old Files**
   - [ ] Archive or delete all old model files/directories after confirming everything works

---

## **Rules and Workflow**

- Always check the current working directory first
- Use absolute paths from the workspace root
- Verify file existence before creating, moving, or deleting files
- Move slowly and deliberately, one action at a time
- Wait for explicit user approval before each action
- Never create or edit files outside `Faraday-AI/app/models/`
- Never remove packages, dependencies, or requirements without approval
- Never overwrite or delete files without backup and user confirmation

---

## **Current Step**

- Preparing to review and merge `safety.py` from legacy to canonical location.

---

> **This document should be updated after each major step or decision.** 