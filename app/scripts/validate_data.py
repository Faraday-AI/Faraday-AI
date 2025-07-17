from sqlalchemy import text
from app.core.database import async_session
import asyncio

async def validate_data():
    async with async_session() as session:
        # Check basic counts
        tables = ['users', 'user_memories', 'memory_interactions', 
                 'activities', 'lessons', 'subject_categories',
                 'students', 'classes', 'safety_checks']
        
        print("\n=== Table Counts ===")
        for table in tables:
            result = await session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar()
            print(f"{table}: {count} records")
        
        # Check relationships
        print("\n=== Relationship Validation ===")
        
        # Users and Memories
        result = await session.execute(text('''
            SELECT u.email, COUNT(m.id) as memory_count 
            FROM users u 
            LEFT JOIN user_memories m ON u.id = m.user_id 
            GROUP BY u.email
        '''))
        rows = result.fetchall()
        print("\nUser-Memory Relationships:")
        for row in rows:
            print(f"User {row[0]}: {row[1]} memories")
        
        # Activities and Categories using explicit type casting
        result = await session.execute(text('''
            SELECT ac.name, COUNT(DISTINCT a.id) as activity_count 
            FROM activity_categories ac 
            LEFT JOIN activity_category_associations aca ON ac.id::integer = aca.category_id::integer
            LEFT JOIN activities a ON a.id::integer = aca.activity_id::integer
            GROUP BY ac.name
        '''))
        rows = result.fetchall()
        print("\nActivity Category Relationships:")
        for row in rows:
            print(f"Category {row[0]}: {row[1]} activities")

        # Detailed Activity Investigation
        print("\n=== Activity Details ===")
        
        # Check all activities and their assigned categories
        result = await session.execute(text('''
            SELECT 
                a.id,
                a.name,
                a.activity_type,
                a.difficulty,
                STRING_AGG(ac.name, ', ') as categories
            FROM activities a
            LEFT JOIN activity_category_associations aca ON a.id::integer = aca.activity_id::integer
            LEFT JOIN activity_categories ac ON aca.category_id::integer = ac.id::integer
            GROUP BY a.id, a.name, a.activity_type, a.difficulty
            ORDER BY a.id
        '''))
        rows = result.fetchall()
        print("\nActivity Assignments:")
        for row in rows:
            print(f"Activity {row[0]} - {row[1]}:")
            print(f"  Type: {row[2]}")
            print(f"  Difficulty: {row[3]}")
            print(f"  Categories: {row[4] or 'None'}")

        # Check categories with no activities
        result = await session.execute(text('''
            SELECT 
                ac.name,
                ac.description,
                ac.parent_id
            FROM activity_categories ac
            LEFT JOIN activity_category_associations aca ON ac.id::integer = aca.category_id::integer
            WHERE aca.id IS NULL
            ORDER BY ac.name
        '''))
        rows = result.fetchall()
        print("\nCategories with No Activities:")
        for row in rows:
            print(f"Category: {row[0]}")
            print(f"  Description: {row[1] or 'None'}")
            print(f"  Parent ID: {row[2] or 'None'}")

        print("\n=== Category Hierarchy Analysis ===")
        
        # Get complete category hierarchy
        result = await session.execute(text('''
            WITH RECURSIVE category_tree AS (
                -- Base case: top-level categories
                SELECT 
                    id,
                    name,
                    description,
                    parent_id,
                    1 as level,
                    ARRAY[name] as path
                FROM activity_categories
                WHERE parent_id IS NULL
                
                UNION ALL
                
                -- Recursive case: child categories
                SELECT 
                    c.id,
                    c.name,
                    c.description,
                    c.parent_id,
                    ct.level + 1,
                    ct.path || c.name
                FROM activity_categories c
                JOIN category_tree ct ON c.parent_id = ct.id
            )
            SELECT 
                level,
                id,
                name,
                description,
                parent_id,
                array_to_string(path, ' > ') as full_path
            FROM category_tree
            ORDER BY path;
        '''))
        rows = result.fetchall()
        print("\nCategory Hierarchy:")
        for row in rows:
            indent = "  " * (row[0] - 1)
            print(f"{indent}Category: {row[2]} (ID: {row[1]})")
            print(f"{indent}  Description: {row[3] or 'None'}")
            print(f"{indent}  Parent ID: {row[4] or 'None'}")
            print(f"{indent}  Full Path: {row[5]}")

        # Activity distribution across hierarchy
        print("\n=== Activity Distribution in Hierarchy ===")
        result = await session.execute(text('''
            WITH RECURSIVE category_tree AS (
                -- Base case: top-level categories
                SELECT 
                    id,
                    name,
                    parent_id,
                    ARRAY[name] as path
                FROM activity_categories
                WHERE parent_id IS NULL
                
                UNION ALL
                
                -- Recursive case: child categories
                SELECT 
                    c.id,
                    c.name,
                    c.parent_id,
                    ct.path || c.name
                FROM activity_categories c
                JOIN category_tree ct ON c.parent_id = ct.id
            )
            SELECT 
                ct.name as category_name,
                array_to_string(ct.path, ' > ') as category_path,
                COUNT(DISTINCT a.id) as direct_activities,
                COUNT(DISTINCT child_a.id) as inherited_activities
            FROM category_tree ct
            LEFT JOIN activity_category_associations aca ON ct.id::integer = aca.category_id::integer
            LEFT JOIN activities a ON aca.activity_id::integer = a.id::integer
            LEFT JOIN activity_categories child_c ON child_c.parent_id = ct.id
            LEFT JOIN activity_category_associations child_aca ON child_c.id::integer = child_aca.category_id::integer
            LEFT JOIN activities child_a ON child_aca.activity_id::integer = child_a.id::integer
            GROUP BY ct.name, ct.path
            ORDER BY ct.path;
        '''))
        rows = result.fetchall()
        print("\nActivity Distribution:")
        for row in rows:
            print(f"\nCategory: {row[0]}")
            print(f"  Path: {row[1]}")
            print(f"  Direct Activities: {row[2]}")
            print(f"  Activities in Subcategories: {row[3]}")

        # Suggested activities for empty categories
        print("\n=== Suggested Activities for Empty Categories ===")
        result = await session.execute(text('''
            SELECT 
                ac.name,
                ac.description,
                parent.name as parent_category
            FROM activity_categories ac
            LEFT JOIN activity_category_associations aca ON ac.id::integer = aca.category_id::integer
            LEFT JOIN activity_categories parent ON ac.parent_id = parent.id
            WHERE aca.id IS NULL
            ORDER BY ac.name;
        '''))
        rows = result.fetchall()
        print("\nGaps to Fill:")
        for row in rows:
            print(f"\nEmpty Category: {row[0]}")
            print(f"  Description: {row[1] or 'None'}")
            print(f"  Parent Category: {row[2] or 'None'}")
            
            # Suggest activities based on category
            if row[0] == 'Agility':
                print("  Suggested Activities:")
                print("  - Agility Ladder Drills (SKILL_DEVELOPMENT, BEGINNER)")
                print("  - Cone Weaving (SKILL_DEVELOPMENT, BEGINNER)")
                print("  - Side Shuffle Practice (SKILL_DEVELOPMENT, INTERMEDIATE)")
            elif row[0] == 'Balance':
                print("  Suggested Activities:")
                print("  - Single Leg Stance (SKILL_DEVELOPMENT, BEGINNER)")
                print("  - Balance Beam Walking (SKILL_DEVELOPMENT, BEGINNER)")
                print("  - Yoga Balance Poses (SKILL_DEVELOPMENT, INTERMEDIATE)")
            elif row[0] == 'Breathing':
                print("  Suggested Activities:")
                print("  - Deep Breathing Exercise (COOL_DOWN, BEGINNER)")
                print("  - Mindful Breathing (COOL_DOWN, BEGINNER)")
            elif row[0] == 'Individual Skills':
                print("  Suggested Activities:")
                print("  - Personal Goal Setting (SKILL_DEVELOPMENT, BEGINNER)")
                print("  - Self-Paced Skill Practice (SKILL_DEVELOPMENT, INTERMEDIATE)")
            elif row[0] == 'Joint Mobility':
                print("  Suggested Activities:")
                print("  - Joint Circles Warm-up (WARM_UP, BEGINNER)")
                print("  - Dynamic Joint Mobility (WARM_UP, INTERMEDIATE)")
            elif row[0] == 'Light Cardio':
                print("  Suggested Activities:")
                print("  - Walking Exercise (FITNESS_TRAINING, BEGINNER)")
                print("  - Light Jogging (FITNESS_TRAINING, BEGINNER)")
            elif row[0] == 'Light Movement':
                print("  Suggested Activities:")
                print("  - Gentle Walking Cool-down (COOL_DOWN, BEGINNER)")
                print("  - Light Stretching (COOL_DOWN, BEGINNER)")
            elif row[0] == 'Running':
                print("  Suggested Activities:")
                print("  - Basic Running Form (SKILL_DEVELOPMENT, BEGINNER)")
                print("  - Interval Running (FITNESS_TRAINING, INTERMEDIATE)")
            elif row[0] == 'Volleyball':
                print("  Suggested Activities:")
                print("  - Volleyball Bumping (SKILL_DEVELOPMENT, BEGINNER)")
                print("  - Volleyball Setting (SKILL_DEVELOPMENT, INTERMEDIATE)")
                print("  - Volleyball Game (GAME, INTERMEDIATE)")

if __name__ == "__main__":
    asyncio.run(validate_data()) 