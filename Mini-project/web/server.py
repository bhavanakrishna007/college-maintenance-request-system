"""
Flask Web Application Server for College Maintenance and Request System
Course Code: 24CS305 / CS3106 - DBMS Laboratory
Implements Strict Role-Based Access Control (RBAC):
- Technician: Selects and logs materials required; executes work and resolves issues.
- Admin: Assigns technicians and VIEWS materials used (read-only for materials, no selection access).
- Faculty & Student: Dedicated issue reporting form & personal ticket status tracking only.
"""

import sys
import os
from flask import Flask, render_template, request, jsonify, session

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.insert(0, SRC_DIR)

import models
import db_connection
from config import load_db_config

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.secret_key = "college_maintenance_db_secret_key_2026"

# ============================================================================
# WEB PAGES
# ============================================================================

@app.route("/")
def index():
    return render_template("index.html")

# ============================================================================
# AUTHENTICATION & ROLE-SWITCHING API
# ============================================================================

ROLE_PRESETS = {
    "student_faculty": {
        "username": "bhavana",
        "default_password": "241141",
        "role_name": "Student / Faculty",
        "description": "Lodge campus complaints & track personal ticket status"
    },
    "student": {
        "username": "bhavana",
        "default_password": "241141",
        "role_name": "Student",
        "description": "Report campus complaints & track personal ticket status"
    },
    "faculty": {
        "username": "abhishek_saji",
        "default_password": "252101",
        "role_name": "Faculty / Staff",
        "description": "Report departmental laboratory & classroom infrastructure faults"
    },
    "technician": {
        "username": "tech_murugan",
        "default_password": "tech123",
        "role_name": "Technician",
        "description": "Inspect assigned work orders, select required materials, and resolve issues"
    },
    "admin": {
        "username": "admin",
        "default_password": "admin123",
        "role_name": "Administrator",
        "description": "Full campus oversight, technician assignment, and materials auditing"
    }
}

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if not username or not password:
        return jsonify({"success": False, "message": "Please enter both username and password."}), 400
        
    user, err = models.authenticate_user(username, password)
    if err or not user:
        return jsonify({"success": False, "message": err or "Invalid credentials."}), 401
    
    # If user is a technician, attach technician_id
    if user["role"] == "Technician":
        tech_row, _ = models.get_technician_by_user_id(user["user_id"])
        if tech_row:
            user["technician_id"] = tech_row["technician_id"]
            user["specialization"] = tech_row["specialization"]
            user["status"] = tech_row["status"]
        else:
            user["technician_id"] = 1
            user["specialization"] = "General Maintenance"
            user["status"] = "Available"

    session["user"] = user
    return jsonify({"success": True, "user": user})

@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"success": True})

@app.route("/api/auth/current_user", methods=["GET"])
def api_current_user():
    user = session.get("user")
    return jsonify({"user": user, "authenticated": user is not None})

@app.route("/api/auth/role_presets", methods=["GET"])
def api_role_presets():
    return jsonify({"presets": ROLE_PRESETS})

# ============================================================================
# TECHNICIAN PROFILE & WORKBENCH STATS
# ============================================================================

@app.route("/api/technician/profile", methods=["GET"])
def api_technician_profile():
    user = session.get("user")
    if not user or user["role"] != "Technician":
        return jsonify({"success": False, "message": "Technician authentication required."}), 403

    tech_row, _ = models.get_technician_by_user_id(user["user_id"])
    if not tech_row:
        # Fallback to technician 1
        tech_row, _ = models.execute_query("SELECT * FROM technicians WHERE technician_id = 1;", fetchone=True)

    tech_id = tech_row["technician_id"]
    # Get stats for this technician
    sql_stats = """
        SELECT 
            COUNT(assignment_id) AS total_assigned,
            SUM(CASE WHEN work_status = 'Assigned' THEN 1 ELSE 0 END) AS pending_start,
            SUM(CASE WHEN work_status = 'Work-Started' THEN 1 ELSE 0 END) AS in_progress,
            SUM(CASE WHEN work_status = 'Completed' THEN 1 ELSE 0 END) AS completed
        FROM assignments
        WHERE technician_id = %s;
    """
    stats, _ = db_connection.execute_query(sql_stats, (tech_id,), fetchone=True)
    
    return jsonify({
        "success": True,
        "technician": tech_row,
        "stats": stats or {"total_assigned": 0, "pending_start": 0, "in_progress": 0, "completed": 0}
    })

