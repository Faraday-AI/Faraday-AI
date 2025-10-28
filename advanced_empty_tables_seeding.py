#!/usr/bin/env python3
"""
Advanced Empty Tables Seeding Script
Handles complex foreign key relationships, UUIDs, and data type requirements
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the Python path
sys.path.append('/app')

def get_database_connection():
    """Get database connection"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://faraday:faraday@localhost:5432/faraday_db')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def get_empty_tables(session):
    """Get list of empty tables"""
    try:
        # Get all tables
        inspector = inspect(session.bind)
        all_tables = inspector.get_table_names()
        
        empty_tables = []
        for table in all_tables:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar_one()
                if count == 0:
                    empty_tables.append(table)
            except Exception as e:
                print(f"  ⚠️  Could not check {table}: {e}")
                continue
        
        return empty_tables
    except Exception as e:
        print(f"❌ Error getting empty tables: {e}")
        return []

def get_table_schema(session, table_name):
    """Get detailed table schema including foreign key information"""
    try:
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        schema = {}
        for col in columns:
            schema[col['name']] = {
                'type': str(col['type']),
                'nullable': col['nullable'],
                'primary_key': col.get('primary_key', False),
                'autoincrement': col.get('autoincrement', False),
                'default': col.get('default'),
                'unique': False  # We'll check this separately
            }
        
        # Add foreign key information
        for fk in foreign_keys:
            for col_name in fk['constrained_columns']:
                if col_name in schema:
                    schema[col_name]['foreign_key'] = {
                        'referenced_table': fk['referred_table'],
                        'referenced_columns': fk['referred_columns']
                    }
        
        # Check for unique constraints
        try:
            unique_constraints = inspector.get_unique_constraints(table_name)
            for constraint in unique_constraints:
                for col_name in constraint['column_names']:
                    if col_name in schema:
                        schema[col_name]['unique'] = True
        except:
            pass
        
        return schema
    except Exception as e:
        print(f"  ⚠️  Could not get schema for {table_name}: {e}")
        return None

