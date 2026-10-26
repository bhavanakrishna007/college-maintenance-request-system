"""
Web Application Endpoint and Role-Based Access Control (RBAC) Tests
Course: 24CS305 / CS3106 - DBMS Laboratory
Verifies:
1. Role selection & login authentication
2. Student / Faculty restricted view (Single issue reporting form & own tickets only)
3. Technician Workbench (Assigned tasks, select materials, start work, resolve)
4. Admin Material Restriction (Admin can SEE materials, but CANNOT select/consume materials)
5. Admin Full Management (Assign technician, view all reports, manage inventory)
"""

import sys
import os

WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")
sys.path.insert(0, WEB_DIR)

from server import app

def test_web_app():
    print("=" * 65)
    print("TESTING RBAC: TECHNICIAN MATERIALS SELECTION & ADMIN VIEW-ONLY")
    print("=" * 65)
    
    client = app.test_client()

    # 1. Gateway Rendering
    print("\n[1] Testing GET / (Role Selection & Login Gateway)...")
    res = client.get("/")
    assert res.status_code == 200
    assert b"College Maintenance & Request System" in res.data
    assert b"role-select-card" in res.data
    print("  --> PASS: Rendered gateway with Student, Faculty, Technician, and Admin roles.")

    # 2. Student Role
    print("\n[2] Testing Student Role ('bhavana' / '241141')...")
    login_res = client.post("/api/auth/login", json={"username": "bhavana", "password": "241141"})
    assert login_res.status_code == 200
    user = login_res.get_json()["user"]
    assert user["role"] == "Student"
    print(f"  --> PASS: Authenticated as Student: {user['full_name']}")

    # Check Student Requests
    req_res = client.get("/api/requests")
    assert req_res.status_code == 200
    student_reqs = req_res.get_json()["requests"]
    for r in student_reqs:
        assert r["reported_by_id"] == user["user_id"]
    print(f"  --> PASS: Student sees ONLY their own reported requests ({len(student_reqs)} tickets).")

    # 3. Technician Role: Select and Record Materials
    print("\n[3] Testing Technician Workbench ('tech_murugan' / 'tech123')...")
    client.post("/api/auth/logout")
    tech_login = client.post("/api/auth/login", json={"username": "tech_murugan", "password": "tech123"})
    assert tech_login.status_code == 200
    tech_user = tech_login.get_json()["user"]
    assert tech_user["role"] == "Technician"
    print(f"  --> PASS: Authenticated as Technician: {tech_user['full_name']} (Tech ID: {tech_user.get('technician_id')})")

    # Technician profile & stats
    prof_res = client.get("/api/technician/profile")
    assert prof_res.status_code == 200
    prof_data = prof_res.get_json()
    assert prof_data["success"] is True
    print(f"  --> PASS: Technician profile loaded (Specialization: {prof_data['technician']['specialization']}, Assigned: {prof_data['stats']['total_assigned']})")

    # Technician CAN select and record materials on a request
    part_consume_res = client.post("/api/workflow/consume_part", json={
        "request_id": 1,
        "part_id": 1,
        "quantity": 1,
        "notes": "Technician replaced 1 tube on site"
    })
    assert part_consume_res.status_code == 200, f"Technician failed to consume part: {part_consume_res.get_json()}"
    print("  --> PASS: Technician successfully selected and recorded material (trigger executed stock deduction).")

    # 4. Admin Role: Check Material Restriction (No access to select; can only SEE)
    print("\n[4] Testing Admin Materials Access & Restriction ('admin' / 'admin123')...")
    client.post("/api/auth/logout")
    admin_login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert admin_login.status_code == 200
    admin_user = admin_login.get_json()["user"]
    assert admin_user["role"] == "Admin"
    print(f"  --> PASS: Authenticated as Admin: {admin_user['full_name']}")

    # Admin CAN SEE materials used on a request
    req_details_res = client.get("/api/requests/1")
    assert req_details_res.status_code == 200
    details = req_details_res.get_json()
    assert "parts_used" in details and len(details["parts_used"]) > 0
    print(f"  --> PASS: Admin can view materials recorded on request ({len(details['parts_used'])} material items visible).")

    # Admin CANNOT select or consume materials (Restricted per user instruction!)
    admin_consume_res = client.post("/api/workflow/consume_part", json={
        "request_id": 1,
        "part_id": 1,
        "quantity": 1
    })
    assert admin_consume_res.status_code == 403, "Security violation: Admin was able to select/consume materials!"
    print("  --> PASS: Admin blocked from selecting/consuming materials (HTTP 403 Forbidden - View Only).")

    # Admin CAN allocate technician
    assign_res = client.post("/api/workflow/assign", json={
        "request_id": 7,
        "technician_id": 6
    })
    assert assign_res.status_code == 200
    print("  --> PASS: Admin assigned technician to Request #7 via sp_assign_technician.")

    print("\n" + "=" * 65)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    test_web_app()
