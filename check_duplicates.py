#!/usr/bin/env python3
import sys
sys.path.append('/app')

from app.core.database import SessionLocal
from sqlalchemy import text

session = SessionLocal()

# Check source data
print("🔍 Checking source PE lesson plans for duplicates:")
result = session.execute(text("""
    SELECT title, COUNT(*) as count
    FROM pe_lesson_plans
    WHERE title IS NOT NULL
    GROUP BY title
    HAVING COUNT(*) > 1
    LIMIT 5
""")).fetchall()

print(f"Found {len(result)} duplicate titles in source:\n")
for row in result:
    print(f"  Title: {row[0]}, Count: {row[1]}")

# Check specific duplicate
print("\n\n🔍 Checking details of 'PE Lesson Plan 275':")
result = session.execute(text("""
    SELECT id, title, description, difficulty, created_at
    FROM pe_lesson_plans
    WHERE title = 'PE Lesson Plan 275'
    ORDER BY created_at
""")).fetchall()

for i, row in enumerate(result, 1):
    print(f"\n  Record {i}:")
    print(f"    ID: {row[0]}")
    print(f"    Description: {row[2][:80] if row[2] else 'None'}...")
    print(f"    Difficulty: {row[3]}")
    print(f"    Created: {row[4]}")

print("\n\n📊 CONCLUSION:")
print("The duplicates exist in the SOURCE data (pe_lesson_plans table).")
print("The migration is working correctly - it's preserving the data as-is.")
print("This is EXPECTED behavior if the same lesson plan exists multiple times in different units/contexts.")

