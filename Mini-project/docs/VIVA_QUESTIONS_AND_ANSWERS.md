# DBMS LABORATORY VIVA QUESTIONS & ANSWERS
## Project Title: College Maintenance and Request System
**Course Code:** 24CS305 / CS3106 - Database Management Systems Laboratory  
**Prepared for:** Group Viva Demonstration  

---

### SECTION 1: DATABASE DESIGN & NORMALIZATION

#### Q1: What is the Entity-Relationship (ER) model of your project?
**Answer:**  
Our ER model consists of 8 core entities:
1. `departments`: Represents collegiate academic and administrative blocks.
2. `users`: Stores system users categorized into Admin, Staff, Student, and Technician roles.
3. `categories`: Defines maintenance disciplines (Electrical, Plumbing, HVAC, IT & Networking, Carpentry, Civil) with target SLAs.
4. `technicians`: Stores technical personnel with specific specializations, hourly labor rates, and availability states.
5. `maintenance_requests`: The central transaction entity capturing student/staff complaints with location, priority, and status.
6. `assignments`: Tracks work orders, linking requests to assigned technicians and logging start/end timestamps.
7. `parts_inventory`: Catalogs spare parts, unit procurement costs, available quantities, and reorder levels.
8. `request_parts_used`: A bridge table recording materials consumed per maintenance ticket.

#### Q2: What normal form does your database achieve? Justify with examples.
**Answer:**  
Our database is normalized up to **Third Normal Form (3NF)**:
- **1NF:** Every attribute contains only atomic scalar values. Repeating groups such as parts consumed were decomposed into the separate table `request_parts_used`.
- **2NF:** It is in 1NF and contains no partial functional dependencies. In composite relationship records, non-prime attributes depend on the entire candidate key rather than any proper subset. Part details (`part_name`, `unit_cost`) are isolated in `parts_inventory` rather than repeated in usage records.
- **3NF:** It is in 2NF and has no transitive dependencies ($X \rightarrow Y$ and $Y \rightarrow Z$). For instance, in `maintenance_requests`, we do not store `department_building` or `user_email`. We only store Foreign Keys `dept_id` and `reported_by_id`, fetching user and location details via relational joins. Thus, every determinant is a superkey.

#### Q3: What is the primary difference between 2NF and 3NF?
**Answer:**  
- **2NF** eliminates **partial dependencies**, where a non-prime attribute depends only on part of a composite primary key.
- **3NF** eliminates **transitive dependencies**, where a non-prime attribute depends on another non-prime attribute rather than directly on the primary key ($A \rightarrow B \rightarrow C$).

---

### SECTION 2: SQL CONSTRAINTS & INTEGRITY RULES

#### Q4: What constraints did you use in your MySQL database schema?
**Answer:**  
1. `PRIMARY KEY`: Uniquely identifies tuples (e.g., `request_id`, `user_id`, `dept_id`).
2. `FOREIGN KEY`: Enforces referential integrity between child and parent tables with `ON UPDATE CASCADE` and `ON DELETE RESTRICT` / `ON DELETE CASCADE`.
3. `NOT NULL`: Ensures required attributes cannot be left blank (e.g., `issue_title`, `location_details`).
4. `UNIQUE`: Guarantees uniqueness for attributes like `tracking_code`, `username`, `email`, and `part_name`.
5. `CHECK`: Restricts permissible ranges, such as `CHECK (stock_quantity >= 0)` and `CHECK (unit_cost >= 0.00)`.
6. `DEFAULT`: Automatically sets initial values, such as `DEFAULT 'Reported'` for request status and `DEFAULT CURRENT_TIMESTAMP`.

#### Q5: What happens when an administrator tries to delete a department with active requests?
**Answer:**  
Because we specified `ON DELETE RESTRICT` on the Foreign Key `dept_id` in `maintenance_requests`, the MySQL engine rejects the deletion and raises a foreign key constraint violation error. This ensures data integrity by preventing orphan request records.

---

### SECTION 3: STORED PROCEDURES, FUNCTIONS & TRIGGERS