# ============================================================================
# DASHBOARD API (ADMIN ONLY)
# ============================================================================

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    user = session.get("user")
    if not user or user["role"] != "Admin":
        return jsonify({"success": False, "message": "Access restricted to administrators."}), 403

    stats = models.get_dashboard_summary()
    cat_summary, _ = models.get_category_distribution_report()
    recent_reqs, _ = models.get_requests(status="All")
    
    urgent = [r for r in recent_reqs if r["priority"] in ("Emergency", "High") and r["status"] != "Resolved"][:5]
    parts, _ = models.get_inventory_parts()
    low_stock = [p for p in parts if p["stock_quantity"] <= p["reorder_level"]]
    
    return jsonify({
        "success": True,
        "stats": stats,
        "categories": cat_summary,
        "urgent_requests": urgent,
        "low_stock_parts": low_stock
    })

# ============================================================================
# MAINTENANCE REQUESTS API (ROLE FILTERED)
# ============================================================================

@app.route("/api/requests", methods=["GET"])
def api_get_requests():
    user = session.get("user")
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    search = request.args.get("search", "")
    status = request.args.get("status", "All")
    category = request.args.get("category", "All")
    priority = request.args.get("priority", "All")
    assigned_to_me = request.args.get("assigned_to_me", "false") == "true"
    
    # Students & Faculty can ONLY see their own requests
    if user["role"] in ("Student", "Staff"):
        user_id = user["user_id"]
        role = user["role"]
    else:
        user_id = None
        role = user["role"]

    data, err = models.get_requests(search=search, status=status, category=category, priority=priority, user_id=user_id, role=role)
    if err:
        return jsonify({"success": False, "message": err}), 500

    # If Technician: ONLY show jobs assigned to this technician (All campus jobs hidden)
    if user["role"] == "Technician":
        tech_id = user.get("technician_id") or 1
        data = [r for r in data if r.get("assigned_technician_id") == tech_id]

    return jsonify({"success": True, "requests": data, "user_role": user["role"]})

@app.route("/api/requests/<int:req_id>", methods=["GET"])
def api_get_request_details(req_id):
    user = session.get("user")
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    req_data, err = models.get_request_by_id(req_id)
    if err or not req_data:
        return jsonify({"success": False, "message": err or "Not found"}), 404

    # Security check: Students/Faculty can only view details of their own requests
    if user["role"] in ("Student", "Staff") and req_data["reported_by_id"] != user["user_id"]:
        return jsonify({"success": False, "message": "Unauthorized access to ticket."}), 403

    assignments, _ = models.get_assignments_for_request(req_id)
    
    # Parts used: Visible to Admin and Technicians (Admin can SEE them, Technician selects them)
    parts_used = []
    if user["role"] in ("Admin", "Technician"):
        parts_used, _ = models.get_request_parts_used(req_id)
    
    return jsonify({
        "success": True,
        "request": req_data,
        "assignments": assignments,
        "parts_used": parts_used,
        "user_role": user["role"]
    })

@app.route("/api/requests", methods=["POST"])
def api_create_request():
    user = session.get("user")
    if not user:
        return jsonify({"success": False, "message": "Authentication required."}), 401

    data = request.json or {}
    title = data.get("issue_title", "").strip()
    desc = data.get("issue_description", "").strip()
    cat_id = data.get("category_id")
    dept_id = data.get("dept_id") or user.get("dept_id", 1)
    loc = data.get("location_details", "").strip()
    pri = data.get("priority", "Medium")
    
    user_id = user["user_id"]
    
    if not title or not desc or not cat_id or not loc:
        return jsonify({"success": False, "message": "Please fill all required fields (Title, Category, Location, Description)."}), 400
        
    req_id, code, err = models.create_request(user_id, int(cat_id), int(dept_id), loc, title, desc, pri)
    if err:
        return jsonify({"success": False, "message": err}), 500
        
    return jsonify({"success": True, "request_id": req_id, "tracking_code": code})

@app.route("/api/requests/<int:req_id>", methods=["PUT"])
def api_update_request(req_id):
    user = session.get("user")
    if not user or user["role"] not in ("Admin", "Technician"):
        return jsonify({"success": False, "message": "Only Administrators and Technicians can edit tickets."}), 403

    data = request.json or {}
    title = data.get("issue_title", "").strip()
    desc = data.get("issue_description", "").strip()
    cat_id = data.get("category_id")
    dept_id = data.get("dept_id")
    loc = data.get("location_details", "").strip()
    pri = data.get("priority", "Medium")
    status = data.get("status", "Reported")
    
    ok, err = models.update_request(req_id, int(cat_id), int(dept_id), loc, title, desc, pri, status)
    if not ok:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True})

