import sqlite3
import pandas as pd
import os

# Path to database
db_path = os.path.join('instance', 'math_master.db')

def get_schema_info(db_path):
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_data = []
    
    for table_name in tables:
        table = table_name[0]
        if table == 'sqlite_sequence':
            continue
            
        # Get column info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # Get foreign key info
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks = cursor.fetchall()
        fk_dict = {}
        for fk in fks:
            # id, seq, table, from, to, on_update, on_delete, match
            # fk[3] is 'from' column (in this table), fk[2] is 'table' (referenced table), fk[4] is 'to' column
            fk_dict[fk[3]] = f"{fk[2]}.{fk[4]}"

        for col in columns:
            # cid, name, type, notnull, dflt_value, pk
            col_name = col[1]
            col_type = col[2]
            not_null = bool(col[3])
            default_val = col[4]
            is_pk = bool(col[5])
            
            fk_ref = fk_dict.get(col_name, "")
            
            schema_data.append({
                "Table": table,
                "Column": col_name,
                "Type": col_type,
                "Primary Key": "Yes" if is_pk else "",
                "Nullable": "No" if not_null else "Yes",
                "Default": default_val,
                "Foreign Key": fk_ref
            })
            
    conn.close()
    return schema_data

if __name__ == "__main__":
    print(f"Reading schema from {db_path}...")
    data = get_schema_info(db_path)
    
    if data:
        df = pd.DataFrame(data)
        output_file = "database_schema_split.xlsx"
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Group by Table and write to separate sheets
                unique_tables = df['Table'].unique()
                for table_name in unique_tables:
                    table_df = df[df['Table'] == table_name].copy()
                    # Remove the 'Table' column as it's redundant in the sheet
                    table_df = table_df.drop(columns=['Table'])
                    table_df.to_excel(writer, sheet_name=table_name, index=False)
            
            print(f"Schema successfully saved to {os.path.abspath(output_file)}")
            print(f"Total tables/sheets: {len(unique_tables)}")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
    else:
        print("No data found or database error.")
