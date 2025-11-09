# Phase 1 & Phase 2 Migration and Beta System Integration Plan

## Current Status Analysis

### ❌ Issues Identified

1. **Phase 1 (Safety Service)**:
   - ✅ Implemented in main system (`app/dashboard/services/safety_service.py`)
   - ❌ NOT available in beta system
   - ❌ Creates NEW data only (doesn't migrate existing safety data)

2. **Phase 2 (Assessment System)**:
   - ✅ Implemented in main system (`app/services/physical_education/assessment_system.py`)
   - ❌ NOT available in beta system
   - ❌ Creates NEW data only (doesn't migrate from existing tables)

### 📊 Existing Data Tables That Need Migration

#### Assessment Data Migration:
- **Source Tables:**
  - `general_assessments` (existing assessment records)
  - `general_skill_assessments` (existing skill assessment records)
  - `general_assessment_criteria` (existing criteria results)
  - `general_assessment_history` (existing assessment history)
  - `general_skill_progress` (existing skill progress records)

- **Target Tables:**
  - `skill_assessment_skill_assessments` (new Phase 2 table)
  - `skill_assessment_assessment_criteria` (new Phase 2 table)
  - `skill_assessment_assessment_results` (new Phase 2 table)
  - `skill_assessment_assessment_history` (new Phase 2 table)
  - `skill_progress` (new Phase 2 table)

#### Safety Data Migration:
- **Source Tables:**
  - Existing `safety_protocols` (if any old format data exists)
  - Existing `risk_assessments` (if any old format data exists)
  - Existing `safety_incidents` (if any old format data exists)

- **Target Tables:**
  - `safety_protocols` (Phase 1 table - already using this)
  - `emergency_procedures` (Phase 1 table - new)
  - `risk_assessments` (Phase 1 table - already using this)
  - `safety_incidents` (Phase 1 table - already using this)

---

## Implementation Plan

### Phase 1: Add Data Migration Logic

#### 1.1 Assessment System Migration (`save_student_data()`)
**Location:** `app/services/physical_education/assessment_system.py`

**Add migration method:**
```python
def migrate_existing_assessments(self):
    """Migrate existing assessment data from general_* tables to skill_assessment_* tables."""
    try:
        if not self.db:
            self.db = next(get_db())
        
        # Migrate general_assessments -> skill_assessment_skill_assessments
        from app.models.assessment import GeneralAssessment, SkillAssessment as GeneralSkillAssessment
        
        general_assessments = self.db.query(GeneralAssessment).all()
        for ga in general_assessments:
            # Check if already migrated
            existing = self.db.query(SkillAssessment).filter(
                SkillAssessment.student_id == ga.student_id,
                SkillAssessment.activity_id == ga.activity_id,
                SkillAssessment.assessment_date == ga.created_at
            ).first()
            
            if not existing:
                # Create new SkillAssessment from GeneralAssessment
                skill_assessment = SkillAssessment(
                    student_id=ga.student_id,
                    activity_id=ga.activity_id,
                    assessment_date=ga.created_at,
                    overall_score=ga.score * 100.0 if ga.score else None,
                    assessor_notes=ga.feedback,
                    assessment_metadata={
                        "migrated_from": "general_assessments",
                        "original_id": ga.id,
                        "type": ga.type.value if hasattr(ga.type, 'value') else str(ga.type),
                        "status": ga.status.value if hasattr(ga.status, 'value') else str(ga.status)
                    }
                )
                self.db.add(skill_assessment)
                self.db.flush()
                
                # Migrate associated GeneralSkillAssessment records
                general_skills = self.db.query(GeneralSkillAssessment).filter(
                    GeneralSkillAssessment.assessment_id == ga.id
                ).all()
                
                for gs in general_skills:
                    # Create AssessmentResult for each skill
                    # (logic to map skill_name to criteria)
                    pass
        
        # Migrate general_assessment_history -> skill_assessment_assessment_history
        # Migrate general_skill_progress -> skill_progress
        
        self.db.commit()
        self.logger.info("Assessment data migration completed")
    except Exception as e:
        if self.db:
            self.db.rollback()
        self.logger.error(f"Error migrating assessment data: {str(e)}")
        raise
```

#### 1.2 Safety Service Migration
**Location:** `app/dashboard/services/safety_service.py`

**Add migration method:**
```python
def migrate_existing_safety_data(self):
    """Migrate existing safety data to new Phase 1 structure."""
    # Check for any existing safety data that needs migration
    # Create emergency_procedures from existing safety_protocols if needed
    pass
```

---

### Phase 2: Integrate into Beta System

#### 2.1 Beta Safety Service
**Create:** `app/services/pe/beta_safety_service.py`

```python
"""
Beta Safety Service
Provides safety management for beta teachers (lesson plan safety, resource safety, etc.)
Independent from district-level safety management.
"""

from app.dashboard.services.safety_service import SafetyService
from app.models.teacher_registration import TeacherRegistration

class BetaSafetyService(SafetyService):
    """Safety service for beta teachers."""
    
    def __init__(self, db, teacher_id: int):
        super().__init__(db)
        self.teacher_id = teacher_id
    
    async def get_safety_protocols(self):
        """Get safety protocols for this beta teacher's context."""
        # Filter to teacher's lesson plans/resources only
        protocols = await super().get_safety_protocols()
        # Filter by teacher_id if needed
        return protocols
```

#### 2.2 Beta Assessment System
**Create:** `app/services/pe/beta_assessment_service.py`

```python
"""
Beta Assessment Service
Provides assessment management for beta teachers (assessment templates, rubric building, etc.)
Independent from student-level assessment tracking.
"""

from app.services.physical_education.assessment_system import AssessmentSystem

class BetaAssessmentService:
    """Assessment service for beta teachers - focuses on templates and tools."""
    
    def __init__(self, db, teacher_id: int):
        self.db = db
        self.teacher_id = teacher_id
        # Use assessment templates, not student assessments
    
    async def load_skill_benchmarks(self):
        """Load skill benchmarks for assessment templates."""
        # Similar to AssessmentSystem but for template creation
        pass
```

---

### Phase 3: Update Endpoints

#### 3.1 Beta Safety Endpoints
**Create:** `app/api/v1/endpoints/beta_safety.py`

```python
router = APIRouter(prefix="/beta/safety", tags=["Beta Safety"])

@router.get("/protocols")
async def get_safety_protocols(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get safety protocols for beta teacher."""
    service = BetaSafetyService(db, current_teacher.id)
    return await service.get_safety_protocols()
```

#### 3.2 Beta Assessment Endpoints
**Create:** `app/api/v1/endpoints/beta_assessment.py`

```python
router = APIRouter(prefix="/beta/assessment", tags=["Beta Assessment"])

@router.post("/benchmarks/load")
async def load_benchmarks(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Load skill benchmarks for assessment template creation."""
    service = BetaAssessmentService(db, current_teacher.id)
    return await service.load_skill_benchmarks()
```

---

## Implementation Steps

1. ✅ Add migration logic to `save_student_data()` and `load_skill_benchmarks()`
2. ✅ Create `BetaSafetyService` extending `SafetyService`
3. ✅ Create `BetaAssessmentService` for beta teacher assessment templates
4. ✅ Create beta endpoints for safety and assessment
5. ✅ Add migration script to seed script or run separately
6. ✅ Test migration with existing data
7. ✅ Test beta system integration

---

## Migration Strategy

### Option 1: One-Time Migration Script
- Run once during deployment
- Migrate all existing data
- Mark migrated records

### Option 2: Lazy Migration
- Migrate on-demand when accessing data
- Check if migrated before accessing
- Migrate if not already migrated

### Option 3: Hybrid
- Run one-time migration for bulk data
- Use lazy migration for new/updated records

**Recommendation:** Option 3 (Hybrid) - Best for production readiness

---

## Testing Requirements

1. Test migration from `general_assessments` → `skill_assessment_skill_assessments`
2. Test migration doesn't duplicate data
3. Test beta system can access safety services
4. Test beta system can access assessment services
5. Test main system still works after migration
6. Test rollback if migration fails

