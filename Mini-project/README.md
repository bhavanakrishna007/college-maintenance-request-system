# College Maintenance and Request System
## Database Design & Implementation Mini Project
**Course Code:** 24CS305 / CS3106 — DBMS Laboratory  
**Technology Stack:** Python 3 (Flask + HTML5 / CSS3 / JavaScript / Chart.js) & Python Tkinter + MySQL 8.0+  

---

## 📌 Project Overview
A complete, relational database application designed to manage and automate campus infrastructure complaints and maintenance workflows:
$$\text{Student/Staff Reports Issue} \longrightarrow \text{Categorized} \longrightarrow \text{Technician Assigned} \longrightarrow \text{Work Started} \longrightarrow \text{Parts Recorded} \longrightarrow \text{Issue Resolved}$$

### Key Technical Highlights:
- **Dual Front-End Interfaces:**
  1. **Modern Web Portal (Recommended):** Custom responsive CSS design system, glassmorphism topbar, Chart.js doughnut analytics, step-by-step interactive workflow console, real-time modal dialogs, and 1-click role switcher pills (`Admin`, `Faculty`, `Student`, `Technician`).
  2. **Desktop GUI Application:** Python Tkinter (`ttk` themed) desktop interface.
- **Relational Model Normalized to 3NF:** 8 interconnected tables with primary keys, foreign keys, and integrity constraints.
- **Advanced MySQL Features:**
  - **Relational Views:** `vw_active_requests`, `vw_technician_workload`, `vw_request_cost_summary`.
  - **Stored Procedures:** `sp_assign_technician`, `sp_start_maintenance_work`, `sp_resolve_maintenance_request`.
  - **Stored Function:** `fn_calculate_request_cost(request_id)`.
  - **Database Triggers:** Stock validation before part usage (`trg_check_stock_before_part_usage`), automatic inventory stock deduction (`trg_after_part_used_deduct_stock`), and delete restock (`trg_after_part_usage_delete_restock`).
- **Comprehensive DML Sample Data:** $\ge 10$ records populated across every major entity table.

---

## 🗂️ Directory Structure
```
college_maintenance_system/
├── web/                     # MODERN WEB APPLICATION
│   ├── server.py            # Flask Web Server & REST API
│   ├── templates/
│   │   └── index.html       # Single-Page Modern Web Portal
│   └── static/
│       ├── css/style.css    # Premium CSS Design System & Theme
│       └── js/app.js        # Dynamic UI Controller, Chart.js, Modals & Filters
├── database/
│   ├── schema.sql           # Complete DDL: Database, Tables, Constraints, Views, Procedures, Triggers
│   ├── sample_data.sql      # DML: Realistic dataset with >= 10 records per table
│   ├── queries.sql          # Advanced SQL queries (JOINs, Aggregates, Nested queries, Views)
│   └── setup_database.py    # Automated Python script to initialize database in MySQL
├── src/
│   ├── app.py               # Tkinter Desktop GUI
│   ├── models.py            # Business logic, CRUD operations, Stored procedure/view callers
│   ├── db_connection.py     # MySQL database connector and transaction manager
│   ├── config.py            # App settings, theme color palette, DB credentials
│   └── db_config.json       # Config file for customized MySQL credentials (auto-generated)
├── tests/
│   ├── test_system.py       # Automated backend integration test suite (10 tests)
│   └── test_web_api.py      # Automated Web API test suite (7 tests)
├── docs/
│   ├── PROJECT_REPORT.md    # Full academic project report (Chapters 1 to 9, References, Contributions)
│   ├── VIVA_QUESTIONS_AND_ANSWERS.md # 25 tailored DBMS lab viva questions & answers
│   └── ER_DIAGRAM.md        # Mermaid diagrams, Cardinalities, Relational Schemas, and 3NF proofs
├── run.bat                  # Interactive launcher (Choice of Web, Desktop, Setup, Tests)
├── run_web.bat              # Direct 1-click launcher for the Web Portal
└── README.md                # Project documentation and guide
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **MySQL Server 8.0+**
- Required Python packages:
  ```bash
  pip install mysql-connector-python flask
  ```

### 2. Initialize Database & Sample Data
Run the automated setup script to create `college_maintenance_db` and insert sample data:
```bash
python database/setup_database.py
```

### 3. Launch the Modern Web Application (Recommended)
Double-click [`run_web.bat`](file:///C:/Users/ASUS/.gemini/antigravity/scratch/college_maintenance_system/run_web.bat) or run:
```bash
python web/server.py
```
Then open your browser at:  
👉 **`http://127.0.0.1:5000`**

### 4. Interactive Launcher
You can also run [`run.bat`](file:///C:/Users/ASUS/.gemini/antigravity/scratch/college_maintenance_system/run.bat) to choose between the **Modern Web Portal**, **Desktop GUI**, **Database Setup**, or **Automated Test Suites**.

---

## 🔑 Login Roles & Credentials

| Role | Username | Password (Roll No) | Full Name / Description |
|---|---|---|---|
| **Student** | `bhavana` | `241141` | Bhavana (Student Reporter) |
| **Student** | `swapna` | `241136` | Swapna (Student Reporter) |
| **Student** | `meghana` | `241160` | Meghana (Student Reporter) |
| **Student** | `arundhathi` | `241107` | Arundhathi (Student Reporter) |
| **Faculty (Staff)** | `abhishek_saji` | `252101` | Prof. Ananya Sharma / Abhishek (Faculty) |
| **Technician** | `tech_murugan` | `tech123` | Murugan K (Electrician - Materials Selection & Repair) |
| **Admin** | `admin` | `admin123` | Dr. Rajesh Sundaram (Full System Access & Materials Auditing) |
