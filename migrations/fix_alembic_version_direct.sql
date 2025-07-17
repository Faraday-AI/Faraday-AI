-- Drop and recreate the alembic_version table
DROP TABLE IF EXISTS alembic_version;

-- Recreate the alembic_version table
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Insert the base revision
INSERT INTO alembic_version (version_num) VALUES ('1317d2febf9d'); 