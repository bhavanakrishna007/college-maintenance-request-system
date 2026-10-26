"""
Database Setup Script for College Maintenance and Request System
Course: 24CS305 / CS3106 - DBMS Laboratory
Executes schema.sql and sample_data.sql into MySQL.
"""

import sys
import os
import mysql.connector
from mysql.connector import errorcode

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "password"
DB_NAME = "college_maintenance_db"

def execute_sql_file(cursor, filepath):
    print(f"Executing: {os.path.basename(filepath)}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split on DELIMITER statements or standard statements
    # Simple delimiter-aware parser for MySQL scripts
    lines = content.splitlines()
    statements = []
    current_statement = []
    current_delimiter = ';'

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith('DELIMITER'):
            parts = stripped.split()
            if len(parts) >= 2:
                current_delimiter = parts[1]
            continue
        
        # Skip pure comment lines when starting a statement
        if not current_statement and (stripped.startswith('--') or stripped.startswith('/*') or not stripped):
            continue

        current_statement.append(line)
        
        # Check if line ends with delimiter
        if stripped.endswith(current_delimiter):
            # Remove the delimiter from the end
            stmt_text = '\n'.join(current_statement)
            if stmt_text.endswith(current_delimiter):
                stmt_text = stmt_text[:-len(current_delimiter)]
            stmt_text = stmt_text.strip()
            if stmt_text:
                statements.append(stmt_text)
            current_statement = []

    if current_statement:
        stmt_text = '\n'.join(current_statement).strip()
        if stmt_text:
            statements.append(stmt_text)

    executed_count = 0
    for stmt in statements:
        # Strip trailing semicolon if leftover
        clean_stmt = stmt.strip()
        if not clean_stmt:
            continue
        try:
            cursor.execute(clean_stmt)
            executed_count += 1
        except mysql.connector.Error as err:
            print(f"Error executing statement:\n{clean_stmt[:100]}...\nMessage: {err}")
            raise

    print(f"Successfully executed {executed_count} statements from {os.path.basename(filepath)}.")

def main():
    print("=" * 60)
    print("College Maintenance & Request System - Database Setup")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, "schema.sql")
    sample_data_path = os.path.join(script_dir, "sample_data.sql")

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        print("Connected to MySQL server successfully.")
        
        execute_sql_file(cursor, schema_path)
        conn.commit()

        execute_sql_file(cursor, sample_data_path)
        conn.commit()

        # Run verification checks
        cursor.execute("USE college_maintenance_db;")
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        print("\nDatabase Tables Created:")
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{t}`;")
            count = cursor.fetchone()[0]
            print(f"  - {t:<25} : {count} records")

        # Test Stored Procedure and Views
        print("\nTesting Relational View (vw_active_requests):")
        cursor.execute("SELECT tracking_code, issue_title, priority, status, category_name FROM vw_active_requests LIMIT 3;")
        for row in cursor.fetchall():
            print(f"  - [{row[0]}] {row[1]} | Priority: {row[2]} | Status: {row[3]} | Cat: {row[4]}")

        # Test Stored Function
        cursor.execute("SELECT request_id, tracking_code, fn_calculate_request_cost(request_id) AS total_cost FROM maintenance_requests WHERE request_id IN (1, 2, 4);")
        print("\nTesting Stored Function (fn_calculate_request_cost):")
        for row in cursor.fetchall():
            print(f"  - Request {row[1]} (ID {row[0]}): Total Material Cost = Rs. {row[2]}")

        cursor.close()
        conn.close()
        print("\n[SUCCESS] Database initialization completed flawlessly!")

    except mysql.connector.Error as err:
        print(f"\n[ERROR] Database setup failed: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
