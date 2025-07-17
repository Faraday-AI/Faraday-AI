# Database Tables, Roles, and Relationships

## Core User System

### `users`
- **Role**: Core user account management
- **Key Fields**:
  - `id` (UUID, primary key)
  - `email` (unique, indexed)
  - `password_hash`
  - `first_name`, `last_name`
  - `is_teacher`, `is_active`
  - `school`, `department`
  - `subjects`, `grade_levels` (JSONB)
  - Timestamps: `created_at`, `updated_at`, `last_login`
- **Relationships**:
  - → `user_preferences` (one-to-one)
  - → `user_memories` (one-to-many)
  - → `memory_interactions` (one-to-many)

### `user_preferences`
- **Role**: User-specific settings and preferences
- **Key Fields**:
  - `user_id` (UUID FK to users)
  - `theme`
  - `notifications` (JSON)
  - `language`
  - `timezone`
- **Relationships**:
  - → `users` (many-to-one)

## Assistant System

### `assistant_profiles`
- **Role**: GPT assistant configuration and management
- **Key Fields**:
  - `id` (Integer PK)
  - `name`, `description`
  - `model_version`
  - `configuration` (JSONB)
  - `is_active`
  - GPT parameters (temperature, context length, etc.)
- **Relationships**:
  - → `subject_categories` (many-to-many via subject_assistant)
  - → `lessons` (one-to-many)
  - → `assistant_capabilities` (one-to-many)
  - → `user_memories` (one-to-many)

### `assistant_capabilities`
- **Role**: Specific abilities of each GPT assistant
- **Key Fields**:
  - `name`, `description`
  - `assistant_profile_id` (FK)
  - `parameters` (JSONB)
  - `is_enabled`
  - `priority`
- **Relationships**:
  - → `assistant_profiles` (many-to-one)

### `subject_categories`
- **Role**: Subject area organization
- **Key Fields**:
  - `name` (unique)
  - `description`
  - `level`, `path` (hierarchical structure)
  - `category_data` (JSONB)
- **Relationships**:
  - → `assistant_profiles` (many-to-many via subject_assistant)
  - → `lessons` (one-to-many)

## Memory System

### `user_memories`
- **Role**: Stores user-specific memory data for GPT assistants
- **Key Fields**:
  - `user_id` (FK to users)
  - `assistant_profile_id` (FK)
  - `content` (Text)
  - `context` (JSON)
  - `importance` (Float)
  - `category`, `tags`
  - `source`, `confidence`
- **Relationships**:
  - → `users` (many-to-one)
  - → `assistant_profiles` (many-to-one)
  - → `memory_interactions` (one-to-many)

### `memory_interactions`
- **Role**: Tracks memory usage and updates
- **Key Fields**:
  - `memory_id` (FK)
  - `user_id` (FK)
  - `interaction_type`
  - `context`, `feedback` (JSON)
- **Relationships**:
  - → `user_memories` (many-to-one)
  - → `users` (many-to-one)

## Education System

### `lessons`
- **Role**: Educational content management
- **Key Fields**:
  - `user_id` (FK)
  - `subject_category_id` (FK)
  - `assistant_profile_id` (FK)
  - `title`, `description`
  - `content`, `metadata` (JSONB)
- **Relationships**:
  - → `users` (many-to-one)
  - → `subject_categories` (many-to-one)
  - → `assistant_profiles` (many-to-one)

## Physical Education System

### Activity Planning

#### `activity_plans`
- **Role**: Manages personalized activity plans for students
- **Key Fields**:
  - `student_id`, `class_id` (FKs)
  - `name`, `description`
  - `start_date`, `end_date`
  - `status` (draft/active/completed/cancelled)
  - `objectives`, `assessment_criteria` (JSONB)
  - `adaptations`, `progress_tracking` (JSONB)
  - `notes`
- **Relationships**:
  - → `students` (many-to-one)
  - → `classes` (many-to-one)
  - → `activity_plan_activities` (one-to-many)

