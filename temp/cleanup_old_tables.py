# -*- coding: utf-8 -*-
"""
Script to clean up old database tables
Tables to remove: user, user_progress, skill_dependency
"""
import sqlite3
import os

def cleanup_old_tables():
    db_path = 'instance/kumon_math.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    print(f"=== Connecting to database: {db_path} ===\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables to remove
    old_tables = ['user', 'user_progress', 'skill_dependency']
    
    try:
        # Check current tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        print(f"Current tables: {all_tables}\n")
        
        # Process each old table
        for table_name in old_tables:
            if table_name in all_tables:
                print(f"Processing '{table_name}' table...")
                
                # Check record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - Found {count} records")
                
                # Drop the table
                cursor.execute(f'DROP TABLE {table_name}')
                print(f"  - SUCCESS: Dropped '{table_name}' table")
            else:
                print(f"INFO: '{table_name}' table does not exist, skipping")
            print()
        
        conn.commit()
        
        # Verify final state
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        remaining_tables = [row[0] for row in cursor.fetchall()]
        
        print("=== Cleanup Complete ===")
        print(f"Remaining tables: {remaining_tables}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\nDatabase connection closed")

if __name__ == '__main__':
    cleanup_old_tables()
