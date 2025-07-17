# Model Standardization Plan

## Current State Analysis
- 35 files use `Base` from `app.db.base_class`
- 2 files use `BaseModel` from `.base`
- Some files mix both patterns

## Enum Standardization
### Current State
- Core enums defined in `app/models/core/core_models.py` (previously `types.py`)
- Additional enums scattered across various modules
- Some enums duplicated in different locations
- Mix of string and integer-based enums

### Enum Categories
1. Activity Related
   - ActivityType
   - ActivityCategoryType
   - DifficultyLevel
   - ProgressionLevel
   - EquipmentRequirement

2. Student Related
   - StudentType
   - Gender
   - FitnessLevel
   - GradeLevel
   - Subject

3. Assessment Related
   - AssessmentType
   - AssessmentStatus
   - AssessmentLevel
   - AssessmentTrigger
   - CriteriaType

4. Safety Related
   - SafetyType
   - IncidentType
   - IncidentSeverity
   - AlertType
   - CheckType
   - RiskLevel

5. Equipment Related
   - EquipmentType
   - EquipmentStatus
   - EquipmentRequirement

6. Movement Related
   - MovementType
   - ExerciseType
   - ExerciseDifficulty
   - WorkoutType

7. Analysis Related
   - AnalysisType
   - AnalysisStatus
   - ConfidenceLevel
   - PerformanceLevel
   - VisualizationType
   - ChartType

8. Collaboration Related
   - CollaborationType
   - AccessLevel
   - SharingStatus
   - NotificationType

9. Adaptation Related
   - AdaptationType
   - AdaptationLevel
   - AdaptationStatus
   - AdaptationTrigger

10. Security Related
    - SecurityLevel
    - SecurityStatus
    - SecurityAction
    - SecurityTrigger
    - RateLimitType
    - RateLimitLevel
    - RateLimitStatus
    - RateLimitTrigger

11. Cache Related
    - CacheType
    - CacheLevel
    - CacheStatus
    - CacheTrigger

12. Circuit Breaker Related
    - CircuitBreakerType
    - CircuitBreakerLevel
    - CircuitBreakerStatus
    - CircuitBreakerTrigger

### Standardization Tasks
1. Consolidate Enums ✅
   - [x] Move all enums to `core_models.py`
   - [x] Remove duplicate enums
   - [x] Standardize naming conventions
   - [x] Add proper documentation

2. Update Import Patterns ✅
   - [x] Update all imports to use `core_models.py`
   - [x] Remove local enum definitions
   - [x] Verify all enum usages

3. Documentation 🔄
   - [ ] Document all enum values and purposes
   - [ ] Add usage examples
   - [ ] Create migration guide for enum changes

4. Testing 🔄
   - [ ] Add unit tests for enum values
   - [ ] Verify enum compatibility
   - [ ] Test enum serialization/deserialization

## Model Categories
1. Core Models
   - activity.py
   - student.py
   - routine.py
   - class_.py
   - teacher.py

2. Feature Models
   - curriculum.py
   - safety.py
   - assessment.py
   - progress_tracking.py
   - goal_setting.py

3. Supporting Models
   - health.py
   - movement_analysis.py
   - environmental.py
   - competition.py
   - injury_prevention.py
   - load_balancer.py

4. Additional Categories
   - activity_adaptation/
   - context/
   - competition/
   - movement_analysis/
   - utils/
   - resource_management/
   - organization/
   - ml/
   - health_fitness/
   - gpt/
   - feedback/
   - environmental/
   - dashboard/
   - security/
   - educational/
   - user_management/
   - system/
   - skill_assessment/

## Standardization Status by Category
### Core Models ✅
- All models use `Base` from `app.db.base_class`
- Import patterns standardized
- Relationships properly defined
- Enums consolidated in `core_models.py`

### Feature Models ✅
- All models use `Base` from `app.db.base_class`
- Import patterns standardized
- Relationships properly defined
- Enums consolidated in `core_models.py`

### Supporting Models ✅
- All models use `Base` from `app.db.base_class`
- Import patterns standardized
- Relationships properly defined
- Enums consolidated in `core_models.py`

### Additional Categories
#### Dashboard Models 🔄
- Uses `Base` from `app.db.base_class`
- Needs standardization review
- Complex widget and theme relationships
- Specific Tasks:
  - [ ] Review widget inheritance patterns
  - [ ] Standardize theme model relationships
  - [ ] Update filter model imports
  - [ ] Verify sharing model constraints

#### Security Models 🔄
- Uses `Base` from `app.db.base_class`
- Needs standardization review
- Complex access control and policy relationships
- Specific Tasks:
  - [ ] Review access control inheritance
  - [ ] Standardize policy model relationships
  - [ ] Update API key model imports
  - [ ] Verify session model constraints
  - [x] Standardize security preferences table naming

#### Educational Models 🔄
- Uses `Base` from `app.db.base_class`
- Needs standardization review
- Curriculum and assessment relationships
- Specific Tasks:
  - [ ] Review base model inheritance
  - [ ] Standardize curriculum relationships
  - [ ] Update classroom model imports
  - [ ] Verify staff model constraints

