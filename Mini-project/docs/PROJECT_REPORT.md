# COLLEGE MAINTENANCE AND REQUEST SYSTEM
## Mini Project Report
**Course Code:** 24CS305 / CS3106  
**Course Name:** Database Management Systems Laboratory  
**Nature of Work:** Group Mini Project (4–5 Members)  
**Academic Year:** 2026–2027  

---

### BONAFIDE CERTIFICATE

Certified that this project report titled **"COLLEGE MAINTENANCE AND REQUEST SYSTEM"** is the bonafide work of the following students who carried out the project work under my supervision in partial fulfillment of the requirements for the award of the degree of Bachelor of Engineering in Computer Science and Engineering during the academic year 2026–2027.

| S.No. | Register Number | Student Name | Role / Task Assigned |
|---|---|---|---|
| 1 | 241141 | Bhavana (Lead) | Database Architecture, ER Modeling & DDL Scripts |
| 2 | 241136 | Swapna | Stored Procedures, Functions, Triggers & DML |
| 3 | 241160 | Meghana | Front-End Web UI Design, RBAC Gateway & Form Validations |
| 4 | 241107 | Arundhathi | Analytical Reports, Database Views & Query Optimization |
| 5 | 252101 | Abhishek Saji | System Testing, Test Cases & Report Documentation |

<br><br>

**Faculty In-Charge / Lab Instructor** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Head of the Department**  
Department of Computer Science & Engineering &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Department of Computer Science & Engineering  

---

### ABSTRACT
*(Word Count: 188 words)*

Managing campus infrastructure faults, repairs, and material allocations across multiple collegiate departments manually through physical registers or informal phone messages is slow, error-prone, lacks accountability, and fails to provide real-time status tracking. This mini project presents a **College Maintenance and Request System** that digitalizes and streamlines the entire maintenance lifecycle in a normalized relational database with an intuitive, role-based graphical web interface for students, faculty, administrators, and technicians.

The database was designed using an Entity–Relationship model comprising the core entities: **Departments, Users, Categories, Technicians, MaintenanceRequests, Assignments, PartsInventory, and RequestPartsUsed**, and was normalized up to Third Normal Form (3NF) to eliminate data redundancy and anomalies. The backend was implemented in MySQL with comprehensive constraints (`PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, and `CHECK`). The front end was developed as a modern web portal in Python (Flask) with HTML5, CSS3, JavaScript, and Chart.js.

The system enforces strict Role-Based Access Control (RBAC): students and faculty access dedicated issue reporting and personal ticket tracking, while administrators and technicians manage workflow progression, active triggers for parts inventory, and analytical DBMS views.

**Keywords:** Database Design, ER Model, 3NF Normalization, MySQL, Python Flask, RBAC, Triggers, Stored Procedures, Maintenance Tracking.

---

### TABLE OF CONTENTS

- **1. INTRODUCTION**
  - 1.1 Background
  - 1.2 Problem Statement
  - 1.3 Objectives
  - 1.4 Scope of the Project
- **2. REQUIREMENT ANALYSIS**
  - 2.1 Modules of the System & Role-Based Access Control
  - 2.2 Functional Requirements
  - 2.3 Hardware Requirements
  - 2.4 Software Requirements
- **3. DATABASE DESIGN**
  - 3.1 Entity–Relationship Diagram & Cardinality
  - 3.2 Relational Schema
  - 3.3 Normalization Steps (1NF, 2NF, 3NF with Justifications)
- **4. TABLE DESCRIPTION (DATA DICTIONARY)**
- **5. IMPLEMENTATION**
  - 5.1 Table Creation (DDL Scripts with Constraints)
  - 5.2 Data Insertion (DML Script with $\ge$ 10 records per table)
  - 5.3 Relational Views
  - 5.4 Stored Procedures and Functions
  - 5.5 Database Triggers
  - 5.6 Database Connectivity Code
- **6. FRONT-END DESIGN & ROLE-BASED INTERFACE**
- **7. OUTPUT SCREENSHOTS WITH EXPLANATION**
- **8. TESTING (TEST CASES & EXECUTION STATUS)**
- **9. CONCLUSION AND FUTURE ENHANCEMENTS**
- **REFERENCES**
- **CONTRIBUTION OF MEMBERS**
- **APPENDIX – SOURCE CODE**

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background
Colleges house extensive infrastructure spanning lecture halls, science laboratories, computer centers, faculty cabins, auditoriums, and residential hostels. Sustaining uninterrupted educational delivery necessitates prompt repair and preventive upkeep of electrical utilities, plumbing fixtures, HVAC systems, civil masonry, and IT network ports.

### 1.2 Problem Statement
In conventional campus setups, repair requests are submitted through handwritten registers, word-of-mouth notifications, or disparate emails. This manual approach presents critical challenges:
1. **Lack of Central Tracking:** Requests are misplaced, with no visibility into which issues are pending, assigned, or resolved.
2. **Untracked Material Costs:** Spare parts (tubelights, switches, CPVC pipes, cables) are consumed without linking them to specific maintenance tickets, enabling inventory leakage.
3. **Inefficient Technician Allocation:** Administrators cannot monitor technician workload or match job specializations to reported issues.
4. **Lack of Role Separation:** Students and faculty do not need to see technician wage structures, inventory procurement costs, or campus-wide administrative workloads; they only require an effortless mechanism to report problems and track their tickets.

### 1.3 Objectives
The principal objectives of this DBMS Mini Project are:
- To architect and normalize a relational database up to 3NF modeling campus maintenance operations.
- To enforce domain integrity using SQL constraints (`PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `UNIQUE`, `NOT NULL`).
- To implement business logic using Stored Procedures (`sp_assign_technician`, `sp_resolve_maintenance_request`) and Stored Functions (`fn_calculate_request_cost`).
- To enforce inventory consistency using active Database Triggers that validate stock and automatically adjust inventory balances.
- To implement Role-Based Access Control (RBAC):
  - **Student & Faculty:** Clean, intuitive interface for logging complaints and monitoring personal ticket progress.
  - **Technician & Admin:** Full operational workbench for task execution, material consumption, and administrative analytics.

