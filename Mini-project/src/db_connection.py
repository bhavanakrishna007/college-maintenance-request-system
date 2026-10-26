"""
Database Connection Manager for College Maintenance System
Course: 24CS305 / CS3106 - DBMS Laboratory
Handles MySQL connections, queries, and transaction management.
"""

import mysql.connector
from mysql.connector import Error
from config import load_db_config

def get_connection():
    """Establishes and returns a connection to MySQL database."""
    cfg = load_db_config()
    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            port=int(cfg["port"]),
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            autocommit=False
        )
        return conn
    except Error as e:
        raise ConnectionError(f"Database Connection Error: {e.msg} (Code: {e.errno})")

def test_connection_params(host, port, user, password, database):
    """Tests connection with arbitrary parameters without modifying saved config."""
    try:
        conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            connection_timeout=5
        )
        if conn.is_connected():
            info = conn.get_server_info()
            conn.close()
            return True, f"Connected successfully! MySQL Server Version: {info}"
        return False, "Failed to connect to MySQL."
    except Error as e:
        return False, f"MySQL Error {e.errno}: {e.msg}"
    except Exception as ex:
        return False, str(ex)

def execute_query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Utility wrapper to execute queries safely.
    Returns (data, error_message).
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

        if commit:
            conn.commit()
            if cursor.lastrowid:
                result = cursor.lastrowid

        cursor.close()
        return result, None
    except Error as e:
        if conn:
            conn.rollback()
        return None, f"SQL Error [{e.errno}]: {e.msg}"
    except Exception as ex:
        if conn:
            conn.rollback()
        return None, str(ex)
    finally:
        if conn and conn.is_connected():
            conn.close()
