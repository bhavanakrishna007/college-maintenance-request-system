-- ============================================================================
-- Course Code: 24CS305 / CS3106 - DBMS Laboratory
-- Project Title: College Maintenance and Request System
-- Relational Database Schema (MySQL 8.0+)
-- ============================================================================

DROP DATABASE IF EXISTS college_maintenance_db;
CREATE DATABASE college_maintenance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE college_maintenance_db;

-- ============================================================================
-- 1. DEPARTMENTS TABLE
-- ============================================================================
CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    building VARCHAR(80) NOT NULL,
    block_no VARCHAR(20) NOT NULL,
    contact_email VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- 2. USERS TABLE (Students, Faculty, Staff, Administrators)
-- ============================================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    role ENUM('Admin', 'Staff', 'Student', 'Technician') NOT NULL DEFAULT 'Student',
    dept_id INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_department 
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================================
-- 3. CATEGORIES TABLE (Maintenance categories: Electrical, Plumbing, HVAC, etc.)
-- ============================================================================
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(60) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL,
    default_priority ENUM('Low', 'Medium', 'High', 'Emergency') NOT NULL DEFAULT 'Medium',
    sla_hours INT NOT NULL CHECK (sla_hours > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- 4. TECHNICIANS TABLE
-- ============================================================================
CREATE TABLE technicians (
    technician_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    status ENUM('Available', 'Busy', 'On-Leave') NOT NULL DEFAULT 'Available',
    hourly_rate DECIMAL(8,2) NOT NULL DEFAULT 150.00 CHECK (hourly_rate >= 0.00),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_technicians_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================================
-- 5. MAINTENANCE REQUESTS TABLE (Core Workflow Entity)
-- Workflow: Reported -> Categorized -> Assigned -> In-Progress -> Resolved -> Closed
-- ============================================================================
CREATE TABLE maintenance_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_code VARCHAR(30) NOT NULL UNIQUE,
    reported_by_id INT NOT NULL,
    category_id INT NOT NULL,
    dept_id INT NOT NULL,
    location_details VARCHAR(150) NOT NULL,
    issue_title VARCHAR(150) NOT NULL,
    issue_description TEXT NOT NULL,
    priority ENUM('Low', 'Medium', 'High', 'Emergency') NOT NULL DEFAULT 'Medium',
    status ENUM('Reported', 'Categorized', 'Assigned', 'In-Progress', 'Resolved', 'Closed') NOT NULL DEFAULT 'Reported',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolution_notes TEXT DEFAULT NULL,
    resolved_at DATETIME DEFAULT NULL,
    CONSTRAINT fk_requests_user 
        FOREIGN KEY (reported_by_id) REFERENCES users(user_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_requests_category 
        FOREIGN KEY (category_id) REFERENCES categories(category_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_requests_dept 
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================================
-- 6. ASSIGNMENTS TABLE (Tracks work allocation & technician execution)
-- ============================================================================
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    technician_id INT NOT NULL,
    assigned_by_id INT NOT NULL,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    work_start_date DATETIME DEFAULT NULL,
    work_end_date DATETIME DEFAULT NULL,
    work_notes TEXT DEFAULT NULL,
    work_status ENUM('Assigned', 'Work-Started', 'Completed') NOT NULL DEFAULT 'Assigned',
    CONSTRAINT fk_assignments_request 
        FOREIGN KEY (request_id) REFERENCES maintenance_requests(request_id) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_assignments_technician 
        FOREIGN KEY (technician_id) REFERENCES technicians(technician_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_assignments_admin 
        FOREIGN KEY (assigned_by_id) REFERENCES users(user_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================================
-- 7. PARTS INVENTORY TABLE (Spare parts, fixtures, supplies)
-- ============================================================================
CREATE TABLE parts_inventory (
    part_id INT AUTO_INCREMENT PRIMARY KEY,
    part_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(60) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'pcs',
    unit_cost DECIMAL(10,2) NOT NULL CHECK (unit_cost >= 0.00),
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    reorder_level INT NOT NULL DEFAULT 5 CHECK (reorder_level >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- 8. REQUEST PARTS USED TABLE (Materials consumed per maintenance job)
-- ============================================================================
CREATE TABLE request_parts_used (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    part_id INT NOT NULL,
    quantity_used INT NOT NULL CHECK (quantity_used > 0),
    unit_cost_charged DECIMAL(10,2) NOT NULL CHECK (unit_cost_charged >= 0.00),
    total_cost DECIMAL(10,2) NOT NULL CHECK (total_cost >= 0.00),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(255) DEFAULT NULL,
    CONSTRAINT fk_usage_request 
        FOREIGN KEY (request_id) REFERENCES maintenance_requests(request_id) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_usage_part 
        FOREIGN KEY (part_id) REFERENCES parts_inventory(part_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================================
-- DATABASE VIEWS
-- ============================================================================

-- View 1: Active Maintenance Requests with complete relational details
CREATE OR REPLACE VIEW vw_active_requests AS
SELECT 
    mr.request_id,
    mr.tracking_code,
    mr.issue_title,
    mr.priority,
    mr.status,
    c.category_name,
    d.dept_name,
    d.building,
    mr.location_details,
    u.full_name AS reported_by,
    u.role AS reporter_role,
    t.name AS assigned_technician,
    mr.reported_at,
    mr.resolved_at
FROM maintenance_requests mr
JOIN categories c ON mr.category_id = c.category_id
JOIN departments d ON mr.dept_id = d.dept_id
JOIN users u ON mr.reported_by_id = u.user_id
LEFT JOIN assignments a ON mr.request_id = a.request_id AND a.work_status != 'Completed'
LEFT JOIN technicians t ON a.technician_id = t.technician_id;

-- View 2: Technician Workload and Performance Summary
CREATE OR REPLACE VIEW vw_technician_workload AS
SELECT 
    t.technician_id,
    t.name AS technician_name,
    t.specialization,
    t.status AS current_status,
    COUNT(a.assignment_id) AS total_assigned_tasks,
    SUM(CASE WHEN a.work_status = 'Assigned' THEN 1 ELSE 0 END) AS pending_tasks,
    SUM(CASE WHEN a.work_status = 'Work-Started' THEN 1 ELSE 0 END) AS in_progress_tasks,
    SUM(CASE WHEN a.work_status = 'Completed' THEN 1 ELSE 0 END) AS completed_tasks
FROM technicians t
LEFT JOIN assignments a ON t.technician_id = a.technician_id
GROUP BY t.technician_id, t.name, t.specialization, t.status;

-- View 3: Maintenance Request Cost Summary
CREATE OR REPLACE VIEW vw_request_cost_summary AS
SELECT 
    mr.request_id,
    mr.tracking_code,
    mr.issue_title,
    c.category_name,
    mr.status,
    COUNT(rpu.usage_id) AS parts_count,
    COALESCE(SUM(rpu.quantity_used), 0) AS total_items_consumed,
    COALESCE(SUM(rpu.total_cost), 0.00) AS total_parts_cost
FROM maintenance_requests mr
JOIN categories c ON mr.category_id = c.category_id
LEFT JOIN request_parts_used rpu ON mr.request_id = rpu.request_id
GROUP BY mr.request_id, mr.tracking_code, mr.issue_title, c.category_name, mr.status;

-- ============================================================================
-- STORED PROCEDURES AND FUNCTIONS
-- ============================================================================

DELIMITER $$

-- Procedure 1: Assign Technician to a Maintenance Request
CREATE PROCEDURE sp_assign_technician (
    IN p_request_id INT,
    IN p_technician_id INT,
    IN p_admin_id INT
)
BEGIN
    DECLARE v_current_status VARCHAR(30);
    
    SELECT status INTO v_current_status 
    FROM maintenance_requests 
    WHERE request_id = p_request_id;
    
    IF v_current_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Maintenance Request not found.';
    END IF;
    
    -- Insert assignment record
    INSERT INTO assignments (request_id, technician_id, assigned_by_id, work_status)
    VALUES (p_request_id, p_technician_id, p_admin_id, 'Assigned');
    
    -- Update request status
    UPDATE maintenance_requests 
    SET status = 'Assigned' 
    WHERE request_id = p_request_id;
    
    -- Set technician status to Busy
    UPDATE technicians 
    SET status = 'Busy' 
    WHERE technician_id = p_technician_id;
END$$

-- Procedure 2: Mark Request Work Started
CREATE PROCEDURE sp_start_maintenance_work (
    IN p_request_id INT,
    IN p_work_notes TEXT
)
BEGIN
    UPDATE assignments 
    SET work_status = 'Work-Started', 
        work_start_date = NOW(),
        work_notes = CONCAT(COALESCE(work_notes, ''), '\n[Work Started]: ', COALESCE(p_work_notes, ''))
    WHERE request_id = p_request_id AND work_status = 'Assigned';

    UPDATE maintenance_requests 
    SET status = 'In-Progress' 
    WHERE request_id = p_request_id;
END$$

-- Procedure 3: Resolve Maintenance Request
CREATE PROCEDURE sp_resolve_maintenance_request (
    IN p_request_id INT,
    IN p_resolution_notes TEXT
)
BEGIN
    DECLARE v_tech_id INT;
    
    -- Find assigned technician
    SELECT technician_id INTO v_tech_id 
    FROM assignments 
    WHERE request_id = p_request_id 
    ORDER BY assignment_id DESC LIMIT 1;
    
    -- Update assignments
    UPDATE assignments 
    SET work_status = 'Completed', 
        work_end_date = NOW(),
        work_notes = CONCAT(COALESCE(work_notes, ''), '\n[Resolved]: ', COALESCE(p_resolution_notes, ''))
    WHERE request_id = p_request_id;
    
    -- Update request
    UPDATE maintenance_requests 
    SET status = 'Resolved',
        resolution_notes = p_resolution_notes,
        resolved_at = NOW()
    WHERE request_id = p_request_id;
    
    -- Free up technician if no other active jobs
    IF v_tech_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM assignments 
            WHERE technician_id = v_tech_id AND work_status IN ('Assigned', 'Work-Started')
        ) THEN
            UPDATE technicians SET status = 'Available' WHERE technician_id = v_tech_id;
        END IF;
    END IF;
END$$

-- Function 1: Calculate Total Expenditure on a Request (Parts + Labor)
CREATE FUNCTION fn_calculate_request_cost (
    p_request_id INT
) RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_parts_cost DECIMAL(10,2) DEFAULT 0.00;
    
    SELECT COALESCE(SUM(total_cost), 0.00) 
    INTO v_parts_cost
    FROM request_parts_used
    WHERE request_id = p_request_id;
    
    RETURN v_parts_cost;
END$$

DELIMITER ;

-- ============================================================================
-- DATABASE TRIGGERS
-- ============================================================================

DELIMITER $$

-- Trigger 1: Validate stock before recording parts used
CREATE TRIGGER trg_check_stock_before_part_usage
BEFORE INSERT ON request_parts_used
FOR EACH ROW
BEGIN
    DECLARE v_available_stock INT;
    
    SELECT stock_quantity INTO v_available_stock
    FROM parts_inventory
    WHERE part_id = NEW.part_id;
    
    IF v_available_stock < NEW.quantity_used THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Insufficient inventory stock available for this part.';
    END IF;
END$$

-- Trigger 2: Automatically deduct inventory stock when part is consumed
CREATE TRIGGER trg_after_part_used_deduct_stock
AFTER INSERT ON request_parts_used
FOR EACH ROW
BEGIN
    UPDATE parts_inventory
    SET stock_quantity = stock_quantity - NEW.quantity_used
    WHERE part_id = NEW.part_id;
END$$

-- Trigger 3: Automatically restock inventory if usage record is removed
CREATE TRIGGER trg_after_part_usage_delete_restock
AFTER DELETE ON request_parts_used
FOR EACH ROW
BEGIN
    UPDATE parts_inventory
    SET stock_quantity = stock_quantity + OLD.quantity_used
    WHERE part_id = OLD.part_id;
END$$

DELIMITER ;
