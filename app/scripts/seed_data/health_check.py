#!/usr/bin/env python3
"""
Database health check for orphans and NULLs in critical columns.
Reports counts; exits 0 always (non-destructive).
"""

from sqlalchemy import text
from app.core.database import SessionLocal


def run_checks() -> None:
    session = SessionLocal()
    try:
        print("\n🔎 Running database health checks...")

        checks = [
            ("Orphan enrollments (invalid school_id)", text(
                """
                SELECT COUNT(*) FROM student_school_enrollments e
                LEFT JOIN schools s ON s.id = e.school_id
                WHERE s.id IS NULL
                """
            )),
            ("Orphan enrollments (invalid student_id)", text(
                """
                SELECT COUNT(*) FROM student_school_enrollments e
                LEFT JOIN students st ON st.id = e.student_id
                WHERE st.id IS NULL
                """
            )),
            ("Duplicate school_code in schools", text(
                """
                SELECT COUNT(*) FROM (
                  SELECT school_code FROM schools GROUP BY school_code HAVING COUNT(*)>1
                ) d
                """
            )),
            ("NULL emails in users", text(
                "SELECT COUNT(*) FROM users WHERE email IS NULL OR email = ''"
            )),
        ]

        for label, query in checks:
            cnt = session.execute(query).scalar() or 0
            status = "✅" if cnt == 0 else "❌"
            print(f"{status} {label}: {cnt}")

        print("\nHealth checks completed.")
    finally:
        session.close()


if __name__ == "__main__":
    run_checks()