@app.route("/api/requests/<int:req_id>", methods=["DELETE"])
def api_delete_request(req_id):
    user = session.get("user")
    if not user or user["role"] != "Admin":
        return jsonify({"success": False, "message": "Only Administrators can delete tickets."}), 403

    ok, err = models.delete_request(req_id)
    if not ok:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True})

# ============================================================================
# WORKFLOW EXECUTION API
# - Assign Technician: ADMIN ONLY
# - Consume Parts: TECHNICIAN ONLY (Admin has no access to select; can only see)
# - Start Work & Resolve: TECHNICIAN & ADMIN
# ============================================================================

@app.route("/api/workflow/assign", methods=["POST"])
def api_wf_assign():
    user = session.get("user")
    if not user or user["role"] != "Admin":
        return jsonify({"success": False, "message": "Only Administrators can assign technicians."}), 403

    data = request.json or {}
    req_id = data.get("request_id")
    tech_id = data.get("technician_id")
    admin_id = user["user_id"]
    
    if not req_id or not tech_id:
        return jsonify({"success": False, "message": "Request ID and Technician ID required."}), 400
        
    ok, err = models.assign_technician(int(req_id), int(tech_id), int(admin_id))
    if not ok:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True, "message": "Technician allocated via sp_assign_technician!"})

@app.route("/api/workflow/start", methods=["POST"])
def api_wf_start():
    user = session.get("user")
    if not user or user["role"] not in ("Admin", "Technician"):
        return jsonify({"success": False, "message": "Only Technicians or Admins can start work."}), 403

    data = request.json or {}
    req_id = data.get("request_id")
    notes = data.get("work_notes", "Work started by technician.")
    
    if not req_id:
        return jsonify({"success": False, "message": "Request ID required."}), 400
        
    ok, err = models.start_maintenance_work(int(req_id), notes)
    if not ok:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True, "message": "Work marked in-progress via sp_start_maintenance_work!"})

@app.route("/api/workflow/resolve", methods=["POST"])
def api_wf_resolve():
    user = session.get("user")
    if not user or user["role"] not in ("Admin", "Technician"):
        return jsonify({"success": False, "message": "Only Technicians or Admins can resolve tickets."}), 403

    data = request.json or {}
    req_id = data.get("request_id")
    notes = data.get("resolution_notes", "Issue inspected and resolved successfully.")
    
    if not req_id:
        return jsonify({"success": False, "message": "Request ID required."}), 400
        
    ok, err = models.resolve_maintenance_request(int(req_id), notes)
    if not ok:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True, "message": "Issue marked resolved via sp_resolve_maintenance_request!"})

@app.route("/api/workflow/consume_part", methods=["POST"])
def api_wf_consume_part():
    user = session.get("user")
    # STRICT RULE: Only the Technician can select and record materials!
    # Admin has view-only auditing access and NO access to select materials.
    if not user or user["role"] != "Technician":
        return jsonify({
            "success": False, 
            "message": "Access Denied: Only technicians on-site can select and record materials. Administrators have view-only access to materials."
        }), 403

    data = request.json or {}
    req_id = data.get("request_id")
    part_id = data.get("part_id")
    qty = data.get("quantity")
    notes = data.get("notes", "")
    
    try:
        qty = int(qty)
        if qty <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Quantity must be a positive integer."}), 400
        
    ok, err = models.record_part_usage(int(req_id), int(part_id), qty, notes)
    if not ok:
        return jsonify({"success": False, "message": f"Trigger Rejection: {err}"}), 400
        
    return jsonify({"success": True, "message": "Material logged! Inventory stock decremented automatically via database trigger."})

@app.route("/api/workflow/consume_part/<int:usage_id>", methods=["DELETE"])
def api_wf_delete_part_usage(usage_id):
    user = session.get("user")
    # STRICT RULE: Only the Technician can remove materials recorded on-site
    if not user or user["role"] != "Technician":
        return jsonify({
            "success": False,
            "message": "Access Denied: Only technicians can remove recorded materials."
        }), 403

    ok, err = models.delete_part_usage(usage_id)
    if not ok:
        return jsonify({"success": False, "message": err or "Failed to remove material record."}), 500

    return jsonify({"success": True, "message": "Material record removed. Stock automatically restored via trigger!"})

# ============================================================================
# INVENTORY & METADATA API
# ============================================================================

