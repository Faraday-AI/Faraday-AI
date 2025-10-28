#!/usr/bin/env python3
"""
Seed Assessment Categories Data
Creates the default assessment categories for the beta teacher system.
"""

import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from app.core.database import get_database_url

def seed_assessment_categories():
    """Seed the assessment categories with explicit IDs."""
    print("🌱 Seeding assessment categories...")
    
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        # Insert assessment categories with explicit IDs
        categories = [
            ('00000000-0000-0000-0000-000000000001', 'Skill Assessment', 'Assessment of specific physical skills and techniques', 'PE', 'K-12', 'skill', '#ff6b6b'),
            ('00000000-0000-0000-0000-000000000002', 'Fitness Assessment', 'Assessment of cardiovascular and muscular fitness', 'PE', 'K-12', 'fitness', '#ff4757'),
            ('00000000-0000-0000-0000-000000000003', 'Knowledge Assessment', 'Assessment of theoretical knowledge and understanding', 'PE', 'K-12', 'knowledge', '#ffa502'),
            ('00000000-0000-0000-0000-000000000004', 'Behavior Assessment', 'Assessment of sportsmanship, teamwork, and behavior', 'PE', 'K-12', 'behavior', '#2ed573'),
            ('00000000-0000-0000-0000-000000000005', 'Safety Assessment', 'Assessment of safety awareness and practices', 'PE', 'K-12', 'safety', '#1e90ff'),
            ('00000000-0000-0000-0000-000000000006', 'Performance Assessment', 'Assessment of overall performance and participation', 'PE', 'K-12', 'performance', '#ff6348'),
            ('00000000-0000-0000-0000-000000000007', 'Peer Assessment', 'Student-to-student assessment activities', 'PE', '3-12', 'peer', '#70a1ff'),
            ('00000000-0000-0000-0000-000000000008', 'Self Assessment', 'Student self-reflection and self-evaluation', 'PE', 'K-12', 'self', '#ff9ff3'),
            ('00000000-0000-0000-0000-000000000009', 'Health Knowledge', 'Assessment of health-related knowledge and concepts', 'Health', 'K-12', 'health', '#26de81'),
            ('00000000-0000-0000-0000-000000000010', 'Safety Knowledge', 'Assessment of safety knowledge and practices', 'Health', 'K-12', 'safety', '#ff3838'),
            ('00000000-0000-0000-0000-000000000011', 'Nutrition Knowledge', 'Assessment of nutrition and healthy eating knowledge', 'Health', 'K-12', 'nutrition', '#ff9f43'),
            ('00000000-0000-0000-0000-000000000012', 'Mental Health Awareness', 'Assessment of mental health knowledge and awareness', 'Health', '6-12', 'mind', '#a55eea'),
            ('00000000-0000-0000-0000-000000000013', 'Driving Knowledge', 'Assessment of driving rules and regulations', 'Drivers Ed', '9-12', 'car', '#26d0ce'),
            ('00000000-0000-0000-0000-000000000014', 'Traffic Safety', 'Assessment of traffic safety knowledge', 'Drivers Ed', '9-12', 'traffic', '#ff6b6b'),
            ('00000000-0000-0000-0000-000000000015', 'Vehicle Knowledge', 'Assessment of vehicle operation and maintenance', 'Drivers Ed', '9-12', 'wrench', '#ffa502')
        ]
        
        for category in categories:
            conn.execute(text("""
                INSERT INTO assessment_categories (id, name, description, subject, grade_level_range, icon_name, color_code) 
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
        print(f"✅ Seeded {len(categories)} assessment categories")

if __name__ == "__main__":
    seed_assessment_categories()