#### `activity_plan_activities`
- **Role**: Links specific activities to activity plans
- **Key Fields**:
  - `plan_id`, `activity_id` (FKs)
  - `scheduled_date`
  - `status` (scheduled/completed/cancelled/skipped)
- **Relationships**:
  - → `activity_plans` (many-to-one)
  - → `activities` (many-to-one)

### Activity Categories

#### `activity_categories`
- **Role**: Categorizes physical activities
- **Key Fields**:
  - `name`
  - `description`
  - `parent_id` (FK, for hierarchical categories)
  - `metadata` (JSONB)
- **Relationships**:
  - → `activities` (many-to-many via activity_category_associations)

#### `activity_category_associations`
- **Role**: Links activities with their categories
- **Key Fields**:
  - `activity_id`, `category_id` (FKs)
  - `primary_category` (Boolean)
- **Relationships**:
  - → `activities` (many-to-one)
  - → `activity_categories` (many-to-one)

### Activities and Exercises

#### `activities`
- **Role**: Physical activities definition
- **Key Fields**:
  - `name` (1-100 chars, non-empty)
  - `description` (max 500 chars)
  - `activity_type` (Enum)
  - `difficulty` (Enum: beginner/intermediate/advanced)
  - `equipment_required` (Enum)
  - `duration_minutes` (1-240 minutes)
  - `instructions`, `safety_guidelines`
  - `variations`, `benefits`
  - `activity_metadata` (JSON)
- **Relationships**:
  - → `routines` (many-to-many via routine_activities)
  - → `risk_assessments` (one-to-many)
  - → `safety_incidents` (one-to-many)
  - → `activity_performances` (one-to-many)
  - → `progressions` (one-to-many)
  - → `plan_activities` (one-to-many)
  - → `exercises` (one-to-many)
  - → `movement_analyses` (one-to-many)
  - → `skill_assessments` (one-to-many)
  - → `activity_adaptations` (one-to-many)
  - → `skill_progress` (one-to-many)
  - → `categories` (many-to-many via activity_category_associations)

#### `activity_adaptations`
- **Role**: Manages customized activity modifications for students
- **Key Fields**:
  - `student_id`, `activity_id` (FKs)
  - `adaptation_type` (intensity/duration/equipment/technique/progression)
  - `adaptation_data` (JSONB)
  - `difficulty_adjustment` (Float, -1.0 to 1.0)
  - `is_active` (Boolean)
  - `start_date`, `end_date`
- **Relationships**:
  - → `students` (many-to-one)
  - → `activities` (many-to-one)
  - → `adaptation_history` (one-to-many)

#### `adaptation_history`
- **Role**: Tracks changes in activity adaptations
- **Key Fields**:
  - `adaptation_id` (FK)
  - `change_type` (created/modified/activated/deactivated)
  - `previous_data`, `new_data` (JSONB)
  - `reason` (Text)
  - `effectiveness_score` (Float, 0.0 to 1.0)
- **Relationships**:
  - → `activity_adaptations` (many-to-one)

#### `exercises`
- **Role**: Exercise definitions
- **Key Fields**:
  - `name`, `description`
  - `type`, `difficulty`
  - `instructions`
- **Relationships**:
  - → `routines` (many-to-many via routine_activities)

### Student Management

#### `students`
- **Role**: Student information
- **Key Fields**:
  - `first_name`, `last_name` (1-50 chars, non-empty)
  - `email` (unique, valid email format)
  - `date_of_birth` (must be 5-18 years old)
  - `gender` (Enum: male/female/other)
  - `fitness_level` (Enum: beginner/intermediate/advanced/elite)
  - `medical_notes` (max 500 chars)
- **Relationships**:
  - → `classes` (many-to-many via class_students)
  - → `skill_progress` (one-to-many)
  - → `safety_incidents` (one-to-many)
  - → `activity_performances` (one-to-many)
  - → `activity_preferences` (one-to-many)
  - → `activity_progressions` (one-to-many)
  - → `activity_plans` (one-to-many)
  - → `movement_analyses` (one-to-many)
  - → `skill_assessments` (one-to-many)
  - → `routine_performances` (one-to-many)
  - → `activity_adaptations` (one-to-many)
