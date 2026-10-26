"""
College Maintenance and Request System - Front-End GUI
Course: 24CS305 / CS3106 - DBMS Laboratory
Technologies: Python Tkinter (ttk) + MySQL Connector
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys

# Ensure local imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import COLORS, load_db_config, save_db_config
from db_connection import test_connection_params, get_connection
import models

class CollegeMaintenanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("College Maintenance and Request System | DBMS Mini Project")
        self.geometry("1180x740")
        self.minsize(980, 640)
        self.configure(bg=COLORS["bg_light"])
        
        # State
        self.current_user = None
        
        # Setup ttk styling
        self.setup_styles()
        
        # Show Login Screen first
        self.show_login_screen()

    def setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # General styling
        style.configure(".", font=("Segoe UI", 10), background=COLORS["bg_light"], foreground=COLORS["text_dark"])
        
        # Treeview styling
        style.configure("Treeview", 
                        font=("Segoe UI", 9), 
                        rowheight=28, 
                        background="#FFFFFF", 
                        fieldbackground="#FFFFFF",
                        bordercolor=COLORS["border"])
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background="#E2E8F0", 
                        foreground=COLORS["primary_dark"])
        style.map("Treeview", background=[("selected", COLORS["secondary"])], foreground=[("selected", "#FFFFFF")])

        # Custom buttons
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=COLORS["primary"], foreground="#FFFFFF")
        style.map("Primary.TButton", background=[("active", COLORS["primary_dark"])])

        style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), background=COLORS["success"], foreground="#FFFFFF")
        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), background=COLORS["danger"], foreground="#FFFFFF")
        style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#94A3B8", foreground="#FFFFFF")

    # =========================================================================
    # LOGIN SCREEN
    # =========================================================================
    def show_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Center Container
        container = tk.Frame(self, bg=COLORS["bg_light"])
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        card = tk.Frame(container, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=35, pady=30)
        card.pack()

        # Header
        lbl_badge = tk.Label(card, text="Course: 24CS305 / CS3106 - DBMS Lab", font=("Segoe UI", 9, "bold"), bg="#EFF6FF", fg=COLORS["primary"], padx=10, pady=4)
        lbl_badge.pack(pady=(0, 10))

        lbl_title = tk.Label(card, text="College Maintenance &\nRequest System", font=("Segoe UI", 18, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"], justify=tk.CENTER)
        lbl_title.pack(pady=(0, 5))

        lbl_sub = tk.Label(card, text="Student / Staff Issue Reporting & Tracking Portal", font=("Segoe UI", 9), bg="#FFFFFF", fg=COLORS["text_light"])
        lbl_sub.pack(pady=(0, 20))

        # Form fields
        form_frame = tk.Frame(card, bg="#FFFFFF")
        form_frame.pack(fill=tk.X, pady=5)

        tk.Label(form_frame, text="Username:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", anchor="w").pack(fill=tk.X, pady=(5, 2))
        self.entry_username = ttk.Entry(form_frame, font=("Segoe UI", 10), width=32)
        self.entry_username.pack(fill=tk.X, pady=(0, 10))
        self.entry_username.insert(0, "admin")

        tk.Label(form_frame, text="Password:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", anchor="w").pack(fill=tk.X, pady=(5, 2))
        self.entry_password = ttk.Entry(form_frame, font=("Segoe UI", 10), width=32, show="*")
        self.entry_password.pack(fill=tk.X, pady=(0, 15))
        self.entry_password.insert(0, "admin123")
        self.entry_password.bind("<Return>", lambda e: self.do_login())

        # Login button
        btn_login = tk.Button(card, text="Sign In to Portal", font=("Segoe UI", 11, "bold"), bg=COLORS["primary"], fg="#FFFFFF", activebackground=COLORS["primary_dark"], activeforeground="#FFFFFF", relief=tk.FLAT, cursor="hand2", padx=15, pady=8, command=self.do_login)
        btn_login.pack(fill=tk.X, pady=(5, 15))

        # Quick Demo Login Pills
        tk.Label(card, text="--- Quick Demo Roles for Viva ---", font=("Segoe UI", 8, "italic"), bg="#FFFFFF", fg=COLORS["text_light"]).pack(pady=(5, 8))
        
        demo_btn_frame = tk.Frame(card, bg="#FFFFFF")
        demo_btn_frame.pack(fill=tk.X)

        demo_roles = [
            ("Admin", "admin", "admin123"),
            ("Abhishek", "abhishek_saji", "252101"),
            ("Bhavana", "bhavana", "241141"),
            ("Swapna", "swapna", "241136"),
            ("Murugan", "tech_murugan", "tech123")
        ]
        for name, u, p in demo_roles:
            btn = tk.Button(demo_btn_frame, text=name, font=("Segoe UI", 8), bg="#F1F5F9", fg=COLORS["primary_dark"], relief=tk.GROOVE, padx=5, pady=2,
                            command=lambda usr=u, pwd=p: self.fill_and_login(usr, pwd))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Bottom Bar: Database Settings
        db_frame = tk.Frame(card, bg="#FFFFFF")
        db_frame.pack(fill=tk.X, pady=(20, 0))
        btn_db = tk.Button(db_frame, text="⚙️ Database Connection Settings", font=("Segoe UI", 9), bg="#FFFFFF", fg=COLORS["secondary"], bd=0, cursor="hand2", command=self.open_db_settings_dialog)
        btn_db.pack()

    def fill_and_login(self, username, password):
        self.entry_username.delete(0, tk.END)
        self.entry_username.insert(0, username)
        self.entry_password.delete(0, tk.END)
        self.entry_password.insert(0, password)
        self.do_login()

    def do_login(self):
        u = self.entry_username.get().strip()
        p = self.entry_password.get().strip()
        if not u or not p:
            messagebox.showwarning("Validation Error", "Please provide both username and password.")
            return
        
        user_data, err = models.authenticate_user(u, p)
        if err:
            messagebox.showerror("Authentication Failed", f"{err}\n\nTip: Ensure the MySQL database is initialized via database/setup_database.py")
            return
        
        self.current_user = user_data
        self.show_main_portal()

    # =========================================================================
    # MAIN APPLICATION PORTAL
    # =========================================================================
    def show_main_portal(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Top Header Bar
        top_bar = tk.Frame(self, bg=COLORS["primary_dark"], height=55)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)

        lbl_app_name = tk.Label(top_bar, text="🏛️ College Maintenance & Request System", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg=COLORS["primary_dark"], padx=15)
        lbl_app_name.pack(side=tk.LEFT, fill=tk.Y)

        user_badge_text = f"👤 {self.current_user['full_name']} ({self.current_user['role']} - {self.current_user['dept_name']})"
        lbl_user = tk.Label(top_bar, text=user_badge_text, font=("Segoe UI", 9), fg="#93C5FD", bg=COLORS["primary_dark"], padx=10)
        lbl_user.pack(side=tk.RIGHT, fill=tk.Y)

        btn_logout = tk.Button(top_bar, text="Logout", font=("Segoe UI", 9, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, padx=12, pady=4, cursor="hand2", command=self.show_login_screen)
        btn_logout.pack(side=tk.RIGHT, padx=10, pady=12)

        # Main Body: Notebook with Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # 1. Dashboard Tab
        self.tab_dashboard = tk.Frame(self.notebook, bg=COLORS["bg_light"])
        self.notebook.add(self.tab_dashboard, text=" 📊 Dashboard ")
        self.build_dashboard_tab()

        # 2. Maintenance Requests Tab (CRUD)
        self.tab_requests = tk.Frame(self.notebook, bg=COLORS["bg_light"])
        self.notebook.add(self.tab_requests, text=" 📋 Maintenance Requests ")
        self.build_requests_tab()

        # 3. Technician Workflow Tab
        self.tab_workflow = tk.Frame(self.notebook, bg=COLORS["bg_light"])
        self.notebook.add(self.tab_workflow, text=" ⚙️ Workflow & Assignments ")
        self.build_workflow_tab()

        # 4. Parts Inventory Tab
        self.tab_inventory = tk.Frame(self.notebook, bg=COLORS["bg_light"])
        self.notebook.add(self.tab_inventory, text=" 📦 Parts & Materials ")
        self.build_inventory_tab()

        # 5. Reports & Analytics Tab
        self.tab_reports = tk.Frame(self.notebook, bg=COLORS["bg_light"])
        self.notebook.add(self.tab_reports, text=" 📈 Reports & Analytics ")
        self.build_reports_tab()

        # 6. About / Project Info Tab
        self.tab_about = tk.Frame(self.notebook, bg=COLORS["bg_light"])
        self.notebook.add(self.tab_about, text=" ℹ️ Project Info ")
        self.build_about_tab()

        # Bind tab change event to refresh data
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text").strip()
        if "Dashboard" in selected_tab:
            self.refresh_dashboard()
        elif "Requests" in selected_tab:
            self.refresh_requests_list()
        elif "Workflow" in selected_tab:
            self.refresh_workflow_tab()
        elif "Parts" in selected_tab:
            self.refresh_inventory_list()
        elif "Reports" in selected_tab:
            self.refresh_reports()

    # =========================================================================
    # TAB 1: DASHBOARD
    # =========================================================================
    def build_dashboard_tab(self):
        # Refresh header
        hdr = tk.Frame(self.tab_dashboard, bg=COLORS["bg_light"], pady=10)
        hdr.pack(fill=tk.X, padx=15)
        tk.Label(hdr, text="Executive Maintenance Dashboard", font=("Segoe UI", 16, "bold"), bg=COLORS["bg_light"], fg=COLORS["primary_dark"]).pack(side=tk.LEFT)
        btn_refresh = ttk.Button(hdr, text="🔄 Refresh Stats", command=self.refresh_dashboard)
        btn_refresh.pack(side=tk.RIGHT)

        # KPI Metric Cards Frame
        self.cards_frame = tk.Frame(self.tab_dashboard, bg=COLORS["bg_light"])
        self.cards_frame.pack(fill=tk.X, padx=15, pady=10)

        # Lower Split Frame: Category summary & Quick Actions
        split_frame = tk.Frame(self.tab_dashboard, bg=COLORS["bg_light"])
        split_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left: Category breakdown table
        left_box = tk.LabelFrame(split_frame, text=" Requests by Maintenance Category ", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=10, pady=10)
        left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        columns = ("category", "total", "open", "resolved", "sla")
        self.tree_cat_dash = ttk.Treeview(left_box, columns=columns, show="headings", height=8)
        self.tree_cat_dash.heading("category", text="Category")
        self.tree_cat_dash.heading("total", text="Total")
        self.tree_cat_dash.heading("open", text="Open")
        self.tree_cat_dash.heading("resolved", text="Resolved")
        self.tree_cat_dash.heading("sla", text="SLA (Hours)")
        self.tree_cat_dash.column("category", width=180)
        self.tree_cat_dash.column("total", width=60, anchor="center")
        self.tree_cat_dash.column("open", width=60, anchor="center")
        self.tree_cat_dash.column("resolved", width=70, anchor="center")
        self.tree_cat_dash.column("sla", width=80, anchor="center")
        self.tree_cat_dash.pack(fill=tk.BOTH, expand=True)

        # Right: Quick Shortcuts & Low Stock Warning
        right_box = tk.LabelFrame(split_frame, text=" Quick Actions & System Status ", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=15, pady=15)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(right_box, text="⚡ Fast Operations", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg=COLORS["primary"]).pack(anchor="w", pady=(0, 8))
        
        btn_new_req = tk.Button(right_box, text="➕ Report New Maintenance Issue", font=("Segoe UI", 10, "bold"), bg=COLORS["primary"], fg="#FFFFFF", padx=10, pady=6, bd=0, cursor="hand2", command=self.open_new_request_dialog)
        btn_new_req.pack(fill=tk.X, pady=4)

        btn_go_work = tk.Button(right_box, text="🛠️ Manage Technician Assignments", font=("Segoe UI", 10), bg="#E0F2FE", fg=COLORS["primary_dark"], padx=10, pady=6, bd=0, cursor="hand2", command=lambda: self.notebook.select(2))
        btn_go_work.pack(fill=tk.X, pady=4)

        btn_go_parts = tk.Button(right_box, text="📦 Check Parts Inventory & Consumption", font=("Segoe UI", 10), bg="#F1F5F9", fg=COLORS["text_dark"], padx=10, pady=6, bd=0, cursor="hand2", command=lambda: self.notebook.select(3))
        btn_go_parts.pack(fill=tk.X, pady=4)

        self.lbl_stock_alert = tk.Label(right_box, text="Checking inventory levels...", font=("Segoe UI", 9, "italic"), bg="#FEF3C7", fg="#92400E", padx=10, pady=8, wraplength=300)
        self.lbl_stock_alert.pack(fill=tk.X, pady=(15, 0))

        self.refresh_dashboard()

    def refresh_dashboard(self):
        # Clear cards
        for w in self.cards_frame.winfo_children():
            w.destroy()

        stats = models.get_dashboard_summary()
        card_data = [
            ("Total Requests", str(stats["total_requests"]), COLORS["primary"], "📋"),
            ("Pending / Assigned", str(stats["pending"]), COLORS["accent"], "⏳"),
            ("In-Progress", str(stats["in_progress"]), COLORS["secondary"], "⚙️"),
            ("Resolved Issues", str(stats["resolved"]), COLORS["success"], "✅"),
            ("Available Techs", str(stats["available_techs"]), "#6366F1", "👨‍🔧"),
            ("Parts Cost (₹)", f"₹{stats['total_parts_cost']:,.2f}", "#0D9488", "💰")
        ]

        for title, val, color, icon in card_data:
            c = tk.Frame(self.cards_frame, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=12, pady=10)
            c.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)

            tk.Label(c, text=f"{icon} {title}", font=("Segoe UI", 9), bg="#FFFFFF", fg=COLORS["text_light"]).pack(anchor="w")
            tk.Label(c, text=val, font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg=color).pack(anchor="w", pady=(4, 0))

        # Update category table
        for item in self.tree_cat_dash.get_children():
            self.tree_cat_dash.delete(item)
        
        cat_data, _ = models.get_category_distribution_report()
        for row in cat_data:
            self.tree_cat_dash.insert("", tk.END, values=(row["category_name"], row["total_requests"], row["open_count"], row["resolved_count"], f"{row['sla_hours']} hrs"))

        # Stock alert text
        low_count = stats["low_stock_parts"]
        if low_count > 0:
            self.lbl_stock_alert.config(text=f"⚠️ Warning: {low_count} inventory part(s) are at or below reorder level. Please check Inventory tab.", bg="#FEF3C7", fg="#92400E")
        else:
            self.lbl_stock_alert.config(text="✅ Inventory status healthy: All items above safety reorder thresholds.", bg="#D1FAE5", fg="#065F46")

    # =========================================================================
    # TAB 2: MAINTENANCE REQUESTS (FULL CRUD)
    # =========================================================================
    def build_requests_tab(self):
        # Filter & Search Toolbar
        filter_bar = tk.Frame(self.tab_requests, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        filter_bar.pack(fill=tk.X, padx=15, pady=(10, 5))

        tk.Label(filter_bar, text="🔍 Search:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(side=tk.LEFT, padx=(5, 2))
        self.entry_req_search = ttk.Entry(filter_bar, width=20)
        self.entry_req_search.pack(side=tk.LEFT, padx=5)
        self.entry_req_search.bind("<Return>", lambda e: self.refresh_requests_list())

        tk.Label(filter_bar, text="Status:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(side=tk.LEFT, padx=(10, 2))
        self.combo_req_status = ttk.Combobox(filter_bar, values=["All", "Reported", "Categorized", "Assigned", "In-Progress", "Resolved", "Closed"], state="readonly", width=12)
        self.combo_req_status.set("All")
        self.combo_req_status.pack(side=tk.LEFT, padx=5)
        self.combo_req_status.bind("<<ComboboxSelected>>", lambda e: self.refresh_requests_list())

        tk.Label(filter_bar, text="Priority:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(side=tk.LEFT, padx=(10, 2))
        self.combo_req_priority = ttk.Combobox(filter_bar, values=["All", "Emergency", "High", "Medium", "Low"], state="readonly", width=10)
        self.combo_req_priority.set("All")
        self.combo_req_priority.pack(side=tk.LEFT, padx=5)
        self.combo_req_priority.bind("<<ComboboxSelected>>", lambda e: self.refresh_requests_list())

        btn_filter = ttk.Button(filter_bar, text="Filter", command=self.refresh_requests_list)
        btn_filter.pack(side=tk.LEFT, padx=5)

        btn_clear_filter = ttk.Button(filter_bar, text="Clear", command=self.clear_request_filters)
        btn_clear_filter.pack(side=tk.LEFT, padx=2)

        # Right Action Buttons
        btn_new = tk.Button(filter_bar, text="➕ New Request", font=("Segoe UI", 9, "bold"), bg=COLORS["primary"], fg="#FFFFFF", padx=8, pady=3, bd=0, cursor="hand2", command=self.open_new_request_dialog)
        btn_new.pack(side=tk.RIGHT, padx=5)

        # Treeview Table for Requests
        table_frame = tk.Frame(self.tab_requests, bg=COLORS["bg_light"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        cols = ("id", "code", "title", "category", "dept", "location", "priority", "status", "reported_by", "technician", "date")
        self.tree_requests = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree_requests.heading("id", text="ID")
        self.tree_requests.heading("code", text="Tracking Code")
        self.tree_requests.heading("title", text="Issue Title")
        self.tree_requests.heading("category", text="Category")
        self.tree_requests.heading("dept", text="Department")
        self.tree_requests.heading("location", text="Location")
        self.tree_requests.heading("priority", text="Priority")
        self.tree_requests.heading("status", text="Status")
        self.tree_requests.heading("reported_by", text="Reported By")
        self.tree_requests.heading("technician", text="Technician")
        self.tree_requests.heading("date", text="Reported Date")

        self.tree_requests.column("id", width=35, anchor="center")
        self.tree_requests.column("code", width=100, anchor="center")
        self.tree_requests.column("title", width=180)
        self.tree_requests.column("category", width=110)
        self.tree_requests.column("dept", width=130)
        self.tree_requests.column("location", width=140)
        self.tree_requests.column("priority", width=75, anchor="center")
        self.tree_requests.column("status", width=85, anchor="center")
        self.tree_requests.column("reported_by", width=110)
        self.tree_requests.column("technician", width=110)
        self.tree_requests.column("date", width=110, anchor="center")

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_requests.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree_requests.xview)
        self.tree_requests.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_requests.pack(fill=tk.BOTH, expand=True)

        self.tree_requests.bind("<Double-1>", lambda e: self.open_request_details_dialog())

        # Bottom Action Bar
        act_bar = tk.Frame(self.tab_requests, bg=COLORS["bg_light"], pady=8)
        act_bar.pack(fill=tk.X, padx=15)

        btn_view = ttk.Button(act_bar, text="👁️ View Details & Timeline", command=self.open_request_details_dialog)
        btn_view.pack(side=tk.LEFT, padx=5)

        btn_edit = ttk.Button(act_bar, text="✏️ Edit Request", command=self.open_edit_request_dialog)
        btn_edit.pack(side=tk.LEFT, padx=5)

        btn_del = tk.Button(act_bar, text="🗑️ Delete Request", font=("Segoe UI", 9), bg=COLORS["danger"], fg="#FFFFFF", bd=0, padx=10, pady=3, cursor="hand2", command=self.delete_selected_request)
        btn_del.pack(side=tk.LEFT, padx=5)

        self.lbl_req_count = tk.Label(act_bar, text="Showing 0 requests", font=("Segoe UI", 9), bg=COLORS["bg_light"], fg=COLORS["text_light"])
        self.lbl_req_count.pack(side=tk.RIGHT, padx=5)

        self.refresh_requests_list()

    def clear_request_filters(self):
        self.entry_req_search.delete(0, tk.END)
        self.combo_req_status.set("All")
        self.combo_req_priority.set("All")
        self.refresh_requests_list()

    def refresh_requests_list(self):
        for item in self.tree_requests.get_children():
            self.tree_requests.delete(item)

        s = self.entry_req_search.get().strip()
        st = self.combo_req_status.get()
        p = self.combo_req_priority.get()

        user_id = self.current_user["user_id"] if self.current_user else None
        role = self.current_user["role"] if self.current_user else None

        data, err = models.get_requests(search=s, status=st, priority=p, user_id=user_id, role=role)
        if err:
            messagebox.showerror("Query Error", err)
            return

        for row in data:
            date_str = str(row["reported_at"])[:16] if row["reported_at"] else ""
            tech_name = row["technician_name"] if row["technician_name"] else "-"
            self.tree_requests.insert("", tk.END, values=(
                row["request_id"],
                row["tracking_code"],
                row["issue_title"],
                row["category_name"],
                row["dept_name"],
                row["location_details"],
                row["priority"],
                row["status"],
                row["reported_by"],
                tech_name,
                date_str
            ))

        self.lbl_req_count.config(text=f"Total records found: {len(data)}")

    def get_selected_request_id(self):
        sel = self.tree_requests.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a maintenance request from the table.")
            return None
        return self.tree_requests.item(sel[0])["values"][0]

    # Modal: Create New Maintenance Request
    def open_new_request_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Report New Maintenance Request")
        dlg.geometry("560x580")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frame = tk.Frame(dlg, bg="#FFFFFF", padx=25, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Lodge Maintenance Request", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w", pady=(0, 15))

        # Departments and Categories lookup
        depts, _ = models.get_departments()
        cats, _ = models.get_categories()

        dept_dict = {d["dept_name"]: d["dept_id"] for d in depts}
        cat_dict = {c["category_name"]: c["category_id"] for c in cats}

        # Issue Title
        tk.Label(frame, text="Issue Title *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(2, 2))
        entry_title = ttk.Entry(frame, width=50)
        entry_title.pack(fill=tk.X, pady=(0, 8))

        # Category & Priority
        row_cp = tk.Frame(frame, bg="#FFFFFF")
        row_cp.pack(fill=tk.X, pady=(0, 8))

        col_c = tk.Frame(row_cp, bg="#FFFFFF")
        col_c.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Label(col_c, text="Category *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_cat = ttk.Combobox(col_c, values=list(cat_dict.keys()), state="readonly")
        combo_cat.pack(fill=tk.X)
        if cats:
            combo_cat.current(0)

        col_p = tk.Frame(row_cp, bg="#FFFFFF")
        col_p.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        tk.Label(col_p, text="Priority *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_pri = ttk.Combobox(col_p, values=["Low", "Medium", "High", "Emergency"], state="readonly")
        combo_pri.set("Medium")
        combo_pri.pack(fill=tk.X)

        # Department
        tk.Label(frame, text="Department *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(2, 2))
        combo_dept = ttk.Combobox(frame, values=list(dept_dict.keys()), state="readonly")
        combo_dept.pack(fill=tk.X, pady=(0, 8))
        if depts:
            combo_dept.current(0)

        # Location Details
        tk.Label(frame, text="Specific Location (Room/Floor/Building) *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(2, 2))
        entry_loc = ttk.Entry(frame, width=50)
        entry_loc.pack(fill=tk.X, pady=(0, 8))
        entry_loc.insert(0, "e.g., Turing Block, 2nd Floor, Room 204")

        # Description
        tk.Label(frame, text="Detailed Issue Description *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(2, 2))
        txt_desc = tk.Text(frame, height=5, font=("Segoe UI", 9), relief=tk.SOLID, bd=1)
        txt_desc.pack(fill=tk.X, pady=(0, 15))

        def submit():
            title = entry_title.get().strip()
            cat_name = combo_cat.get()
            dept_name = combo_dept.get()
            loc = entry_loc.get().strip()
            pri = combo_pri.get()
            desc = txt_desc.get("1.0", tk.END).strip()

            if not title or not cat_name or not dept_name or not loc or not desc:
                messagebox.showerror("Validation Error", "All fields marked with * are required.", parent=dlg)
                return

            cat_id = cat_dict[cat_name]
            dept_id = dept_dict[dept_name]
            reported_by_id = self.current_user["user_id"] if self.current_user else 1

            req_id, code, err = models.create_request(reported_by_id, cat_id, dept_id, loc, title, desc, pri)
            if err:
                messagebox.showerror("Database Error", err, parent=dlg)
                return

            messagebox.showinfo("Success", f"Maintenance request registered successfully!\nGenerated Tracking Code: {code}", parent=dlg)
            dlg.destroy()
            self.refresh_requests_list()
            self.refresh_dashboard()

        btn_submit = tk.Button(frame, text="Submit Request", font=("Segoe UI", 10, "bold"), bg=COLORS["primary"], fg="#FFFFFF", padx=15, pady=8, bd=0, cursor="hand2", command=submit)
        btn_submit.pack(fill=tk.X)

    # Modal: Edit Existing Request
    def open_edit_request_dialog(self):
        req_id = self.get_selected_request_id()
        if not req_id:
            return

        req, err = models.get_request_by_id(req_id)
        if err or not req:
            messagebox.showerror("Error", err or "Request not found.")
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Edit Request #{req_id} - {req['tracking_code']}")
        dlg.geometry("560x600")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frame = tk.Frame(dlg, bg="#FFFFFF", padx=25, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text=f"Update Request: {req['tracking_code']}", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w", pady=(0, 15))

        depts, _ = models.get_departments()
        cats, _ = models.get_categories()
        dept_dict = {d["dept_name"]: d["dept_id"] for d in depts}
        cat_dict = {c["category_name"]: c["category_id"] for c in cats}

        tk.Label(frame, text="Issue Title:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_title = ttk.Entry(frame, width=50)
        entry_title.pack(fill=tk.X, pady=(0, 8))
        entry_title.insert(0, req["issue_title"])

        # Category and Priority
        row_cp = tk.Frame(frame, bg="#FFFFFF")
        row_cp.pack(fill=tk.X, pady=(0, 8))

        col_c = tk.Frame(row_cp, bg="#FFFFFF")
        col_c.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Label(col_c, text="Category:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_cat = ttk.Combobox(col_c, values=list(cat_dict.keys()), state="readonly")
        combo_cat.set(req["category_name"])
        combo_cat.pack(fill=tk.X)

        col_p = tk.Frame(row_cp, bg="#FFFFFF")
        col_p.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        tk.Label(col_p, text="Priority:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_pri = ttk.Combobox(col_p, values=["Low", "Medium", "High", "Emergency"], state="readonly")
        combo_pri.set(req["priority"])
        combo_pri.pack(fill=tk.X)

        # Department and Status
        row_ds = tk.Frame(frame, bg="#FFFFFF")
        row_ds.pack(fill=tk.X, pady=(0, 8))

        col_d = tk.Frame(row_ds, bg="#FFFFFF")
        col_d.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Label(col_d, text="Department:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_dept = ttk.Combobox(col_d, values=list(dept_dict.keys()), state="readonly")
        combo_dept.set(req["dept_name"])
        combo_dept.pack(fill=tk.X)

        col_s = tk.Frame(row_ds, bg="#FFFFFF")
        col_s.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        tk.Label(col_s, text="Status:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_st = ttk.Combobox(col_s, values=["Reported", "Categorized", "Assigned", "In-Progress", "Resolved", "Closed"], state="readonly")
        combo_st.set(req["status"])
        combo_st.pack(fill=tk.X)

        # Location Details
        tk.Label(frame, text="Location:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_loc = ttk.Entry(frame, width=50)
        entry_loc.pack(fill=tk.X, pady=(0, 8))
        entry_loc.insert(0, req["location_details"])

        # Description
        tk.Label(frame, text="Description:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        txt_desc = tk.Text(frame, height=5, font=("Segoe UI", 9), relief=tk.SOLID, bd=1)
        txt_desc.pack(fill=tk.X, pady=(0, 15))
        txt_desc.insert("1.0", req["issue_description"])

        def save_changes():
            ok, uerr = models.update_request(
                req_id,
                cat_dict[combo_cat.get()],
                dept_dict[combo_dept.get()],
                entry_loc.get().strip(),
                entry_title.get().strip(),
                txt_desc.get("1.0", tk.END).strip(),
                combo_pri.get(),
                combo_st.get()
            )
            if not ok:
                messagebox.showerror("Update Error", uerr, parent=dlg)
                return
            messagebox.showinfo("Saved", "Maintenance request updated successfully.", parent=dlg)
            dlg.destroy()
            self.refresh_requests_list()
            self.refresh_dashboard()

        btn_save = tk.Button(frame, text="Save Updates", font=("Segoe UI", 10, "bold"), bg=COLORS["primary"], fg="#FFFFFF", padx=15, pady=8, bd=0, cursor="hand2", command=save_changes)
        btn_save.pack(fill=tk.X)

    # Delete Request
    def delete_selected_request(self):
        req_id = self.get_selected_request_id()
        if not req_id:
            return

        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete Maintenance Request #{req_id}?\nAll associated assignments and material usage will also be removed."):
            return

        ok, err = models.delete_request(req_id)
        if not ok:
            messagebox.showerror("Delete Failed", err)
            return

        messagebox.showinfo("Deleted", f"Request #{req_id} was deleted.")
        self.refresh_requests_list()
        self.refresh_dashboard()

    # View Details Dialog
    def open_request_details_dialog(self):
        req_id = self.get_selected_request_id()
        if not req_id:
            return

        req, err = models.get_request_by_id(req_id)
        if err or not req:
            messagebox.showerror("Error", err or "Request not found.")
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Request Details - {req['tracking_code']}")
        dlg.geometry("700x650")
        dlg.transient(self)

        container = tk.Frame(dlg, bg="#FFFFFF", padx=20, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Header info
        hdr_frame = tk.Frame(container, bg="#FFFFFF")
        hdr_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(hdr_frame, text=f"{req['tracking_code']}: {req['issue_title']}", font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w")
        tk.Label(hdr_frame, text=f"Status: {req['status']} | Priority: {req['priority']} | Category: {req['category_name']}", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg=COLORS["secondary"]).pack(anchor="w")

        # Meta Details Grid
        meta_box = tk.LabelFrame(container, text=" Request Information ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", padx=10, pady=8)
        meta_box.pack(fill=tk.X, pady=5)

        info_items = [
            ("Department:", f"{req['dept_name']} ({req['building']})"),
            ("Location:", req['location_details']),
            ("Reported By:", f"{req['reported_by']} ({req['reporter_email']})"),
            ("Reported Date:", str(req['reported_at'])[:19]),
            ("Resolved Date:", str(req['resolved_at'])[:19] if req['resolved_at'] else "Pending Resolution")
        ]
        for idx, (lbl, val) in enumerate(info_items):
            tk.Label(meta_box, text=lbl, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg=COLORS["text_light"]).grid(row=idx, column=0, sticky="w", pady=2)
            tk.Label(meta_box, text=val, font=("Segoe UI", 9), bg="#FFFFFF", fg=COLORS["text_dark"]).grid(row=idx, column=1, sticky="w", padx=10, pady=2)

        # Issue Description
        desc_box = tk.LabelFrame(container, text=" Description & Resolution Notes ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", padx=10, pady=8)
        desc_box.pack(fill=tk.X, pady=5)

        tk.Label(desc_box, text=f"Problem: {req['issue_description']}", font=("Segoe UI", 9), bg="#FFFFFF", wraplength=640, justify=tk.LEFT).pack(anchor="w", pady=(0, 4))
        if req['resolution_notes']:
            tk.Label(desc_box, text=f"Resolution: {req['resolution_notes']}", font=("Segoe UI", 9, "italic"), bg="#FFFFFF", fg=COLORS["success"], wraplength=640, justify=tk.LEFT).pack(anchor="w")

        # Parts Used Table
        parts_box = tk.LabelFrame(container, text=" Materials & Parts Consumed ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", padx=10, pady=8)
        parts_box.pack(fill=tk.BOTH, expand=True, pady=5)

        parts_data, _ = models.get_request_parts_used(req_id)
        cols_p = ("part", "qty", "unit_cost", "total_cost", "notes")
        tree_p = ttk.Treeview(parts_box, columns=cols_p, show="headings", height=4)
        tree_p.heading("part", text="Part Name")
        tree_p.heading("qty", text="Qty Used")
        tree_p.heading("unit_cost", text="Unit Price (₹)")
        tree_p.heading("total_cost", text="Total (₹)")
        tree_p.heading("notes", text="Usage Notes")

        tree_p.column("part", width=180)
        tree_p.column("qty", width=60, anchor="center")
        tree_p.column("unit_cost", width=90, anchor="center")
        tree_p.column("total_cost", width=90, anchor="center")
        tree_p.column("notes", width=180)
        tree_p.pack(fill=tk.BOTH, expand=True)

        total_parts_cost = 0.0
        for p in parts_data:
            total_parts_cost += float(p["total_cost"])
            tree_p.insert("", tk.END, values=(p["part_name"], f"{p['quantity_used']} {p['unit_of_measure']}", f"₹{p['unit_cost_charged']:.2f}", f"₹{p['total_cost']:.2f}", p["notes"] or "-"))

        tk.Label(parts_box, text=f"Total Material Cost: ₹{total_parts_cost:,.2f}", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="e", pady=(5, 0))

    # =========================================================================
    # TAB 3: TECHNICIAN WORKFLOW & ASSIGNMENTS
    # =========================================================================
    def build_workflow_tab(self):
        # Interactive Workflow Stepper Guide
        stepper_bar = tk.Frame(self.tab_workflow, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=15, pady=10)
        stepper_bar.pack(fill=tk.X, padx=15, pady=10)

        steps = [
            ("1. Report Issue", "Student / Faculty lodges maintenance complaint"),
            ("2. Categorize", "Assign category & priority (Electrical, HVAC, Plumbing)"),
            ("3. Assign Technician", "System assigns qualified technician"),
            ("4. Work In-Progress", "Technician begins on-site inspection & repair"),
            ("5. Parts Consumed", "Record replacement materials from inventory"),
            ("6. Issue Resolved", "Technician completes task & logs resolution")
        ]
        tk.Label(stepper_bar, text="Complete Lifecycle Process Flow", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w", pady=(0, 6))
        flow_line = " ➔ ".join([f"[{s[0]}]" for s in steps])
        tk.Label(stepper_bar, text=flow_line, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg=COLORS["secondary"]).pack(anchor="w")

        # Two Column Layout: Left Request Selector, Right Execution Actions
        split_frame = tk.Frame(self.tab_workflow, bg=COLORS["bg_light"])
        split_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Left: Active Requests Selector
        left_box = tk.LabelFrame(split_frame, text=" Select Active Request to Advance Workflow ", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=10, pady=10)
        left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        cols_wf = ("id", "code", "title", "category", "status", "priority", "technician")
        self.tree_wf_reqs = ttk.Treeview(left_box, columns=cols_wf, show="headings", selectmode="browse")
        self.tree_wf_reqs.heading("id", text="ID")
        self.tree_wf_reqs.heading("code", text="Code")
        self.tree_wf_reqs.heading("title", text="Issue")
        self.tree_wf_reqs.heading("category", text="Category")
        self.tree_wf_reqs.heading("status", text="Status")
        self.tree_wf_reqs.heading("priority", text="Priority")
        self.tree_wf_reqs.heading("technician", text="Technician")

        self.tree_wf_reqs.column("id", width=35, anchor="center")
        self.tree_wf_reqs.column("code", width=85, anchor="center")
        self.tree_wf_reqs.column("title", width=140)
        self.tree_wf_reqs.column("category", width=95)
        self.tree_wf_reqs.column("status", width=85, anchor="center")
        self.tree_wf_reqs.column("priority", width=70, anchor="center")
        self.tree_wf_reqs.column("technician", width=95)

        self.tree_wf_reqs.pack(fill=tk.BOTH, expand=True)
        self.tree_wf_reqs.bind("<<TreeviewSelect>>", self.on_workflow_request_selected)

        # Right: Step Execution Panel
        right_box = tk.LabelFrame(split_frame, text=" Workflow Actions ", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=15, pady=10)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.lbl_selected_wf = tk.Label(right_box, text="Please select a request from the list.", font=("Segoe UI", 10, "italic"), bg="#FFFFFF", fg=COLORS["text_light"])
        self.lbl_selected_wf.pack(anchor="w", pady=(0, 10))

        # Action 1: Assign Technician
        act1_box = tk.LabelFrame(right_box, text=" Step 1: Assign Technician (Stored Proc) ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", padx=10, pady=8)
        act1_box.pack(fill=tk.X, pady=5)

        tk.Label(act1_box, text="Available Technicians:", font=("Segoe UI", 8, "bold"), bg="#FFFFFF").pack(anchor="w")
        self.combo_techs = ttk.Combobox(act1_box, state="readonly", width=35)
        self.combo_techs.pack(fill=tk.X, pady=(2, 6))

        btn_assign = tk.Button(act1_box, text="Assign Selected Technician", font=("Segoe UI", 9, "bold"), bg=COLORS["primary"], fg="#FFFFFF", bd=0, padx=10, pady=4, cursor="hand2", command=self.do_assign_technician)
        btn_assign.pack(anchor="w")

        # Action 2: Start Work
        act2_box = tk.LabelFrame(right_box, text=" Step 2: Start Work (Stored Proc) ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", padx=10, pady=8)
        act2_box.pack(fill=tk.X, pady=5)

        self.entry_start_notes = ttk.Entry(act2_box, width=35)
        self.entry_start_notes.pack(fill=tk.X, pady=(2, 6))
        self.entry_start_notes.insert(0, "e.g. Tools gathered; on-site inspection begun")

        btn_start = tk.Button(act2_box, text="Mark Work Started (In-Progress)", font=("Segoe UI", 9, "bold"), bg=COLORS["secondary"], fg="#FFFFFF", bd=0, padx=10, pady=4, cursor="hand2", command=self.do_start_work)
        btn_start.pack(anchor="w")

        # Action 3: Record Materials Used
        act3_box = tk.LabelFrame(right_box, text=" Step 3: Record Used Parts (Trigger Deducts Stock) ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", padx=10, pady=8)
        act3_box.pack(fill=tk.X, pady=5)

        btn_add_part = tk.Button(act3_box, text="➕ Consume Inventory Parts...", font=("Segoe UI", 9, "bold"), bg="#0D9488", fg="#FFFFFF", bd=0, padx=10, pady=4, cursor="hand2", command=self.open_record_parts_dialog)
        btn_add_part.pack(anchor="w")

        # Action 4: Resolve Request
        act4_box = tk.LabelFrame(right_box, text=" Step 4: Resolve & Close Request (Stored Proc) ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", padx=10, pady=8)
        act4_box.pack(fill=tk.X, pady=5)

        self.entry_resolve_notes = ttk.Entry(act4_box, width=35)
        self.entry_resolve_notes.pack(fill=tk.X, pady=(2, 6))
        self.entry_resolve_notes.insert(0, "e.g. Parts replaced, tested successfully and signed off")

        btn_resolve = tk.Button(act4_box, text="Mark Resolved & Complete Task", font=("Segoe UI", 9, "bold"), bg=COLORS["success"], fg="#FFFFFF", bd=0, padx=10, pady=4, cursor="hand2", command=self.do_resolve_request)
        btn_resolve.pack(anchor="w")

        self.refresh_workflow_tab()

    def refresh_workflow_tab(self):
        for item in self.tree_wf_reqs.get_children():
            self.tree_wf_reqs.delete(item)

        reqs, _ = models.get_requests()
        for r in reqs:
            tech = r["technician_name"] or "-"
            self.tree_wf_reqs.insert("", tk.END, values=(r["request_id"], r["tracking_code"], r["issue_title"], r["category_name"], r["status"], r["priority"], tech))

        # Refresh technicians combobox
        techs, _ = models.get_technicians()
        self.tech_dict = {f"{t['name']} ({t['specialization']}) - Status: {t['status']}": t["technician_id"] for t in techs}
        self.combo_techs["values"] = list(self.tech_dict.keys())
        if self.tech_dict:
            self.combo_techs.current(0)

    def on_workflow_request_selected(self, event):
        sel = self.tree_wf_reqs.selection()
        if not sel:
            return
        vals = self.tree_wf_reqs.item(sel[0])["values"]
        self.lbl_selected_wf.config(text=f"Selected: #{vals[0]} - {vals[1]} ({vals[2]})\nCurrent Status: {vals[4]} | Assigned Tech: {vals[6]}", fg=COLORS["primary_dark"])

    def get_selected_wf_request_id(self):
        sel = self.tree_wf_reqs.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a request from the left table.")
            return None
        return self.tree_wf_reqs.item(sel[0])["values"][0]

    def do_assign_technician(self):
        req_id = self.get_selected_wf_request_id()
        if not req_id:
            return
        tech_str = self.combo_techs.get()
        if not tech_str or tech_str not in self.tech_dict:
            messagebox.showerror("Error", "Please select a technician.")
            return

        tech_id = self.tech_dict[tech_str]
        admin_id = self.current_user["user_id"] if self.current_user else 1

        ok, err = models.assign_technician(req_id, tech_id, admin_id)
        if not ok:
            messagebox.showerror("Procedure Error", f"Failed to assign technician: {err}")
            return

        messagebox.showinfo("Success", f"Technician successfully assigned to Request #{req_id} via sp_assign_technician!")
        self.refresh_workflow_tab()
        self.refresh_dashboard()

    def do_start_work(self):
        req_id = self.get_selected_wf_request_id()
        if not req_id:
            return
        notes = self.entry_start_notes.get().strip()

        ok, err = models.start_maintenance_work(req_id, notes)
        if not ok:
            messagebox.showerror("Procedure Error", f"Failed to start work: {err}")
            return

        messagebox.showinfo("Success", f"Work marked as In-Progress via sp_start_maintenance_work!")
        self.refresh_workflow_tab()
        self.refresh_dashboard()

    def do_resolve_request(self):
        req_id = self.get_selected_wf_request_id()
        if not req_id:
            return
        notes = self.entry_resolve_notes.get().strip()

        ok, err = models.resolve_maintenance_request(req_id, notes)
        if not ok:
            messagebox.showerror("Procedure Error", f"Failed to resolve request: {err}")
            return

        messagebox.showinfo("Success", f"Request #{req_id} marked as Resolved via sp_resolve_maintenance_request!\nTechnician has been freed and reset to 'Available'.")
        self.refresh_workflow_tab()
        self.refresh_dashboard()

    # Modal: Consume Inventory Parts for Request
    def open_record_parts_dialog(self):
        req_id = self.get_selected_wf_request_id()
        if not req_id:
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Record Parts Used for Request #{req_id}")
        dlg.geometry("520x460")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frame = tk.Frame(dlg, bg="#FFFFFF", padx=25, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text=f"Record Materials for Request #{req_id}", font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w", pady=(0, 10))
        tk.Label(frame, text="Note: Database triggers will automatically validate stock availability and deduct quantities.", font=("Segoe UI", 8, "italic"), bg="#FFFFFF", fg=COLORS["text_light"], wraplength=460).pack(anchor="w", pady=(0, 12))

        parts, _ = models.get_inventory_parts()
        part_dict = {f"{p['part_name']} [Stock: {p['stock_quantity']} {p['unit_of_measure']} @ ₹{p['unit_cost']}]": p for p in parts}

        tk.Label(frame, text="Select Part from Inventory *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_part = ttk.Combobox(frame, values=list(part_dict.keys()), state="readonly", width=45)
        combo_part.pack(fill=tk.X, pady=(2, 10))
        if part_dict:
            combo_part.current(0)

        tk.Label(frame, text="Quantity Used *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_qty = ttk.Entry(frame, width=20)
        entry_qty.pack(fill=tk.X, pady=(2, 10))
        entry_qty.insert(0, "1")

        tk.Label(frame, text="Usage Notes (Optional):", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_notes = ttk.Entry(frame, width=45)
        entry_notes.pack(fill=tk.X, pady=(2, 15))
        entry_notes.insert(0, "e.g. Installed during on-site visit")

        def submit_usage():
            sel_str = combo_part.get()
            if not sel_str or sel_str not in part_dict:
                messagebox.showerror("Error", "Please select a valid part.", parent=dlg)
                return

            part_obj = part_dict[sel_str]
            try:
                qty = int(entry_qty.get().strip())
                if qty <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Validation Error", "Quantity must be a positive integer.", parent=dlg)
                return

            notes = entry_notes.get().strip()

            ok, err = models.record_part_usage(req_id, part_obj["part_id"], qty, notes)
            if not ok:
                messagebox.showerror("Trigger Rejection", f"Database Trigger prevented insertion:\n\n{err}", parent=dlg)
                return

            messagebox.showinfo("Success", f"Recorded {qty} {part_obj['unit_of_measure']} of '{part_obj['part_name']}'!\nInventory stock was automatically decremented by database trigger.", parent=dlg)
            dlg.destroy()
            self.refresh_dashboard()

        btn_save = tk.Button(frame, text="Record Part & Deduct Stock", font=("Segoe UI", 10, "bold"), bg=COLORS["success"], fg="#FFFFFF", padx=15, pady=8, bd=0, cursor="hand2", command=submit_usage)
        btn_save.pack(fill=tk.X)

    # =========================================================================
    # TAB 4: PARTS INVENTORY
    # =========================================================================
    def build_inventory_tab(self):
        # Top toolbar
        toolbar = tk.Frame(self.tab_inventory, bg=COLORS["bg_light"], pady=8)
        toolbar.pack(fill=tk.X, padx=15)

        tk.Label(toolbar, text="Spare Parts, Consumables & Fixtures Inventory", font=("Segoe UI", 14, "bold"), bg=COLORS["bg_light"], fg=COLORS["primary_dark"]).pack(side=tk.LEFT)

        btn_add = tk.Button(toolbar, text="➕ Add New Part", font=("Segoe UI", 9, "bold"), bg=COLORS["primary"], fg="#FFFFFF", padx=10, pady=4, bd=0, cursor="hand2", command=self.open_add_part_dialog)
        btn_add.pack(side=tk.RIGHT, padx=5)

        btn_update_stock = ttk.Button(toolbar, text="✏️ Adjust Stock", command=self.adjust_part_stock)
        btn_update_stock.pack(side=tk.RIGHT, padx=5)

        # Inventory Table
        cols_inv = ("id", "name", "category", "unit", "cost", "stock", "reorder", "status")
        self.tree_inv = ttk.Treeview(self.tab_inventory, columns=cols_inv, show="headings", selectmode="browse")

        self.tree_inv.heading("id", text="Part ID")
        self.tree_inv.heading("name", text="Part / Material Name")
        self.tree_inv.heading("category", text="Category")
        self.tree_inv.heading("unit", text="UOM")
        self.tree_inv.heading("cost", text="Unit Price (₹)")
        self.tree_inv.heading("stock", text="Stock Available")
        self.tree_inv.heading("reorder", text="Reorder Level")
        self.tree_inv.heading("status", text="Stock Status")

        self.tree_inv.column("id", width=60, anchor="center")
        self.tree_inv.column("name", width=220)
        self.tree_inv.column("category", width=140)
        self.tree_inv.column("unit", width=65, anchor="center")
        self.tree_inv.column("cost", width=95, anchor="center")
        self.tree_inv.column("stock", width=95, anchor="center")
        self.tree_inv.column("reorder", width=90, anchor="center")
        self.tree_inv.column("status", width=110, anchor="center")

        self.tree_inv.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.refresh_inventory_list()

    def refresh_inventory_list(self):
        for item in self.tree_inv.get_children():
            self.tree_inv.delete(item)

        parts, err = models.get_inventory_parts()
        if err:
            messagebox.showerror("Error", err)
            return

        for p in parts:
            stock = p["stock_quantity"]
            reorder = p["reorder_level"]
            status_str = "⚠️ Reorder Needed" if stock <= reorder else "✅ In Stock"
            self.tree_inv.insert("", tk.END, values=(
                p["part_id"],
                p["part_name"],
                p["category"],
                p["unit_of_measure"],
                f"₹{p['unit_cost']:.2f}",
                stock,
                reorder,
                status_str
            ))

    def adjust_part_stock(self):
        sel = self.tree_inv.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Select an inventory item to update stock.")
            return

        vals = self.tree_inv.item(sel[0])["values"]
        part_id = vals[0]
        curr_stock = vals[5]

        new_val = simpledialog.askinteger("Adjust Stock", f"Enter new stock quantity for '{vals[1]}':", initialvalue=curr_stock, minvalue=0, parent=self)
        if new_val is not None:
            ok, err = models.update_inventory_stock(part_id, new_val)
            if not ok:
                messagebox.showerror("Update Error", err)
                return
            messagebox.showinfo("Updated", "Inventory stock updated successfully.")
            self.refresh_inventory_list()
            self.refresh_dashboard()

    def open_add_part_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add New Inventory Part")
        dlg.geometry("450x420")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frame = tk.Frame(dlg, bg="#FFFFFF", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Add Item to Parts Inventory", font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Part Name *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_name = ttk.Entry(frame, width=40)
        entry_name.pack(fill=tk.X, pady=(2, 8))

        tk.Label(frame, text="Category *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        combo_cat = ttk.Combobox(frame, values=["Electrical", "Plumbing", "HVAC / Air Conditioning", "IT & Networking", "Carpentry & Furniture", "Civil & Masonry"], state="readonly")
        combo_cat.current(0)
        combo_cat.pack(fill=tk.X, pady=(2, 8))

        row_cost = tk.Frame(frame, bg="#FFFFFF")
        row_cost.pack(fill=tk.X, pady=(0, 8))

        c1 = tk.Frame(row_cost, bg="#FFFFFF")
        c1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Label(c1, text="Unit Cost (₹) *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_cost = ttk.Entry(c1)
        entry_cost.pack(fill=tk.X)
        entry_cost.insert(0, "150.00")

        c2 = tk.Frame(row_cost, bg="#FFFFFF")
        c2.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        tk.Label(c2, text="Unit of Measure *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_uom = ttk.Entry(c2)
        entry_uom.pack(fill=tk.X)
        entry_uom.insert(0, "pcs")

        row_stock = tk.Frame(frame, bg="#FFFFFF")
        row_stock.pack(fill=tk.X, pady=(0, 15))

        s1 = tk.Frame(row_stock, bg="#FFFFFF")
        s1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Label(s1, text="Initial Stock *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_stock = ttk.Entry(s1)
        entry_stock.pack(fill=tk.X)
        entry_stock.insert(0, "20")

        s2 = tk.Frame(row_stock, bg="#FFFFFF")
        s2.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        tk.Label(s2, text="Reorder Level *:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
        entry_reorder = ttk.Entry(s2)
        entry_reorder.pack(fill=tk.X)
        entry_reorder.insert(0, "5")

        def submit():
            name = entry_name.get().strip()
            cat = combo_cat.get()
            uom = entry_uom.get().strip()
            try:
                cost = float(entry_cost.get().strip())
                stock = int(entry_stock.get().strip())
                reorder = int(entry_reorder.get().strip())
                if cost < 0 or stock < 0 or reorder < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Validation Error", "Numeric values must be valid and non-negative.", parent=dlg)
                return

            if not name or not uom:
                messagebox.showerror("Validation Error", "Name and unit of measure are required.", parent=dlg)
                return

            part_id, err = models.add_inventory_part(name, cat, uom, cost, stock, reorder)
            if err:
                messagebox.showerror("Database Error", err, parent=dlg)
                return

            messagebox.showinfo("Success", f"Part '{name}' added successfully (ID #{part_id}).", parent=dlg)
            dlg.destroy()
            self.refresh_inventory_list()
            self.refresh_dashboard()

        btn_save = tk.Button(frame, text="Add Part to Inventory", font=("Segoe UI", 10, "bold"), bg=COLORS["primary"], fg="#FFFFFF", padx=15, pady=8, bd=0, cursor="hand2", command=submit)
        btn_save.pack(fill=tk.X)

    # =========================================================================
    # TAB 5: REPORTS & ANALYTICS (VIEWS & AGGREGATE QUERIES)
    # =========================================================================
    def build_reports_tab(self):
        # Selector bar
        bar = tk.Frame(self.tab_reports, bg=COLORS["bg_light"], pady=10)
        bar.pack(fill=tk.X, padx=15)

        tk.Label(bar, text="Select DBMS Analytical Report:", font=("Segoe UI", 11, "bold"), bg=COLORS["bg_light"], fg=COLORS["primary_dark"]).pack(side=tk.LEFT, padx=(0, 10))
        
        self.report_type = ttk.Combobox(bar, values=[
            "1. Technician Workload & Performance (View: vw_technician_workload)",
            "2. Request Cost Breakdown (View: vw_request_cost_summary)",
            "3. Department Maintenance Expenditure (JOIN & Aggregate SUM)",
            "4. Category-Wise SLA & Request Volume (GROUP BY)"
        ], state="readonly", width=55)
        self.report_type.current(0)
        self.report_type.pack(side=tk.LEFT, padx=5)
        self.report_type.bind("<<ComboboxSelected>>", lambda e: self.refresh_reports())

        btn_run = ttk.Button(bar, text="Run Report Query", command=self.refresh_reports)
        btn_run.pack(side=tk.LEFT, padx=5)

        # SQL Explanation Label
        self.lbl_report_sql = tk.Label(self.tab_reports, text="", font=("Courier New", 9), bg="#F1F5F9", fg=COLORS["text_dark"], bd=1, relief=tk.SOLID, padx=10, pady=6, anchor="w", justify=tk.LEFT)
        self.lbl_report_sql.pack(fill=tk.X, padx=15, pady=(0, 5))

        # Report Treeview
        self.tree_reports = ttk.Treeview(self.tab_reports, show="headings", height=15)
        self.tree_reports.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.refresh_reports()

    def refresh_reports(self):
        # Clear existing treeview
        self.tree_reports.delete(*self.tree_reports.get_children())
        choice = self.report_type.current()

        if choice == 0:
            # Technician Workload View
            self.lbl_report_sql.config(text="SQL: SELECT * FROM vw_technician_workload ORDER BY total_assigned_tasks DESC;")
            cols = ("id", "name", "spec", "status", "total", "pending", "in_prog", "completed")
            self.tree_reports["columns"] = cols
            self.tree_reports.heading("id", text="Tech ID")
            self.tree_reports.heading("name", text="Technician Name")
            self.tree_reports.heading("spec", text="Specialization")
            self.tree_reports.heading("status", text="Current Status")
            self.tree_reports.heading("total", text="Total Tasks")
            self.tree_reports.heading("pending", text="Pending")
            self.tree_reports.heading("in_prog", text="In-Progress")
            self.tree_reports.heading("completed", text="Completed")

            data, err = models.get_technician_workload_report()
            for r in data:
                self.tree_reports.insert("", tk.END, values=(
                    r["technician_id"], r["technician_name"], r["specialization"], r["current_status"],
                    r["total_assigned_tasks"], r["pending_tasks"] or 0, r["in_progress_tasks"] or 0, r["completed_tasks"] or 0
                ))

        elif choice == 1:
            # Request Cost Summary View
            self.lbl_report_sql.config(text="SQL: SELECT * FROM vw_request_cost_summary ORDER BY total_parts_cost DESC;")
            cols = ("code", "title", "cat", "status", "parts_count", "items_qty", "cost")
            self.tree_reports["columns"] = cols
            self.tree_reports.heading("code", text="Tracking Code")
            self.tree_reports.heading("title", text="Issue Title")
            self.tree_reports.heading("cat", text="Category")
            self.tree_reports.heading("status", text="Status")
            self.tree_reports.heading("parts_count", text="Part Types")
            self.tree_reports.heading("items_qty", text="Total Units Consumed")
            self.tree_reports.heading("cost", text="Total Materials Cost (₹)")

            data, err = models.get_request_cost_summary_report()
            for r in data:
                self.tree_reports.insert("", tk.END, values=(
                    r["tracking_code"], r["issue_title"], r["category_name"], r["status"],
                    r["parts_count"], r["total_items_consumed"], f"₹{r['total_parts_cost']:,.2f}"
                ))

        elif choice == 2:
            # Department Expenditure JOIN & SUM
            self.lbl_report_sql.config(text="SQL: SELECT d.dept_name, d.building, COUNT(mr.request_id), SUM(rpu.total_cost) FROM departments d ... GROUP BY dept_id;")
            cols = ("dept", "bldg", "reqs", "expenditure")
            self.tree_reports["columns"] = cols
            self.tree_reports.heading("dept", text="Department")
            self.tree_reports.heading("bldg", text="Campus Building")
            self.tree_reports.heading("reqs", text="Total Requests Lodged")
            self.tree_reports.heading("expenditure", text="Total Parts Expenditure (₹)")

            data, err = models.get_department_expenditure_report()
            for r in data:
                self.tree_reports.insert("", tk.END, values=(
                    r["dept_name"], r["building"], r["request_count"], f"₹{r['total_cost']:,.2f}"
                ))

        elif choice == 3:
            # Category SLA & Request Volume
            self.lbl_report_sql.config(text="SQL: SELECT c.category_name, COUNT(mr.request_id), SUM(Resolved), SLA FROM categories c GROUP BY category_id;")
            cols = ("cat", "total", "resolved", "open", "sla")
            self.tree_reports["columns"] = cols
            self.tree_reports.heading("cat", text="Maintenance Category")
            self.tree_reports.heading("total", text="Total Requests")
            self.tree_reports.heading("resolved", text="Resolved")
            self.tree_reports.heading("open", text="Open / Pending")
            self.tree_reports.heading("sla", text="Target SLA (Hours)")

            data, err = models.get_category_distribution_report()
            for r in data:
                self.tree_reports.insert("", tk.END, values=(
                    r["category_name"], r["total_requests"], r["resolved_count"], r["open_count"], f"{r['sla_hours']} hrs"
                ))

    # =========================================================================
    # TAB 6: ABOUT / PROJECT INFO
    # =========================================================================
    def build_about_tab(self):
        container = tk.Frame(self.tab_about, bg="#FFFFFF", padx=25, pady=20)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(container, text="Course: 24CS305 / CS3106 - DBMS Laboratory", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w")
        tk.Label(container, text="Project Title: College Maintenance and Request System", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg=COLORS["secondary"]).pack(anchor="w", pady=(2, 10))

        desc = (
            "This application automates and optimizes the end-to-end campus maintenance lifecycle:\n"
            "Student/Staff reports issue ➔ Request categorized ➔ Technician assigned ➔ Work started ➔ Parts recorded ➔ Issue resolved.\n\n"
            "Key Database Features Demonstrated:\n"
            "• Relational Schema Normalized up to 3NF (7 core entity tables)\n"
            "• Relational Constraints: PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK, DEFAULT\n"
            "• Advanced Views: vw_active_requests, vw_technician_workload, vw_request_cost_summary\n"
            "• Stored Procedures: sp_assign_technician, sp_start_maintenance_work, sp_resolve_maintenance_request\n"
            "• Stored Function: fn_calculate_request_cost(request_id)\n"
            "• Database Triggers: trg_check_stock_before_part_usage, trg_after_part_used_deduct_stock, trg_after_part_usage_delete_restock\n"
            "• Front-End: Python Tkinter (ttk themed) with role-based UI and full CRUD support."
        )
        tk.Label(container, text=desc, font=("Segoe UI", 9), bg="#FFFFFF", justify=tk.LEFT, wraplength=850).pack(anchor="w", pady=(0, 15))

        group_box = tk.LabelFrame(container, text=" Group Members & Contribution Details ", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=15, pady=10)
        group_box.pack(fill=tk.X)

        members = [
            ("Student 1 (Team Lead)", "Database Architecture, ER Modeling, 3NF Normalization & DDL Script"),
            ("Student 2", "Stored Procedures, Functions, Triggers & Business Logic Implementation"),
            ("Student 3", "Python Tkinter Front-End UI, Role Authentication & Form Validations"),
            ("Student 4", "Analytical Views, JOIN Reports, Test Case Execution & Project Documentation")
        ]
        for role, contrib in members:
            row = tk.Frame(group_box, bg="#FFFFFF")
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=f"• {role}:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", width=22, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=contrib, font=("Segoe UI", 9), bg="#FFFFFF").pack(side=tk.LEFT)

    # =========================================================================
    # DB SETTINGS DIALOG
    # =========================================================================
    def open_db_settings_dialog(self):
        cfg = load_db_config()
        dlg = tk.Toplevel(self)
        dlg.title("MySQL Database Connection Settings")
        dlg.geometry("450x380")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frame = tk.Frame(dlg, bg="#FFFFFF", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Configure MySQL Connection", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg=COLORS["primary_dark"]).pack(anchor="w", pady=(0, 10))

        fields = [
            ("Host:", "host", cfg["host"]),
            ("Port:", "port", str(cfg["port"])),
            ("User:", "user", cfg["user"]),
            ("Password:", "password", cfg["password"]),
            ("Database:", "database", cfg["database"])
        ]
        entries = {}
        for lbl, key, default in fields:
            tk.Label(frame, text=lbl, font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack(anchor="w")
            e = ttk.Entry(frame, width=35, show="*" if key == "password" else "")
            e.pack(fill=tk.X, pady=(2, 6))
            e.insert(0, default)
            entries[key] = e

        def test_conn():
            h = entries["host"].get().strip()
            p = entries["port"].get().strip()
            u = entries["user"].get().strip()
            pwd = entries["password"].get().strip()
            db = entries["database"].get().strip()
            ok, msg = test_connection_params(h, p, u, pwd, db)
            if ok:
                messagebox.showinfo("Connection Test", f"✅ {msg}", parent=dlg)
            else:
                messagebox.showerror("Connection Test", f"❌ {msg}", parent=dlg)

        def save_and_close():
            new_cfg = {
                "host": entries["host"].get().strip(),
                "port": int(entries["port"].get().strip()),
                "user": entries["user"].get().strip(),
                "password": entries["password"].get().strip(),
                "database": entries["database"].get().strip()
            }
            save_db_config(new_cfg)
            messagebox.showinfo("Saved", "Database configuration saved successfully.", parent=dlg)
            dlg.destroy()

        btn_row = tk.Frame(frame, bg="#FFFFFF")
        btn_row.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(btn_row, text="🔌 Test Connection", command=test_conn).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_row, text="Save & Apply", font=("Segoe UI", 9, "bold"), bg=COLORS["primary"], fg="#FFFFFF", bd=0, padx=12, pady=4, cursor="hand2", command=save_and_close).pack(side=tk.RIGHT)

def main():
    app = CollegeMaintenanceApp()
    app.mainloop()

if __name__ == "__main__":
    main()
