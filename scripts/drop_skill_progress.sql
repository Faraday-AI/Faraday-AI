DO $$ 
BEGIN
    -- Drop foreign key constraints
    ALTER TABLE IF EXISTS skill_progress 
    DROP CONSTRAINT IF EXISTS skill_progress_student_id_fkey,
    DROP CONSTRAINT IF EXISTS skill_progress_activity_id_fkey;
    
    -- Drop check constraints
    ALTER TABLE IF EXISTS skill_progress 
    DROP CONSTRAINT IF EXISTS valid_skill_level;
EXCEPTION WHEN OTHERS THEN
    -- If any error occurs, just continue
    NULL;
END $$;

-- Drop the table
DROP TABLE IF EXISTS skill_progress CASCADE; 