- **Cascade Behavior**: All child records are deleted when student is deleted

#### `classes`
- **Role**: Class organization
- **Key Fields**:
  - `name`
  - `schedule`
  - `capacity`
- **Relationships**:
  - → `students` (many-to-many via class_students)
  - → `routines` (one-to-many)

### Performance Tracking

#### `skill_assessments`
- **Role**: Student skill evaluation
- **Key Fields**:
  - `student_id` (FK)
  - `activity_id` (FK)
  - `overall_score`
  - `assessment_date`
- **Relationships**:
  - → `students` (many-to-one)
  - → `activities` (many-to-one)
  - → `assessment_results` (one-to-many)

#### `skill_progress`
- **Role**: Progress tracking
- **Key Fields**:
  - `student_id` (FK)
  - `activity_id` (FK)
  - `skill_level`
  - `progress_data` (JSONB)
  - `goals` (JSONB)
- **Relationships**:
  - → `students` (many-to-one)
  - → `activities` (many-to-one)

#### `routine_performance`
- **Role**: Records student performance in routines
- **Key Fields**:
  - `routine_id`, `student_id` (FKs)
  - `performance_data` (JSON)
  - `completion_time` (Float)
  - `accuracy_score`, `effort_score` (Float)
  - `notes` (Text)
  - `is_completed` (Boolean)
- **Relationships**:
  - → `routines` (many-to-one)
  - → `students` (many-to-one)
  - → `performance_metrics` (one-to-many)

#### `performance_metrics`
- **Role**: Stores detailed performance measurements
- **Key Fields**:
  - `performance_id` (FK)
  - `metric_type`
  - `metric_value` (Float)
  - `metric_data` (JSON)
- **Relationships**:
  - → `routine_performance` (many-to-one)

### Safety Management

#### `safety_checks`
- **Role**: Safety verification records
- **Key Fields**:
  - `check_type`
  - `status`
  - `notes`
  - `completed_at`
- **Additional Fields**:
  - `location`
  - `inspector_id` (FK to users)
  - `severity_level`
  - `action_required` (Boolean)
  - `follow_up_date`

#### `equipment_checks`
- **Role**: Equipment status tracking
- **Key Fields**:
  - `equipment_type`
  - `condition`
  - `last_maintenance`
  - `next_maintenance`
- **Additional Fields**:
  - `inspector_id` (FK to users)
  - `maintenance_history` (JSONB)
  - `replacement_date`
  - `safety_rating` (Float)

#### `risk_assessments`
- **Role**: Risk evaluation records
- **Key Fields**:
  - `activity_id` (FK)
  - `risk_level`
  - `mitigation_measures`
  - `assessment_date`
- **Additional Fields**:
  - `assessor_id` (FK to users)
  - `risk_factors` (JSONB)
  - `probability` (Float)
  - `impact` (Float)
  - `review_date`
- **Relationships**:
  - → `activities` (many-to-one)
  - → `users` (many-to-one)

#### `safety_incidents`
- **Role**: Records and tracks safety-related incidents
- **Key Fields**:
  - `student_id`, `activity_id` (FKs)
  - `date`
  - `incident_type`, `severity` (required)
  - `description`, `action_taken` (required)
  - `incident_metadata` (JSON)
- **Relationships**:
  - → `students` (many-to-one)
  - → `activities` (many-to-one)
- **Constraints**: All fields except metadata must be non-null

#### `environmental_checks`
- **Role**: Monitors environmental safety conditions
- **Key Fields**:
  - `class_id` (FK)
  - `check_date`
  - `temperature`, `humidity`, `air_quality` (Float)
  - `surface_conditions` (JSON)
  - `lighting` (Float)
  - `equipment_condition` (JSON)
  - `environmental_metadata` (JSON)
- **Relationships**:
  - → `classes` (many-to-one)

### Movement Analysis

#### `movement_analysis`
- **Role**: Movement data analysis
- **Key Fields**:
  - `student_id` (FK)
  - `activity_id` (FK)
  - `analysis_data` (JSONB)
  - `recommendations`

