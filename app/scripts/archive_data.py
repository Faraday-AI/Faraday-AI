#!/usr/bin/env python3
"""
PostgreSQL Data Archiving System
Archives old data to improve performance while maintaining data integrity
"""

import os
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.core.database import SessionLocal

class DataArchivingSystem:
    def __init__(self):
        self.session = SessionLocal()
        self.archive_retention_days = {
            'activity_logs': 365,      # Keep 1 year of activity logs
            'progress': 1095,          # Keep 3 years of progress (legal requirement)
            'student_activity_performances': 365,  # Keep 1 year
            'movement_analysis_analyses': 180,      # Keep 6 months
            'routine_performance_metrics': 365,     # Keep 1 year
        }
        
    def analyze_archiving_candidates(self):
        """Analyze which tables are candidates for archiving"""
        print("📊 Analyzing Archiving Candidates...")
        print("=" * 50)
        
        for table_name, retention_days in self.archive_retention_days.items():
            try:
                # Check if table exists and has data
                result = self.session.execute(text(f"""
                    SELECT 
                        COUNT(*) as total_rows,
                        MIN(created_at) as oldest_record,
                        MAX(created_at) as newest_record
                    FROM {table_name}
                    WHERE created_at IS NOT NULL
                """)).fetchone()
                
                if result and result.total_rows > 0:
                    oldest_date = result.oldest_record
                    cutoff_date = datetime.now() - timedelta(days=retention_days)
                    
                    # Count records that would be archived
                    archive_count = self.session.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM {table_name}
                        WHERE created_at < :cutoff_date
                    """), {'cutoff_date': cutoff_date}).scalar()
                    
                    print(f"📋 {table_name}:")
                    print(f"   Total rows: {result.total_rows:,}")
                    print(f"   Oldest record: {oldest_date}")
                    print(f"   Records to archive: {archive_count:,} (older than {cutoff_date.strftime('%Y-%m-%d')})")
                    print(f"   Retention: {retention_days} days")
                    print()
                    
            except Exception as e:
                print(f"⚠️  Could not analyze {table_name}: {e}")
                
    def create_archive_tables(self):
        """Create archive tables for each candidate"""
        print("🗄️  Creating Archive Tables...")
        print("=" * 40)
        
        for table_name in self.archive_retention_days.keys():
            try:
                # Check if archive table already exists
                exists = self.session.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table_name}_archive'
                    )
                """)).scalar()
                
                if not exists:
                    # Create archive table with same structure
                    self.session.execute(text(f"""
                        CREATE TABLE {table_name}_archive (LIKE {table_name} INCLUDING ALL)
                    """))
                    self.session.commit()
                    print(f"✅ Created {table_name}_archive")
                else:
                    print(f"ℹ️  {table_name}_archive already exists")
                    
            except Exception as e:
                print(f"❌ Error creating {table_name}_archive: {e}")
                self.session.rollback()
                
    def archive_old_data(self, dry_run=True):
        """Archive old data based on retention policies"""
        print(f"📦 Archiving Old Data ({'DRY RUN' if dry_run else 'LIVE RUN'})...")
        print("=" * 50)
        
        for table_name, retention_days in self.archive_retention_days.items():
            try:
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                # Count records to archive
                count = self.session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM {table_name}
                    WHERE created_at < :cutoff_date
                """), {'cutoff_date': cutoff_date}).scalar()
                
                if count > 0:
                    print(f"📋 {table_name}: {count:,} records to archive")
                    
                    if not dry_run:
                        # Move data to archive table
                        self.session.execute(text(f"""
                            INSERT INTO {table_name}_archive 
                            SELECT * FROM {table_name}
                            WHERE created_at < :cutoff_date
                        """), {'cutoff_date': cutoff_date})
                        
                        # Delete from main table
                        self.session.execute(text(f"""
                            DELETE FROM {table_name}
                            WHERE created_at < :cutoff_date
                        """), {'cutoff_date': cutoff_date})
                        
                        self.session.commit()
                        print(f"✅ Archived {count:,} records from {table_name}")
                    else:
                        print(f"🔍 Would archive {count:,} records from {table_name}")
                else:
                    print(f"ℹ️  {table_name}: No records to archive")
                    
            except Exception as e:
                print(f"❌ Error archiving {table_name}: {e}")
                self.session.rollback()
                
    def optimize_archived_tables(self):
        """Optimize archived tables for storage"""
        print("🔧 Optimizing Archived Tables...")
        print("=" * 40)
        
        for table_name in self.archive_retention_days.keys():
            archive_table = f"{table_name}_archive"
            try:
                # Check if archive table has data
                count = self.session.execute(text(f"SELECT COUNT(*) FROM {archive_table}")).scalar()
                
                if count > 0:
                    # Run VACUUM and ANALYZE on archive table
                    self.session.execute(text(f"VACUUM ANALYZE {archive_table}"))
                    self.session.commit()
                    print(f"✅ Optimized {archive_table} ({count:,} records)")
                else:
                    print(f"ℹ️  {archive_table}: No data to optimize")
                    
            except Exception as e:
                print(f"❌ Error optimizing {archive_table}: {e}")
                
    def generate_archiving_report(self):
        """Generate a comprehensive archiving report"""
        print("📊 Archiving Report")
        print("=" * 30)
        
        total_main_size = 0
        total_archive_size = 0
        
        for table_name in self.archive_retention_days.keys():
            try:
                # Main table size
                main_size = self.session.execute(text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
                """)).scalar()
                
                # Archive table size
                archive_size = self.session.execute(text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table_name}_archive'))
                """)).scalar()
                
                print(f"📋 {table_name}:")
                print(f"   Main table: {main_size}")
                print(f"   Archive table: {archive_size}")
                print()
                
            except Exception as e:
                print(f"⚠️  Could not get size for {table_name}: {e}")
                
    def run_archiving_process(self, dry_run=True):
        """Run complete archiving process"""
        print(f"🚀 Starting Data Archiving Process...")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE RUN'}")
        print("=" * 60)
        
        try:
            self.analyze_archiving_candidates()
            self.create_archive_tables()
            self.archive_old_data(dry_run=dry_run)
            
            if not dry_run:
                self.optimize_archived_tables()
                
            self.generate_archiving_report()
            
            print(f"\n✅ Archiving process complete!")
            if dry_run:
                print(f"💡 Run with dry_run=False to perform actual archiving")
                
        except Exception as e:
            print(f"❌ Archiving error: {e}")
        finally:
            self.session.close()

if __name__ == "__main__":
    import sys
    
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        dry_run = False
        print("⚠️  LIVE MODE: This will actually archive data!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cancelled")
            exit(1)
    
    archiver = DataArchivingSystem()
    archiver.run_archiving_process(dry_run=dry_run)