#### User Management Models 🔄
- Uses `Base` from `app.db.base_class`
- Needs standardization review
- User preferences and avatar relationships
- Specific Tasks:
  - [x] Review user model inheritance
  - [x] Standardize preferences relationships
  - [x] Update avatar model imports
  - [ ] Verify user model constraints
  - [x] Standardize user management preferences table naming
  - [x] Standardize voice preferences table naming

#### Preference Models ✅
- Uses `Base` from `app.db.base_class`
- Standardized naming pattern with domain prefixes
- Specific Tasks:
  - [x] Standardize physical education preferences (`pe_activity_preferences`)
  - [x] Standardize activity adaptation preferences (`adaptation_activity_preferences`)
  - [x] Standardize user management preferences (`user_management_preferences`)
  - [x] Standardize notification preferences (`context_notification_preferences`)
  - [x] Standardize voice preferences (`user_management_voice_preferences`)
  - [x] Standardize security preferences (`security_preferences`)

##### Preference Model Details

###### Physical Education Preferences (`pe_activity_preferences`)
- **Purpose**: Tracks student preferences for specific physical education activities
- **Relationships**:
  - Belongs to: students, activities
  - Fields: preference_score, preference_level, notes, metadata
- **Validation Rules**:
  - preference_score: Float between 0.0 and 1.0
  - preference_level: Integer between 1 and 5
  - activity_id: Must reference valid activity
  - student_id: Must reference valid student
- **Implementation**:
  - Uses `Base` from `app.db.base_class`
  - Includes `BaseModelMixin` and `TimestampMixin`
  - JSON fields for metadata and notes

###### Activity Adaptation Preferences (`adaptation_activity_preferences`)
- **Purpose**: Tracks student preferences for activity types in adaptation system
- **Relationships**:
  - Belongs to: students
  - Fields: activity_type, preference_score
- **Validation Rules**:
  - activity_type: Must be valid PreferenceActivityType enum
  - preference_score: Float between 0.0 and 1.0
  - student_id: Must reference valid student
- **Implementation**:
  - Uses `BaseModel` and `TimestampedMixin`
  - Includes `__table_args__ = {'extend_existing': True}`

###### User Management Preferences (`user_management_preferences`)
- **Purpose**: Manages user-specific settings and preferences
- **Relationships**:
  - Belongs to: users
  - Fields: theme, layout, notifications, language, accessibility
- **Validation Rules**:
  - theme: Must be one of ["light", "dark", "system"]
  - font_size: Must be one of ["small", "medium", "large"]
  - language: Must be valid ISO language code
  - timezone: Must be valid timezone string
- **Implementation**:
  - Uses `Base` from `app.db.base_class`
  - Includes `BaseModelMixin` and `TimestampMixin`
  - JSON fields for layout and custom settings

###### Notification Preferences (`context_notification_preferences`)
- **Purpose**: Manages user notification settings
- **Relationships**:
  - Belongs to: users
  - Fields: channel, type, priority_threshold, quiet_hours
- **Validation Rules**:
  - channel: Must be valid NotificationChannel enum
  - type: Must be valid NotificationType enum
  - priority_threshold: Must be valid NotificationPriority enum
  - quiet_hours: Must be valid time format
- **Implementation**:
  - Uses `BaseModel` and `StatusMixin`
  - Includes `MetadataMixin` for additional data

###### Voice Preferences (`user_management_voice_preferences`)
- **Purpose**: Manages avatar voice settings
- **Relationships**:
  - Belongs to: users, avatars
  - Fields: voice_id, language, speed, pitch, provider
- **Validation Rules**:
  - speed: Integer between 50 and 200
  - pitch: Integer between 50 and 200
  - provider: Must be valid VoiceProvider enum
  - language: Must be valid language code
- **Implementation**:
  - Uses `Base` from `app.db.base_class`
  - Includes `BaseModel` and `MetadataMixin`
  - Timestamps for created_at and updated_at

###### Security Preferences (`security_preferences`)
- **Purpose**: Manages security-related user settings
- **Relationships**:
  - Belongs to: users
  - Fields: data_sharing, analytics_opt_in, backup_settings
- **Validation Rules**:
  - data_sharing: Boolean
  - analytics_opt_in: Boolean
  - backup_frequency: Must be one of ["daily", "weekly", "monthly"]
- **Implementation**:
  - Uses `BaseModel` and `StatusMixin`
  - Includes comprehensive settings for security features

##### Common Preference Model Features
1. **Base Classes**:
   - All models use appropriate base classes
   - Mixins for common functionality
   - Timestamp tracking

2. **Validation**:
   - Type checking for all fields
   - Range validation for numeric values
   - Enum validation for constrained choices
   - Foreign key validation

3. **Relationships**:
   - Clear parent-child relationships
   - Proper cascade behavior
   - Bidirectional relationships where needed

4. **Metadata**:
   - JSON fields for flexible data
   - Timestamps for tracking changes
   - Status tracking where applicable

