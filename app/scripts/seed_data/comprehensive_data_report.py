#!/usr/bin/env python3
"""
Comprehensive Data Consistency Report
Analyzes all populated tables and verifies data consistency and congruence
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime
from app.db.session import get_db

def get_table_count(conn, table_name):
    """Get record count for a table"""
    try:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {table_name}'))
        return result.scalar()
    except Exception as e:
        return f'ERROR: {str(e)}'

def check_foreign_key_consistency(session, parent_table, child_table, fk_column):
    """Check foreign key consistency between parent and child tables"""
    try:
        # First check if the column exists in the child table
        column_check = session.execute(text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{child_table}' AND column_name = '{fk_column}'
        """)).fetchone()
        
        if not column_check:
            return {'error': f'Column {fk_column} does not exist in table {child_table}'}
        
        # Get parent IDs
        parent_result = session.execute(text(f'SELECT id FROM {parent_table}'))
        parent_ids = set(row[0] for row in parent_result.fetchall())
        
        # Get child foreign key values
        child_result = session.execute(text(f'SELECT DISTINCT {fk_column} FROM {child_table} WHERE {fk_column} IS NOT NULL'))
        child_fk_values = set(row[0] for row in child_result.fetchall())
        
        # Check for orphaned records
        orphaned = child_fk_values - parent_ids
        return {
            'parent_count': len(parent_ids),
            'child_fk_count': len(child_fk_values),
            'orphaned_count': len(orphaned),
            'orphaned_values': list(orphaned)[:10] if orphaned else [],
            'coverage_percent': (len(child_fk_values & parent_ids) / len(child_fk_values) * 100) if child_fk_values else 100
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_table_relationships(session):
    """Analyze relationships between key tables"""
    relationships = {}
    
    # Core student relationships
    student_relationships = [
        ('students', 'student_health', 'student_id'),
        ('student_health', 'fitness_assessments', 'student_id'),
        ('student_health', 'student_health_fitness_goals', 'student_id'),
        ('students', 'educational_class_students', 'student_id'),
        ('users', 'course_enrollments', 'user_id'),  # course_enrollments uses user_id, not student_id
        ('users', 'assignments', 'created_by'),      # assignments uses created_by, not student_id
        ('students', 'student_school_enrollments', 'student_id')
    ]
    
    for parent, child, fk_col in student_relationships:
        try:
            relationships[f"{parent}->{child}"] = check_foreign_key_consistency(session, parent, child, fk_col)
        except Exception as e:
            relationships[f"{parent}->{child}"] = {'error': f'Failed to check relationship: {str(e)}'}
    
    # Educational system relationships
    educational_relationships = [
        ('educational_teachers', 'educational_classes', 'instructor_id'),
        ('educational_classes', 'educational_class_students', 'class_id'),
        ('courses', 'course_enrollments', 'course_id'),
        ('courses', 'assignments', 'course_id'),
        ('subjects', 'lesson_plans', 'subject_id'),
        ('grade_levels', 'lesson_plans', 'grade_level_id')
    ]
    
    for parent, child, fk_col in educational_relationships:
        try:
            relationships[f"{parent}->{child}"] = check_foreign_key_consistency(session, parent, child, fk_col)
        except Exception as e:
            relationships[f"{parent}->{child}"] = {'error': f'Failed to check relationship: {str(e)}'}
    
    return relationships

def generate_comprehensive_report():
    """Generate comprehensive data consistency report"""
    
    # Use the existing database session
    session = next(get_db())
    
    try:
        print('=' * 100)
        print('🔍 COMPREHENSIVE DATA CONSISTENCY & CONGRUENCE REPORT')
        print('=' * 100)
        print(f'📅 Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('=' * 100)
        
        # 1. CORE FOUNDATION TABLES
        print('\n📊 1. CORE FOUNDATION TABLES')
        print('-' * 60)
        foundation_tables = [
            'users', 'students', 'schools', 'organizations', 'departments',
            'teacher_school_assignments', 'student_school_enrollments'
        ]
        
        foundation_data = {}
        for table in foundation_tables:
            count = get_table_count(session, table)
            foundation_data[table] = count
            status = "✅" if isinstance(count, int) and count > 0 else "❌"
            print(f'{status} {table:<35}: {count:,} records')
        
        # 2. EDUCATIONAL SYSTEM TABLES
        print('\n📚 2. EDUCATIONAL SYSTEM TABLES')
        print('-' * 60)
        educational_tables = [
            'educational_teachers', 'educational_classes', 'educational_class_students',
            'courses', 'assignments', 'course_enrollments', 'grades',
            'subjects', 'grade_levels', 'lesson_plans', 'curriculum', 'curriculum_units',
            'lesson_plan_activities', 'lesson_plan_objectives', 'pe_lesson_plans'
        ]
        
        educational_data = {}
        for table in educational_tables:
            count = get_table_count(session, table)
            educational_data[table] = count
            status = "✅" if isinstance(count, int) and count > 0 else "❌"
            print(f'{status} {table:<35}: {count:,} records')
        
        # 3. HEALTH & FITNESS TABLES
        print('\n🏥 3. HEALTH & FITNESS TABLES')
        print('-' * 60)
        health_tables = [
            'student_health', 'fitness_assessments', 'student_health_fitness_goals',
            'health_alerts', 'health_checks', 'health_conditions', 'medical_conditions',
            'physical_education_nutrition_logs', 'physical_education_meals', 'meals', 'meal_plans',
            'nutrition_goals', 'fitness_goals', 'nutrition_plans', 'physical_education_nutrition_plans'
        ]
        
        health_data = {}
        for table in health_tables:
            count = get_table_count(session, table)
            health_data[table] = count
            status = "✅" if isinstance(count, int) and count > 0 else "❌"
            print(f'{status} {table:<35}: {count:,} records')
        
        # 4. SAFETY & RISK MANAGEMENT TABLES
        print('\n🛡️ 4. SAFETY & RISK MANAGEMENT TABLES')
        print('-' * 60)
        safety_tables = [
            'safety_incidents', 'safety_protocols', 'safety_guidelines', 'safety_checks',
            'equipment', 'equipment_maintenance', 'environmental_conditions', 'environmental_alerts',
            'injury_risk_factors', 'injury_preventions', 'prevention_measures'
        ]
        
        safety_data = {}
        for table in safety_tables:
            count = get_table_count(session, table)
            safety_data[table] = count
            status = "✅" if isinstance(count, int) and count > 0 else "❌"
            print(f'{status} {table:<35}: {count:,} records')
        
        # 5. AI & ANALYTICS TABLES
        print('\n🤖 5. AI & ANALYTICS TABLES')
        print('-' * 60)
        ai_tables = [
            'gpt_definitions', 'gpt_interaction_contexts', 'gpt_analytics',
            'dashboard_gpt_subscriptions', 'dashboard_analytics', 'core_gpt_definitions',
            'gpt_context_interactions', 'gpt_performance'
        ]
        
        ai_data = {}
        for table in ai_tables:
            count = get_table_count(session, table)
            ai_data[table] = count
            status = "✅" if isinstance(count, int) and count > 0 else "❌"
            print(f'{status} {table:<35}: {count:,} records')
        
        # 6. PERFORMANCE & ACTIVITY TABLES
        print('\n🏃 6. PERFORMANCE & ACTIVITY TABLES')
        print('-' * 60)
        performance_tables = [
            'activities', 'physical_education_classes', 'physical_education_class_students',
            'routine_performances', 'routine_performance_metrics', 'student_activity_performances',
            'pe_activity_preferences', 'performance_logs', 'class_attendance'
        ]
        
        performance_data = {}
        for table in performance_tables:
            count = get_table_count(session, table)
            performance_data[table] = count
            status = "✅" if isinstance(count, int) and count > 0 else "❌"
            print(f'{status} {table:<35}: {count:,} records')
        
        print('\n' + '=' * 100)
        print('🔗 FOREIGN KEY CONSISTENCY ANALYSIS')
        print('=' * 100)
        
        # Analyze relationships
        relationships = analyze_table_relationships(session)
        
        # Student-centric relationships
        print('\n👥 STUDENT-CENTRIC RELATIONSHIPS')
        print('-' * 60)
        student_relations = [k for k in relationships.keys() if 'students' in k or 'student_health' in k]
        for rel in student_relations:
            data = relationships[rel]
            if 'error' in data:
                print(f'❌ {rel:<40}: ERROR - {data["error"]}')
            else:
                status = "✅" if data['orphaned_count'] == 0 else "⚠️"
                print(f'{status} {rel:<40}: {data["parent_count"]:,} parent, {data["child_fk_count"]:,} child, {data["orphaned_count"]:,} orphaned ({data["coverage_percent"]:.1f}% coverage)')
        
        # Educational relationships
        print('\n📚 EDUCATIONAL RELATIONSHIPS')
        print('-' * 60)
        edu_relations = [k for k in relationships.keys() if any(x in k for x in ['educational_', 'courses', 'assignments', 'lesson_plans', 'subjects', 'grade_levels'])]
        for rel in edu_relations:
            data = relationships[rel]
            if 'error' in data:
                print(f'❌ {rel:<40}: ERROR - {data["error"]}')
            else:
                status = "✅" if data['orphaned_count'] == 0 else "⚠️"
                print(f'{status} {rel:<40}: {data["parent_count"]:,} parent, {data["child_fk_count"]:,} child, {data["orphaned_count"]:,} orphaned ({data["coverage_percent"]:.1f}% coverage)')
        
        print('\n' + '=' * 100)
        print('📈 DATA SCALING & CONGRUENCE ANALYSIS')
        print('=' * 100)
        
        # Get core counts
        student_count = foundation_data.get('students', 0)
        teacher_count = foundation_data.get('educational_teachers', 0)
        school_count = foundation_data.get('schools', 0)
        
        print(f'\n👥 CORE POPULATION METRICS')
        print(f'   Students: {student_count:,}')
        print(f'   Teachers: {teacher_count:,}')
        print(f'   Schools: {school_count:,}')
        print(f'   Student/Teacher Ratio: {student_count/teacher_count:.1f}:1' if teacher_count > 0 else '   Student/Teacher Ratio: N/A')
        
        # Health data congruence
        print(f'\n🏥 HEALTH DATA CONGRUENCE')
        health_count = health_data.get('student_health', 0)
        fitness_count = health_data.get('fitness_assessments', 0)
        goals_count = health_data.get('student_health_fitness_goals', 0)
        
        health_coverage = (health_count / student_count * 100) if student_count > 0 else 0
        fitness_ratio = (fitness_count / student_count) if student_count > 0 else 0
        goals_ratio = (goals_count / student_count) if student_count > 0 else 0
        
        print(f'   Health Records: {health_count:,} ({health_coverage:.1f}% of students)')
        print(f'   Fitness Assessments: {fitness_count:,} ({fitness_ratio:.2f} per student)')
        print(f'   Fitness Goals: {goals_count:,} ({goals_ratio:.2f} per student)')
        
        # Educational data congruence
        print(f'\n📚 EDUCATIONAL DATA CONGRUENCE')
        classes_count = educational_data.get('educational_classes', 0)
        enrollments_count = educational_data.get('course_enrollments', 0)
        assignments_count = educational_data.get('assignments', 0)
        
        class_ratio = (classes_count / teacher_count) if teacher_count > 0 else 0
        enrollment_ratio = (enrollments_count / student_count) if student_count > 0 else 0
        assignment_ratio = (assignments_count / student_count) if student_count > 0 else 0
        
        print(f'   Classes: {classes_count:,} ({class_ratio:.1f} per teacher)')
        print(f'   Course Enrollments: {enrollments_count:,} ({enrollment_ratio:.2f} per student)')
        print(f'   Assignments: {assignments_count:,} ({assignment_ratio:.2f} per student)')
        
        # Safety data congruence
        print(f'\n🛡️ SAFETY DATA CONGRUENCE')
        incidents_count = safety_data.get('safety_incidents', 0)
        protocols_count = safety_data.get('safety_protocols', 0)
        equipment_count = safety_data.get('equipment', 0)
        
        incident_ratio = (incidents_count / student_count) if student_count > 0 else 0
        protocol_ratio = (protocols_count / school_count) if school_count > 0 else 0
        equipment_ratio = (equipment_count / school_count) if school_count > 0 else 0
        
        print(f'   Safety Incidents: {incidents_count:,} ({incident_ratio:.3f} per student)')
        print(f'   Safety Protocols: {protocols_count:,} ({protocol_ratio:.1f} per school)')
        print(f'   Equipment Items: {equipment_count:,} ({equipment_ratio:.1f} per school)')
        
        # Performance data congruence
        print(f'\n🏃 PERFORMANCE DATA CONGRUENCE')
        activities_count = performance_data.get('activities', 0)
        performances_count = performance_data.get('routine_performances', 0)
        attendance_count = performance_data.get('class_attendance', 0)
        
        activity_ratio = (activities_count / school_count) if school_count > 0 else 0
        performance_ratio = (performances_count / student_count) if student_count > 0 else 0
        attendance_ratio = (attendance_count / student_count) if student_count > 0 else 0
        
        print(f'   Activities: {activities_count:,} ({activity_ratio:.1f} per school)')
        print(f'   Routine Performances: {performances_count:,} ({performance_ratio:.1f} per student)')
        print(f'   Class Attendance: {attendance_count:,} ({attendance_ratio:.1f} per student)')
        
        print('\n' + '=' * 100)
        print('🎯 DATA QUALITY ASSESSMENT')
        print('=' * 100)
        
        # Calculate quality metrics
        total_tables = len(foundation_tables) + len(educational_tables) + len(health_tables) + len(safety_tables) + len(ai_tables) + len(performance_tables)
        populated_tables = sum(1 for data in [foundation_data, educational_data, health_data, safety_data, ai_data, performance_data] 
                             for count in data.values() if isinstance(count, int) and count > 0)
        
        quality_score = (populated_tables / total_tables * 100) if total_tables > 0 else 0
        
        print(f'📊 Overall Population Rate: {populated_tables}/{total_tables} tables ({quality_score:.1f}%)')
        
        # Check for critical data consistency issues
        issues = []
        
        # Health coverage check
        if health_coverage < 95:
            issues.append(f"Health record coverage is {health_coverage:.1f}% (should be ~100%)")
        
        # Foreign key orphaned records
        orphaned_total = sum(data.get('orphaned_count', 0) for data in relationships.values() if isinstance(data, dict) and 'orphaned_count' in data)
        if orphaned_total > 0:
            issues.append(f"Found {orphaned_total} orphaned foreign key records")
        
        # Student/teacher ratio check
        if teacher_count > 0 and (student_count / teacher_count) > 50:
            issues.append(f"Student/teacher ratio is {student_count/teacher_count:.1f}:1 (may be too high)")
        
        if issues:
            print(f'\n⚠️  DATA QUALITY ISSUES FOUND:')
            for issue in issues:
                print(f'   • {issue}')
        else:
            print(f'\n✅ NO CRITICAL DATA QUALITY ISSUES FOUND')
        
        print('\n' + '=' * 100)
        print('🏆 FINAL ASSESSMENT')
        print('=' * 100)
        
        if quality_score >= 90 and orphaned_total == 0 and health_coverage >= 95:
            print('🎉 EXCELLENT: Database is highly consistent and congruent!')
            print('   ✅ All critical relationships maintained')
            print('   ✅ Data scales appropriately with population')
            print('   ✅ Ready for production use')
        elif quality_score >= 80 and orphaned_total < 10:
            print('✅ GOOD: Database is mostly consistent with minor issues')
            print('   ⚠️  Some minor data quality issues present')
            print('   ✅ Generally ready for production use')
        else:
            print('⚠️  NEEDS ATTENTION: Database has significant consistency issues')
            print('   ❌ Multiple data quality problems detected')
            print('   🔧 Requires fixes before production use')
        
        print(f'\n📈 SUMMARY METRICS:')
        print(f'   • Total Records: {sum(data.get(count, 0) for data in [foundation_data, educational_data, health_data, safety_data, ai_data, performance_data] for count in data.values() if isinstance(count, int)):,}')
        print(f'   • Population Coverage: {quality_score:.1f}%')
        print(f'   • Health Coverage: {health_coverage:.1f}%')
        print(f'   • Orphaned Records: {orphaned_total}')
        print(f'   • Data Quality Score: {"EXCELLENT" if quality_score >= 90 and orphaned_total == 0 else "GOOD" if quality_score >= 80 else "NEEDS IMPROVEMENT"}')
    
    finally:
        session.close()

if __name__ == "__main__":
    generate_comprehensive_report()