#### Q6: What is a Stored Procedure, and where did you use it?
**Answer:**  
A Stored Procedure is a precompiled set of one or more SQL statements saved in the database server:
1. `sp_assign_technician`: Takes `request_id`, `technician_id`, and `admin_id`. It inserts an assignment record, changes request status from `'Reported'` to `'Assigned'`, and sets technician status to `'Busy'` inside a single transaction.
2. `sp_start_maintenance_work`: Updates request status to `'In-Progress'` and logs work start timestamp.
3. `sp_resolve_maintenance_request`: Sets request status to `'Resolved'`, stamps `resolved_at = NOW()`, marks the assignment as completed, and resets the technician to `'Available'`.

#### Q7: What is the difference between a Stored Procedure and a Stored Function?
**Answer:**  
- A **Stored Function** must return a single value using the `RETURN` statement and can be embedded directly within `SELECT` statements (e.g., `SELECT tracking_code, fn_calculate_request_cost(request_id) FROM maintenance_requests`).
- A **Stored Procedure** is executed using `CALL` and can execute multiple DDL/DML statements, modify table states, and return zero, one, or multiple output parameters.

#### Q8: What triggers are implemented in your project?
**Answer:**  
1. `trg_check_stock_before_part_usage` (`BEFORE INSERT ON request_parts_used`):  
   Verifies whether `stock_quantity >= NEW.quantity_used`. If insufficient stock exists, it raises an error via `SIGNAL SQLSTATE '45000'`, preventing the insert.
2. `trg_after_part_used_deduct_stock` (`AFTER INSERT ON request_parts_used`):  
   Automatically subtracts the consumed quantity from `parts_inventory.stock_quantity`.
3. `trg_after_part_usage_delete_restock` (`AFTER DELETE ON request_parts_used`):  
   Automatically restores stock in `parts_inventory` if a usage record is deleted.

---

### SECTION 4: VIEWS & COMPLEX QUERIES

#### Q9: What is a Database View, and why did you use it?
**Answer:**  
A View is a virtual table defined by an underlying SQL `SELECT` query. It does not store physical data itself (unless materialized), but simplifies complex queries, improves security by hiding sensitive columns, and provides a clean abstraction for front-end reporting.  
In our project:
- `vw_active_requests`: Flattens a 5-table join into an easy-to-query virtual table.
- `vw_technician_workload`: Aggregates active and completed jobs per technician.
- `vw_request_cost_summary`: Computes material expenses per maintenance ticket.

#### Q10: How do you find the department with the highest maintenance costs?
**Answer:**  
Using `JOIN`, `GROUP BY`, and aggregate `SUM`:
```sql
SELECT 
    d.dept_name, 
    COALESCE(SUM(rpu.total_cost), 0.00) AS total_expenditure
FROM departments d
JOIN maintenance_requests mr ON d.dept_id = mr.dept_id
LEFT JOIN request_parts_used rpu ON mr.request_id = rpu.request_id
GROUP BY d.dept_id, d.dept_name
ORDER BY total_expenditure DESC
LIMIT 1;
```

#### Q11: What is the difference between `WHERE` and `HAVING` in SQL?
**Answer:**  
- `WHERE` filters rows *before* any groupings or aggregate functions are calculated.
- `HAVING` filters groups *after* the `GROUP BY` clause and aggregation have been performed (e.g., `HAVING SUM(rpu.total_cost) > 1000`).

---

### SECTION 5: FRONT-END & CONNECTIVITY

#### Q12: How does Python Tkinter communicate with MySQL?
**Answer:**  
Using the official `mysql-connector-python` library. The application creates a connection via `mysql.connector.connect()`, acquires a cursor, executes parameterized queries using `%s` placeholders (which prevents SQL injection), commits transactions via `conn.commit()`, and closes resources in `finally` blocks.

#### Q13: What measures did you take against SQL Injection?
**Answer:**  
We avoided string concatenation (e.g. `f"SELECT * FROM users WHERE username = '{u}'"`). Instead, we utilized parameterized queries across all database calls (`cursor.execute(sql, (param1, param2))`), ensuring that user inputs are treated strictly as data literals and never executed as executable SQL syntax.
