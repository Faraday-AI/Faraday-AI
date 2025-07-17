-- Drop the existing alembic_version table
DROP TABLE IF EXISTS alembic_version;

-- Recreate the alembic_version table with longer VARCHAR
CREATE TABLE alembic_version (
    version_num VARCHAR(64) NOT NULL
);

-- Insert the new base version
INSERT INTO alembic_version (version_num) VALUES ('20250429_000022_reset_version_chain'); 