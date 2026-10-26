-- ============================================================================
-- Course Code: 24CS305 / CS3106 - DBMS Laboratory
-- Project Title: College Maintenance and Request System
-- SQL Queries Collection for Demonstration, Reports, and Viva
-- ============================================================================

USE college_maintenance_db;

-- ============================================================================
-- 1. BASIC & FILTERED QUERIES (DML / DQL)
-- ============================================================================

-- Q1.1: Retrieve all pending/active maintenance requests sorted by priority
SELECT 
    request_id,
    tracking_code,
    issue_title,
    priority,
    status,
    reported_at
FROM maintenance_requests
WHERE status IN ('Reported', 'Categorized', 'Assigned', 'In-Progress')
ORDER BY 
    FIELD(priority, 'Emergency', 'High', 'Medium', 'Low'),
    reported_at ASC;

-- Q1.2: Retrieve low stock parts needing reordering
SELECT 
    part_id,
    part_name,
    category,
    unit_cost,
    stock_quantity,
    reorder_level
FROM parts_inventory
WHERE stock_quantity <= reorder_level;

-- ============================================================================
-- 2. COMPLEX JOIN QUERIES
-- ============================================================================

-- Q2.1: 4-Table JOIN showing request details, requester, department, and category
SELECT 
    mr.tracking_code,
    mr.issue_title,
    c.category_name,
    d.dept_name,
    d.building,
    mr.location_details,
    u.full_name AS reported_by,
    u.email AS reporter_email,
    mr.priority,
    mr.status,
    mr.reported_at
FROM maintenance_requests mr
JOIN users u ON mr.reported_by_id = u.user_id
JOIN departments d ON mr.dept_id = d.dept_id
JOIN categories c ON mr.category_id = c.category_id
ORDER BY mr.reported_at DESC;

-- Q2.2: 5-Table JOIN showing assigned technician and technician specialization
SELECT 
    mr.tracking_code,
    mr.issue_title,
    c.category_name,
    t.name AS technician_name,
    t.phone AS technician_phone,
    t.specialization,
    a.work_status,
    a.assigned_date,
    a.work_start_date
FROM assignments a
JOIN maintenance_requests mr ON a.request_id = mr.request_id
JOIN categories c ON mr.category_id = c.category_id
JOIN technicians t ON a.technician_id = t.technician_id
WHERE a.work_status != 'Completed'
ORDER BY a.assigned_date DESC;

-- ============================================================================
-- 3. AGGREGATE FUNCTIONS & GROUP BY QUERIES
-- ============================================================================

-- Q3.1: Request counts and resolution summary grouped by category
SELECT 
    c.category_name,
    COUNT(mr.request_id) AS total_requests,
    SUM(CASE WHEN mr.status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN mr.status != 'Resolved' THEN 1 ELSE 0 END) AS open_count,
    ROUND(AVG(c.sla_hours), 1) AS target_sla_hrs
FROM categories c
LEFT JOIN maintenance_requests mr ON c.category_id = mr.category_id
GROUP BY c.category_id, c.category_name
ORDER BY total_requests DESC;

-- Q3.2: Department-wise total maintenance expenditure (GROUP BY + HAVING)
SELECT 
    d.dept_name,
    d.building,
    COUNT(DISTINCT mr.request_id) AS total_requests_lodged,
    COALESCE(SUM(rpu.total_cost), 0.00) AS total_parts_spent,
    ROUND(AVG(rpu.total_cost), 2) AS avg_cost_per_usage
FROM departments d
JOIN maintenance_requests mr ON d.dept_id = mr.dept_id
LEFT JOIN request_parts_used rpu ON mr.request_id = rpu.request_id
GROUP BY d.dept_id, d.dept_name, d.building
HAVING total_requests_lodged > 0
ORDER BY total_parts_spent DESC;

-- ============================================================================
-- 4. NESTED SUBQUERIES
-- ============================================================================

-- Q4.1: Find all technicians who have handled more tasks than the average technician
SELECT 
    t.technician_id,
    t.name,
    t.specialization,
    COUNT(a.assignment_id) AS task_count
FROM technicians t
JOIN assignments a ON t.technician_id = a.technician_id
GROUP BY t.technician_id, t.name, t.specialization
HAVING task_count > (
    SELECT AVG(tech_total) 
    FROM (
        SELECT COUNT(assignment_id) AS tech_total 
        FROM assignments 
        GROUP BY technician_id
    ) AS avg_subquery
);

-- Q4.2: Subquery with NOT EXISTS - Find departments with zero unresolved issues
SELECT 
    d.dept_id,
    d.dept_name,
    d.building
FROM departments d
WHERE NOT EXISTS (
    SELECT 1 
    FROM maintenance_requests mr
    WHERE mr.dept_id = d.dept_id 
      AND mr.status NOT IN ('Resolved', 'Closed')
);

-- ============================================================================
-- 5. TESTING STORED PROCEDURES & FUNCTIONS
-- ============================================================================

-- Call stored function
SELECT 
    tracking_code,
    issue_title,
    fn_calculate_request_cost(request_id) AS total_expense_rs
FROM maintenance_requests
WHERE request_id IN (1, 2, 4);

-- Query the views
SELECT * FROM vw_active_requests;
SELECT * FROM vw_technician_workload;
SELECT * FROM vw_request_cost_summary;