#### `movement_patterns`
- **Role**: Movement pattern recognition
- **Key Fields**:
  - `pattern_type`
  - `description`
  - `metrics` (JSONB)

## Junction Tables

### `subject_assistant`
- **Role**: Links subjects with assistant profiles
- **Fields**:
  - `subject_category_id` (FK)
  - `assistant_profile_id` (FK)

### `class_students`
- **Role**: Links students with classes
- **Fields**:
  - `class_id` (FK)
  - `student_id` (FK)
  - `enrollment_date`

### `routine_activities`
- **Role**: Links routines with activities
- **Fields**:
  - `routine_id` (FK)
  - `activity_id` (FK)
  - `sequence_order`
  - `duration`

### Additional Junction Tables

#### `student_activity_performances`
- **Role**: Records individual student performances in activities
- **Fields**:
  - `student_id`, `activity_id` (FKs)
  - `performance_date`
  - `score`
  - `feedback` (JSONB)

#### `student_activity_preferences`
- **Role**: Tracks student activity preferences
- **Key Fields**:
  - `student_id` (FK)
  - `activity_type` (Enum: WARM_UP/SKILL_DEVELOPMENT/FITNESS_TRAINING/GAME/COOL_DOWN)
  - `preference_score` (Float, default 0.5)
  - `last_updated`

#### `activity_progressions`
- **Role**: Defines progression paths between activities
- **Fields**:
  - `from_activity_id`, `to_activity_id` (FKs)
  - `progression_type`
  - `requirements` (JSONB)
  - `difficulty_increase` (Float)

#### `pe_activity_preferences`
- Purpose: Tracks student preferences for specific physical education activities
- Relationships:
  - Belongs to: students, activities
  - Fields: preference_score, preference_level, notes, metadata

#### `adaptation_activity_preferences`
- Purpose: Tracks student preferences for activity types in adaptation system
- Relationships:
  - Belongs to: students
  - Fields: activity_type, preference_score

### Additional Notes

#### Cascade Behaviors
- Most parent-child relationships include `cascade="all, delete-orphan"` for automatic cleanup
- Foreign keys typically include `ondelete="CASCADE"` for referential integrity
- Hierarchical relationships (e.g., AssessmentCriteria) use self-referential cascades

#### Validation Rules
- Names and descriptions cannot be empty or whitespace
- Email addresses must be in valid format
- Numeric scores typically range from 0.0 to 1.0
- Dates include various business rules (e.g., end_date >= start_date)

**Activity-Specific Rules**:
- Duration must be between 1-240 minutes
- Equipment requirements must be one of: none/minimal/moderate/extensive
- Activity types must be: warm_up/skill_development/fitness_training/game/cool_down
- Difficulty levels: beginner/intermediate/advanced

**Assessment Rules**:
- Overall scores must be between 0.0 and 100.0
- Assessment status must be: pending/in_progress/completed/archived
- Criteria weights must sum to 1.0
- Min scores must be less than max scores
- Change types must be: created/updated/completed/archived

**Progress Tracking**:
- Skill levels must be: beginner/intermediate/advanced/expert
- Progression levels include an additional 'master' level
- Improvement rates must be non-negative

**Routine-Specific Rules**:
- Status transitions must follow: draft → scheduled → in_progress → completed/cancelled
- Activity types within routines must be: warm_up/main/cool_down
- Activities must have a valid sequence order (no gaps or duplicates)
- Duration must be specified for timed activities

**Movement Analysis Rules**:
- Confidence scores must be between 0.0 and 1.0
- Pattern types must be predefined (e.g., "jumping", "running", "throwing")
- Quality scores must be between 0.0 and 1.0
- Repetitions must be non-negative integers
- Duration must be positive float (seconds)

**Activity Plan Rules**:
- Plan status must be: draft/active/completed/cancelled
- End date must be greater than or equal to start date
- Plan activities status must be: scheduled/completed/cancelled/skipped
- Objectives and assessment criteria are required
- Activity dates must fall within plan date range

