#!/usr/bin/env python3
"""
Comprehensive Database Status Report

Generates a detailed report of all tables and their record counts.
"""

import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from collections import defaultdict

# Database connection setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_all_tables(session):
    """Get all tables from the database"""
    result = session.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """))
    return [row[0] for row in result]

def count_records(session, table_name):
    """Safely count records in a table"""
    try:
        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar() or 0
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

def categorize_table(table_name):
    """Categorize table by name patterns"""
    name_lower = table_name.lower()
    
    if 'job' in name_lower:
        return "System/Jobs"
    elif 'beta' in name_lower or 'teacher' in name_lower:
        return "Beta Teacher System"
    elif 'student' in name_lower:
        return "Students"
    elif 'health' in name_lower or 'fitness' in name_lower:
        return "Health & Fitness"
    elif 'drivers_ed' in name_lower or 'driver' in name_lower:
        return "Drivers Education"
    elif 'dashboard' in name_lower:
        return "Dashboard"
    elif 'gpt' in name_lower or 'ai' in name_lower:
        return "AI/GPT"
    elif 'curriculum' in name_lower or 'lesson' in name_lower:
        return "Curriculum & Lessons"
    elif 'activity' in name_lower or 'exercise' in name_lower:
        return "Activities & Exercises"
    elif 'safety' in name_lower or 'risk' in name_lower or 'incident' in name_lower:
        return "Safety & Risk"
    elif 'equipment' in name_lower:
        return "Equipment"
    elif 'assessment' in name_lower or 'skill' in name_lower:
        return "Assessments & Skills"
    elif 'analytics' in name_lower or 'event' in name_lower:
        return "Analytics & Events"
    elif 'user' in name_lower or 'profile' in name_lower:
        return "Users & Profiles"
    elif 'organization' in name_lower or 'school' in name_lower:
        return "Organizations & Schools"
    elif 'workout' in name_lower or 'routine' in name_lower:
        return "Workouts & Routines"
    elif 'progress' in name_lower or 'tracking' in name_lower:
        return "Progress & Tracking"
    elif 'cache' in name_lower:
        return "Cache"
    elif 'security' in name_lower or 'audit' in name_lower:
        return "Security & Auditing"
    elif 'resource' in name_lower:
        return "Resources"
    elif 'goal' in name_lower:
        return "Goals"
    elif 'feedback' in name_lower:
        return "Feedback"
    elif 'notification' in name_lower:
        return "Notifications"
    elif 'class' in name_lower or 'course' in name_lower:
        return "Classes & Courses"
    elif 'permission' in name_lower or 'role' in name_lower:
        return "Permissions & Roles"
    else:
        return "Other"

def generate_report():
    """Generate comprehensive database status report"""
    print("=" * 100)
    print("COMPREHENSIVE DATABASE STATUS REPORT".center(100))
    print("=" * 100)
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Local'}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    session = SessionLocal()
    try:
        # Get all tables
        print("📊 Collecting table information...")
        all_tables = get_all_tables(session)
        total_tables = len(all_tables)
        
        # Count records for each table
        table_data = []
        categories = defaultdict(list)
        empty_tables = []
        error_tables = []
        total_records = 0
        
        for table_name in all_tables:
            category = categorize_table(table_name)
            count = count_records(session, table_name)
            
            if isinstance(count, str):  # Error
                error_tables.append((table_name, count))
                categories[category].append((table_name, 0, "ERROR"))
            else:
                if count == 0:
                    empty_tables.append((table_name, category))
                else:
                    total_records += count
                
                table_data.append((table_name, count, category))
                categories[category].append((table_name, count, "OK"))
        
        # Summary
        print("\n" + "=" * 100)
        print("SUMMARY".center(100))
        print("=" * 100)
        print(f"Total Tables: {total_tables}")
        print(f"Tables with Data: {total_tables - len(empty_tables) - len(error_tables)}")
        print(f"Empty Tables: {len(empty_tables)}")
        print(f"Error Tables: {len(error_tables)}")
        print(f"Total Records: {total_records:,}")
        print()
        
        # Empty tables
        if empty_tables:
            print("=" * 100)
            print("EMPTY TABLES".center(100))
            print("=" * 100)
            for table_name, category in sorted(empty_tables):
                print(f"  • {table_name:<60} [{category}]")
            print()
        
        # Error tables
        if error_tables:
            print("=" * 100)
            print("TABLES WITH ERRORS".center(100))
            print("=" * 100)
            for table_name, error in error_tables:
                print(f"  ❌ {table_name:<60} {error}")
            print()
        
        # Detailed breakdown by category
        print("=" * 100)
        print("DETAILED BREAKDOWN BY CATEGORY".center(100))
        print("=" * 100)
        
        for category in sorted(categories.keys()):
            cat_tables = categories[category]
            cat_count = len(cat_tables)
            cat_records = sum(count for _, count, _ in cat_tables if isinstance(count, int))
            cat_empty = sum(1 for _, count, _ in cat_tables if count == 0)
            
            print(f"\n📁 {category}")
            print("-" * 100)
            print(f"   Tables: {cat_count} | Records: {cat_records:,} | Empty: {cat_empty}")
            print()
            
            # Show top 10 tables by record count, then list all
            sorted_tables = sorted(
                [(name, count, status) for name, count, status in cat_tables],
                key=lambda x: (0 if isinstance(x[1], int) else 1, -x[1] if isinstance(x[1], int) else 0)
            )
            
            for table_name, count, status in sorted_tables[:20]:  # Show top 20 per category
                if isinstance(count, int):
                    if count == 0:
                        symbol = "⚪"
                    elif count < 10:
                        symbol = "🔵"
                    elif count < 100:
                        symbol = "🟢"
                    elif count < 1000:
                        symbol = "🟡"
                    else:
                        symbol = "🔴"
                    print(f"   {symbol} {table_name:<65} {count:>12,} records")
                else:
                    print(f"   ❌ {table_name:<65} {count}")
            
            if len(sorted_tables) > 20:
                print(f"   ... and {len(sorted_tables) - 20} more tables")
        
        # Top 20 largest tables
        print("\n" + "=" * 100)
        print("TOP 20 LARGEST TABLES".center(100))
        print("=" * 100)
        sorted_by_size = sorted(
            [(name, count) for name, count, _ in table_data if isinstance(count, int) and count > 0],
            key=lambda x: -x[1]
        )
        
        for i, (table_name, count) in enumerate(sorted_by_size[:20], 1):
            print(f"   {i:2d}. {table_name:<70} {count:>12,} records")
        
        # Final summary
        print("\n" + "=" * 100)
        print("FINAL SUMMARY".center(100))
        print("=" * 100)
        populated = total_tables - len(empty_tables) - len(error_tables)
        coverage = (populated / total_tables * 100) if total_tables > 0 else 0
        
        print(f"✅ Total Tables: {total_tables}")
        print(f"✅ Populated Tables: {populated} ({coverage:.1f}%)")
        print(f"⚪ Empty Tables: {len(empty_tables)}")
        print(f"❌ Error Tables: {len(error_tables)}")
        print(f"📊 Total Records: {total_records:,}")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n❌ ERROR generating report: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    generate_report()

