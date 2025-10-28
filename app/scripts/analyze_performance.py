#!/usr/bin/env python3
"""
PostgreSQL Query Performance Analysis and Optimization
Analyzes slow queries and suggests performance improvements
"""

import os
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.core.database import SessionLocal

class QueryPerformanceAnalyzer:
    def __init__(self):
        self.session = SessionLocal()
        
    def analyze_slow_queries(self):
        """Analyze queries that might be slow based on table access patterns"""
        print("🔍 Analyzing Query Performance Patterns...")
        print("=" * 60)
        
        # 1. Most accessed tables
        table_access = self.session.execute(text("""
            SELECT 
                schemaname,
                relname as table_name,
                seq_scan,
                seq_tup_read,
                idx_scan,
                idx_tup_fetch,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes
            FROM pg_stat_user_tables 
            ORDER BY (seq_tup_read + idx_tup_fetch) DESC
            LIMIT 10
        """)).fetchall()
        
        print("📊 Most Accessed Tables:")
        for table in table_access:
            seq_reads = table.seq_tup_read or 0
            idx_reads = table.idx_tup_fetch or 0
            total_reads = seq_reads + idx_reads
            seq_scans = table.seq_scan or 0
            idx_scans = table.idx_scan or 0
            print(f"  - {table.table_name}: {total_reads:,} reads ({seq_scans} seq scans, {idx_scans} idx scans)")
            
        # 2. Tables with high sequential scan ratio (potential optimization targets)
        seq_scan_heavy = self.session.execute(text("""
            SELECT 
                relname as table_name,
                COALESCE(seq_scan, 0) as seq_scan,
                COALESCE(idx_scan, 0) as idx_scan,
                CASE 
                    WHEN COALESCE(seq_scan, 0) + COALESCE(idx_scan, 0) = 0 THEN 0
                    ELSE ROUND(100.0 * COALESCE(seq_scan, 0) / (COALESCE(seq_scan, 0) + COALESCE(idx_scan, 0)), 2)
                END as seq_scan_percentage
            FROM pg_stat_user_tables 
            WHERE COALESCE(seq_scan, 0) + COALESCE(idx_scan, 0) > 0
            ORDER BY seq_scan_percentage DESC
            LIMIT 10
        """)).fetchall()
        
        print(f"\n⚠️  Tables with High Sequential Scan Ratio:")
        for table in seq_scan_heavy:
            if table.seq_scan_percentage > 50:
                print(f"  - {table.table_name}: {table.seq_scan_percentage}% seq scans ({table.seq_scan}/{table.idx_scan})")
                
        # 3. Missing indexes analysis
        self.analyze_missing_indexes()
        
        # 4. Table bloat analysis
        self.analyze_table_bloat()
        
    def analyze_missing_indexes(self):
        """Suggest indexes based on foreign key patterns and common queries"""
        print(f"\n🔍 Missing Index Analysis:")
        
        # Find tables with foreign keys that might need indexes
        fk_analysis = self.session.execute(text("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """)).fetchall()
        
        print("🔗 Foreign Key Relationships (potential index candidates):")
        for fk in fk_analysis[:15]:  # Show first 15
            print(f"  - {fk.table_name}.{fk.column_name} -> {fk.foreign_table_name}.{fk.foreign_column_name}")
            
    def analyze_table_bloat(self):
        """Analyze table bloat and suggest maintenance"""
        print(f"\n📈 Table Bloat Analysis:")
        
        # Get table sizes and row counts
        table_stats = self.session.execute(text("""
            SELECT 
                schemaname,
                relname as tablename,
                n_tup_ins as total_inserts,
                n_tup_upd as total_updates,
                n_tup_del as total_deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                CASE 
                    WHEN n_live_tup + n_dead_tup = 0 THEN 0
                    ELSE ROUND(100.0 * n_dead_tup / (n_live_tup + n_dead_tup), 2)
                END as dead_tuple_percentage
            FROM pg_stat_user_tables 
            WHERE n_live_tup + n_dead_tup > 1000  -- Only tables with significant data
            ORDER BY dead_tuple_percentage DESC
            LIMIT 10
        """)).fetchall()
        
        print("🗑️  Tables with High Dead Tuple Ratio:")
        for table in table_stats:
            if table.dead_tuple_percentage > 10:
                print(f"  - {table.tablename}: {table.dead_tuple_percentage}% dead tuples ({table.dead_tuples:,}/{table.live_tuples:,})")
                
    def suggest_optimizations(self):
        """Suggest specific optimizations based on analysis"""
        print(f"\n💡 Optimization Suggestions:")
        print("=" * 40)
        
        suggestions = [
            "1. Add indexes on frequently queried foreign key columns",
            "2. Consider partial indexes for commonly filtered columns",
            "3. Run VACUUM ANALYZE on tables with high dead tuple ratios",
            "4. Monitor query execution plans with EXPLAIN ANALYZE",
            "5. Consider partitioning for very large tables (>1M rows)",
            "6. Use covering indexes for SELECT-only queries",
            "7. Consider materialized views for complex aggregations"
        ]
        
        for suggestion in suggestions:
            print(f"  {suggestion}")
            
    def generate_index_suggestions(self):
        """Generate specific index creation statements"""
        print(f"\n📝 Suggested Index Creation Statements:")
        print("=" * 50)
        
        # Common patterns for Faraday AI tables
        index_suggestions = [
            "-- Performance indexes for student queries",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_students_school_id ON students(school_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_students_grade_level ON students(grade_level);",
            "",
            "-- Performance indexes for enrollment queries", 
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_enrollments_student_school ON student_school_enrollments(student_id, school_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_course_enrollments_active ON course_enrollments(course_id) WHERE active = true;",
            "",
            "-- Performance indexes for activity queries",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_activity_logs_student_date ON activity_logs(student_id, created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_progress_student_subject ON progress(student_id, subject);",
            "",
            "-- Performance indexes for analytics queries",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_events_student_date ON analytics_events(student_id, created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_events_event_type ON analytics_events(event_type, created_at);"
        ]
        
        for suggestion in index_suggestions:
            print(suggestion)
            
    def run_performance_analysis(self):
        """Run complete performance analysis"""
        try:
            self.analyze_slow_queries()
            self.suggest_optimizations()
            self.generate_index_suggestions()
            
            print(f"\n✅ Performance analysis complete!")
            print(f"📊 Run this analysis regularly to track performance trends")
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
        finally:
            self.session.close()

if __name__ == "__main__":
    analyzer = QueryPerformanceAnalyzer()
    analyzer.run_performance_analysis()
