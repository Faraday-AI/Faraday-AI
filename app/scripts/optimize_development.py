#!/usr/bin/env python3
"""
PostgreSQL Development Optimization Script
Focuses on Performance Indexes, Regular Cleanup, and Growth Monitoring
"""

import os
import time
from datetime import datetime
from sqlalchemy import create_engine, text
from app.core.database import SessionLocal

class DevelopmentOptimizer:
    def __init__(self):
        self.session = SessionLocal()
        
    def apply_performance_indexes(self):
        """Apply suggested performance indexes for development"""
        print("🚀 Applying Performance Indexes...")
        print("=" * 50)
        
        # High-impact indexes based on analysis (using regular CREATE for development)
        indexes = [
            # Student queries (most accessed)
            "CREATE INDEX IF NOT EXISTS idx_students_school_id ON students(school_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_grade_level ON students(grade_level)",
            
            # Enrollment queries (2.5M reads!)
            "CREATE INDEX IF NOT EXISTS idx_enrollments_student_school ON student_school_enrollments(student_id, school_id)",
            "CREATE INDEX IF NOT EXISTS idx_enrollments_active ON student_school_enrollments(active) WHERE active = true",
            
            # Activity queries
            "CREATE INDEX IF NOT EXISTS idx_activity_logs_student_date ON activity_logs(student_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_activities_category ON activities(category_id)",
            
            # Performance queries
            "CREATE INDEX IF NOT EXISTS idx_performances_student_activity ON student_activity_performances(student_id, activity_id)",
            "CREATE INDEX IF NOT EXISTS idx_performances_date ON student_activity_performances(created_at)",
            
            # Progress queries
            "CREATE INDEX IF NOT EXISTS idx_progress_student_subject ON progress(student_id, subject)",
            "CREATE INDEX IF NOT EXISTS idx_progress_date ON progress(created_at)",
        ]
        
        applied_count = 0
        for index_sql in indexes:
            try:
                # Regular CREATE INDEX works in transactions
                self.session.execute(text(index_sql))
                self.session.commit()
                index_name = index_sql.split("idx_")[1].split(" ")[0]
                print(f"✅ Applied: idx_{index_name}")
                applied_count += 1
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️  Already exists: {index_sql.split('idx_')[1].split(' ')[0]}")
                else:
                    print(f"❌ Error: {e}")
                self.session.rollback()
        
        print(f"\n📊 Applied {applied_count} new indexes")
        
    def regular_cleanup(self):
        """Perform regular database cleanup"""
        print("\n🧹 Performing Regular Cleanup...")
        print("=" * 40)
        
        # Tables that showed dead tuples in analysis
        cleanup_tables = [
            'student_school_enrollments',  # 11.21% dead tuples
            'students',
            'activities', 
            'student_activity_performances',
            'progress'
        ]
        
        for table in cleanup_tables:
            try:
                # Check if table exists
                exists = self.session.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    )
                """)).scalar()
                
                if exists:
                    # Run VACUUM ANALYZE
                    self.session.execute(text(f"VACUUM ANALYZE {table}"))
                    self.session.commit()
                    print(f"✅ Cleaned: {table}")
                else:
                    print(f"ℹ️  Table not found: {table}")
                    
            except Exception as e:
                print(f"❌ Error cleaning {table}: {e}")
                self.session.rollback()
        
        print("🧹 Cleanup complete!")
        
    def monitor_growth(self):
        """Monitor database and table growth"""
        print("\n📈 Monitoring Database Growth...")
        print("=" * 40)
        
        try:
            # Overall database size
            db_size = self.session.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """)).scalar()
            print(f"💾 Total Database Size: {db_size}")
            
            # Top 10 tables by size
            table_sizes = self.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10
            """)).fetchall()
            
            print(f"\n📋 Top 10 Tables by Size:")
            for table in table_sizes:
                print(f"  - {table.tablename}: {table.size} (table: {table.table_size}, indexes: {table.index_size})")
            
            # Growth indicators
            print(f"\n📊 Growth Indicators:")
            
            # Row counts for key tables
            key_tables = ['students', 'student_school_enrollments', 'activities', 'student_activity_performances']
            for table in key_tables:
                try:
                    count = self.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"  - {table}: {count:,} rows")
                except:
                    print(f"  - {table}: Table not found")
            
            # Dead tuple analysis
            dead_tuples = self.session.execute(text("""
                SELECT 
                    relname as table_name,
                    n_dead_tup as dead_tuples,
                    n_live_tup as live_tuples,
                    CASE 
                        WHEN n_live_tup + n_dead_tup = 0 THEN 0
                        ELSE ROUND(100.0 * n_dead_tup / (n_live_tup + n_dead_tup), 2)
                    END as dead_percentage
                FROM pg_stat_user_tables 
                WHERE n_dead_tup > 0
                ORDER BY dead_percentage DESC
                LIMIT 5
            """)).fetchall()
            
            if dead_tuples:
                print(f"\n🗑️  Dead Tuple Analysis:")
                for table in dead_tuples:
                    if table.dead_percentage > 5:  # Only show significant dead tuples
                        print(f"  - {table.table_name}: {table.dead_percentage}% dead ({table.dead_tuples:,}/{table.live_tuples:,})")
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            
    def run_optimization(self):
        """Run complete development optimization"""
        print("🔧 Faraday AI Development Optimization")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            self.apply_performance_indexes()
            self.regular_cleanup()
            self.monitor_growth()
            
            print(f"\n✅ Development optimization complete!")
            print(f"💡 Run this script regularly during development")
            print(f"📊 Monitor growth trends over time")
            
        except Exception as e:
            print(f"❌ Optimization error: {e}")
        finally:
            self.session.close()

if __name__ == "__main__":
    optimizer = DevelopmentOptimizer()
    optimizer.run_optimization()
