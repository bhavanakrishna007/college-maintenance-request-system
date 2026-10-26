"""
Data Models and Business Logic for College Maintenance and Request System
Implements CRUD operations, Stored Procedure calls, Views, and Analytics.
Course: 24CS305 / CS3106 - DBMS Laboratory
"""

import time
from db_connection import get_connection, execute_query
import mysql.connector

# ============================================================================
# 1. AUTHENTICATION & USER MANAGEMENT
# ============================================================================

def authenticate_user(username, password):
    """
    Validates user credentials against database.
    Supports login via username, full name, roll number, or email.
    Returns (user_dict, error_msg).
    """
    clean_identifier = username.strip()
    sql = """
        SELECT u.user_id, u.username, u.full_name, u.email, u.phone, 
               u.role, u.dept_id, d.dept_name, u.password_hash
        FROM users u
        JOIN departments d ON u.dept_id = d.dept_id
        WHERE (LOWER(u.username) = LOWER(%s) 
            OR LOWER(u.full_name) = LOWER(%s)
            OR u.password_hash = %s
            OR LOWER(u.email) LIKE CONCAT(LOWER(%s), '@%%'))
          AND u.is_active = TRUE
        LIMIT 1;
    """
    row, err = execute_query(sql, (clean_identifier, clean_identifier, clean_identifier, clean_identifier), fetchone=True)
    if err:
        return None, err
    if not row:
        return None, "Invalid username / roll number or account inactive."
    if row["password_hash"] != password:
        return None, "Incorrect password."
    return row, None

def get_users_list():
    sql = "SELECT user_id, username, full_name, role, email FROM users ORDER BY full_name;"
    return execute_query(sql, fetchall=True)

# ============================================================================
# 2. METADATA LOOKUPS
# ============================================================================

def get_departments():
    sql = "SELECT dept_id, dept_name, building, block_no FROM departments ORDER BY dept_name;"
    rows, err = execute_query(sql, fetchall=True)
    return rows or [], err

def get_categories():
    sql = "SELECT category_id, category_name, default_priority, sla_hours FROM categories ORDER BY category_name;"
    rows, err = execute_query(sql, fetchall=True)
    return rows or [], err

# ============================================================================
# 3. MAINTENANCE REQUESTS (CRUD)
# ============================================================================

def get_requests(search="", status="All", category="All", priority="All", user_id=None, role=None):
    """
    Retrieves maintenance requests with multi-condition filtering and search.
    """
    sql = """
        SELECT 
            mr.request_id,
            mr.tracking_code,
            mr.issue_title,
            mr.issue_description,
            mr.priority,
            mr.status,
            c.category_id,
            c.category_name,
            d.dept_id,
            d.dept_name,
            d.building,
            mr.location_details,
            u.full_name AS reported_by,
            mr.reported_by_id,
            mr.reported_at,
            mr.resolution_notes,
            mr.resolved_at,
            (SELECT t.name FROM assignments a JOIN technicians t ON a.technician_id = t.technician_id 
             WHERE a.request_id = mr.request_id ORDER BY a.assignment_id DESC LIMIT 1) AS technician_name,
            (SELECT a.technician_id FROM assignments a 
             WHERE a.request_id = mr.request_id ORDER BY a.assignment_id DESC LIMIT 1) AS assigned_technician_id
        FROM maintenance_requests mr
        JOIN categories c ON mr.category_id = c.category_id
        JOIN departments d ON mr.dept_id = d.dept_id
        JOIN users u ON mr.reported_by_id = u.user_id
        WHERE 1=1
    """
    params = []

    # Role filter: Students and Faculty can see their own requests by default, or all if Admin
    if role in ('Student', 'Staff') and user_id:
        sql += " AND mr.reported_by_id = %s"
        params.append(user_id)

    if status and status != "All":
        sql += " AND mr.status = %s"
        params.append(status)

    if category and category != "All":
        sql += " AND c.category_name = %s"
        params.append(category)

    if priority and priority != "All":
        sql += " AND mr.priority = %s"
        params.append(priority)

    if search:
        search_like = f"%{search.strip()}%"
        sql += """ AND (
            mr.tracking_code LIKE %s OR 
            mr.issue_title LIKE %s OR 
            mr.location_details LIKE %s OR 
            u.full_name LIKE %s
        )"""
        params.extend([search_like, search_like, search_like, search_like])

    sql += " ORDER BY mr.reported_at DESC;"
    rows, err = execute_query(sql, tuple(params), fetchall=True)
    return rows or [], err