**Class Management Rules**:
- Class names must be 1-100 characters, non-empty
- Maximum 50 students per class
- End date must be after start date
- Class status transitions: planned → active → completed
- Student enrollment status must be tracked
- Grade level is required

**Category Organization Rules**:
- Category names must be unique
- Self-referential parent-child relationships allowed
- Categories can be primary or secondary for activities
- Hierarchical depth is unlimited but practical
- Category metadata must be valid JSON

#### JSON/JSONB Structures

**Assessment Criteria Rubric**:
```json
{
  "criteria": {
    "technique": {
      "weight": 0.4,
      "sub_criteria": {
        "form": 0.5,
        "accuracy": 0.5
      }
    },
    "performance": {
      "weight": 0.6,
      "sub_criteria": {
        "speed": 0.3,
        "consistency": 0.7
      }
    }
  }
}
```

**Activity Metadata**:
```json
{
  "prerequisites": ["basic_balance", "core_strength"],
  "progression_path": ["beginner", "intermediate", "advanced"],
  "equipment_details": {
    "required": ["mat", "cones"],
    "optional": ["weights"]
  },
  "safety_considerations": [
    "clear_space_needed",
    "proper_footwear_required"
  ]
}
```

**Progress Data**:
```json
{
  "metrics": {
    "accuracy": 0.85,
    "speed": 0.70,
    "endurance": 0.65
  },
  "milestones_achieved": [
    "basic_form_mastered",
    "intermediate_speed_reached"
  ],
  "areas_for_improvement": [
    "advanced_techniques",
    "consistency"
  ]
}
```

**Movement Analysis Data**:
```json
{
  "movement_data": {
    "landmarks": {
      "pose_landmarks": [...],
      "world_landmarks": [...]
    },
    "metrics": {
      "smoothness": 0.85,
      "consistency": 0.78,
      "speed": 0.92,
      "range_of_motion": 0.88
    }
  },
  "analysis_results": {
    "movement_type": "jumping",
    "quality_score": 0.82,
    "issues_detected": [
      {
        "type": "knee_alignment",
        "severity": "moderate",
        "recommendation": "Focus on keeping knees aligned with toes"
      }
    ],
    "recommendations": [
      "Increase jump height gradually",
      "Maintain consistent landing pattern"
    ]
  }
}
```

**Routine Focus Areas**:
```json
{
  "primary_focus": "cardio",
  "secondary_focus": ["strength", "flexibility"],
  "target_muscle_groups": ["legs", "core"],
  "intensity_distribution": {
    "high": 0.3,
    "medium": 0.5,
    "low": 0.2
  },
  "progression_goals": [
    "increase_duration",
    "add_complexity"
  ]
}
```

**Movement Pattern Data**:
```json
{
  "pattern_data": {
    "sequence": ["preparation", "execution", "follow_through"],
    "key_points": {
      "start_position": {"x": 0.5, "y": 0.8},
      "peak_position": {"x": 0.5, "y": 0.2},
      "end_position": {"x": 0.5, "y": 0.7}
    },
    "velocity_profile": [
      {"time": 0, "velocity": 0},
      {"time": 0.5, "velocity": 2.5},
      {"time": 1.0, "velocity": 0}
    ]
  }
}
```

**Activity Plan Objectives**:
```json
{
  "learning_objectives": [
    {
      "area": "skill_development",
      "target": "master_basic_dribbling",
      "success_criteria": [
        "maintain ball control while walking",
        "change direction without losing control"
      ]
    },
    {
      "area": "fitness",
      "target": "improve_endurance",
      "success_criteria": [
        "complete 20-minute continuous activity",
        "maintain target heart rate"
      ]
    }
  ],
  "priority_levels": {
    "skill_development": "high",
    "fitness": "medium",
    "teamwork": "low"
  }
}
```

**Assessment Criteria**:
```json
{
  "skill_criteria": {
    "technique": {
      "weight": 0.4,
      "minimum_score": 7.0,
      "evaluation_points": [
        "proper form",
        "movement control",
        "body positioning"
      ]
    },
    "performance": {
      "weight": 0.6,
      "minimum_score": 6.5,
      "evaluation_points": [
        "speed",
        "accuracy",
        "consistency"
      ]
    }
  },
  "progress_indicators": [
    "improvement_rate",
    "skill_mastery",
    "effort_level"
  ]
}
```