@app.route("/api/metadata", methods=["GET"])
def api_get_metadata():
    depts, _ = models.get_departments()
    cats, _ = models.get_categories()
    techs, _ = models.get_technicians()
    parts, _ = models.get_inventory_parts()
    return jsonify({
        "departments": depts,
        "categories": cats,
        "technicians": techs,
        "inventory": parts
    })

@app.route("/api/inventory", methods=["GET"])
def api_get_inventory():
    user = session.get("user")
    if not user or user["role"] not in ("Admin", "Technician"):
        return jsonify({"success": False, "message": "Access restricted to technicians and administrators."}), 403

    parts, err = models.get_inventory_parts()
    if err:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True, "parts": parts})

@app.route("/api/inventory", methods=["POST"])
def api_add_inventory():
    user = session.get("user")
    if not user or user["role"] != "Admin":
        return jsonify({"success": False, "message": "Only Administrators can add catalog items."}), 403

    data = request.json or {}
    name = data.get("part_name", "").strip()
    cat = data.get("category", "").strip()
    uom = data.get("unit_of_measure", "pcs").strip()
    cost = float(data.get("unit_cost", 0))
    stock = int(data.get("stock_quantity", 0))
    reorder = int(data.get("reorder_level", 5))
    
    if not name or not cat:
        return jsonify({"success": False, "message": "Part name and category required."}), 400
        
    part_id, err = models.add_inventory_part(name, cat, uom, cost, stock, reorder)
    if err:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True, "part_id": part_id})

@app.route("/api/inventory/<int:part_id>/stock", methods=["PUT"])
def api_update_stock(part_id):
    user = session.get("user")
    if not user or user["role"] != "Admin":
        return jsonify({"success": False, "message": "Only Administrators can adjust physical stock balances."}), 403

    new_stock = request.json.get("stock_quantity")
    if new_stock is None or int(new_stock) < 0:
        return jsonify({"success": False, "message": "Stock quantity must be non-negative."}), 400
        
    ok, err = models.update_inventory_stock(part_id, int(new_stock))
    if not ok:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True})

# ============================================================================
# REPORTS & VIEWS API (ADMIN ONLY)
# ============================================================================

@app.route("/api/reports/<report_type>", methods=["GET"])
def api_get_report(report_type):
    user = session.get("user")
    if not user or user["role"] != "Admin":
        return jsonify({"success": False, "message": "Access restricted to administrators."}), 403

    if report_type == "technician_workload":
        data, err = models.get_technician_workload_report()
        sql = "SELECT * FROM vw_technician_workload ORDER BY total_assigned_tasks DESC;"
    elif report_type == "request_cost_summary":
        data, err = models.get_request_cost_summary_report()
        sql = "SELECT * FROM vw_request_cost_summary ORDER BY total_parts_cost DESC;"
    elif report_type == "department_expenditure":
        data, err = models.get_department_expenditure_report()
        sql = "SELECT d.dept_name, d.building, COUNT(DISTINCT mr.request_id), COALESCE(SUM(rpu.total_cost), 0.00) FROM departments d LEFT JOIN maintenance_requests mr ... GROUP BY dept_id;"
    elif report_type == "category_distribution":
        data, err = models.get_category_distribution_report()
        sql = "SELECT c.category_name, COUNT(mr.request_id), SUM(Resolved), c.sla_hours FROM categories c ... GROUP BY category_id;"
    else:
        return jsonify({"success": False, "message": "Invalid report type"}), 400
        
    if err:
        return jsonify({"success": False, "message": err}), 500
    return jsonify({"success": True, "sql": sql, "data": data})

@app.route("/api/system/status", methods=["GET"])
def api_system_status():
    user = session.get("user")
    if not user or user["role"] != "Admin":
        return jsonify({"success": False, "message": "Access restricted to administrators."}), 403

    cfg = load_db_config()
    conn = None
    tables_info = []
    server_info = "Unknown"
    is_connected = False
    
    try:
        conn = db_connection.get_connection()
        is_connected = True
        server_info = conn.get_server_info()
        cursor = conn.cursor()
        cursor.execute("USE college_maintenance_db;")
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{t}`;")
            count = cursor.fetchone()[0]
            tables_info.append({"name": t, "count": count, "type": "view" if t.startswith("vw_") else "table"})
        cursor.close()
    except Exception as ex:
        is_connected = False
        server_info = str(ex)
    finally:
        if conn and conn.is_connected():
            conn.close()
            
    return jsonify({
        "connected": is_connected,
        "server_info": server_info,
        "config": {
            "host": cfg["host"],
            "port": cfg["port"],
            "user": cfg["user"],
            "database": cfg["database"]
        },
        "tables": tables_info
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
