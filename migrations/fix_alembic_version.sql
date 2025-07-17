-- Check current version
SELECT * FROM alembic_version;

-- Update incorrect version ID if it exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM alembic_version WHERE version_num = '164427_asst_cap_fields') THEN
        UPDATE alembic_version 
        SET version_num = '20250427_164427_add_assistant_capability_fields'
        WHERE version_num = '164427_asst_cap_fields';
    END IF;
END $$; 