def get_existing_ids(session, table_name, column_name='id', limit=100):
    """Get existing IDs from a table"""
    try:
        result = session.execute(text(f"SELECT {column_name} FROM {table_name} LIMIT {limit}"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def get_existing_uuids(session, table_name, column_name='id', limit=100):
    """Get existing UUIDs from a table"""
    try:
        result = session.execute(text(f"SELECT {column_name}::text FROM {table_name} LIMIT {limit}"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def create_missing_reference(session, table_name, column_name, referenced_table, referenced_column='id'):
    """Create a missing reference by inserting a record in the referenced table"""
    try:
        # Get schema of referenced table
        schema = get_table_schema(session, referenced_table)
        if not schema:
            return None
        
        # Generate minimal data for the referenced table
        data = {}
        for col_name, col_info in schema.items():
            if col_name == referenced_column:
                continue  # Skip the primary key
            
            if col_name.endswith('_id') and 'foreign_key' in col_info:
                # Skip foreign keys for now to avoid circular dependencies
                continue
            
            if not col_info['nullable'] and col_name != referenced_column:
                if 'UUID' in col_info['type']:
                    data[col_name] = f"gen_random_uuid()"
                elif 'SERIAL' in col_info['type'] or col_info.get('autoincrement'):
                    continue  # Let database generate
                elif 'TEXT' in col_info['type'] or 'VARCHAR' in col_info['type']:
                    data[col_name] = f"'{table_name}_{col_name}_ref'"
                elif 'INTEGER' in col_info['type']:
                    data[col_name] = 1
                elif 'BOOLEAN' in col_info['type']:
                    data[col_name] = True
                elif 'JSON' in col_info['type']:
                    data[col_name] = "'{}'"
                else:
                    data[col_name] = f"'{col_name}_ref'"
        
        # Insert the record
        if data:
            columns = list(data.keys())
            values = list(data.values())
            query = f"INSERT INTO {referenced_table} ({', '.join(columns)}) VALUES ({', '.join(values)}) RETURNING {referenced_column}"
            result = session.execute(text(query))
            return result.scalar_one()
        else:
            # If no data needed, just insert with default values
            query = f"INSERT INTO {referenced_table} DEFAULT VALUES RETURNING {referenced_column}"
            result = session.execute(text(query))
            return result.scalar_one()
            
    except Exception as e:
        print(f"    ⚠️  Could not create reference in {referenced_table}: {e}")
        return None

def generate_advanced_data(session, table_name, schema, existing_ids_cache):
    """Generate advanced data that handles all complex requirements"""
    data = []
    
    for i in range(5):  # Generate 5 records
        record = {}
        
        for col_name, col_info in schema.items():
            col_type = col_info['type']
            is_nullable = col_info['nullable']
            is_primary_key = col_info['primary_key']
            is_auto_increment = col_info.get('autoincrement', False)
            
            # Skip primary key if it's auto-generated
            if is_primary_key and ('UUID' in col_type or is_auto_increment):
                continue
            
            # Handle foreign keys
            if 'foreign_key' in col_info:
                fk_info = col_info['foreign_key']
                ref_table = fk_info['referenced_table']
                ref_column = fk_info['referenced_columns'][0]
                
                # Check if we have existing IDs for this reference
                cache_key = f"{ref_table}_{ref_column}"
                if cache_key not in existing_ids_cache:
                    if 'UUID' in col_type:
                        existing_ids_cache[cache_key] = get_existing_uuids(session, ref_table, ref_column)
                    else:
                        existing_ids_cache[cache_key] = get_existing_ids(session, ref_table, ref_column)
                
                existing_refs = existing_ids_cache[cache_key]
                
                if existing_refs:
                    record[col_name] = random.choice(existing_refs)
                else:
                    # Create a missing reference
                    new_ref_id = create_missing_reference(session, table_name, col_name, ref_table, ref_column)
                    if new_ref_id:
                        record[col_name] = new_ref_id
                        existing_ids_cache[cache_key].append(new_ref_id)
                    else:
                        if is_nullable:
                            continue  # Skip nullable foreign keys we can't resolve
                        else:
                            # For non-nullable foreign keys, we must have a value
                            record[col_name] = 1 if 'INTEGER' in col_type else '00000000-0000-0000-0000-000000000000'
            
            # Handle primary key
            elif is_primary_key:
                if 'UUID' in col_type:
                    record[col_name] = f"gen_random_uuid()"
                elif is_auto_increment:
                    continue  # Let database generate
                else:
                    record[col_name] = i + 1
            
            # Handle regular columns
            else:
                if not is_nullable or random.random() > 0.1:  # 90% chance to populate non-nullable
                    if 'UUID' in col_type:
                        record[col_name] = f"gen_random_uuid()"
                    elif 'TEXT' in col_type or 'VARCHAR' in col_type:
                        if col_name in ['name', 'title']:
                            record[col_name] = f"{table_name.replace('_', ' ').title()} {i+1}"
                        elif col_name in ['description', 'content', 'message']:
                            if 'JSON' in col_type:
                                record[col_name] = json.dumps({"content": f"Description for {table_name} {i+1}", "type": "test"})
                            else:
                                record[col_name] = f"Description for {table_name} {i+1}"
                        elif col_name == 'email':
                            record[col_name] = f"user{i+1}@example.com"
                        else:
                            record[col_name] = f"{col_name}_{i+1}"
                    elif 'INTEGER' in col_type or 'BIGINT' in col_type:
                        if col_name in ['rating', 'score', 'count', 'level']:
                            record[col_name] = random.randint(1, 10)
                        elif col_name in ['percentage', 'completion_percentage']:
                            record[col_name] = random.randint(0, 100)
                        else:
                            record[col_name] = random.randint(1, 100)
                    elif 'NUMERIC' in col_type or 'DECIMAL' in col_type:
                        record[col_name] = round(random.uniform(0.0, 100.0), 2)
                    elif 'BOOLEAN' in col_type:
                        record[col_name] = random.choice([True, False])
                    elif 'JSON' in col_type:
                        record[col_name] = json.dumps({"key": f"value_{i+1}", "type": "test"})
                    elif 'ARRAY' in col_type:
                        if 'TEXT' in col_type or 'VARCHAR' in col_type:
                            record[col_name] = f"{{item_{i+1},item_{i+2}}}"
                        else:
                            record[col_name] = f"{{{i+1},{i+2}}}"
                    elif 'TIMESTAMP' in col_type or 'DATETIME' in col_type:
                        record[col_name] = datetime.now() - timedelta(days=random.randint(1, 30))
                    elif 'DATE' in col_type:
                        record[col_name] = (datetime.now() - timedelta(days=random.randint(1, 30))).date()
                    elif col_name in ['status']:
                        record[col_name] = random.choice(['ACTIVE', 'INACTIVE', 'PENDING', 'COMPLETED'])
                    elif col_name in ['is_active', 'is_enabled', 'is_public']:
                        record[col_name] = random.choice([True, False])
                    else:
                        record[col_name] = f"value_{i+1}"
        
        data.append(record)
    
    return data

def insert_advanced_data(session, table_name, data):
    """Insert data with advanced error handling and recovery"""
    if not data:
        return 0
    
    try:
        # Get table schema to determine primary key type
        schema = get_table_schema(session, table_name)
        if not schema:
            return 0
        
        # Find primary key column
        pk_column = None
        pk_is_uuid = False
        for col_name, col_info in schema.items():
            if col_info['primary_key']:
                pk_column = col_name
                pk_is_uuid = 'UUID' in col_info['type']
                break
        
        # Build the INSERT query
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join([f':{col}' for col in columns])
        
        # Handle UUID primary keys
        if pk_is_uuid and pk_column and pk_column not in columns:
            columns_str = f'{pk_column}, {columns_str}'
            placeholders = f'gen_random_uuid(), {placeholders}'
        
        base_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Try upsert first
        if pk_column:
            update_columns = [f"{col} = EXCLUDED.{col}" for col in columns if col != pk_column]
            if update_columns:
                upsert_query = f"{base_query} ON CONFLICT ({pk_column}) DO UPDATE SET {', '.join(update_columns)}"
            else:
                upsert_query = f"{base_query} ON CONFLICT ({pk_column}) DO NOTHING"
        else:
            upsert_query = base_query
        
        # Execute the query
        try:
            for record in data:
                session.execute(text(upsert_query), record)
        except Exception as upsert_error:
            print(f"    ⚠️  Upsert failed, trying simple insert: {upsert_error}")
            for record in data:
                session.execute(text(base_query), record)
        
        return len(data)
        
    except Exception as e:
        print(f"    ⚠️  Error inserting into {table_name}: {e}")
        return 0

def advanced_empty_tables_seeding():
    """Main function to seed empty tables with advanced logic"""
    print("🚀 Starting Advanced Empty Tables Seeding...")
    
    session = get_database_connection()
    
    try:
        # Get empty tables
        empty_tables = get_empty_tables(session)
        if not empty_tables:
            print("✅ No empty tables found!")
            return
        
        print(f"📋 Found {len(empty_tables)} empty tables to seed")
        
        # Cache for existing IDs to avoid repeated queries
        existing_ids_cache = {}
        
        # Seed each empty table
        seeded_count = 0
        for table in empty_tables:
            try:
                print(f"  🌱 Seeding {table}...")
                
                # Clear any transaction issues
                session.rollback()
                
                # Get table schema
                schema = get_table_schema(session, table)
                if not schema:
                    print(f"  ⚠️  {table}: Could not get schema, skipping")
                    continue
                
                # Generate advanced data
                data = generate_advanced_data(session, table, schema, existing_ids_cache)
                
                if data:
                    count = insert_advanced_data(session, table, data)
                    if count > 0:
                        # Commit this table's data immediately
                        session.commit()
                        print(f"  ✅ {table}: {count} records")
                        seeded_count += 1
                    else:
                        print(f"  ⚠️  {table}: No data inserted")
                        session.rollback()
                else:
                    print(f"  ⚠️  {table}: No suitable data generated")
                    
            except Exception as e:
                print(f"  ❌ {table}: {e}")
                session.rollback()
        
        print(f"\n🎉 Advanced seeding completed! Seeded {seeded_count} empty tables successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    advanced_empty_tables_seeding()