### 1.4 Scope of the Project
The application addresses the full maintenance lifecycle:
$$\text{Student/Staff reports issue} \longrightarrow \text{Request categorized} \longrightarrow \text{Technician assigned} \longrightarrow \text{Work started} \longrightarrow \text{Parts recorded} \longrightarrow \text{Issue resolved}$$

---

## CHAPTER 2: REQUIREMENT ANALYSIS

### 2.1 Modules of the System & Role-Based Access Control
The system is divided into role-segmented modules:

1. **Role Selection & Authentication Gateway:**
   - Presents a modern card selection interface for **Student, Faculty, Technician, and Admin** with password authentication.
2. **Issue Reporting Module (Student & Faculty):**
   - Streamlined, non-cluttered form allowing users to enter issue title, category, priority, room/location, and problem description.
   - Auto-generates unique tracking codes (`REQ-2026-XXXX`).
3. **My Reported Requests Module (Student & Faculty):**
   - Dedicated table displaying only the tickets lodged by the logged-in user, showing real-time status (`Reported`, `Assigned`, `In-Progress`, `Resolved`), assigned technician name, and resolution remarks upon completion.
   - Internal parts costs, technician hourly wages, and campus-wide administrative data are strictly hidden.
4. **Technician Workbench & Workflow Module (Technician & Admin):**
   - Active task allocation console. Technicians mark work started via `sp_start_maintenance_work`, record replacement parts used with trigger validation, and resolve tickets via `sp_resolve_maintenance_request`.
5. **Parts Inventory Management Module (Admin & Technician):**
   - Real-time stock counts, reorder warnings, catalog management, and stock adjustments.
6. **Executive Analytics & DBMS Views Module (Admin Only):**
   - 6 KPI metric cards, Chart.js doughnut visualization, `vw_technician_workload`, `vw_request_cost_summary`, and departmental expenditure aggregations.

---

## CHAPTER 6: FRONT-END DESIGN & ROLE-BASED INTERFACE

The web portal was built using HTML5, CSS3, and JavaScript connected to Python Flask:
1. **Login Gateway:**
   - 4 responsive cards representing **Student**, **Faculty / Staff**, **Technician**, and **Administrator**.
   - Clicking any card populates the corresponding role credentials and allows instant entry with a single click.