def get_request_by_id(request_id):
    sql = """
        SELECT 
            mr.*,
            c.category_name,
            d.dept_name,
            d.building,
            u.full_name AS reported_by,
            u.email AS reporter_email,
            u.phone AS reporter_phone
        FROM maintenance_requests mr
        JOIN categories c ON mr.category_id = c.category_id
        JOIN departments d ON mr.dept_id = d.dept_id
        JOIN users u ON mr.reported_by_id = u.user_id
        WHERE mr.request_id = %s;
    """
    return execute_query(sql, (request_id,), fetchone=True)

def create_request(reported_by_id, category_id, dept_id, location_details, issue_title, issue_description, priority):
    """
    Creates a new maintenance request with an automatically generated tracking code.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Generate unique tracking code
        timestamp_part = int(time.time()) % 1000000
        cursor.execute("SELECT COUNT(*) AS total FROM maintenance_requests;")
        row = cursor.fetchone()
        next_num = (row["total"] if row else 0) + 1
        tracking_code = f"REQ-2026-{next_num:04d}"

        sql = """
            INSERT INTO maintenance_requests 
            (tracking_code, reported_by_id, category_id, dept_id, location_details, issue_title, issue_description, priority, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Reported');
        """
        cursor.execute(sql, (tracking_code, reported_by_id, category_id, dept_id, location_details, issue_title, issue_description, priority))
        req_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        return req_id, tracking_code, None
    except Exception as e:
        if conn:
            conn.rollback()
        return None, None, str(e)
    finally:
        if conn and conn.is_connected():
            conn.close()

def update_request(request_id, category_id, dept_id, location_details, issue_title, issue_description, priority, status):
    sql = """
        UPDATE maintenance_requests
        SET category_id = %s,
            dept_id = %s,
            location_details = %s,
            issue_title = %s,
            issue_description = %s,
            priority = %s,
            status = %s
        WHERE request_id = %s;
    """
    _, err = execute_query(sql, (category_id, dept_id, location_details, issue_title, issue_description, priority, status, request_id), commit=True)
    return err is None, err

def delete_request(request_id):
    sql = "DELETE FROM maintenance_requests WHERE request_id = %s;"
    _, err = execute_query(sql, (request_id,), commit=True)
    return err is None, err

# ============================================================================
# 4. WORKFLOW & ASSIGNMENTS (STORED PROCEDURES)
# ============================================================================

def get_technicians(specialization=None):
    sql = "SELECT technician_id, name, specialization, phone, email, status, hourly_rate FROM technicians"
    params = []
    if specialization:
        sql += " WHERE specialization = %s"
        params.append(specialization)
    sql += " ORDER BY name;"
    rows, err = execute_query(sql, tuple(params), fetchall=True)
    return rows or [], err

def get_technician_by_user_id(user_id):
    sql = "SELECT technician_id, user_id, name, specialization, phone, email, status, hourly_rate FROM technicians WHERE user_id = %s;"
    row, err = execute_query(sql, (user_id,), fetchone=True)
    return row, err

def assign_technician(request_id, technician_id, admin_id):
    """
    Calls Stored Procedure `sp_assign_technician`.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("sp_assign_technician", [request_id, technician_id, admin_id])
        conn.commit()
        cursor.close()
        return True, None
    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn and conn.is_connected():
            conn.close()

def start_maintenance_work(request_id, work_notes):
    """
    Calls Stored Procedure `sp_start_maintenance_work`.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("sp_start_maintenance_work", [request_id, work_notes])
        conn.commit()
        cursor.close()
        return True, None
    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn and conn.is_connected():
            conn.close()

def resolve_maintenance_request(request_id, resolution_notes):
    """
    Calls Stored Procedure `sp_resolve_maintenance_request`.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("sp_resolve_maintenance_request", [request_id, resolution_notes])
        conn.commit()
        cursor.close()
        return True, None
    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_assignments_for_request(request_id):
    sql = """
        SELECT 
            a.assignment_id,
            t.name AS technician_name,
            t.specialization,
            t.phone AS technician_phone,
            u.full_name AS assigned_by,
            a.assigned_date,
            a.work_start_date,
            a.work_end_date,
            a.work_notes,
            a.work_status
        FROM assignments a
        JOIN technicians t ON a.technician_id = t.technician_id
        JOIN users u ON a.assigned_by_id = u.user_id
        WHERE a.request_id = %s
        ORDER BY a.assignment_id DESC;
    """
    rows, err = execute_query(sql, (request_id,), fetchall=True)
    return rows or [], err

# ============================================================================
# 5. PARTS INVENTORY & USAGE (TRIGGERS IN ACTION)
# ============================================================================

def get_inventory_parts():
    sql = "SELECT part_id, part_name, category, unit_of_measure, unit_cost, stock_quantity, reorder_level FROM parts_inventory ORDER BY category, part_name;"
    rows, err = execute_query(sql, fetchall=True)
    return rows or [], err

def add_inventory_part(part_name, category, unit_of_measure, unit_cost, stock_quantity, reorder_level):
    sql = """
        INSERT INTO parts_inventory (part_name, category, unit_of_measure, unit_cost, stock_quantity, reorder_level)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    part_id, err = execute_query(sql, (part_name, category, unit_of_measure, unit_cost, stock_quantity, reorder_level), commit=True)
    return part_id, err

def update_inventory_stock(part_id, new_quantity):
    sql = "UPDATE parts_inventory SET stock_quantity = %s WHERE part_id = %s;"
    _, err = execute_query(sql, (new_quantity, part_id), commit=True)
    return err is None, err

def get_request_parts_used(request_id):
    sql = """
        SELECT 
            rpu.usage_id,
            rpu.request_id,
            pi.part_name,
            pi.category,
            pi.unit_of_measure,
            rpu.quantity_used,
            rpu.unit_cost_charged,
            rpu.total_cost,
            rpu.notes,
            rpu.recorded_at
        FROM request_parts_used rpu
        JOIN parts_inventory pi ON rpu.part_id = pi.part_id
        WHERE rpu.request_id = %s
        ORDER BY rpu.recorded_at ASC;
    """
    rows, err = execute_query(sql, (request_id,), fetchall=True)
    return rows or [], err

def record_part_usage(request_id, part_id, quantity_used, notes=""):
    """
    Inserts part usage record. Database Triggers will automatically:
    1. Check if sufficient stock exists (BEFORE INSERT trigger).
    2. Deduct the used quantity from parts_inventory (AFTER INSERT trigger).
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch current unit cost
        cursor.execute("SELECT unit_cost FROM parts_inventory WHERE part_id = %s;", (part_id,))
        part = cursor.fetchone()
        if not part:
            return False, "Selected part not found in inventory."
        
        unit_cost = float(part["unit_cost"])
        total_cost = unit_cost * float(quantity_used)

        sql = """
            INSERT INTO request_parts_used (request_id, part_id, quantity_used, unit_cost_charged, total_cost, notes)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(sql, (request_id, part_id, quantity_used, unit_cost, total_cost, notes))
        conn.commit()
        cursor.close()
        return True, None
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, err.msg
    except Exception as ex:
        if conn:
            conn.rollback()
        return False, str(ex)
    finally:
        if conn and conn.is_connected():
            conn.close()

def delete_part_usage(usage_id):
    """
    Deletes part usage record. AFTER DELETE trigger will automatically restore the stock!
    """
    sql = "DELETE FROM request_parts_used WHERE usage_id = %s;"
    _, err = execute_query(sql, (usage_id,), commit=True)
    return err is None, err

# ============================================================================
# 6. DASHBOARD & ANALYTICAL REPORTS (VIEWS & AGGREGATE QUERIES)
# ============================================================================

def get_dashboard_summary():
    """Calculates top-level KPI metrics."""
    metrics = {
        "total_requests": 0,
        "pending": 0,
        "in_progress": 0,
        "resolved": 0,
        "total_parts_cost": 0.0,
        "available_techs": 0,
        "low_stock_parts": 0
    }
    
    # Request stats
    sql_req = """
        SELECT 
            COUNT(*) AS total,
            SUM(CASE WHEN status IN ('Reported', 'Categorized', 'Assigned') THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'In-Progress' THEN 1 ELSE 0 END) AS in_progress,
            SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved
        FROM maintenance_requests;
    """
    res, _ = execute_query(sql_req, fetchone=True)
    if res:
        metrics["total_requests"] = int(res["total"] or 0)
        metrics["pending"] = int(res["pending"] or 0)
        metrics["in_progress"] = int(res["in_progress"] or 0)
        metrics["resolved"] = int(res["resolved"] or 0)

    # Total cost
    sql_cost = "SELECT COALESCE(SUM(total_cost), 0.00) AS total_spent FROM request_parts_used;"
    cost_res, _ = execute_query(sql_cost, fetchone=True)
    if cost_res:
        metrics["total_parts_cost"] = float(cost_res["total_spent"])

    # Available techs
    sql_tech = "SELECT COUNT(*) AS avail FROM technicians WHERE status = 'Available';"
    tech_res, _ = execute_query(sql_tech, fetchone=True)
    if tech_res:
        metrics["available_techs"] = tech_res["avail"] or 0

    # Low stock items
    sql_stock = "SELECT COUNT(*) AS low FROM parts_inventory WHERE stock_quantity <= reorder_level;"
    stock_res, _ = execute_query(sql_stock, fetchone=True)
    if stock_res:
        metrics["low_stock_parts"] = stock_res["low"] or 0

    return metrics

def get_category_distribution_report():
    """Aggregate query with GROUP BY and COUNT."""
    sql = """
        SELECT 
            c.category_name,
            COUNT(mr.request_id) AS total_requests,
            SUM(CASE WHEN mr.status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
            SUM(CASE WHEN mr.status != 'Resolved' THEN 1 ELSE 0 END) AS open_count,
            c.sla_hours
        FROM categories c
        LEFT JOIN maintenance_requests mr ON c.category_id = mr.category_id
        GROUP BY c.category_id, c.category_name, c.sla_hours
        ORDER BY total_requests DESC;
    """
    rows, err = execute_query(sql, fetchall=True)
    if rows:
        for r in rows:
            r["total_requests"] = int(r["total_requests"] or 0)
            r["resolved_count"] = int(r["resolved_count"] or 0)
            r["open_count"] = int(r["open_count"] or 0)
    return rows or [], err

def get_department_expenditure_report():
    """JOIN query with aggregate SUM and AVG."""
    sql = """
        SELECT 
            d.dept_name,
            d.building,
            COUNT(DISTINCT mr.request_id) AS request_count,
            COALESCE(SUM(rpu.total_cost), 0.00) AS total_cost
        FROM departments d
        LEFT JOIN maintenance_requests mr ON d.dept_id = mr.dept_id
        LEFT JOIN request_parts_used rpu ON mr.request_id = rpu.request_id
        GROUP BY d.dept_id, d.dept_name, d.building
        ORDER BY total_cost DESC;
    """
    rows, err = execute_query(sql, fetchall=True)
    if rows:
        for r in rows:
            r["request_count"] = int(r["request_count"] or 0)
            r["total_cost"] = float(r["total_cost"] or 0.0)
    return rows or [], err

def get_technician_workload_report():
    """Queries Database View: vw_technician_workload."""
    sql = "SELECT * FROM vw_technician_workload ORDER BY total_assigned_tasks DESC;"
    rows, err = execute_query(sql, fetchall=True)
    if rows:
        for r in rows:
            r["total_assigned_tasks"] = int(r["total_assigned_tasks"] or 0)
            r["pending_tasks"] = int(r["pending_tasks"] or 0)
            r["in_progress_tasks"] = int(r["in_progress_tasks"] or 0)
            r["completed_tasks"] = int(r["completed_tasks"] or 0)
    return rows or [], err

def get_request_cost_summary_report():
    """Queries Database View: vw_request_cost_summary."""
    sql = "SELECT * FROM vw_request_cost_summary ORDER BY total_parts_cost DESC;"
    rows, err = execute_query(sql, fetchall=True)
    if rows:
        for r in rows:
            r["parts_count"] = int(r["parts_count"] or 0)
            r["total_items_consumed"] = int(r["total_items_consumed"] or 0)
            r["total_parts_cost"] = float(r["total_parts_cost"] or 0.0)
    return rows or [], err
