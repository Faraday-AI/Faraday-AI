# Movement Analysis Schema

## Tables

### Movement Analysis Table
```sql
CREATE TABLE movement_analysis (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    activity_id INTEGER REFERENCES activities(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    movement_data JSONB NOT NULL,
    analysis_results JSONB NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    is_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_movement_data CHECK (
        movement_data ? 'key_points' AND 
        movement_data ? 'metrics'
    ),
    CONSTRAINT valid_analysis_results CHECK (
        analysis_results ? 'form_score' AND 
        analysis_results ? 'alignment_score' AND
        analysis_results ? 'stability_score' AND
        analysis_results ? 'recommendations'
    )
);

-- Indexes
CREATE INDEX idx_movement_analysis_student ON movement_analysis(student_id);
CREATE INDEX idx_movement_analysis_activity ON movement_analysis(activity_id);
CREATE INDEX idx_movement_analysis_timestamp ON movement_analysis(timestamp);
CREATE INDEX idx_movement_analysis_confidence ON movement_analysis(confidence_score);
CREATE INDEX idx_movement_analysis_movement_data ON movement_analysis USING GIN (movement_data);
CREATE INDEX idx_movement_analysis_analysis_results ON movement_analysis USING GIN (analysis_results);
```

### Movement Patterns Table
```sql
CREATE TABLE movement_patterns (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES movement_analysis(id),
    pattern_type VARCHAR(50) NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    pattern_data JSONB NOT NULL,
    duration FLOAT,
    repetitions INTEGER NOT NULL,
    quality_score FLOAT CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_pattern_type CHECK (
        pattern_type IN ('jumping', 'running', 'throwing', 'catching')
    ),
    CONSTRAINT valid_pattern_data CHECK (
        pattern_data ? 'sequence' AND 
        pattern_data ? 'metrics'
    )
);

-- Indexes
CREATE INDEX idx_movement_patterns_analysis ON movement_patterns(analysis_id);
CREATE INDEX idx_movement_patterns_type ON movement_patterns(pattern_type);
CREATE INDEX idx_movement_patterns_confidence ON movement_patterns(confidence_score);
CREATE INDEX idx_movement_patterns_pattern_data ON movement_patterns USING GIN (pattern_data);
```

## Data Structure

### Movement Analysis Data
- `movement_data`: JSONB containing:
  - `key_points`: Joint positions and tracking data
  - `metrics`: Movement quality metrics
    - `smoothness`
    - `consistency`
    - `speed`
    - `range_of_motion`

- `analysis_results`: JSONB containing:
  - `form_score`: Overall form quality score
  - `alignment_score`: Body alignment score
  - `stability_score`: Movement stability score
  - `recommendations`: Array of improvement suggestions

### Movement Patterns Data
- `pattern_data`: JSONB containing:
  - `sequence`: Array of movement frames
  - `metrics`: Pattern-specific metrics
    - `average_speed`
    - `peak_force`
    - `efficiency`

## Relationships
- `movement_analysis.student_id` → `students.id`
- `movement_analysis.activity_id` → `activities.id`
- `movement_patterns.analysis_id` → `movement_analysis.id`

## Constraints
1. Movement Analysis:
   - Valid movement data structure
   - Valid analysis results structure
   - Confidence score between 0 and 1
   - Required timestamps

2. Movement Patterns:
   - Valid pattern types
   - Valid pattern data structure
   - Quality score between 0 and 1
   - Required timestamps
   - Nullable duration field 