2. **Student & Faculty Portal:**
   - Displays a clean hero section and a dedicated **"Report New Issue"** form.
   - The sidebar displays only **"Report New Issue"** and **"My Reported Requests"**, ensuring a clean experience.
3. **Technician Workspace:**
   - Displays **"Workflow & Active Tasks"**, **"All Campus Requests"**, and **"Parts & Inventory"**.
   - Allows technicians to commence tasks, consume replacement parts, and sign off tickets.
4. **Administrator Console:**
   - Full access to all 6 modules, including the Executive Dashboard, Full CRUD operations, Technician Assignment, Inventory, DBMS Reports, and Database Health Diagnostics.
5. **Session Management:**
   - A persistent topbar badge displays the user's name and role, with a prominent **"Switch Role / Logout"** button to return to the gateway at any time.

---

## CHAPTER 8: TESTING

### Table 8.1: Test Suite Matrix
| Test ID | Module Tested | Test Input / Action | Expected Output | Actual Output | Status |
|---|---|---|---|---|---|
| **TC-01** | Gateway Authentication | Select Student (`student_arun` / `pass123`) | Logged in as Student; Dashboard & Inventory hidden | Directed to Report Issue; Admin features hidden | **PASS** |
| **TC-02** | Gateway Authentication | Select Faculty (`staff_cse` / `staff123`) | Logged in as Faculty; Only personal tickets visible | Authenticated as Prof. Ananya Sharma | **PASS** |
| **TC-03** | Gateway Authentication | Select Technician (`tech_murugan` / `tech123`) | Logged in as Tech; Sees workflow & inventory | Authenticated as Murugan K (Electrician) | **PASS** |
| **TC-04** | Gateway Authentication | Select Admin (`admin` / `admin123`) | Logged in as Admin; Full access to all 6 modules | Full access granted to Dr. Rajesh Sundaram | **PASS** |
| **TC-05** | Access Control (RBAC) | Student requests `/api/dashboard` | Access denied with HTTP 403 Forbidden | HTTP 403 Forbidden returned | **PASS** |
| **TC-06** | Access Control (RBAC) | Student requests `/api/inventory` | Access denied with HTTP 403 Forbidden | HTTP 403 Forbidden returned | **PASS** |
| **TC-07** | Issue Reporting | Student submits issue for Ramanujan Hostel | Generates tracking code (`REQ-2026-0019`) & status 'Reported' | Record created and listed under student's tickets | **PASS** |
| **TC-08** | My Requests Filter | Student views requests table | Displays only tickets reported by student | Only student's tickets displayed | **PASS** |
| **TC-09** | Stored Procedure | Admin executes `sp_assign_technician` | Request status becomes 'Assigned'; Tech becomes 'Busy' | Status updated to 'Assigned' | **PASS** |
| **TC-10** | Stored Procedure | Tech executes `sp_start_maintenance_work` | Request status becomes 'In-Progress' | Status updated to 'In-Progress' | **PASS** |
| **TC-11** | Database Trigger | Record 2 units of part used | Trigger deducts 2 units from `parts_inventory.stock_quantity` | Stock decremented automatically | **PASS** |
| **TC-12** | Trigger Validation | Record quantity exceeding current stock | Trigger raises exception via `SIGNAL SQLSTATE '45000'` | Transaction aborted: "Insufficient stock" | **PASS** |
| **TC-13** | Stored Procedure | Tech executes `sp_resolve_maintenance_request` | Status becomes 'Resolved'; Tech freed to 'Available' | Status updated to 'Resolved' | **PASS** |
| **TC-14** | Relational View | Admin queries `vw_technician_workload` | Returns aggregated task counts per technician | 10 technician records populated | **PASS** |
| **TC-15** | Logout / Switch | Click "Switch Role / Logout" | Session cleared; returns to 4-role selection screen | Returned to Role Selection Gateway | **PASS** |

---

## CHAPTER 9: CONCLUSION
The application delivers strict separation of concerns, ensuring students and staff enjoy a straightforward complaint registration experience, while technical staff and administrators retain full visibility and control over campus infrastructure, parts inventory, and financial analytics.
