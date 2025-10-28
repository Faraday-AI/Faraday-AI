#!/usr/bin/env python3
"""
Seed Resource Categories Data
Creates the default resource categories for the beta teacher system.
"""

import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from app.core.database import DATABASE_URL

def seed_resource_categories():
    """Seed the resource categories with explicit IDs."""
    print("🌱 Seeding resource categories...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Insert resource categories with explicit IDs
        categories = [
            ('00000000-0000-0000-0000-000000000001', 'Lesson Plans', 'Complete lesson plans and instructional materials', 'PE', 'K-12', 'lesson', '#ff6b6b'),
            ('00000000-0000-0000-0000-000000000002', 'Activities', 'Individual activities and games', 'PE', 'K-12', 'activity', '#ff4757'),
            ('00000000-0000-0000-0000-000000000003', 'Worksheets', 'Printable worksheets and handouts', 'PE', 'K-12', 'worksheet', '#ffa502'),
            ('00000000-0000-0000-0000-000000000004', 'Videos', 'Instructional videos and demonstrations', 'PE', 'K-12', 'video', '#2ed573'),
            ('00000000-0000-0000-0000-000000000005', 'Images', 'Photos, diagrams, and visual aids', 'PE', 'K-12', 'image', '#1e90ff'),
            ('00000000-0000-0000-0000-000000000006', 'Audio', 'Music, sound effects, and audio instructions', 'PE', 'K-12', 'audio', '#ff6348'),
            ('00000000-0000-0000-0000-000000000007', 'Presentations', 'PowerPoint presentations and slideshows', 'PE', 'K-12', 'presentation', '#70a1ff'),
            ('00000000-0000-0000-0000-000000000008', 'Assessments', 'Tests, rubrics, and evaluation tools', 'PE', 'K-12', 'assessment', '#ff9ff3'),
            ('00000000-0000-0000-0000-000000000009', 'Equipment Guides', 'Equipment setup and safety guides', 'PE', 'K-12', 'equipment', '#26de81'),
            ('00000000-0000-0000-0000-000000000010', 'Safety Materials', 'Safety protocols and emergency procedures', 'PE', 'K-12', 'safety', '#ff3838'),
            ('00000000-0000-0000-0000-000000000011', 'Health Education', 'Health-related educational materials', 'Health', 'K-12', 'health', '#ff9f43'),
            ('00000000-0000-0000-0000-000000000012', 'Nutrition Resources', 'Nutrition education and healthy eating materials', 'Health', 'K-12', 'nutrition', '#a55eea'),
            ('00000000-0000-0000-0000-000000000013', 'Mental Health', 'Mental wellness and stress management resources', 'Health', '6-12', 'mind', '#26d0ce'),
            ('00000000-0000-0000-0000-000000000014', 'Drivers Education', 'Driving instruction and safety materials', 'Drivers Ed', '9-12', 'car', '#ff6b6b'),
            ('00000000-0000-0000-0000-000000000015', 'Traffic Safety', 'Traffic rules and road safety resources', 'Drivers Ed', '9-12', 'traffic', '#ffa502'),
            ('00000000-0000-0000-0000-000000000016', 'Vehicle Maintenance', 'Vehicle care and maintenance guides', 'Drivers Ed', '9-12', 'wrench', '#2ed573')
        ]
        
        for category in categories:
            conn.execute(text("""
                INSERT INTO resource_categories (id, name, description, subject, grade_level_range, icon_name, color_code) 
                VALUES (:id, :name, :description, :subject, :grade_level_range, :icon_name, :color_code)
                ON CONFLICT (id) DO NOTHING
            """), {
                'id': category[0],
                'name': category[1],
                'description': category[2],
                'subject': category[3],
                'grade_level_range': category[4],
                'icon_name': category[5],
                'color_code': category[6]
            })
        
        conn.commit()
        print(f"✅ Seeded {len(categories)} resource categories")

if __name__ == "__main__":
    seed_resource_categories()
