#!/usr/bin/env python3
"""
Check table structure for Phase 1 tables
"""

import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.core.database import SessionLocal
from sqlalchemy import text

def check_table_structure():
    """Check the structure of Phase 1 tables"""
    session = SessionLocal()
    try:
        print("🔍 CHECKING PHASE 1 TABLE STRUCTURES")
        print("=" * 50)
        
        # Check user_profiles table
        print("\n📋 user_profiles table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_profiles' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_roles table
        print("\n📋 user_roles table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_roles' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_sessions table
        print("\n📋 user_sessions table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_sessions' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_activities table
        print("\n📋 user_activities table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_activities' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_behaviors table
        print("\n📋 user_behaviors table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_behaviors' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_engagements table
        print("\n📋 user_engagements table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_engagements' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_insights table
        print("\n📋 user_insights table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_insights' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_trends table
        print("\n📋 user_trends table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_trends' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_predictions table
        print("\n📋 user_predictions table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_predictions' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check user_comparisons table
        print("\n📋 user_comparisons table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_comparisons' 
            ORDER BY ordinal_position
        """))
        
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    check_table_structure() 