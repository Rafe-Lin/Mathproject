import sqlite3
import os

# Define database path
db_path = os.path.join(os.getcwd(), 'instance', 'kumon_math.db')

def run_migration():
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return

    print(f"🔗 Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List of columns to add
    migrations = [
        ("raw_output_length", "INTEGER DEFAULT 0"),
        ("perfect_utils_length", "INTEGER DEFAULT 0"),
        ("gpu_usage", "FLOAT DEFAULT 0.0"),
        ("gpuram_usage", "FLOAT DEFAULT 0.0"),
        ("error_category", "TEXT")
    ]

    for col_name, col_def in migrations:
        try:
            sql = f"ALTER TABLE experiment_log ADD COLUMN {col_name} {col_def};"
            cursor.execute(sql)
            print(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"⚠️ Column already exists: {col_name}")
            else:
                print(f"❌ Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("🏁 Migration tasks completed.")

if __name__ == "__main__":
    run_migration()