**Progress Tracking**:
```json
{
  "weekly_metrics": [
    {
      "week": 1,
      "attendance": 0.9,
      "completion_rate": 0.85,
      "skill_improvements": {
        "dribbling": 0.2,
        "shooting": 0.15
      }
    }
  ],
  "achievement_milestones": [
    {
      "milestone": "basic_dribbling",
      "achieved_date": "2025-05-01",
      "proficiency_level": "intermediate"
    }
  ],
  "adaptation_history": [
    {
      "date": "2025-04-15",
      "type": "difficulty_increase",
      "reason": "consistent high performance",
      "details": {
        "from_level": "beginner",
        "to_level": "intermediate"
      }
    }
  ]
}
```

**Class Schedule**:
```json
{
  "weekly_schedule": [
    {
      "day": "monday",
      "time": "14:00",
      "duration_minutes": 45,
      "location": "main_gym",
      "equipment_needed": ["mats", "balls"],
      "setup_time_minutes": 10
    },
    {
      "day": "wednesday",
      "time": "15:30",
      "duration_minutes": 45,
      "location": "outdoor_field",
      "weather_dependent": true,
      "backup_location": "auxiliary_gym"
    }
  ],
  "exceptions": [
    {
      "date": "2025-05-01",
      "reason": "school_holiday",
      "status": "cancelled"
    }
  ],
  "term_breaks": [
    {
      "start_date": "2025-07-01",
      "end_date": "2025-07-15",
      "type": "summer_break"
    }
  ]
}
```

**Category Metadata**:
```json
{
  "display_settings": {
    "color": "#4287f5",
    "icon": "running",
    "order": 1
  },
  "requirements": {
    "minimum_age": 8,
    "prerequisite_categories": ["basic_movement"],
    "equipment_needs": "minimal",
    "space_needs": "large"
  },
  "curriculum_alignment": {
    "standards": ["PE.1.2", "PE.1.3"],
    "learning_outcomes": [
      "body_awareness",
      "spatial_orientation"
    ]
  },
  "safety_considerations": {
    "risk_level": "low",
    "supervision_required": true,
    "certification_needed": false
  }
}
```

#### Relationship Details

**Hierarchical Organizations**:
- Categories form a tree structure with unlimited depth
- Each category can have multiple subcategories
- Activities can belong to multiple categories
- Primary category designation for main classification
- Secondary categories for additional organization

**Class Organization**:
- Classes → Students: Many-to-many with enrollment dates
- Classes → Routines: One-to-many with scheduling
- Classes → Activity Plans: One-to-many with tracking
- Classes → Safety Checks: One-to-many with timestamps

**Enrollment Management**:
- Student enrollment tracked with status and dates
- Class size limits enforced at database level
- Waitlist management through enrollment status
- Historical enrollment data preserved

#### Additional Considerations

**Data Integrity**:
- Foreign key constraints with appropriate ON DELETE actions
- Unique constraints on natural keys
- Check constraints on numeric ranges
- Date range validations
- Status transition validations

**Performance Optimization**:
- Indexes on frequently queried columns
- Composite indexes for common joins
- Partial indexes for filtered queries
- JSONB for flexible but queryable data

**Audit and History**:
- All tables track creation and updates
- Status changes recorded with timestamps
- User actions logged with context
- Historical data preserved for analysis

**Business Rules**:
- Class scheduling respects school calendar
- Activity progression follows curriculum
- Safety checks required before activities
- Assessment criteria linked to standards
- Adaptations based on student needs

**Hierarchical Relationships**:
- Assessment Criteria can have parent-child relationships
- Activity Categories support nested categorization
- Skill Progressions follow defined advancement paths

**Composite Relationships**:
- Activities → Categories: Many-to-many with primary category flag
- Students → Classes: Many-to-many with enrollment dates
- Activities → Routines: Many-to-many with sequence ordering

