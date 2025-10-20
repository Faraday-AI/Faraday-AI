#!/usr/bin/env python3
"""
Apply idempotent unique constraints and performance indexes.

This script is safe to run multiple times.
"""

from sqlalchemy import text
from app.core.database import SessionLocal


def apply_indexes() -> None:
    session = SessionLocal()
    try:
        print("\n🔧 Applying unique constraints and performance indexes...")

        # Unique constraint on schools.school_code
        session.execute(text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'uk_schools_school_code'
                ) THEN
                    ALTER TABLE schools
                    ADD CONSTRAINT uk_schools_school_code UNIQUE (school_code);
                END IF;
            END$$;
            """
        ))

        # Unique index on users.email (handles both constraint + lookup speed)
        session.execute(text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email ON users (email);
            """
        ))

        # Performance indexes
        session.execute(text(
            """
            CREATE INDEX IF NOT EXISTS idx_enrollments_school_id
            ON student_school_enrollments (school_id);
            """
        ))

        session.execute(text(
            """
            CREATE INDEX IF NOT EXISTS idx_students_grade_level
            ON students (grade_level);
            """
        ))

        # Additional common FK and composite indexes
        session.execute(text(
            """
            CREATE INDEX IF NOT EXISTS idx_enrollments_student_id
            ON student_school_enrollments (student_id);
            """
        ))

        session.execute(text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables WHERE table_name = 'course_enrollments'
                ) THEN
                    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_course_enrollments_course_id') THEN
                        EXECUTE 'CREATE INDEX idx_course_enrollments_course_id ON course_enrollments (course_id)';
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_course_enrollments_student_id') THEN
                        EXECUTE 'CREATE INDEX idx_course_enrollments_student_id ON course_enrollments (student_id)';
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ux_course_enrollments_course_student') THEN
                        EXECUTE 'CREATE UNIQUE INDEX ux_course_enrollments_course_student ON course_enrollments (course_id, student_id)';
                    END IF;
                END IF;
            END$$;
            """
        ))

        # Natural key unique constraints (idempotent)
        # Courses: unique course_code if column exists
        session.execute(text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'courses' AND column_name = 'course_code'
                ) THEN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes WHERE indexname = 'ux_courses_course_code'
                    ) THEN
                        EXECUTE 'CREATE UNIQUE INDEX ux_courses_course_code ON courses (course_code)';
                    END IF;
                END IF;
            END$$;
            """
        ))

        # Lesson plans: unique slug if column exists
        session.execute(text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'lesson_plans' AND column_name = 'slug'
                ) THEN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes WHERE indexname = 'ux_lesson_plans_slug'
                    ) THEN
                        EXECUTE 'CREATE UNIQUE INDEX ux_lesson_plans_slug ON lesson_plans (slug)';
                    END IF;
                END IF;
            END$$;
            """
        ))

        session.commit()
        print("✅ Indexes applied")
    except Exception as e:
        session.rollback()
        print(f"❌ Error applying indexes: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    apply_indexes()


