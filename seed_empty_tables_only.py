#!/usr/bin/env python3
"""
Seed only the empty tables that have existing seeding functions.
This script calls the specific seeding functions for tables that are currently empty.
"""

import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import DATABASE_URL

def get_database_connection():
    """Get database connection."""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def get_empty_tables(session):
    """Get list of empty tables."""
    result = session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """))
    all_tables = [row[0] for row in result.fetchall()]
    
    empty_tables = []
    for table in all_tables:
        try:
            count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = count_result.scalar()
            if count == 0:
                empty_tables.append(table)
        except Exception as e:
            print(f"Warning: Could not count {table}: {e}")
    
    return empty_tables

def seed_empty_tables():
    """Seed only the empty tables."""
    session = get_database_connection()
    
    try:
        # Get empty tables
        empty_tables = get_empty_tables(session)
        print(f"Found {len(empty_tables)} empty tables:")
        for table in empty_tables:
            print(f"  - {table}")
        
        # Import and call specific seeding functions
        from app.scripts.seed_data.seed_ai_analytics_data import seed_ai_analytics_data
        from app.scripts.seed_data.seed_assessment_criteria import seed_assessment_criteria
        from app.scripts.seed_data.seed_lesson_plans import seed_lesson_plans
        
        # Seed AI analytics data (populates ai_assistant_analytics, ai_assistant_conversations, etc.)
        if any(table.startswith('ai_assistant') for table in empty_tables):
            print("\n🌱 Seeding AI analytics data...")
            try:
                seed_ai_analytics_data(session)
                print("✅ AI analytics data seeded successfully!")
            except Exception as e:
                print(f"❌ Error seeding AI analytics data: {e}")
        
        # Seed assessment criteria (populates assessment_criteria, assessment_rubrics, etc.)
        if any(table.startswith('assessment') for table in empty_tables):
            print("\n🌱 Seeding assessment criteria...")
            try:
                seed_assessment_criteria(session)
                print("✅ Assessment criteria seeded successfully!")
            except Exception as e:
                print(f"❌ Error seeding assessment criteria: {e}")
        
        # Seed lesson plans (populates lesson_plans, lesson_plan_sharing, etc.)
        if any(table.startswith('lesson_plan') for table in empty_tables):
            print("\n🌱 Seeding lesson plans...")
            try:
                seed_lesson_plans(session)
                print("✅ Lesson plans seeded successfully!")
            except Exception as e:
                print(f"❌ Error seeding lesson plans: {e}")
        
        # Check final counts
        print("\n📊 Final table counts:")
        for table in empty_tables:
            try:
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error getting count - {e}")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_empty_tables()
