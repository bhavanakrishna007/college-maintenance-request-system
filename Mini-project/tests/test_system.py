"""
Automated Integration and End-to-End System Tests
College Maintenance and Request System
Course: 24CS305 / CS3106 - DBMS Laboratory
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import models

def run_all_tests():
    print("=" * 65)
    print("RUNNING DBMS MINI PROJECT INTEGRATION AND SYSTEM TEST SUITE")
    print("=" * 65)

    # Test 1: User Authentication
    print("\n[Test 1] Testing Role-based Authentication...")
    user, err = models.authenticate_user("admin", "admin123")
    assert user is not None, f"Admin auth failed: {err}"
    assert user["role"] == "Admin"
    print(f"  --> PASS: Authenticated user: {user['full_name']} (Role: {user['role']})")

    # Test 2: Invalid Login Handling
    print("\n[Test 2] Testing Invalid Credentials Handling...")
    bad_user, err = models.authenticate_user("admin", "wrongpassword")
    assert bad_user is None
    print(f"  --> PASS: Rejected invalid password correctly ({err})")

    # Test 3: Dashboard Summary Aggregation
    print("\n[Test 3] Testing Dashboard Metrics Aggregation...")
    stats = models.get_dashboard_summary()
    assert stats["total_requests"] > 0
    print(f"  --> PASS: Total Requests={stats['total_requests']}, Pending={stats['pending']}, Cost=Rs.{stats['total_parts_cost']}")

    # Test 4: Create Maintenance Request
    print("\n[Test 4] Testing Request Creation (DML INSERT with auto tracking code)...")
    req_id, code, err = models.create_request(
        reported_by_id=user["user_id"],
        category_id=1,
        dept_id=1,
        location_details="Turing Block, AI Lab 4",
        issue_title="UPS Inverter Beeping Constantly",
        issue_description="Main battery backup unit giving overload alarm during lab sessions.",
        priority="High"
    )
    assert err is None, f"Create request failed: {err}"
    assert req_id > 0 and code.startswith("REQ-2026-")
    print(f"  --> PASS: Created Request #{req_id} with Code '{code}'")

    # Test 5: Call Stored Procedure sp_assign_technician
    print("\n[Test 5] Testing Stored Procedure 'sp_assign_technician'...")
    ok, err = models.assign_technician(req_id, technician_id=1, admin_id=user["user_id"])
    assert ok, f"sp_assign_technician error: {err}"
    req_check, _ = models.get_request_by_id(req_id)
    assert req_check["status"] == "Assigned"
    print(f"  --> PASS: Request #{req_id} status updated to '{req_check['status']}'")

    # Test 6: Call Stored Procedure sp_start_maintenance_work
    print("\n[Test 6] Testing Stored Procedure 'sp_start_maintenance_work'...")
    ok, err = models.start_maintenance_work(req_id, "Technician inspected circuit board.")
    assert ok, f"sp_start_maintenance_work error: {err}"
    req_check, _ = models.get_request_by_id(req_id)
    assert req_check["status"] == "In-Progress"
    print(f"  --> PASS: Request #{req_id} status updated to '{req_check['status']}'")

    # Test 7: Database Trigger trg_after_part_used_deduct_stock
    print("\n[Test 7] Testing Database Trigger 'trg_after_part_used_deduct_stock'...")
    parts, _ = models.get_inventory_parts()
    test_part = parts[0]
    part_id = test_part["part_id"]
    old_stock = test_part["stock_quantity"]
    qty_to_consume = 2

    ok, err = models.record_part_usage(req_id, part_id, qty_to_consume, "Replaced 2 damaged fuses")
    assert ok, f"Failed to record parts: {err}"

    parts_after, _ = models.get_inventory_parts()
    new_stock = next(p["stock_quantity"] for p in parts_after if p["part_id"] == part_id)
    assert new_stock == old_stock - qty_to_consume, f"Stock discrepancy! Old: {old_stock}, New: {new_stock}"
    print(f"  --> PASS: Part '{test_part['part_name']}' stock automatically reduced from {old_stock} to {new_stock} via trigger.")

    # Test 8: Database Trigger trg_check_stock_before_part_usage (Prevent Negative Stock)
    print("\n[Test 8] Testing Stock Overflow Prevention Trigger...")
    excess_qty = new_stock + 9999
    ok_excess, err_excess = models.record_part_usage(req_id, part_id, excess_qty, "Excessive parts attempt")
    assert not ok_excess, "Database failed to reject excessive inventory usage!"
    print(f"  --> PASS: Excess usage successfully rejected with trigger message: '{err_excess}'")

    # Test 9: Call Stored Procedure sp_resolve_maintenance_request
    print("\n[Test 9] Testing Stored Procedure 'sp_resolve_maintenance_request'...")
    ok, err = models.resolve_maintenance_request(req_id, "Inverter circuits re-soldered and fuses renewed. Verified working.")
    assert ok, f"sp_resolve_maintenance_request error: {err}"
    req_check, _ = models.get_request_by_id(req_id)
    assert req_check["status"] == "Resolved"
    print(f"  --> PASS: Request #{req_id} status updated to '{req_check['status']}'")

    # Test 10: Test Relational Views
    print("\n[Test 10] Testing Relational Views...")
    v1, _ = models.get_technician_workload_report()
    assert len(v1) > 0
    print(f"  --> PASS: View 'vw_technician_workload' returned {len(v1)} technician summary rows.")

    v2, _ = models.get_request_cost_summary_report()
    assert len(v2) > 0
    print(f"  --> PASS: View 'vw_request_cost_summary' returned {len(v2)} request cost records.")

    print("\n" + "=" * 65)
    print("ALL 10 TESTS EXECUTED AND PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_tests()
