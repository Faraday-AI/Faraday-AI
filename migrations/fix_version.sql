-- Drop the existing alembic_version table
DROP TABLE IF EXISTS alembic_version;

-- Recreate the alembic_version table with the correct version
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- Insert the correct version
INSERT INTO alembic_version (version_num) VALUES ('20250429_000020_merge_all_heads'); 