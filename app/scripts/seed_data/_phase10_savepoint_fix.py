# Phase 10 Savepoint Fix Tracking
# This file tracks which tables have been wrapped with savepoints

# ✅ COMPLETED (all 30 tables now have savepoints):
completed = [
    "skill_assessment_assessment_metrics",           # ✅ Done
    "skill_assessment_assessments",                  # ✅ Done
    "skill_assessment_risk_assessments",             # ✅ Done
    "skill_assessment_safety_alerts",                # ✅ Done
    "skill_assessment_safety_incidents",            # ✅ Done
    "skill_assessment_safety_protocols",             # ✅ Done
    "general_assessment_criteria",                   # ✅ Done
    "general_assessment_history",                    # ✅ Done
    "assessment_changes",                            # ✅ Done
    "analysis_movement_feedback",                    # ✅ Done
    "skill_assessment_assessment_criteria",          # ✅ Done
    "skill_assessment_assessment_history",           # ✅ Done
    "skill_assessment_assessment_results",           # ✅ Done
    "skill_assessment_skill_assessments",            # ✅ Done
    "general_skill_assessments",                     # ✅ Done
    "student_health_skill_assessments",              # ✅ Done
    "movement_analysis_metrics",                     # ✅ Done
    "movement_analysis_patterns",                    # ✅ Done
    "physical_education_movement_analysis",          # ✅ Done
    "safety_incidents",                              # ✅ Done
    "safety_guidelines",                             # ✅ Done
    "safety_protocols",                              # ✅ Done
    "safety_reports",                                # ✅ Done
    "safety_measures",                               # ✅ Done
    "safety_checklists",                             # ✅ Done
    "injury_preventions",                            # ✅ Done
    "safety",                                        # ✅ Done
    "safety_incident_base",                          # ✅ Done
    "activity_injury_preventions",                   # ✅ Done
    "activity_logs",                                 # ✅ Done
]

# ⏳ REMAINING (need savepoints):
remaining = []

print(f"✅ ALL {len(completed)}/30 tables wrapped with savepoints!")
print("All Phase 10 tables now have transaction isolation - failures won't cascade.")
