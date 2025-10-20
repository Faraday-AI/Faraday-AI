#!/usr/bin/env python3
"""
Post-seed validation: verifies student distribution and basic data health.

Checks:
- High >= Middle + one grade (420)
- Exactly 4 elementaries, 1 middle, 1 high
- No orphaned enrollments (student_id without students or bad school_id)
- Basic presence constraints on key tables
"""

from sqlalchemy import create_engine, text
from app.core.database import SessionLocal
import os

GRADE_SIZE = 420

def validate():
    session = SessionLocal()
    try:
        print("Running post-seed validation...")

        # Schools by type
        rows = session.execute(text("SELECT id, name, school_type FROM schools ORDER BY school_type, name")).fetchall()
        elem = [r for r in rows if r.school_type == 'ELEMENTARY']
        mids = [r for r in rows if r.school_type == 'MIDDLE']
        highs = [r for r in rows if r.school_type == 'HIGH']

        ok = True

        # Structure checks
        if len(elem) != 4:
            print(f"❌ Expected 4 elementary schools, found {len(elem)}")
            ok = False
        if len(mids) != 1:
            print(f"❌ Expected 1 middle school, found {len(mids)}")
            ok = False
        if len(highs) != 1:
            print(f"❌ Expected 1 high school, found {len(highs)}")
            ok = False

        # Counts
        def count_for(sid: int) -> int:
            return session.execute(text("SELECT COUNT(*) FROM student_school_enrollments WHERE school_id = :sid"), {"sid": sid}).scalar() or 0

        if mids and highs:
            mid_count = count_for(mids[0].id)
            high_count = count_for(highs[0].id)
            print(f"Middle={mid_count}, High={high_count}")
            if high_count < mid_count + GRADE_SIZE:
                print(f"❌ High should be at least Middle + {GRADE_SIZE}")
                ok = False
            else:
                print("✅ Relative distribution rule satisfied (High >= Middle + one grade)")

        # Orphan checks: enrollments with non-existent student or school
        bad_school = session.execute(text("""
            SELECT COUNT(*) FROM student_school_enrollments e
            LEFT JOIN schools s ON s.id = e.school_id
            WHERE s.id IS NULL
        """)).scalar() or 0
        bad_student = session.execute(text("""
            SELECT COUNT(*) FROM student_school_enrollments e
            LEFT JOIN students st ON st.id = e.student_id
            WHERE st.id IS NULL
        """)).scalar() or 0
        if bad_school > 0:
            print(f"❌ Orphan enrollments with invalid school_id: {bad_school}")
            ok = False
        if bad_student > 0:
            print(f"❌ Orphan enrollments with invalid student_id: {bad_student}")
            ok = False

        # Optional lightweight checks for later phases (only if not skipped)
        def env_true(name: str) -> bool:
            val = os.getenv(name, "").strip().lower()
            return val in ("1", "true", "yes", "y", "on")

        try:
            if not env_true('SKIP_PHASE_2'):
                # Courses and lesson plans presence (informational only here; Phase 2 runs later)
                courses = session.execute(text("SELECT COUNT(*) FROM courses")).scalar() or 0
                lesson_plans = session.execute(text("SELECT COUNT(*) FROM lesson_plans")).scalar() or 0
                if courses == 0:
                    print("⚠️ Phase 2 check: no courses present (expected if Phase 2 not yet run)")
                if lesson_plans == 0:
                    print("⚠️ Phase 2 check: no lesson_plans present (expected if Phase 2 not yet run)")
            if not env_true('SKIP_PHASE_3'):
                # Basic health/fitness tables
                try:
                    fitness_goals = session.execute(text("SELECT COUNT(*) FROM fitness_goals")).scalar() or 0
                    if fitness_goals == 0:
                        print("⚠️ Phase 3 check: fitness_goals empty")
                except Exception:
                    print("⚠️ Phase 3 check: fitness_goals table missing")
            if not env_true('SKIP_PHASE_4'):
                try:
                    safety_incidents = session.execute(text("SELECT COUNT(*) FROM safety_incidents")).scalar() or 0
                    print(f"Phase 4 check: safety_incidents={safety_incidents}")
                except Exception:
                    print("⚠️ Phase 4 check: safety_incidents table missing")
            if not env_true('SKIP_PHASE_5'):
                try:
                    ai_tools = session.execute(text("SELECT COUNT(*) FROM ai_tools")).scalar() or 0
                    print(f"Phase 5 check: ai_tools={ai_tools}")
                except Exception:
                    print("⚠️ Phase 5 check: ai_tools table missing")
            if not env_true('SKIP_PHASE_6'):
                try:
                    movement_sessions = session.execute(text("SELECT COUNT(*) FROM movement_sessions")).scalar() or 0
                    print(f"Phase 6 check: movement_sessions={movement_sessions}")
                except Exception:
                    print("⚠️ Phase 6 check: movement_sessions table missing")
            if not env_true('SKIP_PHASE_7'):
                try:
                    adaptations = session.execute(text("SELECT COUNT(*) FROM pe_activity_adaptations")).scalar() or 0
                    if adaptations == 0:
                        print("⚠️ Phase 7 check: pe_activity_adaptations empty")
                except Exception:
                    print("⚠️ Phase 7 check: pe_activity_adaptations table missing")
            if not env_true('SKIP_PHASE_8'):
                try:
                    pe_lesson_plans = session.execute(text("SELECT COUNT(*) FROM pe_lesson_plans")).scalar() or 0
                    print(f"Phase 8 check: pe_lesson_plans={pe_lesson_plans}")
                except Exception:
                    print("⚠️ Phase 8 check: pe_lesson_plans table missing")
            if not env_true('SKIP_PHASE_9'):
                try:
                    workouts = session.execute(text("SELECT COUNT(*) FROM health_fitness_workouts")).scalar() or 0
                    print(f"Phase 9 check: health_fitness_workouts={workouts}")
                except Exception:
                    print("⚠️ Phase 9 check: health_fitness_workouts table missing")
            if not env_true('SKIP_PHASE_10'):
                try:
                    skill_assessments = session.execute(text("SELECT COUNT(*) FROM skill_assessment_skill_assessments")).scalar() or 0
                    print(f"Phase 10 check: skill_assessment_skill_assessments={skill_assessments}")
                except Exception:
                    print("⚠️ Phase 10 check: skill_assessment_skill_assessments table missing")
            if not env_true('SKIP_PHASE_11'):
                try:
                    analytics_events = session.execute(text("SELECT COUNT(*) FROM analytics_events")).scalar() or 0
                    print(f"Phase 11 check: analytics_events={analytics_events}")
                except Exception:
                    print("⚠️ Phase 11 check: analytics_events table missing")
        except Exception as e:
            print(f"⚠️ Later-phase validation checks encountered an error: {e}")

        # Summary
        if ok:
            print("\n🎉 Validation passed")
        else:
            print("\n⚠️ Validation issues detected")
        return ok
    finally:
        session.close()

if __name__ == "__main__":
    validate()