**Temporal Relationships**:
- Assessment History tracks state changes over time
- Activity Progressions record advancement through levels
- Performance Metrics maintain time-series data

**Dependency Relationships**:
- Activities require specific Equipment Checks
- Assessments depend on defined Criteria
- Adaptations reference base Activities

**Analysis Relationships**:
- Movement Analysis → Movement Patterns: One-to-many with cascade delete
- Movement Analysis → Student: Many-to-one with activity history
- Movement Analysis → Activity: Many-to-one with performance tracking

**Performance Tracking Chains**:
- Student → Activities → Movement Analysis → Patterns
- Student → Routines → Activities → Performance Metrics
- Activity → Adaptations → Progress Tracking

**Temporal Analysis Chains**:
- Movement Analysis tracks patterns over time
- Performance Metrics maintain historical data
- Progress Tracking follows improvement trajectories

**Plan Relationships**:
- Activity Plan → Activities: Many-to-many with scheduling
- Activity Plan → Student: Many-to-one with progress tracking
- Activity Plan → Class: Many-to-one with shared context

**Scheduling Chains**:
- Class → Activity Plans → Scheduled Activities
- Student → Activity Plans → Progress Tracking
- Activity → Plan Activities → Adaptations

#### Common Fields
Most tables include:
- `id` (Integer, primary key, auto-increment)
- `created_at` (DateTime, default=now)
- `updated_at` (DateTime, auto-updates)
- Metadata fields using JSON or JSONB for flexibility
- Status tracking with defined state transitions
- Soft deletion support where appropriate

#### Security Considerations
- Row-Level Security (RLS) policies on sensitive tables
- Audit trails for critical operations
- Cascading deletes controlled by foreign key constraints
- Data validation at both database and application levels

#### Technical Implementation Details

**Database Constraints**:
- **Unique Constraints**:
  - User email addresses
  - Category names
  - Activity-student combinations in performance records
  - Class-student enrollment pairs
  
- **Check Constraints**:
  - Score ranges (0.0 to 1.0 or 0.0 to 100.0)
  - Valid status transitions
  - Date range validations
  - Numeric value boundaries

- **Foreign Key Actions**:
  - `ON DELETE CASCADE` for dependent records
  - `ON DELETE SET NULL` for optional relationships
  - `ON UPDATE CASCADE` for key propagation

**Index Strategy**:
- **Primary Indexes**:
  - All primary keys are btree indexed
  - UUID columns use specialized indexes
  - Timestamp columns for temporal queries

- **Secondary Indexes**:
  - Foreign key columns
  - Frequently filtered status columns
  - Search fields (name, email)
  - Range query columns (dates, scores)

- **Composite Indexes**:
  - (student_id, activity_id) for performance queries
  - (class_id, date) for schedule lookups
  - (user_id, created_at) for timeline views

**JSONB Optimization**:
- **GIN Indexes** on:
  - Activity metadata
  - Assessment criteria
  - Progress tracking data
  - Movement analysis results

- **Expression Indexes** for:
  - Common JSON path queries
  - Computed values from JSON
  - Frequently accessed nested fields

**Concurrency Controls**:
- Row-level locking for updates
- Optimistic locking with version columns
- Transaction isolation levels defined
- Deadlock prevention strategies

**Partitioning Strategy**:
- Time-based partitioning for:
  - Performance metrics
  - Movement analysis data
  - Safety incident records
  - Activity logs

- Range partitioning for:
  - Historical records
  - Archive data
  - Large result sets

**Query Optimization**:
- Materialized views for complex reports
- Function-based indexes for computations
- Statistics gathering strategies
- Query plan management

**Data Lifecycle**:
- Archival strategy for old records
- Cleanup procedures for temporary data
- Data retention policies
- Backup and recovery procedures

**Error Handling**:
- Custom exception types
- Error logging and tracking
- Retry mechanisms
- Fallback procedures

**Security Implementation**:
- Row-level security policies
- Column-level encryption
- Audit logging triggers
- Access control functions

This completes the comprehensive documentation of the database structure, relationships, and implementation details. 