5. **Security**:
   - Row-level security policies
   - Access control integration
   - Audit logging

##### Preference Model Best Practices
1. **Naming Convention**:
   - Use domain prefix for table names
   - Clear, descriptive field names
   - Consistent naming patterns

2. **Data Types**:
   - Use appropriate SQL types
   - JSON for flexible data
   - Enums for constrained choices

3. **Indexing**:
   - Index foreign keys
   - Index frequently queried fields
   - Consider composite indexes

4. **Documentation**:
   - Clear purpose statements
   - Field descriptions
   - Relationship documentation
   - Validation rules

5. **Testing**:
   - Unit tests for validation
   - Integration tests for relationships
   - Performance testing for queries

#### Other Categories ⏳
- Status pending review
- Need to verify inheritance patterns
- Need to check relationship definitions
- Specific Tasks:
  - [ ] Review context models
  - [ ] Review feedback models
  - [ ] Review GPT models
  - [ ] Review ML models
  - [ ] Review organization models
  - [ ] Review skill assessment models
  - [ ] Review system models

## Detailed Standardization Plan
### Phase 1: Analysis and Preparation ✅
- [x] Identify current state
- [x] Document required changes
- [x] Create standardization plan

### Phase 2: Implementation Plan
#### Step 1: Update Base Classes ✅
- [x] Update base.py to use correct inheritance
- [x] Standardize imports

#### Step 2: Update Model Files ✅
##### First Batch (Core Models)
- [x] activity.py
- [x] student.py
- [x] routine.py
- [x] class_.py
- [x] teacher.py

##### Second Batch (Feature Models)
- [x] curriculum.py
- [x] safety.py
- [x] assessment.py
- [x] progress_tracking.py
- [x] goal_setting.py

##### Third Batch (Supporting Models)
- [x] health.py
- [x] movement_analysis.py
- [x] environmental.py
- [x] competition.py
- [x] injury_prevention.py
- [x] load_balancer.py

#### Step 3: Standardize Import Pattern ✅
- [x] Update all model files to use consistent import pattern
  - [x] activity.py
  - [x] student.py
  - [x] routine.py
  - [x] class_.py
  - [x] teacher.py
  - [x] curriculum.py
  - [x] safety.py
  - [x] assessment.py
  - [x] progress_tracking.py
  - [x] goal_setting.py
  - [x] health.py
  - [x] movement_analysis.py
  - [x] environmental.py
  - [x] competition.py
  - [x] injury_prevention.py
  - [x] load_balancer.py
- [x] Verify all relationships are properly defined
- [x] Ensure all models use appropriate mixins

### Phase 3: Testing and Validation
- [ ] Unit tests for all models
- [ ] Integration tests for relationships
- [ ] Validation of all constraints
- [ ] Performance testing

### Phase 4: Documentation
- [ ] Update model documentation
- [ ] Create migration guide
- [ ] Document best practices
- [ ] Add relationship diagrams
- [ ] Document inheritance patterns
- [ ] Add usage examples

## Progress Tracking
### Completed Phases
- [x] Phase 1: Analysis and Preparation
- [x] Phase 2, Step 1: Base Classes Update
- [x] Phase 2, Step 2: Model Files Update
- [x] Phase 2, Step 3: Import Pattern Standardization

### In Progress
- 🔄 Phase 3: Testing and Validation
  - Next task: Run test suite
- 🔄 Additional Categories Standardization
  - Next task: Review dashboard models

### Remaining Work
#### Phase 3: Testing and Validation
- [ ] Run test suite
- [ ] Verify all relationships work correctly
- [ ] Check for any remaining inconsistencies
- [ ] Validate model inheritance patterns

#### Phase 4: Documentation
- [ ] Update model documentation
- [ ] Create migration guide
- [ ] Document best practices
- [ ] Add relationship diagrams
- [ ] Document inheritance patterns
- [ ] Add usage examples

#### Additional Categories Standardization
##### Dashboard Models
- [ ] Review widget inheritance patterns
- [ ] Standardize theme model relationships
- [ ] Update filter model imports
- [ ] Verify sharing model constraints

##### Security Models
- [ ] Review access control inheritance
- [ ] Standardize policy model relationships
- [ ] Update API key model imports
- [ ] Verify session model constraints

##### Educational Models
- [ ] Review base model inheritance
- [ ] Standardize curriculum relationships
- [ ] Update classroom model imports
- [ ] Verify staff model constraints

##### User Management Models
- [ ] Review user model inheritance
- [ ] Standardize preferences relationships
- [ ] Update avatar model imports
- [ ] Verify user model constraints

##### Preference Models
- [ ] Review physical education preferences
- [ ] Review activity adaptation preferences
- [ ] Review user management preferences
- [ ] Review notification preferences
- [ ] Review voice preferences
- [ ] Review security preferences

##### Other Categories
- [ ] Review context models
- [ ] Review feedback models
- [ ] Review GPT models
- [ ] Review ML models
- [ ] Review organization models
- [ ] Review skill assessment models
- [ ] Review system models 