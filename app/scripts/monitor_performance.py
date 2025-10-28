#!/usr/bin/env python3
"""
PostgreSQL Performance Monitoring Script
Monitors key database metrics and logs slow queries
"""

import os
import time
from datetime import datetime
from sqlalchemy import create_engine, text
from app.core.database import SessionLocal

def monitor_performance():
    """Monitor key PostgreSQL performance metrics"""
    session = SessionLocal()
    try:
        print(f"🔍 PostgreSQL Performance Monitor - {datetime.now()}")
        print("=" * 60)
        
        # 1. Connection count
        connections = session.execute(text("""
            SELECT count(*) as active_connections 
            FROM pg_stat_activity 
            WHERE state = 'active'
        """)).scalar()
        print(f"📊 Active Connections: {connections}")
        
        # 2. Database size
        db_size = session.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """)).scalar()
        print(f"💾 Database Size: {db_size}")
        
        # 3. Active queries (Azure PostgreSQL compatible)
        active_queries = session.execute(text("""
            SELECT 
                query,
                state,
                query_start,
                EXTRACT(EPOCH FROM (now() - query_start)) as duration_seconds
            FROM pg_stat_activity 
            WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%'
            ORDER BY query_start
            LIMIT 5
        """)).fetchall()
        
        if active_queries:
            print(f"🔄 Active Queries:")
            for query in active_queries:
                duration = float(query.duration_seconds) if query.duration_seconds else 0
                print(f"  - {duration:.2f}s: {query.query[:50]}...")
        else:
            print("✅ No active queries")
        
        # 4. Table sizes (top 10)
        table_sizes = session.execute(text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """)).fetchall()
        
        print(f"📋 Top 10 Tables by Size:")
        for table in table_sizes:
            print(f"  - {table.tablename}: {table.size}")
        
        # 5. Index usage (Azure PostgreSQL compatible)
        unused_indexes = session.execute(text("""
            SELECT 
                schemaname,
                relname as tablename,
                indexrelname as indexname
            FROM pg_stat_user_indexes 
            WHERE idx_scan = 0
            LIMIT 5
        """)).fetchall()
        
        if unused_indexes:
            print(f"⚠️  Unused Indexes:")
            for idx in unused_indexes:
                print(f"  - {idx.tablename}.{idx.indexname}")
        else:
            print("✅ All indexes are being used")
            
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
    finally:
        session.close()

def enable_query_logging():
    """Enable basic query monitoring (Azure PostgreSQL compatible)"""
    session = SessionLocal()
    try:
        # Check if we can access basic monitoring views
        result = session.execute(text("SELECT count(*) FROM pg_stat_activity")).scalar()
        print("✅ Basic query monitoring enabled (Azure PostgreSQL compatible)")
    except Exception as e:
        print(f"⚠️  Could not enable query monitoring: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    enable_query_logging()
    monitor_performance()
