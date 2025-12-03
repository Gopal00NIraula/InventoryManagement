import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from controllers.inventory_controller import create_item, edit_item, remove_item, find_items
from controllers.supplier_controller import create_supplier, list_suppliers, update_supplier, delete_supplier, search_suppliers
from controllers.customer_controller import create_customer, list_customers, update_customer, delete_customer, search_customers
from controllers.reports_controller import (
    generate_inventory_summary, generate_sales_report, generate_purchase_report,
    generate_stock_movement_report, generate_low_stock_report, generate_profit_analysis
)
from controllers.purchase_order_controller import (
    create_purchase_order, list_purchase_orders, complete_purchase_order, 
    cancel_purchase_order, delete_purchase_order
)
from controllers.sales_order_controller import (
    create_sales_order, list_sales_orders, complete_sales_order,
    cancel_sales_order, delete_sales_order
)
from models.user_model import create_user, delete_user, list_team_employees, list_all_users, update_user
from utils.permissions import can_manage_inventory, can_manage_users, is_admin, is_staff, has_permission

class DashboardPage(tk.Frame):
    def __init__(self, master, current_user: dict):
        super().__init__(master, bg="#f5f3ff")
        self.current_user = current_user

        # Header with purple gradient
        hdr = tk.Frame(self, bg="#7c3aed", height=80)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        
        # Title and user info
        tk.Label(
            hdr,
            text=f"Inventory Dashboard",
            font=("Segoe UI", 22, "bold"),
            bg="#7c3aed", fg="white"
        ).pack(side="left", padx=20, pady=20)
        
        # User info and actions container
        actions_frame = tk.Frame(hdr, bg="#7c3aed")
        actions_frame.pack(side="right", padx=20, pady=20)
        
        tk.Label(
            actions_frame,
            text=f"{current_user['username']} [{current_user['role']}]",
            font=("Segoe UI", 11),
            bg="#7c3aed", fg="white"
        ).pack(side="left", padx=10)
        
        # Email Settings button (Admin only)
        if current_user.get('role') == 'ADMIN':
            tk.Button(
                actions_frame, text="⚙️ Email Settings",
                font=("Segoe UI", 10, "bold"),
                bg="#c084fc", fg="white",
                activebackground="#a855f7",
                activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                command=self._open_email_settings
            ).pack(side="left", padx=5, ipady=8, ipadx=15)
        
        # User Management button
        self.btn_user_mgmt = tk.Button(
            actions_frame, text="User Management",
            font=("Segoe UI", 10, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._open_user_mgmt
        )
        self.btn_user_mgmt.pack(side="left", padx=5, ipady=8, ipadx=15)
        
        # Logout button
        tk.Button(
            actions_frame, text="Log out",
            font=("Segoe UI", 10, "bold"),
            bg="#6b21a8", fg="white",
            activebackground="#581c87",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._logout
        ).pack(side="left", padx=5, ipady=8, ipadx=15)

        # Stock Alerts Panel
        self._create_alerts_panel()

        # Main content area with tabs
        content = tk.Frame(self, bg="#f5f3ff")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create notebook (tabbed interface)
        style = ttk.Style()
        style.theme_use("clam")
        
        # Tab styling
        style.configure("Dashboard.TNotebook", background="#f5f3ff", borderwidth=0)
        style.configure("Dashboard.TNotebook.Tab",
            background="#ddd6fe",
            foreground="#1f2937",
            padding=[20, 10],
            font=("Segoe UI", 11, "bold")
        )
        style.map("Dashboard.TNotebook.Tab",
            background=[("selected", "#7c3aed"), ("active", "#a78bfa")],
            foreground=[("selected", "white"), ("active", "white")]
        )
        
        self.notebook = ttk.Notebook(content, style="Dashboard.TNotebook")
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self._create_dashboard_overview_tab()
        self._create_inventory_tab()
        self._create_suppliers_tab()
        self._create_customers_tab()
        self._create_purchase_orders_tab()
        self._create_sales_orders_tab()
        self._create_reports_tab()
        self._create_audit_logs_tab()
        
        self._apply_role_locks()
        self._on_search()

    def _create_alerts_panel(self):
        """Create stock alerts notification panel"""
        from models.stock_alert_model import get_alert_summary
        
        alerts_container = tk.Frame(self, bg="#f5f3ff")
        alerts_container.pack(fill="x", padx=20, pady=(10, 0))
        
        self.alerts_frame = tk.Frame(alerts_container, bg="#fef3c7", relief="solid", bd=1)
        self.alerts_label = tk.Label(
            self.alerts_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#fef3c7",
            fg="#92400e",
            anchor="w",
            padx=15,
            pady=10
        )
        self.alerts_label.pack(fill="x")
        
        # View Details button
        self.btn_view_alerts = tk.Button(
            self.alerts_frame,
            text="View Details →",
            font=("Segoe UI", 9, "bold"),
            bg="#fbbf24",
            fg="#78350f",
            activebackground="#f59e0b",
            activeforeground="#78350f",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._show_alerts_dialog
        )
        self.btn_view_alerts.pack(side="right", padx=15, pady=5)
        
        # Initially hidden, will show when alerts exist
        self._update_alerts_panel()

    def _update_alerts_panel(self):
        """Update the alerts panel with current alert counts"""
        from models.stock_alert_model import get_alert_summary
        
        result = get_alert_summary()
        if result.get("success"):
            summary = result["summary"]
            total = summary["TOTAL"]
            
            if total > 0:
                out_of_stock = summary.get("OUT_OF_STOCK", 0)
                low_stock = summary.get("LOW_STOCK", 0)
                reorder = summary.get("REORDER", 0)
                
                parts = []
                if out_of_stock > 0:
                    parts.append(f"🔴 {out_of_stock} out of stock")
                if low_stock > 0:
                    parts.append(f"🟡 {low_stock} low stock")
                if reorder > 0:
                    parts.append(f"⚠️ {reorder} need reorder")
                
                alert_text = f"⚠️ STOCK ALERTS: {', '.join(parts)}"
                self.alerts_label.config(text=alert_text)
                self.alerts_frame.pack(fill="x", pady=(0, 10))
            else:
                self.alerts_frame.pack_forget()

    def _show_alerts_dialog(self):
        """Show detailed stock alerts dialog"""
        from models.stock_alert_model import get_active_alerts, resolve_alert
        
        dialog = tk.Toplevel(self)
        dialog.title("Stock Alerts")
        dialog.configure(bg="#f5f3ff")
        dialog.geometry("900x600")
        
        # Header
        header = tk.Frame(dialog, bg="#f59e0b")
        header.pack(fill="x")
        tk.Label(header, text="Stock Alerts & Notifications", font=("Segoe UI", 18, "bold"),
                bg="#f59e0b", fg="white").pack(pady=15)
        
        # Table
        table_frame = tk.Frame(dialog, bg="white", bd=0)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        cols = ("id", "type", "item", "sku", "qty_alert", "current_qty", "message", "created")
        alerts_table = ttk.Treeview(table_frame, columns=cols, show="headings", style="Purple.Treeview")
        for c, h, w in (("id", "ID", 50), ("type", "Type", 120), ("item", "Item", 150),
                        ("sku", "SKU", 100), ("qty_alert", "Qty@Alert", 90),
                        ("current_qty", "Current", 80), ("message", "Message", 250),
                        ("created", "Created", 140)):
            alerts_table.heading(c, text=h)
            alerts_table.column(c, width=w, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=alerts_table.yview)
        alerts_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        alerts_table.pack(fill="both", expand=True)
        
        def load_alerts():
            result = get_active_alerts()
            for i in alerts_table.get_children():
                alerts_table.delete(i)
            
            if result.get("success"):
                for alert in result["alerts"]:
                    alerts_table.insert("", "end", values=(
                        alert["id"],
                        alert["alert_type"],
                        alert["item_name"],
                        alert["sku"],
                        alert["quantity_at_alert"],
                        alert["current_quantity"],
                        alert["message"],
                        alert["created_at"][:16] if alert["created_at"] else ""
                    ))
        
        load_alerts()
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="#f5f3ff")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def resolve_selected():
            sel = alerts_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select an alert to resolve")
                return
            
            vals = alerts_table.item(sel)["values"]
            alert_id = int(vals[0])
            
            result = resolve_alert(alert_id)
            if result.get("success"):
                load_alerts()
                self._update_alerts_panel()
                messagebox.showinfo("Success", "Alert resolved")
            else:
                messagebox.showerror("Error", result.get("message"))
        
        tk.Button(btn_frame, text="Resolve Selected", font=("Segoe UI", 11, "bold"),
                 bg="#10b981", fg="white", relief="flat", cursor="hand2",
                 command=resolve_selected).pack(side="left", ipady=10, ipadx=30)
        
        tk.Button(btn_frame, text="Refresh", font=("Segoe UI", 11, "bold"),
                 bg="#7c3aed", fg="white", relief="flat", cursor="hand2",
                 command=load_alerts).pack(side="left", padx=10, ipady=10, ipadx=30)
        
        tk.Button(btn_frame, text="Close", font=("Segoe UI", 11),
                 bg="#d1d5db", fg="#1f2937", relief="flat", cursor="hand2",
                 command=dialog.destroy).pack(side="right", ipady=10, ipadx=30)

    def _create_dashboard_overview_tab(self):
        """Create dashboard overview tab with statistics and widgets"""
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="🏠 Dashboard", sticky="nsew")
        
        # Create scrollable container
        canvas = tk.Canvas(tab, bg="#f5f3ff", highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient="vertical", command=canvas.yview, width=8)
        scrollable_frame = tk.Frame(canvas, bg="#f5f3ff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Main content
        content = tk.Frame(scrollable_frame, bg="#f5f3ff")
        content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Welcome header
        tk.Label(
            content,
            text=f"Welcome back, {self.current_user['username']}!",
            font=("Segoe UI", 18, "bold"),
            bg="#f5f3ff", fg="#6b21a8"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            content,
            text=f"Role: {self.current_user['role']} | {datetime.now().strftime('%A, %B %d, %Y')}",
            font=("Segoe UI", 11),
            bg="#f5f3ff", fg="#6b7280"
        ).pack(anchor="w", pady=(0, 20))
        
        # Statistics cards frame (8 cards in 2 rows)
        stats_frame = tk.Frame(content, bg="#f5f3ff")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Activity frames (two side by side at bottom)
        bottom_frame = tk.Frame(content, bg="#f5f3ff")
        bottom_frame.pack(fill="both", expand=True)
        
        activity_frame1 = tk.Frame(bottom_frame, bg="#f5f3ff")
        activity_frame1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        activity_frame2 = tk.Frame(bottom_frame, bg="#f5f3ff")
        activity_frame2.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Refresh button
        refresh_btn = tk.Button(
            content,
            text="🔄 Refresh Dashboard",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6b21a8",
            relief="flat", cursor="hand2",
            command=lambda: self._refresh_dashboard(stats_frame, activity_frame1, activity_frame2)
        )
        refresh_btn.pack(anchor="e", pady=(0, 15))
        
        # Load initial data
        self._refresh_dashboard(stats_frame, activity_frame1, activity_frame2)
    
    def _refresh_dashboard(self, stats_frame, activity_frame1, activity_frame2):
        """Refresh dashboard with latest data"""
        from models.dashboard_stats import get_dashboard_stats, get_recent_activity, get_items_needing_attention
        
        # Clear existing widgets
        for widget in stats_frame.winfo_children():
            widget.destroy()
        for widget in activity_frame1.winfo_children():
            widget.destroy()
        for widget in activity_frame2.winfo_children():
            widget.destroy()
        
        # Get statistics
        stats_result = get_dashboard_stats()
        if stats_result.get("success"):
            stats = stats_result.get("stats", {})
            
            # Create stat cards - 8 cards in 2 rows of 4
            cards_data = [
                ("📦", "Total Items", stats.get('total_items', 0), "#7c3aed"),
                ("💰", "Inventory Value", f"${stats.get('total_inventory_value', 0):,.2f}", "#059669"),
                ("⚠️", "Low Stock", stats.get('low_stock_count', 0), "#d97706"),
                ("🔴", "Out of Stock", stats.get('out_of_stock_count', 0), "#dc2626"),
                ("🏢", "Suppliers", stats.get('total_suppliers', 0), "#0284c7"),
                ("👥", "Customers", stats.get('total_customers', 0), "#7c3aed"),
                ("📋", "Pending POs", stats.get('pending_purchase_orders', 0), "#a855f7"),
                ("🛒", "Pending SOs", stats.get('pending_sales_orders', 0), "#c084fc"),
            ]
            
            for i, (icon, label, value, color) in enumerate(cards_data):
                card = tk.Frame(stats_frame, bg="white", relief="solid", bd=1)
                card.grid(row=i//4, column=i%4, padx=3, pady=5, sticky="nsew")
                
                # Icon
                tk.Label(
                    card, text=icon,
                    font=("Segoe UI", 20),
                    bg="white", fg=color
                ).pack(pady=(10, 5))
                
                # Value
                tk.Label(
                    card, text=str(value),
                    font=("Segoe UI", 16, "bold"),
                    bg="white", fg="#1f2937"
                ).pack(pady=(0, 2))
                
                # Label
                tk.Label(
                    card, text=label,
                    font=("Segoe UI", 9),
                    bg="white", fg="#6b7280"
                ).pack(pady=(0, 10))
            
            # Configure grid weights for equal sizing and fill width
            for i in range(4):
                stats_frame.grid_columnconfigure(i, weight=1, uniform="col")
            for i in range(2):
                stats_frame.grid_rowconfigure(i, weight=0, minsize=100)
        
        # Left Recent Activity Section
        tk.Label(
            activity_frame1,
            text="Recent Activity",
            font=("Segoe UI", 14, "bold"),
            bg="#f5f3ff", fg="#6b21a8"
        ).pack(anchor="w", pady=(0, 10))
        
        activity_container1 = tk.Frame(activity_frame1, bg="white", relief="solid", bd=1)
        activity_container1.pack(fill="both", expand=True)
        
        activity_result = get_recent_activity(10)
        if activity_result.get("success"):
            activities = activity_result.get("activities", [])
            
            if activities:
                for activity in activities[:5]:
                    item_frame = tk.Frame(activity_container1, bg="white")
                    item_frame.pack(fill="x", padx=15, pady=8)
                    
                    action_text = f"{activity['action']} {activity['resource_type']}"
                    tk.Label(
                        item_frame,
                        text=f"• {action_text}",
                        font=("Segoe UI", 10, "bold"),
                        bg="white", fg="#1f2937",
                        anchor="w"
                    ).pack(side="left", fill="x", expand=True)
                    
                    tk.Label(
                        item_frame,
                        text=activity['username'],
                        font=("Segoe UI", 9),
                        bg="white", fg="#6b7280"
                    ).pack(side="right")
            else:
                tk.Label(
                    activity_container1,
                    text="No recent activity",
                    font=("Segoe UI", 10),
                    bg="white", fg="#9ca3af"
                ).pack(pady=40)
        
        # Right Recent Activity Section
        tk.Label(
            activity_frame2,
            text="Recent Activity",
            font=("Segoe UI", 14, "bold"),
            bg="#f5f3ff", fg="#6b21a8"
        ).pack(anchor="w", pady=(0, 10))
        
        activity_container2 = tk.Frame(activity_frame2, bg="white", relief="solid", bd=1)
        activity_container2.pack(fill="both", expand=True)
        
        if activity_result.get("success"):
            activities = activity_result.get("activities", [])
            
            if len(activities) > 5:
                for activity in activities[5:10]:
                    item_frame = tk.Frame(activity_container2, bg="white")
                    item_frame.pack(fill="x", padx=15, pady=8)
                    
                    action_text = f"{activity['action']} {activity['resource_type']}"
                    tk.Label(
                        item_frame,
                        text=f"• {action_text}",
                        font=("Segoe UI", 10, "bold"),
                        bg="white", fg="#1f2937",
                        anchor="w"
                    ).pack(side="left", fill="x", expand=True)
                    
                    tk.Label(
                        item_frame,
                        text=activity['username'],
                        font=("Segoe UI", 9),
                        bg="white", fg="#6b7280"
                    ).pack(side="right")
            else:
                tk.Label(
                    activity_container2,
                    text="No additional activity",
                    font=("Segoe UI", 10),
                    bg="white", fg="#9ca3af"
                ).pack(pady=40)

    def _create_inventory_tab(self):
        """Create the inventory management tab"""
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="📦 Inventory")
        
        # Toolbar with modern buttons
        toolbar = tk.Frame(tab, bg="#f5f3ff")
        toolbar.pack(fill="x", pady=(15, 15), padx=15)
        
        self.btn_add = tk.Button(
            toolbar, text="➕ Add Item",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_add_item
        )
        self.btn_add.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_edit = tk.Button(
            toolbar, text="✏️ Edit Item",
            font=("Segoe UI", 11, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_edit_item
        )
        self.btn_edit.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_delete = tk.Button(
            toolbar, text="🗑️ Delete Item",
            font=("Segoe UI", 11, "bold"),
            bg="#c084fc", fg="white",
            activebackground="#a855f7",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_delete_item
        )
        self.btn_delete.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        # Import/Export buttons
        tk.Button(
            toolbar, text="📥 Import",
            font=("Segoe UI", 11, "bold"),
            bg="#059669", fg="white",
            activebackground="#047857",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._import_inventory
        ).pack(side="right", padx=(10, 0), ipady=10, ipadx=20)
        
        tk.Button(
            toolbar, text="📤 Export",
            font=("Segoe UI", 11, "bold"),
            bg="#0284c7", fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._export_inventory
        ).pack(side="right", padx=(0, 0), ipady=10, ipadx=20)

        # Search bar
        search_frame = tk.Frame(tab, bg="white", bd=0)
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_container = tk.Frame(search_frame, bg="white")
        search_container.pack(fill="x", padx=2, pady=2)
        
        tk.Label(
            search_container, text="🔍 Search:",
            font=("Segoe UI", 11, "bold"),
            bg="white", fg="#6b21a8"
        ).pack(side="left", padx=(15, 10), pady=12)
        
        self.ent_q = tk.Entry(
            search_container,
            font=("Segoe UI", 11),
            bg="#f3f4f6", fg="#1f2937",
            relief="flat", bd=0,
            insertbackground="#6b21a8"
        )
        self.ent_q.pack(side="left", fill="x", expand=True, ipady=8, ipadx=10)
        self.ent_q.bind("<Return>", lambda e: self._on_search())
        
        tk.Button(
            search_container, text="Search",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_search
        ).pack(side="left", padx=10, ipady=8, ipadx=20)
        
        tk.Button(
            search_container, text="Refresh",
            font=("Segoe UI", 10, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_search
        ).pack(side="right", padx=(0, 15), ipady=8, ipadx=20)
        
        tk.Button(
            search_container, text="📷 Barcode Lookup",
            font=("Segoe UI", 10, "bold"),
            bg="#059669", fg="white",
            activebackground="#047857",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_barcode_lookup
        ).pack(side="right", padx=(0, 10), ipady=8, ipadx=20)

        # Table with purple theme
        table_frame = tk.Frame(tab, bg="white", bd=0)
        table_frame.pack(fill="both", expand=True)
        
        # Create a style for the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Purple.Treeview",
            background="white",
            foreground="#1f2937",
            fieldbackground="white",
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure("Purple.Treeview.Heading",
            background="#7c3aed",
            foreground="white",
            borderwidth=0,
            font=("Segoe UI", 11, "bold")
        )
        style.map("Purple.Treeview.Heading",
            background=[("active", "#6d28d9")]
        )
        style.map("Purple.Treeview",
            background=[("selected", "#ddd6fe")],
            foreground=[("selected", "#1f2937")]
        )
        
        # Add tag styles for stock alerts
        style.configure("Alert.Treeview", background="white")
        
        cols = ("id","name","sku","barcode","quantity","price","status")
        self.table = ttk.Treeview(table_frame, columns=cols, show="headings", style="Purple.Treeview")
        for c, h, w in (("id","ID",60), ("name","Name",150), ("sku","SKU",100), 
                        ("barcode","Barcode",130), ("quantity","Qty",70), ("price","Price",90), ("status","Status",110)):
            self.table.heading(c, text=h)
            self.table.column(c, width=w, anchor="w")
        
        # Configure tags for stock alerts
        self.table.tag_configure("out_of_stock", background="#fee2e2", foreground="#991b1b")
        self.table.tag_configure("low_stock", background="#fef3c7", foreground="#92400e")
        self.table.tag_configure("reorder", background="#fef9c3", foreground="#854d0e")
        self.table.tag_configure("normal", background="white", foreground="#1f2937")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True, padx=2, pady=2)

    def _create_suppliers_tab(self):
        """Create the suppliers management tab"""
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="🏢 Suppliers")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#f5f3ff")
        toolbar.pack(fill="x", pady=(15, 15), padx=15)
        
        self.btn_add_supplier = tk.Button(
            toolbar, text="➕ Add Supplier",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_add_supplier
        )
        self.btn_add_supplier.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_edit_supplier = tk.Button(
            toolbar, text="✏️ Edit Supplier",
            font=("Segoe UI", 11, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_edit_supplier
        )
        self.btn_edit_supplier.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_delete_supplier = tk.Button(
            toolbar, text="🗑️ Delete Supplier",
            font=("Segoe UI", 11, "bold"),
            bg="#c084fc", fg="white",
            activebackground="#a855f7",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_delete_supplier
        )
        self.btn_delete_supplier.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        # Import/Export buttons
        tk.Button(
            toolbar, text="📥 Import",
            font=("Segoe UI", 11, "bold"),
            bg="#059669", fg="white",
            activebackground="#047857",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._import_suppliers
        ).pack(side="right", padx=(10, 0), ipady=10, ipadx=20)
        
        tk.Button(
            toolbar, text="📤 Export",
            font=("Segoe UI", 11, "bold"),
            bg="#0284c7", fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._export_suppliers
        ).pack(side="right", padx=(0, 0), ipady=10, ipadx=20)
        
        # Search bar
        search_frame = tk.Frame(tab, bg="white", bd=0)
        search_frame.pack(fill="x", pady=(0, 15), padx=15)
        
        search_container = tk.Frame(search_frame, bg="white")
        search_container.pack(fill="x", padx=2, pady=2)
        
        tk.Label(
            search_container, text="🔍 Search:",
            font=("Segoe UI", 11, "bold"),
            bg="white", fg="#6b21a8"
        ).pack(side="left", padx=(15, 10), pady=12)
        
        self.ent_supplier_q = tk.Entry(
            search_container,
            font=("Segoe UI", 11),
            bg="#f3f4f6", fg="#1f2937",
            relief="flat", bd=0,
            insertbackground="#6b21a8"
        )
        self.ent_supplier_q.pack(side="left", fill="x", expand=True, ipady=8, ipadx=10)
        self.ent_supplier_q.bind("<Return>", lambda e: self._on_search_suppliers())
        
        tk.Button(
            search_container, text="Search",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_search_suppliers
        ).pack(side="left", padx=10, ipady=8, ipadx=20)
        
        tk.Button(
            search_container, text="Refresh",
            font=("Segoe UI", 10, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_search_suppliers
        ).pack(side="right", padx=(0, 15), ipady=8, ipadx=20)
        
        # Table
        table_frame = tk.Frame(tab, bg="white", bd=0)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        cols = ("id", "name", "contact_person", "email", "phone", "address")
        self.suppliers_table = ttk.Treeview(table_frame, columns=cols, show="headings", style="Purple.Treeview")
        for c, h, w in (("id", "ID", 60), ("name", "Name", 150), ("contact_person", "Contact", 130), 
                        ("email", "Email", 180), ("phone", "Phone", 120), ("address", "Address", 200)):
            self.suppliers_table.heading(c, text=h)
            self.suppliers_table.column(c, width=w, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.suppliers_table.yview)
        self.suppliers_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.suppliers_table.pack(fill="both", expand=True, padx=2, pady=2)

    def _create_customers_tab(self):
        """Create the customers management tab"""
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="👥 Customers")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#f5f3ff")
        toolbar.pack(fill="x", pady=(15, 15), padx=15)
        
        self.btn_add_customer = tk.Button(
            toolbar, text="➕ Add Customer",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_add_customer
        )
        self.btn_add_customer.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_edit_customer = tk.Button(
            toolbar, text="✏️ Edit Customer",
            font=("Segoe UI", 11, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_edit_customer
        )
        self.btn_edit_customer.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_delete_customer = tk.Button(
            toolbar, text="🗑️ Delete Customer",
            font=("Segoe UI", 11, "bold"),
            bg="#c084fc", fg="white",
            activebackground="#a855f7",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_delete_customer
        )
        self.btn_delete_customer.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        # Import/Export buttons
        tk.Button(
            toolbar, text="📥 Import",
            font=("Segoe UI", 11, "bold"),
            bg="#059669", fg="white",
            activebackground="#047857",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._import_customers
        ).pack(side="right", padx=(10, 0), ipady=10, ipadx=20)
        
        tk.Button(
            toolbar, text="📤 Export",
            font=("Segoe UI", 11, "bold"),
            bg="#0284c7", fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._export_customers
        ).pack(side="right", padx=(0, 0), ipady=10, ipadx=20)
        
        # Search bar
        search_frame = tk.Frame(tab, bg="white", bd=0)
        search_frame.pack(fill="x", pady=(0, 15), padx=15)
        
        search_container = tk.Frame(search_frame, bg="white")
        search_container.pack(fill="x", padx=2, pady=2)
        
        tk.Label(
            search_container, text="🔍 Search:",
            font=("Segoe UI", 11, "bold"),
            bg="white", fg="#6b21a8"
        ).pack(side="left", padx=(15, 10), pady=12)
        
        self.ent_customer_q = tk.Entry(
            search_container,
            font=("Segoe UI", 11),
            bg="#f3f4f6", fg="#1f2937",
            relief="flat", bd=0,
            insertbackground="#6b21a8"
        )
        self.ent_customer_q.pack(side="left", fill="x", expand=True, ipady=8, ipadx=10)
        self.ent_customer_q.bind("<Return>", lambda e: self._on_search_customers())
        
        tk.Button(
            search_container, text="Search",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_search_customers
        ).pack(side="left", padx=10, ipady=8, ipadx=20)
        
        tk.Button(
            search_container, text="Refresh",
            font=("Segoe UI", 10, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_search_customers
        ).pack(side="right", padx=(0, 15), ipady=8, ipadx=20)
        
        # Table
        table_frame = tk.Frame(tab, bg="white", bd=0)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        cols = ("id", "name", "email", "phone", "address")
        self.customers_table = ttk.Treeview(table_frame, columns=cols, show="headings", style="Purple.Treeview")
        for c, h, w in (("id", "ID", 60), ("name", "Name", 180), ("email", "Email", 200), 
                        ("phone", "Phone", 130), ("address", "Address", 250)):
            self.customers_table.heading(c, text=h)
            self.customers_table.column(c, width=w, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.customers_table.yview)
        self.customers_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.customers_table.pack(fill="both", expand=True, padx=2, pady=2)

    def _create_purchase_orders_tab(self):
        """Create the purchase orders tab"""
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="📥 Purchase Orders")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#f5f3ff")
        toolbar.pack(fill="x", pady=(15, 15), padx=15)
        
        self.btn_create_po = tk.Button(
            toolbar, text="➕ Create Purchase Order",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_create_purchase_order
        )
        self.btn_create_po.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_complete_po = tk.Button(
            toolbar, text="✓ Complete Order",
            font=("Segoe UI", 11, "bold"),
            bg="#10b981", fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_complete_purchase_order
        )
        self.btn_complete_po.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_cancel_po = tk.Button(
            toolbar, text="✗ Cancel Order",
            font=("Segoe UI", 11, "bold"),
            bg="#ef4444", fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_cancel_purchase_order
        )
        self.btn_cancel_po.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        # Status filter
        filter_frame = tk.Frame(tab, bg="#f5f3ff")
        filter_frame.pack(fill="x", pady=(0, 15), padx=15)
        
        tk.Label(filter_frame, text="Filter by Status:", font=("Segoe UI", 11),
                bg="#f5f3ff", fg="#1f2937").pack(side="left", padx=(0, 10))
        
        self.po_status_var = tk.StringVar(value="ALL")
        for status in ["ALL", "PENDING", "COMPLETED", "CANCELLED"]:
            tk.Radiobutton(
                filter_frame, text=status, variable=self.po_status_var, value=status,
                font=("Segoe UI", 10), bg="#f5f3ff", fg="#1f2937",
                selectcolor="#ddd6fe", activebackground="#f5f3ff",
                command=self._on_filter_purchase_orders
            ).pack(side="left", padx=5)
        
        # Table
        table_frame = tk.Frame(tab, bg="white", bd=0)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        cols = ("id", "order_number", "supplier", "item", "qty", "unit_price", "total", "status", "created_at")
        self.po_table = ttk.Treeview(table_frame, columns=cols, show="headings", style="Purple.Treeview")
        for c, h, w in (("id", "ID", 50), ("order_number", "Order #", 130), ("supplier", "Supplier", 150),
                        ("item", "Item", 150), ("qty", "Qty", 60), ("unit_price", "Unit Price", 90),
                        ("total", "Total", 90), ("status", "Status", 100), ("created_at", "Created", 140)):
            self.po_table.heading(c, text=h)
            self.po_table.column(c, width=w, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.po_table.yview)
        self.po_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.po_table.pack(fill="both", expand=True, padx=2, pady=2)

    def _create_sales_orders_tab(self):
        """Create the sales orders tab"""
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="📤 Sales Orders")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#f5f3ff")
        toolbar.pack(fill="x", pady=(15, 15), padx=15)
        
        self.btn_create_so = tk.Button(
            toolbar, text="➕ Create Sales Order",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_create_sales_order
        )
        self.btn_create_so.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_complete_so = tk.Button(
            toolbar, text="✓ Complete Order",
            font=("Segoe UI", 11, "bold"),
            bg="#10b981", fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_complete_sales_order
        )
        self.btn_complete_so.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        self.btn_cancel_so = tk.Button(
            toolbar, text="✗ Cancel Order",
            font=("Segoe UI", 11, "bold"),
            bg="#ef4444", fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=self._on_cancel_sales_order
        )
        self.btn_cancel_so.pack(side="left", padx=(0, 10), ipady=10, ipadx=20)
        
        # Status filter
        filter_frame = tk.Frame(tab, bg="#f5f3ff")
        filter_frame.pack(fill="x", pady=(0, 15), padx=15)
        
        tk.Label(filter_frame, text="Filter by Status:", font=("Segoe UI", 11),
                bg="#f5f3ff", fg="#1f2937").pack(side="left", padx=(0, 10))
        
        self.so_status_var = tk.StringVar(value="ALL")
        for status in ["ALL", "PENDING", "COMPLETED", "CANCELLED"]:
            tk.Radiobutton(
                filter_frame, text=status, variable=self.so_status_var, value=status,
                font=("Segoe UI", 10), bg="#f5f3ff", fg="#1f2937",
                selectcolor="#ddd6fe", activebackground="#f5f3ff",
                command=self._on_filter_sales_orders
            ).pack(side="left", padx=5)
        
        # Table
        table_frame = tk.Frame(tab, bg="white", bd=0)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        cols = ("id", "order_number", "customer", "item", "qty", "unit_price", "total", "status", "created_at")
        self.so_table = ttk.Treeview(table_frame, columns=cols, show="headings", style="Purple.Treeview")
        for c, h, w in (("id", "ID", 50), ("order_number", "Order #", 130), ("customer", "Customer", 150),
                        ("item", "Item", 150), ("qty", "Qty", 60), ("unit_price", "Unit Price", 90),
                        ("total", "Total", 90), ("status", "Status", 100), ("created_at", "Created", 140)):
            self.so_table.heading(c, text=h)
            self.so_table.column(c, width=w, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.so_table.yview)
        self.so_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.so_table.pack(fill="both", expand=True, padx=2, pady=2)


    # ---- session / nav ----
    def _logout(self):
        if messagebox.askyesno("Log out", "Log out and return to sign-in?"):
            app = self.winfo_toplevel()   # the root App()
            app.show_auth()               # swap back to AuthPage

    def _is_manager(self):
        """Check if user can manage inventory (ADMIN or STAFF)"""
        return can_manage_inventory(self.current_user)
    
    def _is_admin(self):
        """Check if user is ADMIN"""
        return is_admin(self.current_user)

    def _apply_role_locks(self):
        # Hide user management button for non-ADMIN users
        if not can_manage_users(self.current_user):
            self.btn_user_mgmt.pack_forget()
        
        # Hide audit logs tab for non-ADMIN users
        if not is_admin(self.current_user):
            # Find and hide the audit logs tab
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text") == "📋 Audit Logs":
                    self.notebook.hide(i)
                    break
        
        # Disable inventory management for VIEWER role
        if not can_manage_inventory(self.current_user):
            for b in (self.btn_add, self.btn_edit, self.btn_delete):
                b.configure(state="disabled", bg="#d1d5db")
        
        # Disable supplier management for non-STAFF/non-ADMIN
        if not has_permission(self.current_user, "manage_suppliers"):
            for b in (self.btn_add_supplier, self.btn_edit_supplier, self.btn_delete_supplier):
                b.configure(state="disabled", bg="#d1d5db")
        
        # Disable customer management for non-STAFF/non-ADMIN
        if not has_permission(self.current_user, "manage_customers"):
            for b in (self.btn_add_customer, self.btn_edit_customer, self.btn_delete_customer):
                b.configure(state="disabled", bg="#d1d5db")
        
        # Disable purchase order management for non-STAFF/non-ADMIN
        if not has_permission(self.current_user, "create_purchase"):
            for b in (self.btn_create_po, self.btn_complete_po, self.btn_cancel_po):
                b.configure(state="disabled", bg="#d1d5db")
        
        # Disable sales order management for non-STAFF/non-ADMIN
        if not has_permission(self.current_user, "create_sale"):
            for b in (self.btn_create_so, self.btn_complete_so, self.btn_cancel_so):
                b.configure(state="disabled", bg="#d1d5db")
        
        # Load initial data for order tabs
        self._on_filter_purchase_orders()
        self._on_filter_sales_orders()
        self._on_search_suppliers()
        self._on_search_customers()

    # ---- inventory handlers ----
    def _on_search(self):
        from models.stock_alert_model import check_and_create_alerts
        
        q = self.ent_q.get().strip()
        rows = find_items(q)
        
        # Check for stock alerts
        check_and_create_alerts()
        
        # Update alerts panel
        self._update_alerts_panel()
        
        # Clear table
        for i in self.table.get_children():
            self.table.delete(i)
        
        # Populate with color coding
        for r in rows:
            price_display = f"${r.get('price', 0.0):.2f}"
            qty = r["quantity"]
            min_stock = r.get("min_stock_level", 10)
            reorder = r.get("reorder_point", 20)
            barcode = r.get("barcode", "-")
            
            # Determine status and tag
            if qty == 0:
                status = "🔴 OUT OF STOCK"
                tag = "out_of_stock"
            elif qty <= min_stock:
                status = "🟡 LOW STOCK"
                tag = "low_stock"
            elif qty <= reorder:
                status = "⚠️ REORDER SOON"
                tag = "reorder"
            else:
                status = "✓ OK"
                tag = "normal"
            
            self.table.insert("", "end", values=(r["id"], r["name"], r["sku"], barcode, qty, price_display, status), tags=(tag,))

    def _selected_item_id(self):
        sel = self.table.focus()
        if not sel:
            return None
        vals = self.table.item(sel)["values"]
        return int(vals[0]) if vals else None
    
    def _create_scrollable_dialog(self, title, width=500, height=750):
        """Create a scrollable dialog with hidden scrollbar"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg="#f5f3ff")
        dialog.geometry(f"{width}x{height}")
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg="#7c3aed")
        header.pack(fill="x")
        tk.Label(
            header, text=title,
            font=("Segoe UI", 16, "bold"),
            bg="#7c3aed", fg="white"
        ).pack(pady=15)
        
        # Create canvas and scrollbar for scrollable content
        canvas_container = tk.Frame(dialog, bg="#f5f3ff")
        canvas_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_container, bg="#f5f3ff", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview, width=8)
        
        # Scrollable frame inside canvas
        scrollable_frame = tk.Frame(canvas, bg="#f5f3ff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Hide scrollbar when not needed
        def on_canvas_configure(event):
            canvas_height = canvas.winfo_height()
            content_height = scrollable_frame.winfo_reqheight()
            if content_height > canvas_height:
                scrollbar.pack(side="right", fill="y")
            else:
                scrollbar.pack_forget()
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        
        return dialog, scrollable_frame
    
    def _get_selected_item_data(self):
        """Get the full data for the selected item"""
        from models.inventory_model import get_item
        
        sel = self.table.focus()
        if not sel:
            return None
        vals = self.table.item(sel)["values"]
        if not vals:
            return None
        
        # Get full item data from database (includes barcode)
        item_id = int(vals[0])
        result = get_item(item_id)
        
        if result.get("success"):
            return result.get("item")
        return None

    def _on_add_item(self):
        try:
            # Create scrollable dialog
            dialog, form = self._create_scrollable_dialog("Add New Item", width=450, height=650)
            
            # Form content
            form_content = tk.Frame(form, bg="#f5f3ff")
            form_content.pack(fill="both", expand=True, padx=30, pady=30)
            
            def create_field(label_text, default_value=""):
                tk.Label(
                    form_content, text=label_text,
                    font=("Segoe UI", 10, "bold"),
                    bg="#f5f3ff", fg="#6b21a8"
                ).pack(anchor="w", pady=(10, 5))
                
                entry = tk.Entry(
                    form_content,
                    font=("Segoe UI", 11),
                    bg="#ddd6fe", fg="#1f2937",
                    relief="flat", bd=0,
                    insertbackground="#6b21a8"
                )
                entry.pack(fill="x", ipady=10, ipadx=10)
                if default_value:
                    entry.insert(0, default_value)
                return entry
            
            ent_name = create_field("Item Name")
            ent_sku = create_field("SKU")
            ent_qty = create_field("Quantity", "0")
            ent_price = create_field("Price ($)", "0.00")
            ent_min_stock = create_field("Min Stock Level (Alert when below)", "10")
            ent_reorder = create_field("Reorder Point (Alert to reorder)", "20")
            
            result = {"cancelled": True}
            
            def on_submit():
                name = ent_name.get().strip()
                sku = ent_sku.get().strip()
                qty = ent_qty.get().strip()
                price = ent_price.get().strip()
                min_stock = ent_min_stock.get().strip()
                reorder = ent_reorder.get().strip()
                
                if not name:
                    messagebox.showwarning("Validation", "Please enter item name.")
                    return
                if not sku:
                    messagebox.showwarning("Validation", "Please enter SKU.")
                    return
                if not qty.isdigit():
                    messagebox.showwarning("Validation", "Quantity must be a number.")
                    return
                if not min_stock.isdigit():
                    messagebox.showwarning("Validation", "Min stock level must be a number.")
                    return
                if not reorder.isdigit():
                    messagebox.showwarning("Validation", "Reorder point must be a number.")
                    return
                try:
                    price_val = float(price) if price else 0.0
                    if price_val < 0:
                        messagebox.showwarning("Validation", "Price cannot be negative.")
                        return
                except ValueError:
                    messagebox.showwarning("Validation", "Price must be a valid number.")
                    return
                
                result["name"] = name
                result["sku"] = sku
                result["quantity"] = int(qty)
                result["price"] = price_val
                result["min_stock_level"] = int(min_stock)
                result["reorder_point"] = int(reorder)
                result["cancelled"] = False
                dialog.destroy()
            
            # Buttons
            btn_frame = tk.Frame(form_content, bg="#f5f3ff")
            btn_frame.pack(fill="x", pady=(20, 0))
            
            tk.Button(
                btn_frame, text="Create Item",
                font=("Segoe UI", 11, "bold"),
                bg="#7c3aed", fg="white",
                activebackground="#6d28d9",
                activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                command=on_submit
            ).pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 5))
            
            tk.Button(
                btn_frame, text="Cancel",
                font=("Segoe UI", 11, "bold"),
                bg="#9ca3af", fg="white",
                activebackground="#6b7280",
                activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                command=dialog.destroy
            ).pack(side="left", fill="x", expand=True, ipady=10, padx=(5, 0))
            
            dialog.wait_window()
            
            if not result["cancelled"]:
                create_item(self.current_user, result)
                messagebox.showinfo("Success", "Item created.")
                self._on_search()
                
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_edit_item(self):
        try:
            item_data = self._get_selected_item_data()
            if item_data is None:
                messagebox.showwarning("Selection", "Please select an item to edit.")
                return
            
            # Ensure we have all required fields
            if not all(k in item_data for k in ['id', 'name', 'sku', 'quantity', 'price']):
                messagebox.showerror("Error", "Item data is incomplete. Please refresh and try again.")
                return
            
            # Create scrollable dialog
            dialog, form = self._create_scrollable_dialog("Edit Item", width=500, height=750)
            
            # Add padding to form
            form_content = tk.Frame(form, bg="#f5f3ff")
            form_content.pack(fill="both", expand=True, padx=30, pady=30)
            
            # Track original values to detect changes
            original_values = {
                "name": str(item_data.get("name", "")),
                "sku": str(item_data.get("sku", "")),
                "quantity": str(item_data.get("quantity", 0)),
                "price": f"{float(item_data.get('price', 0.0)):.2f}"
            }
            
            def create_field(label_text, initial_value=""):
                tk.Label(
                    form_content, text=label_text,
                    font=("Segoe UI", 10, "bold"),
                    bg="#f5f3ff", fg="#6b21a8"
                ).pack(anchor="w", pady=(10, 5))
                
                entry = tk.Entry(
                    form_content,
                    font=("Segoe UI", 11),
                    bg="#ddd6fe", fg="#1f2937",
                    relief="flat", bd=0,
                    insertbackground="#6b21a8"
                )
                entry.pack(fill="x", ipady=10, ipadx=10)
                if initial_value:
                    entry.insert(0, str(initial_value))
                return entry
            
            ent_name = create_field("Item Name", item_data.get("name", ""))
            ent_sku = create_field("SKU", item_data.get("sku", ""))
            ent_qty = create_field("Quantity", str(item_data.get("quantity", 0)))
            ent_price = create_field("Price ($)", f"{float(item_data.get('price', 0.0)):.2f}")
            
            # Barcode section
            barcode_frame = tk.Frame(form_content, bg="white", relief="solid", bd=1)
            barcode_frame.pack(fill="x", pady=15)
            
            tk.Label(
                barcode_frame, text="Barcode",
                font=("Segoe UI", 10, "bold"),
                bg="white", fg="#6b21a8"
            ).pack(anchor="w", padx=10, pady=(10, 5))
            
            barcode_value = item_data.get("barcode", "")
            
            if barcode_value:
                tk.Label(
                    barcode_frame, text=barcode_value,
                    font=("Consolas", 12),
                    bg="white", fg="#1f2937"
                ).pack(anchor="w", padx=10, pady=(0, 10))
                
                # Show barcode image
                try:
                    from utils.barcode_utils import get_barcode_tk_image
                    barcode_img = get_barcode_tk_image(barcode_value, item_data.get('name', ''), width=400)
                    if barcode_img:
                        img_label = tk.Label(barcode_frame, image=barcode_img, bg="white")
                        img_label.image = barcode_img  # Keep reference
                        img_label.pack(pady=10)
                except Exception as e:
                    print(f"Error displaying barcode: {e}")
                
                # Regenerate button
                tk.Button(
                    barcode_frame, text="🔄 Regenerate Barcode",
                    font=("Segoe UI", 9),
                    bg="#6b7280", fg="white",
                    activebackground="#4b5563",
                    relief="flat", cursor="hand2",
                    command=lambda: self._regenerate_barcode(item_data["id"], barcode_frame, dialog)
                ).pack(pady=(0, 10), ipady=5, ipadx=15)
            else:
                tk.Label(
                    barcode_frame, text="No barcode assigned",
                    font=("Segoe UI", 10, "italic"),
                    bg="white", fg="#9ca3af"
                ).pack(anchor="w", padx=10, pady=10)
                
                # Generate button
                tk.Button(
                    barcode_frame, text="Generate Barcode",
                    font=("Segoe UI", 9),
                    bg="#059669", fg="white",
                    activebackground="#047857",
                    relief="flat", cursor="hand2",
                    command=lambda: self._regenerate_barcode(item_data["id"], barcode_frame, dialog)
                ).pack(pady=(0, 10), ipady=5, ipadx=15)
            
            result = {"cancelled": True}
            
            # Save button (initially disabled)
            btn_frame = tk.Frame(form_content, bg="#f5f3ff")
            btn_frame.pack(fill="x", pady=(20, 0))
            
            btn_save = tk.Button(
                btn_frame, text="Save Changes",
                font=("Segoe UI", 11, "bold"),
                bg="#d1d5db", fg="white",
                activebackground="#d1d5db",
                activeforeground="white",
                relief="flat", bd=0,
                state="disabled"
            )
            btn_save.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 5))
            
            tk.Button(
                btn_frame, text="Cancel",
                font=("Segoe UI", 11, "bold"),
                bg="#9ca3af", fg="white",
                activebackground="#6b7280",
                activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                command=dialog.destroy
            ).pack(side="left", fill="x", expand=True, ipady=10, padx=(5, 0))
            
            def check_changes(*args):
                """Enable save button if any field has changed"""
                has_changes = (
                    ent_name.get() != original_values["name"] or
                    ent_sku.get() != original_values["sku"] or
                    ent_qty.get() != original_values["quantity"] or
                    ent_price.get() != original_values["price"]
                )
                
                if has_changes:
                    btn_save.config(
                        state="normal",
                        bg="#7c3aed",
                        activebackground="#6d28d9",
                        cursor="hand2",
                        command=on_submit
                    )
                else:
                    btn_save.config(
                        state="disabled",
                        bg="#d1d5db",
                        activebackground="#d1d5db",
                        cursor=""
                    )
            
            # Bind change detection to all entry fields
            for entry in [ent_name, ent_sku, ent_qty, ent_price]:
                entry.bind("<KeyRelease>", check_changes)
            
            def on_submit():
                name = ent_name.get().strip()
                sku = ent_sku.get().strip()
                qty = ent_qty.get().strip()
                price = ent_price.get().strip()
                
                if not name:
                    messagebox.showwarning("Validation", "Please enter item name.")
                    return
                if not sku:
                    messagebox.showwarning("Validation", "Please enter SKU.")
                    return
                if not qty.isdigit():
                    messagebox.showwarning("Validation", "Quantity must be a number.")
                    return
                try:
                    price_val = float(price) if price else 0.0
                    if price_val < 0:
                        messagebox.showwarning("Validation", "Price cannot be negative.")
                        return
                except ValueError:
                    messagebox.showwarning("Validation", "Price must be a valid number.")
                    return
                
                result["name"] = name
                result["sku"] = sku
                result["quantity"] = int(qty)
                result["price"] = price_val
                result["cancelled"] = False
                dialog.destroy()
            
            dialog.wait_window()
            
            if not result["cancelled"]:
                edit_item(self.current_user, item_data["id"], result)
                messagebox.showinfo("Success", "Item updated.")
                self._on_search()
                
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to edit item: {str(e)}")

    def _on_delete_item(self):
        try:
            vid = self._selected_item_id()
            if vid is None: return
            if not messagebox.askyesno("Confirm", "Delete this item?"): return
            remove_item(self.current_user, vid)
            messagebox.showinfo("Success", "Item deleted.")
            self._on_search()
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- supplier handlers ----
    def _on_search_suppliers(self):
        try:
            q = self.ent_supplier_q.get().strip()
            if q:
                result = search_suppliers(self.current_user, q)
            else:
                result = list_suppliers(self.current_user)
            
            # Clear table
            for i in self.suppliers_table.get_children():
                self.suppliers_table.delete(i)
            
            # Populate
            if result.get("success"):
                for s in result.get("suppliers", []):
                    self.suppliers_table.insert("", "end", values=(
                        s["id"], s["name"], s.get("contact_person", ""), 
                        s.get("email", ""), s.get("phone", ""), s.get("address", "")
                    ))
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_add_supplier(self):
        try:
            # Create scrollable dialog
            dialog, form_frame = self._create_scrollable_dialog("Add New Supplier", width=500, height=500)
            
            # Form content
            form_content = tk.Frame(form_frame, bg="#f5f3ff")
            form_content.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            fields = [
                ("name", "Supplier Name *"),
                ("contact_person", "Contact Person"),
                ("email", "Email"),
                ("phone", "Phone"),
                ("address", "Address")
            ]
            
            for field, label in fields:
                tk.Label(form_content, text=label, font=("Segoe UI", 11),
                        bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
                ent = tk.Entry(form_content, font=("Segoe UI", 11), bg="white", 
                              relief="solid", bd=1)
                ent.pack(fill="x", ipady=8, ipadx=10)
                entries[field] = ent
            
            # Buttons
            btn_frame = tk.Frame(form_content, bg="#f5f3ff")
            btn_frame.pack(fill="x", pady=(20, 0))
            
            def submit():
                form_data = {k: v.get().strip() for k, v in entries.items()}
                if not form_data["name"]:
                    messagebox.showerror("Error", "Supplier name is required")
                    return
                
                result = create_supplier(self.current_user, form_data)
                if result.get("success"):
                    messagebox.showinfo("Success", result.get("message"))
                    dialog.destroy()
                    self._on_search_suppliers()
                else:
                    messagebox.showerror("Error", result.get("message"))
            
            tk.Button(btn_frame, text="Add Supplier", font=("Segoe UI", 11, "bold"),
                     bg="#7c3aed", fg="white", relief="flat", cursor="hand2",
                     command=submit).pack(side="left", ipady=10, ipadx=30)
            
            tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11),
                     bg="#d1d5db", fg="#1f2937", relief="flat", cursor="hand2",
                     command=dialog.destroy).pack(side="right", ipady=10, ipadx=30)
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_edit_supplier(self):
        try:
            sel = self.suppliers_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a supplier to edit")
                return
            
            vals = self.suppliers_table.item(sel)["values"]
            supplier_id = int(vals[0])
            
            # Create scrollable dialog
            dialog, form_frame = self._create_scrollable_dialog("Edit Supplier", width=500, height=500)
            
            # Form content
            form_content = tk.Frame(form_frame, bg="#f5f3ff")
            form_content.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            fields = [
                ("name", "Supplier Name *", vals[1]),
                ("contact_person", "Contact Person", vals[2]),
                ("email", "Email", vals[3]),
                ("phone", "Phone", vals[4]),
                ("address", "Address", vals[5])
            ]
            
            for field, label, default_value in fields:
                tk.Label(form_content, text=label, font=("Segoe UI", 11),
                        bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
                ent = tk.Entry(form_content, font=("Segoe UI", 11), bg="white",
                              relief="solid", bd=1)
                ent.insert(0, default_value or "")
                ent.pack(fill="x", ipady=8, ipadx=10)
                entries[field] = ent
            
            # Buttons
            btn_frame = tk.Frame(form_content, bg="#f5f3ff")
            btn_frame.pack(fill="x", pady=(20, 0))
            
            def submit():
                form_data = {k: v.get().strip() for k, v in entries.items()}
                result = update_supplier(self.current_user, supplier_id, form_data)
                if result.get("success"):
                    messagebox.showinfo("Success", result.get("message"))
                    dialog.destroy()
                    self._on_search_suppliers()
                else:
                    messagebox.showerror("Error", result.get("message"))
            
            tk.Button(btn_frame, text="Update", font=("Segoe UI", 11, "bold"),
                     bg="#7c3aed", fg="white", relief="flat", cursor="hand2",
                     command=submit).pack(side="left", ipady=10, ipadx=30)
            
            tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11),
                     bg="#d1d5db", fg="#1f2937", relief="flat", cursor="hand2",
                     command=dialog.destroy).pack(side="right", ipady=10, ipadx=30)
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_delete_supplier(self):
        try:
            sel = self.suppliers_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a supplier to delete")
                return
            
            vals = self.suppliers_table.item(sel)["values"]
            supplier_id = int(vals[0])
            
            if not messagebox.askyesno("Confirm", f"Delete supplier '{vals[1]}'?"):
                return
            
            result = delete_supplier(self.current_user, supplier_id)
            if result.get("success"):
                messagebox.showinfo("Success", result.get("message"))
                self._on_search_suppliers()
            else:
                messagebox.showerror("Error", result.get("message"))
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- customer handlers ----
    def _on_search_customers(self):
        try:
            q = self.ent_customer_q.get().strip()
            if q:
                result = search_customers(self.current_user, q)
            else:
                result = list_customers(self.current_user)
            
            # Clear table
            for i in self.customers_table.get_children():
                self.customers_table.delete(i)
            
            # Populate
            if result.get("success"):
                for c in result.get("customers", []):
                    self.customers_table.insert("", "end", values=(
                        c["id"], c["name"], c.get("email", ""), 
                        c.get("phone", ""), c.get("address", "")
                    ))
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_add_customer(self):
        try:
            # Create scrollable dialog
            dialog, form_frame = self._create_scrollable_dialog("Add New Customer", width=500, height=450)
            
            # Form content
            form_content = tk.Frame(form_frame, bg="#f5f3ff")
            form_content.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            fields = [
                ("name", "Customer Name *"),
                ("email", "Email"),
                ("phone", "Phone"),
                ("address", "Address")
            ]
            
            for field, label in fields:
                tk.Label(form_content, text=label, font=("Segoe UI", 11),
                        bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
                ent = tk.Entry(form_content, font=("Segoe UI", 11), bg="white",
                              relief="solid", bd=1)
                ent.pack(fill="x", ipady=8, ipadx=10)
                entries[field] = ent
            
            # Buttons
            btn_frame = tk.Frame(form_content, bg="#f5f3ff")
            btn_frame.pack(fill="x", pady=(20, 0))
            
            def submit():
                form_data = {k: v.get().strip() for k, v in entries.items()}
                if not form_data["name"]:
                    messagebox.showerror("Error", "Customer name is required")
                    return
                
                result = create_customer(self.current_user, form_data)
                if result.get("success"):
                    messagebox.showinfo("Success", result.get("message"))
                    dialog.destroy()
                    self._on_search_customers()
                else:
                    messagebox.showerror("Error", result.get("message"))
            
            tk.Button(btn_frame, text="Add Customer", font=("Segoe UI", 11, "bold"),
                     bg="#7c3aed", fg="white", relief="flat", cursor="hand2",
                     command=submit).pack(side="left", ipady=10, ipadx=30)
            
            tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11),
                     bg="#d1d5db", fg="#1f2937", relief="flat", cursor="hand2",
                     command=dialog.destroy).pack(side="right", ipady=10, ipadx=30)
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_edit_customer(self):
        try:
            sel = self.customers_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a customer to edit")
                return
            
            vals = self.customers_table.item(sel)["values"]
            customer_id = int(vals[0])
            
            # Create scrollable dialog
            dialog, form_frame = self._create_scrollable_dialog("Edit Customer", width=500, height=450)
            
            # Form content
            form_content = tk.Frame(form_frame, bg="#f5f3ff")
            form_content.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            fields = [
                ("name", "Customer Name *", vals[1]),
                ("email", "Email", vals[2]),
                ("phone", "Phone", vals[3]),
                ("address", "Address", vals[4])
            ]
            
            for field, label, default_value in fields:
                tk.Label(form_content, text=label, font=("Segoe UI", 11),
                        bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
                ent = tk.Entry(form_content, font=("Segoe UI", 11), bg="white",
                              relief="solid", bd=1)
                ent.insert(0, default_value or "")
                ent.pack(fill="x", ipady=8, ipadx=10)
                entries[field] = ent
            
            # Buttons
            btn_frame = tk.Frame(form_content, bg="#f5f3ff")
            btn_frame.pack(fill="x", pady=(20, 0))
            
            def submit():
                form_data = {k: v.get().strip() for k, v in entries.items()}
                result = update_customer(self.current_user, customer_id, form_data)
                if result.get("success"):
                    messagebox.showinfo("Success", result.get("message"))
                    dialog.destroy()
                    self._on_search_customers()
                else:
                    messagebox.showerror("Error", result.get("message"))
            
            tk.Button(btn_frame, text="Update", font=("Segoe UI", 11, "bold"),
                     bg="#7c3aed", fg="white", relief="flat", cursor="hand2",
                     command=submit).pack(side="left", ipady=10, ipadx=30)
            
            tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11),
                     bg="#d1d5db", fg="#1f2937", relief="flat", cursor="hand2",
                     command=dialog.destroy).pack(side="right", ipady=10, ipadx=30)
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_delete_customer(self):
        try:
            sel = self.customers_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a customer to delete")
                return
            
            vals = self.customers_table.item(sel)["values"]
            customer_id = int(vals[0])
            
            if not messagebox.askyesno("Confirm", f"Delete customer '{vals[1]}'?"):
                return
            
            result = delete_customer(self.current_user, customer_id)
            if result.get("success"):
                messagebox.showinfo("Success", result.get("message"))
                self._on_search_customers()
            else:
                messagebox.showerror("Error", result.get("message"))
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- purchase order handlers ----
    def _on_filter_purchase_orders(self):
        """Refresh purchase orders based on status filter"""
        try:
            status = self.po_status_var.get()
            status_filter = None if status == "ALL" else status
            
            result = list_purchase_orders(self.current_user, status_filter)
            
            # Clear table
            for i in self.po_table.get_children():
                self.po_table.delete(i)
            
            # Populate
            if result.get("success"):
                for po in result.get("orders", []):
                    self.po_table.insert("", "end", values=(
                        po["id"], po["order_number"], po["supplier_name"],
                        po["item_name"], po["quantity"],
                        f"${po['unit_price']:.2f}", f"${po['total_price']:.2f}",
                        po["status"], po["created_at"][:16] if po["created_at"] else ""
                    ))
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_create_purchase_order(self):
        """Create a new purchase order"""
        try:
            # Get suppliers and items for selection
            suppliers_result = list_suppliers(self.current_user)
            items_result = find_items("")
            
            if not suppliers_result.get("success") or not suppliers_result.get("suppliers"):
                messagebox.showerror("Error", "No suppliers available. Please create a supplier first.")
                return
            
            if not items_result:
                messagebox.showerror("Error", "No items available. Please create items first.")
                return
            
            dialog = tk.Toplevel(self)
            dialog.title("Create Purchase Order")
            dialog.configure(bg="#f5f3ff")
            dialog.geometry("550x500")
            
            # Header
            header = tk.Frame(dialog, bg="#7c3aed")
            header.pack(fill="x")
            tk.Label(header, text="Create Purchase Order", font=("Segoe UI", 16, "bold"),
                    bg="#7c3aed", fg="white").pack(pady=15)
            
            # Form
            form_frame = tk.Frame(dialog, bg="#f5f3ff")
            form_frame.pack(fill="both", expand=True, padx=30, pady=20)
            
            # Supplier selection
            tk.Label(form_frame, text="Supplier *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            supplier_var = tk.StringVar()
            supplier_combo = ttk.Combobox(form_frame, textvariable=supplier_var, font=("Segoe UI", 11), state="readonly")
            supplier_combo['values'] = [f"{s['id']}: {s['name']}" for s in suppliers_result["suppliers"]]
            supplier_combo.pack(fill="x", ipady=8)
            
            # Item selection
            tk.Label(form_frame, text="Item *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            item_var = tk.StringVar()
            item_combo = ttk.Combobox(form_frame, textvariable=item_var, font=("Segoe UI", 11), state="readonly")
            item_combo['values'] = [f"{i['id']}: {i['name']} ({i['sku']})" for i in items_result]
            item_combo.pack(fill="x", ipady=8)
            
            # Quantity
            tk.Label(form_frame, text="Quantity *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            qty_entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg="white", relief="solid", bd=1)
            qty_entry.pack(fill="x", ipady=8, ipadx=10)
            
            # Unit Price
            tk.Label(form_frame, text="Unit Price *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            price_entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg="white", relief="solid", bd=1)
            price_entry.pack(fill="x", ipady=8, ipadx=10)
            
            # Notes
            tk.Label(form_frame, text="Notes", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            notes_entry = tk.Text(form_frame, font=("Segoe UI", 10), bg="white", relief="solid", bd=1, height=4)
            notes_entry.pack(fill="x", padx=10)
            
            # Buttons
            btn_frame = tk.Frame(dialog, bg="#f5f3ff")
            btn_frame.pack(fill="x", padx=30, pady=(0, 20))
            
            def submit():
                try:
                    supplier_id = int(supplier_var.get().split(":")[0])
                    item_id = int(item_var.get().split(":")[0])
                    quantity = int(qty_entry.get())
                    unit_price = float(price_entry.get())
                    notes = notes_entry.get("1.0", "end").strip()
                    
                    form_data = {
                        "supplier_id": supplier_id,
                        "item_id": item_id,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "notes": notes
                    }
                    
                    result = create_purchase_order(self.current_user, form_data)
                    if result.get("success"):
                        messagebox.showinfo("Success", f"Purchase Order {result['order_number']} created successfully")
                        dialog.destroy()
                        self._on_filter_purchase_orders()
                    else:
                        messagebox.showerror("Error", result.get("message"))
                except ValueError as e:
                    messagebox.showerror("Error", "Please enter valid numbers for quantity and price")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            tk.Button(btn_frame, text="Create Order", font=("Segoe UI", 11, "bold"),
                     bg="#7c3aed", fg="white", relief="flat", cursor="hand2",
                     command=submit).pack(side="left", ipady=10, ipadx=30)
            
            tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11),
                     bg="#d1d5db", fg="#1f2937", relief="flat", cursor="hand2",
                     command=dialog.destroy).pack(side="right", ipady=10, ipadx=30)
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_complete_purchase_order(self):
        """Complete selected purchase order"""
        try:
            sel = self.po_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a purchase order to complete")
                return
            
            vals = self.po_table.item(sel)["values"]
            order_id = int(vals[0])
            order_number = vals[1]
            status = vals[7]
            
            if status != "PENDING":
                messagebox.showerror("Error", f"Cannot complete order with status: {status}")
                return
            
            if not messagebox.askyesno("Confirm", f"Complete purchase order {order_number}?\nThis will add inventory."):
                return
            
            result = complete_purchase_order(self.current_user, order_id)
            if result.get("success"):
                messagebox.showinfo("Success", result.get("message"))
                self._on_filter_purchase_orders()
                self._on_search()  # Refresh inventory
            else:
                messagebox.showerror("Error", result.get("message"))
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_cancel_purchase_order(self):
        """Cancel selected purchase order"""
        try:
            sel = self.po_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a purchase order to cancel")
                return
            
            vals = self.po_table.item(sel)["values"]
            order_id = int(vals[0])
            order_number = vals[1]
            
            if not messagebox.askyesno("Confirm", f"Cancel purchase order {order_number}?"):
                return
            
            result = cancel_purchase_order(self.current_user, order_id)
            if result.get("success"):
                messagebox.showinfo("Success", result.get("message"))
                self._on_filter_purchase_orders()
            else:
                messagebox.showerror("Error", result.get("message"))
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- sales order handlers ----
    def _on_filter_sales_orders(self):
        """Refresh sales orders based on status filter"""
        try:
            status = self.so_status_var.get()
            status_filter = None if status == "ALL" else status
            
            result = list_sales_orders(self.current_user, status_filter)
            
            # Clear table
            for i in self.so_table.get_children():
                self.so_table.delete(i)
            
            # Populate
            if result.get("success"):
                for so in result.get("orders", []):
                    self.so_table.insert("", "end", values=(
                        so["id"], so["order_number"], so["customer_name"],
                        so["item_name"], so["quantity"],
                        f"${so['unit_price']:.2f}", f"${so['total_price']:.2f}",
                        so["status"], so["created_at"][:16] if so["created_at"] else ""
                    ))
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_create_sales_order(self):
        """Create a new sales order"""
        try:
            # Get customers and items for selection
            customers_result = list_customers(self.current_user)
            items_result = find_items("")
            
            if not customers_result.get("success") or not customers_result.get("customers"):
                messagebox.showerror("Error", "No customers available. Please create a customer first.")
                return
            
            if not items_result:
                messagebox.showerror("Error", "No items available. Please create items first.")
                return
            
            dialog = tk.Toplevel(self)
            dialog.title("Create Sales Order")
            dialog.configure(bg="#f5f3ff")
            dialog.geometry("550x500")
            
            # Header
            header = tk.Frame(dialog, bg="#7c3aed")
            header.pack(fill="x")
            tk.Label(header, text="Create Sales Order", font=("Segoe UI", 16, "bold"),
                    bg="#7c3aed", fg="white").pack(pady=15)
            
            # Form
            form_frame = tk.Frame(dialog, bg="#f5f3ff")
            form_frame.pack(fill="both", expand=True, padx=30, pady=20)
            
            # Customer selection
            tk.Label(form_frame, text="Customer *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            customer_var = tk.StringVar()
            customer_combo = ttk.Combobox(form_frame, textvariable=customer_var, font=("Segoe UI", 11), state="readonly")
            customer_combo['values'] = [f"{c['id']}: {c['name']}" for c in customers_result["customers"]]
            customer_combo.pack(fill="x", ipady=8)
            
            # Item selection
            tk.Label(form_frame, text="Item *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            item_var = tk.StringVar()
            item_combo = ttk.Combobox(form_frame, textvariable=item_var, font=("Segoe UI", 11), state="readonly")
            item_combo['values'] = [f"{i['id']}: {i['name']} ({i['sku']}) - Stock: {i['quantity']}" for i in items_result]
            item_combo.pack(fill="x", ipady=8)
            
            # Quantity
            tk.Label(form_frame, text="Quantity *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            qty_entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg="white", relief="solid", bd=1)
            qty_entry.pack(fill="x", ipady=8, ipadx=10)
            
            # Unit Price
            tk.Label(form_frame, text="Unit Price *", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            price_entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg="white", relief="solid", bd=1)
            price_entry.pack(fill="x", ipady=8, ipadx=10)
            
            # Notes
            tk.Label(form_frame, text="Notes", font=("Segoe UI", 11),
                    bg="#f5f3ff", fg="#1f2937").pack(anchor="w", pady=(10, 2))
            notes_entry = tk.Text(form_frame, font=("Segoe UI", 10), bg="white", relief="solid", bd=1, height=4)
            notes_entry.pack(fill="x", padx=10)
            
            # Buttons
            btn_frame = tk.Frame(dialog, bg="#f5f3ff")
            btn_frame.pack(fill="x", padx=30, pady=(0, 20))
            
            def submit():
                try:
                    customer_id = int(customer_var.get().split(":")[0])
                    item_id = int(item_var.get().split(":")[0])
                    quantity = int(qty_entry.get())
                    unit_price = float(price_entry.get())
                    notes = notes_entry.get("1.0", "end").strip()
                    
                    form_data = {
                        "customer_id": customer_id,
                        "item_id": item_id,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "notes": notes
                    }
                    
                    result = create_sales_order(self.current_user, form_data)
                    if result.get("success"):
                        messagebox.showinfo("Success", f"Sales Order {result['order_number']} created successfully")
                        dialog.destroy()
                        self._on_filter_sales_orders()
                    else:
                        messagebox.showerror("Error", result.get("message"))
                except ValueError as e:
                    messagebox.showerror("Error", "Please enter valid numbers for quantity and price")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            tk.Button(btn_frame, text="Create Order", font=("Segoe UI", 11, "bold"),
                     bg="#7c3aed", fg="white", relief="flat", cursor="hand2",
                     command=submit).pack(side="left", ipady=10, ipadx=30)
            
            tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11),
                     bg="#d1d5db", fg="#1f2937", relief="flat", cursor="hand2",
                     command=dialog.destroy).pack(side="right", ipady=10, ipadx=30)
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_complete_sales_order(self):
        """Complete selected sales order"""
        try:
            sel = self.so_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a sales order to complete")
                return
            
            vals = self.so_table.item(sel)["values"]
            order_id = int(vals[0])
            order_number = vals[1]
            status = vals[7]
            
            if status != "PENDING":
                messagebox.showerror("Error", f"Cannot complete order with status: {status}")
                return
            
            if not messagebox.askyesno("Confirm", f"Complete sales order {order_number}?\nThis will reduce inventory."):
                return
            
            result = complete_sales_order(self.current_user, order_id)
            if result.get("success"):
                messagebox.showinfo("Success", result.get("message"))
                self._on_filter_sales_orders()
                self._on_search()  # Refresh inventory
            else:
                messagebox.showerror("Error", result.get("message"))
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_cancel_sales_order(self):
        """Cancel selected sales order"""
        try:
            sel = self.so_table.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a sales order to cancel")
                return
            
            vals = self.so_table.item(sel)["values"]
            order_id = int(vals[0])
            order_number = vals[1]
            
            if not messagebox.askyesno("Confirm", f"Cancel sales order {order_number}?"):
                return
            
            result = cancel_sales_order(self.current_user, order_id)
            if result.get("success"):
                messagebox.showinfo("Success", result.get("message"))
                self._on_filter_sales_orders()
            else:
                messagebox.showerror("Error", result.get("message"))
        
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- user management ----
    def _open_user_mgmt(self):
        if not can_manage_users(self.current_user) and not is_staff(self.current_user):
            messagebox.showerror("Forbidden", "Only ADMIN and STAFF can manage users.")
            return
        
        win = tk.Toplevel(self)
        win.title("User Management")
        win.configure(bg="#f5f3ff")
        win.geometry("600x750")
        
        # Header
        header = tk.Frame(win, bg="#7c3aed")
        header.pack(fill="x")
        
        header_content = tk.Frame(header, bg="#7c3aed")
        header_content.pack(fill="x", padx=20, pady=15)
        
        tk.Label(
            header_content, text="User Management",
            font=("Segoe UI", 18, "bold"),
            bg="#7c3aed", fg="white"
        ).pack(side="left")
        
        # View Users button in header
        view_btn_text = "👥 View All Users" if is_admin(self.current_user) else "👥 View Team"
        tk.Button(
            header_content, text=view_btn_text,
            font=("Segoe UI", 10, "bold"),
            bg="#a78bfa", fg="white",
            activebackground="#8b5cf6",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=lambda: self._show_employees_list(win)
        ).pack(side="right", ipady=8, ipadx=15)
        
        # Form container
        form_container = tk.Frame(win, bg="white")
        form_container.pack(fill="x", padx=20, pady=20)
        
        form_inner = tk.Frame(form_container, bg="white")
        form_inner.pack(padx=20, pady=20)
        
        form_title = "Create New User" if is_admin(self.current_user) else "Create New Team Member"
        tk.Label(
            form_inner, text=form_title,
            font=("Segoe UI", 14, "bold"),
            bg="white", fg="#6b21a8"
        ).pack(pady=(0, 15))
        
        def create_field(placeholder):
            entry = tk.Entry(
                form_inner,
                font=("Segoe UI", 11),
                bg="#ddd6fe", fg="#1f2937",
                relief="flat", bd=0,
                insertbackground="#6b21a8"
            )
            entry.pack(fill="x", pady=5, ipady=8, ipadx=10)
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e: entry.delete(0, "end") if entry.get() == placeholder else None)
            entry.bind("<FocusOut>", lambda e: entry.insert(0, placeholder) if not entry.get() else None)
            return entry
        
        ent_first = create_field("First Name")
        ent_last = create_field("Last Name")
        ent_email = create_field("Email")
        ent_phone = create_field("Phone")
        
        # Role selector (only for ADMIN)
        role_var = tk.StringVar(value="STAFF")
        if is_admin(self.current_user):
            role_frame = tk.Frame(form_inner, bg="white")
            role_frame.pack(fill="x", pady=5)
            tk.Label(
                role_frame, text="Role:",
                font=("Segoe UI", 10, "bold"),
                bg="white", fg="#6b21a8"
            ).pack(side="left", padx=(0, 10))
            for role in ["ADMIN", "STAFF", "VIEWER"]:
                tk.Radiobutton(
                    role_frame, text=role,
                    variable=role_var, value=role,
                    font=("Segoe UI", 10),
                    bg="white", fg="#1f2937",
                    selectcolor="#ddd6fe",
                    activebackground="white"
                ).pack(side="left", padx=5)
        
        ent_pass = create_field("Temporary Password")
        ent_pass.config(show="*")
        ent_pass2 = create_field("Confirm Password")
        ent_pass2.config(show="*")

        def strong(p): return len(p) >= 8 and any(c.isalpha() for c in p) and any(c.isdigit() for c in p)

        def do_create():
            p1, p2 = ent_pass.get(), ent_pass2.get()
            if p1 == "Temporary Password" or p2 == "Confirm Password" or not p1 or not p2:
                messagebox.showwarning("Validation", "Please enter and confirm password.")
                return
            if p1 != p2:
                messagebox.showwarning("Mismatch", "Passwords do not match.")
                return
            if not strong(p1):
                messagebox.showwarning("Weak", "Use ≥8 chars with letters and numbers.")
                return
            
            first = ent_first.get() if ent_first.get() != "First Name" else ""
            last = ent_last.get() if ent_last.get() != "Last Name" else ""
            email = ent_email.get() if ent_email.get() != "Email" else None
            phone = ent_phone.get() if ent_phone.get() != "Phone" else None
            
            # Determine role and manager
            selected_role = role_var.get() if is_admin(self.current_user) else "STAFF"
            manager_id = None if is_admin(self.current_user) and selected_role == "ADMIN" else self.current_user["id"]
            
            try:
                res = create_user(
                    password=p1,
                    role=selected_role,
                    manager_id=manager_id,
                    first_name=first,
                    last_name=last,
                    email=email,
                    phone=phone,
                    business_name=None,
                    username=None,  # auto-generate
                )
                user_type = "User" if is_admin(self.current_user) else "Team member"
                messagebox.showinfo("Success", f"{user_type} created.\nUsername: {res['username']}\nRole: {selected_role}")
                # Clear form
                for e in [ent_first, ent_last, ent_email, ent_phone, ent_pass, ent_pass2]:
                    e.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            form_inner, text="Create User" if is_admin(self.current_user) else "Create Team Member",
            font=("Segoe UI", 12, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=do_create
        ).pack(fill="x", pady=(15, 0), ipady=10)
        
        # Note about viewing employees
        tk.Label(
            form_container, 
            text="Click button above to view your team" if is_staff(self.current_user) else "Click button above to view all users",
            font=("Segoe UI", 9, "italic"),
            bg="white", fg="#6b7280"
        ).pack(pady=(10, 0))
    
    def _show_employees_list(self, parent_win):
        """Show a detailed list of users - all users for ADMIN, team for STAFF"""
        emp_win = tk.Toplevel(parent_win)
        emp_win.title("User List" if is_admin(self.current_user) else "Team List")
        emp_win.configure(bg="#f5f3ff")
        emp_win.geometry("850x550")
        emp_win.transient(parent_win)
        
        # Header
        header = tk.Frame(emp_win, bg="#7c3aed")
        header.pack(fill="x")
        tk.Label(
            header, text="All Users" if is_admin(self.current_user) else "Your Team",
            font=("Segoe UI", 18, "bold"),
            bg="#7c3aed", fg="white"
        ).pack(pady=20, padx=20)
        
        # Content
        content = tk.Frame(emp_win, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Table with user details
        style = ttk.Style()
        style.configure("Employee.Treeview",
            background="white",
            foreground="#1f2937",
            fieldbackground="white",
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure("Employee.Treeview.Heading",
            background="#7c3aed",
            foreground="white",
            borderwidth=0,
            font=("Segoe UI", 11, "bold")
        )
        
        cols = ("id", "username", "role", "name", "email", "phone", "status")
        emp_table = ttk.Treeview(content, columns=cols, show="headings", style="Employee.Treeview", height=15)
        
        emp_table.heading("id", text="ID")
        emp_table.heading("username", text="Username")
        emp_table.heading("role", text="Role")
        emp_table.heading("name", text="Full Name")
        emp_table.heading("email", text="Email")
        emp_table.heading("phone", text="Phone")
        emp_table.heading("status", text="Status")
        
        emp_table.column("id", width=50, anchor="center")
        emp_table.column("username", width=100, anchor="w")
        emp_table.column("role", width=80, anchor="center")
        emp_table.column("name", width=150, anchor="w")
        emp_table.column("email", width=160, anchor="w")
        emp_table.column("phone", width=100, anchor="w")
        emp_table.column("status", width=80, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=emp_table.yview)
        emp_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        emp_table.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        # Load users
        if is_admin(self.current_user):
            users = list_all_users(self.current_user)
        else:
            users = list_team_employees(self.current_user["id"])
        
        for user in users:
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "N/A"
            email = user.get('email', '') or "N/A"
            phone = user.get('phone', '') or "N/A"
            status = "Active" if user.get('is_active', 1) == 1 else "Inactive"
            emp_table.insert("", "end", values=(
                user['id'],
                user['username'],
                user.get('role', 'N/A'),
                full_name,
                email,
                phone,
                status
            ))
        
        # Footer with count
        footer = tk.Frame(emp_win, bg="#f5f3ff")
        footer.pack(fill="x", padx=20, pady=(0, 20))
        tk.Label(
            footer,
            text=f"Total Users: {len(users)}",
            font=("Segoe UI", 11, "bold"),
            bg="#f5f3ff", fg="#6b21a8"
        ).pack(anchor="w")
        
        # Close button
        tk.Button(
            footer, text="Close",
            font=("Segoe UI", 11, "bold"),
            bg="#9ca3af", fg="white",
            activebackground="#6b7280",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=emp_win.destroy
        ).pack(pady=(10, 0), ipady=10, ipadx=40)

    def _create_audit_logs_tab(self):
        """Create audit logs tab (admin-only)"""
        from models.audit_log_model import filter_logs, get_filtered_count
        import json
        from datetime import datetime, timedelta
        
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="📋 Audit Logs")
        
        # Store reference for admin check
        self.audit_tab = tab
        
        # Title
        tk.Label(
            tab,
            text="Audit Logs",
            font=("Segoe UI", 18, "bold"),
            bg="#f5f3ff", fg="#6b21a8"
        ).pack(pady=(20, 10))
        
        # Filters frame
        filters_frame = tk.Frame(tab, bg="white", relief="solid", bd=1)
        filters_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        # Filter row 1
        row1 = tk.Frame(filters_frame, bg="white")
        row1.pack(fill="x", padx=10, pady=10)
        
        tk.Label(row1, text="User:", font=("Segoe UI", 10), bg="white").pack(side="left", padx=5)
        self.audit_user_var = tk.StringVar()
        user_entry = tk.Entry(row1, textvariable=self.audit_user_var, font=("Segoe UI", 10), width=15)
        user_entry.pack(side="left", padx=5)
        
        tk.Label(row1, text="Action:", font=("Segoe UI", 10), bg="white").pack(side="left", padx=(20, 5))
        self.audit_action_var = tk.StringVar()
        action_combo = ttk.Combobox(row1, textvariable=self.audit_action_var, 
                                    values=["", "LOGIN", "CREATE", "UPDATE", "DELETE", "COMPLETE", "CANCEL"],
                                    font=("Segoe UI", 10), width=13, state="readonly")
        action_combo.pack(side="left", padx=5)
        action_combo.set("")
        
        tk.Label(row1, text="Resource:", font=("Segoe UI", 10), bg="white").pack(side="left", padx=(20, 5))
        self.audit_resource_var = tk.StringVar()
        resource_combo = ttk.Combobox(row1, textvariable=self.audit_resource_var,
                                      values=["", "ITEM", "SUPPLIER", "CUSTOMER", "PURCHASE_ORDER", "SALES_ORDER", "USER", "AUTH"],
                                      font=("Segoe UI", 10), width=15, state="readonly")
        resource_combo.pack(side="left", padx=5)
        resource_combo.set("")
        
        # Filter row 2 - Date range
        row2 = tk.Frame(filters_frame, bg="white")
        row2.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Label(row2, text="Date Range:", font=("Segoe UI", 10), bg="white").pack(side="left", padx=5)
        self.audit_date_range_var = tk.StringVar()
        date_combo = ttk.Combobox(row2, textvariable=self.audit_date_range_var,
                                  values=["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
                                  font=("Segoe UI", 10), width=15, state="readonly")
        date_combo.pack(side="left", padx=5)
        date_combo.set("Last 30 Days")
        
        # Filter and Clear buttons
        tk.Button(
            row2, text="Apply Filters",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6b21a8",
            relief="flat", cursor="hand2",
            command=self._apply_audit_filters
        ).pack(side="left", padx=20, ipady=5, ipadx=15)
        
        tk.Button(
            row2, text="Clear Filters",
            font=("Segoe UI", 10),
            bg="#9ca3af", fg="white",
            activebackground="#6b7280",
            relief="flat", cursor="hand2",
            command=self._clear_audit_filters
        ).pack(side="left", padx=5, ipady=5, ipadx=15)
        
        # Export button
        tk.Button(
            row2, text="Export to CSV",
            font=("Segoe UI", 10),
            bg="#059669", fg="white",
            activebackground="#047857",
            relief="flat", cursor="hand2",
            command=self._export_audit_logs
        ).pack(side="left", padx=20, ipady=5, ipadx=15)
        
        # Table frame with scrollbar
        table_frame = tk.Frame(tab, bg="white", relief="solid", bd=1)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scrollbar
        scroll_y = tk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")
        
        # Treeview for logs
        self.audit_tree = ttk.Treeview(
            table_frame,
            columns=("id", "timestamp", "user", "action", "resource", "resource_id", "details"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=15
        )
        
        scroll_y.config(command=self.audit_tree.yview)
        scroll_x.config(command=self.audit_tree.xview)
        
        # Configure columns
        self.audit_tree.heading("id", text="ID")
        self.audit_tree.heading("timestamp", text="Timestamp")
        self.audit_tree.heading("user", text="User")
        self.audit_tree.heading("action", text="Action")
        self.audit_tree.heading("resource", text="Resource Type")
        self.audit_tree.heading("resource_id", text="Resource ID")
        self.audit_tree.heading("details", text="Details")
        
        self.audit_tree.column("id", width=50, anchor="center")
        self.audit_tree.column("timestamp", width=180, anchor="w")
        self.audit_tree.column("user", width=120, anchor="w")
        self.audit_tree.column("action", width=100, anchor="center")
        self.audit_tree.column("resource", width=150, anchor="w")
        self.audit_tree.column("resource_id", width=100, anchor="center")
        self.audit_tree.column("details", width=400, anchor="w")
        
        self.audit_tree.pack(fill="both", expand=True)
        
        # Status bar
        status_frame = tk.Frame(tab, bg="#f5f3ff")
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.audit_status_label = tk.Label(
            status_frame,
            text="Loading audit logs...",
            font=("Segoe UI", 10),
            bg="#f5f3ff", fg="#6b21a8"
        )
        self.audit_status_label.pack(anchor="w")
        
        # Load initial data
        self._load_audit_logs()
    
    def _apply_audit_filters(self):
        """Apply filters to audit logs"""
        self._load_audit_logs()
    
    def _clear_audit_filters(self):
        """Clear all audit log filters"""
        self.audit_user_var.set("")
        self.audit_action_var.set("")
        self.audit_resource_var.set("")
        self.audit_date_range_var.set("Last 30 Days")
        self._load_audit_logs()
    
    def _load_audit_logs(self):
        """Load audit logs with current filters"""
        from models.audit_log_model import filter_logs
        from datetime import datetime, timedelta
        import json
        
        # Clear existing items
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
        
        # Build filter parameters
        username = self.audit_user_var.get().strip() or None
        action = self.audit_action_var.get() or None
        resource_type = self.audit_resource_var.get() or None
        
        # Calculate date range
        start_date = None
        date_range = self.audit_date_range_var.get()
        if date_range == "Today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        elif date_range == "Last 7 Days":
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif date_range == "Last 30 Days":
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        elif date_range == "Last 90 Days":
            start_date = (datetime.now() - timedelta(days=90)).isoformat()
        
        # Fetch logs
        logs = filter_logs(
            username=username,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            limit=500
        )
        
        # Populate tree
        for log in logs:
            # Format details
            details = log.get('details', '')
            if details:
                try:
                    # Try to parse JSON for better display
                    details_obj = json.loads(details)
                    if isinstance(details_obj, dict):
                        details = ', '.join([f"{k}: {v}" for k, v in details_obj.items()])
                except:
                    pass  # Keep as-is if not JSON
            
            # Format timestamp
            timestamp = log.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            
            self.audit_tree.insert("", "end", values=(
                log.get('id', ''),
                timestamp,
                log.get('username', ''),
                log.get('action', ''),
                log.get('resource_type', ''),
                log.get('resource_id', '') or '-',
                details[:100] + '...' if len(details) > 100 else details
            ))
        
        # Update status
        self.audit_status_label.config(text=f"Showing {len(logs)} audit log entries")
    
    def _export_audit_logs(self):
        """Export audit logs to CSV file"""
        from models.audit_log_model import filter_logs
        from datetime import datetime, timedelta
        from tkinter import filedialog
        import csv
        import json
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        # Build filter parameters (same as _load_audit_logs)
        username = self.audit_user_var.get().strip() or None
        action = self.audit_action_var.get() or None
        resource_type = self.audit_resource_var.get() or None
        
        start_date = None
        date_range = self.audit_date_range_var.get()
        if date_range == "Today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        elif date_range == "Last 7 Days":
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif date_range == "Last 30 Days":
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        elif date_range == "Last 90 Days":
            start_date = (datetime.now() - timedelta(days=90)).isoformat()
        
        # Fetch all matching logs
        logs = filter_logs(
            username=username,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            limit=10000  # Export more records
        )
        
        # Write to CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Timestamp', 'User ID', 'Username', 'Action', 
                             'Resource Type', 'Resource ID', 'Details', 'IP Address']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for log in logs:
                    writer.writerow({
                        'ID': log.get('id', ''),
                        'Timestamp': log.get('timestamp', ''),
                        'User ID': log.get('user_id', ''),
                        'Username': log.get('username', ''),
                        'Action': log.get('action', ''),
                        'Resource Type': log.get('resource_type', ''),
                        'Resource ID': log.get('resource_id', ''),
                        'Details': log.get('details', ''),
                        'IP Address': log.get('ip_address', '')
                    })
            
            messagebox.showinfo("Export Successful", f"Exported {len(logs)} audit logs to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export audit logs:\n{str(e)}")

    def _create_reports_tab(self):
        """Create Reports & Analytics tab"""
        from datetime import datetime, timedelta
        
        tab = tk.Frame(self.notebook, bg="#f5f3ff")
        self.notebook.add(tab, text="📊 Reports")
        
        # Title
        tk.Label(
            tab,
            text="Reports & Analytics",
            font=("Segoe UI", 18, "bold"),
            bg="#f5f3ff", fg="#6b21a8"
        ).pack(pady=(20, 10))
        
        # Main container with two columns
        main_container = tk.Frame(tab, bg="#f5f3ff")
        main_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Left column - Report selection and filters
        left_column = tk.Frame(main_container, bg="white", relief="solid", bd=1, width=300)
        left_column.pack(side="left", fill="y", padx=(0, 10))
        left_column.pack_propagate(False)
        
        tk.Label(
            left_column,
            text="Select Report Type",
            font=("Segoe UI", 12, "bold"),
            bg="white", fg="#6b21a8"
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        # Report type selection
        self.report_type_var = tk.StringVar(value="inventory_summary")
        
        report_types = [
            ("Inventory Summary", "inventory_summary"),
            ("Sales Report", "sales_report"),
            ("Purchase Report", "purchase_report"),
            ("Stock Movement", "stock_movement"),
            ("Low Stock Alert", "low_stock"),
            ("Profit Analysis", "profit_analysis")
        ]
        
        for text, value in report_types:
            rb = tk.Radiobutton(
                left_column,
                text=text,
                variable=self.report_type_var,
                value=value,
                font=("Segoe UI", 10),
                bg="white",
                activebackground="white",
                selectcolor="#ddd6fe",
                command=self._on_report_type_changed
            )
            rb.pack(anchor="w", padx=20, pady=5)
        
        # Date range filter
        tk.Label(
            left_column,
            text="Date Range",
            font=("Segoe UI", 11, "bold"),
            bg="white", fg="#6b21a8"
        ).pack(pady=(20, 10), padx=15, anchor="w")
        
        self.date_range_var = tk.StringVar(value="last_30_days")
        
        date_ranges = [
            ("All Time", "all_time"),
            ("Today", "today"),
            ("Last 7 Days", "last_7_days"),
            ("Last 30 Days", "last_30_days"),
            ("Last 90 Days", "last_90_days"),
            ("This Year", "this_year")
        ]
        
        for text, value in date_ranges:
            rb = tk.Radiobutton(
                left_column,
                text=text,
                variable=self.date_range_var,
                value=value,
                font=("Segoe UI", 10),
                bg="white",
                activebackground="white",
                selectcolor="#ddd6fe"
            )
            rb.pack(anchor="w", padx=20, pady=3)
        
        # Generate button
        tk.Button(
            left_column,
            text="Generate Report",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6b21a8",
            relief="flat", cursor="hand2",
            command=self._generate_report
        ).pack(pady=20, ipady=10, ipadx=30)
        
        # Export button
        self.btn_export_report = tk.Button(
            left_column,
            text="Export to CSV",
            font=("Segoe UI", 10),
            bg="#059669", fg="white",
            activebackground="#047857",
            relief="flat", cursor="hand2",
            command=self._export_report
        )
        self.btn_export_report.pack(pady=(0, 20), ipady=8, ipadx=25)
        
        # Right column - Report display
        right_column = tk.Frame(main_container, bg="#f5f3ff")
        right_column.pack(side="left", fill="both", expand=True)
        
        # Report display area with scrollbar
        display_frame = tk.Frame(right_column, bg="white", relief="solid", bd=1)
        display_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scroll_y = tk.Scrollbar(display_frame)
        scroll_y.pack(side="right", fill="y")
        
        # Text widget for report display
        self.report_text = tk.Text(
            display_frame,
            font=("Consolas", 10),
            bg="white", fg="#1f2937",
            wrap="word",
            yscrollcommand=scroll_y.set,
            padx=20, pady=20,
            state="disabled"
        )
        self.report_text.pack(fill="both", expand=True)
        scroll_y.config(command=self.report_text.yview)
        
        # Configure text tags for styling
        self.report_text.tag_config("title", font=("Segoe UI", 14, "bold"), foreground="#6b21a8")
        self.report_text.tag_config("heading", font=("Segoe UI", 12, "bold"), foreground="#7c3aed")
        self.report_text.tag_config("subheading", font=("Segoe UI", 10, "bold"), foreground="#374151")
        self.report_text.tag_config("metric", font=("Segoe UI", 11), foreground="#059669")
        self.report_text.tag_config("warning", font=("Segoe UI", 10), foreground="#dc2626")
        self.report_text.tag_config("normal", font=("Segoe UI", 10), foreground="#1f2937")
        
        # Store current report data for export
        self.current_report_data = None
        
        # Generate initial report
        self._generate_report()
    
    def _on_report_type_changed(self):
        """Update date range visibility based on report type"""
        # Some reports don't use date ranges (inventory_summary, low_stock)
        report_type = self.report_type_var.get()
        if report_type in ["inventory_summary", "low_stock"]:
            self.date_range_var.set("all_time")
    
    def _calculate_date_range(self):
        """Calculate start and end dates based on selected range"""
        from datetime import datetime, timedelta
        
        range_type = self.date_range_var.get()
        now = datetime.now()
        
        if range_type == "all_time":
            return None, None
        elif range_type == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return start.isoformat(), now.isoformat()
        elif range_type == "last_7_days":
            start = now - timedelta(days=7)
            return start.isoformat(), now.isoformat()
        elif range_type == "last_30_days":
            start = now - timedelta(days=30)
            return start.isoformat(), now.isoformat()
        elif range_type == "last_90_days":
            start = now - timedelta(days=90)
            return start.isoformat(), now.isoformat()
        elif range_type == "this_year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return start.isoformat(), now.isoformat()
        
        return None, None
    
    def _generate_report(self):
        """Generate the selected report"""
        try:
            report_type = self.report_type_var.get()
            start_date, end_date = self._calculate_date_range()
            
            # Clear report display
            self.report_text.config(state="normal")
            self.report_text.delete(1.0, tk.END)
            
            # Generate based on type
            if report_type == "inventory_summary":
                self._display_inventory_summary()
            elif report_type == "sales_report":
                self._display_sales_report(start_date, end_date)
            elif report_type == "purchase_report":
                self._display_purchase_report(start_date, end_date)
            elif report_type == "stock_movement":
                self._display_stock_movement(start_date, end_date)
            elif report_type == "low_stock":
                self._display_low_stock_report()
            elif report_type == "profit_analysis":
                self._display_profit_analysis(start_date, end_date)
            
            self.report_text.config(state="disabled")
            
        except PermissionError as e:
            messagebox.showerror("Permission Denied", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def _display_inventory_summary(self):
        """Display inventory summary report"""
        data = generate_inventory_summary(self.current_user)
        self.current_report_data = {"type": "inventory_summary", "data": data}
        
        self.report_text.insert(tk.END, "INVENTORY SUMMARY REPORT\n", "title")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "normal")
        
        self.report_text.insert(tk.END, "Key Metrics:\n", "heading")
        self.report_text.insert(tk.END, f"  Total Items: {data['total_items']}\n", "metric")
        self.report_text.insert(tk.END, f"  Total Quantity in Stock: {data['total_quantity']:,}\n", "metric")
        self.report_text.insert(tk.END, f"  Total Inventory Value: ${data['total_value']:,.2f}\n", "metric")
        self.report_text.insert(tk.END, f"  Average Item Price: ${data['average_price']:.2f}\n\n", "metric")
        
        self.report_text.insert(tk.END, "Stock Status:\n", "heading")
        if data['out_of_stock_count'] > 0:
            self.report_text.insert(tk.END, f"  ⚠️  Out of Stock Items: {data['out_of_stock_count']}\n", "warning")
        else:
            self.report_text.insert(tk.END, f"  ✓ No Out of Stock Items\n", "normal")
        
        if data['low_stock_count'] > 0:
            self.report_text.insert(tk.END, f"  ⚠️  Low Stock Items: {data['low_stock_count']}\n", "warning")
        else:
            self.report_text.insert(tk.END, f"  ✓ No Low Stock Items\n", "normal")
    
    def _display_sales_report(self, start_date, end_date):
        """Display sales report"""
        data = generate_sales_report(self.current_user, start_date, end_date)
        self.current_report_data = {"type": "sales_report", "data": data, "start_date": start_date, "end_date": end_date}
        
        self.report_text.insert(tk.END, "SALES REPORT\n", "title")
        self.report_text.insert(tk.END, f"Period: {self.date_range_var.get().replace('_', ' ').title()}\n", "normal")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "normal")
        
        self.report_text.insert(tk.END, "Sales Summary:\n", "heading")
        self.report_text.insert(tk.END, f"  Total Orders: {data['total_orders']}\n", "metric")
        self.report_text.insert(tk.END, f"  Total Quantity Sold: {data['total_quantity_sold']:,}\n", "metric")
        self.report_text.insert(tk.END, f"  Total Revenue: ${data['total_revenue']:,.2f}\n", "metric")
        self.report_text.insert(tk.END, f"  Average Order Value: ${data['average_order_value']:.2f}\n\n", "metric")
        
        if data['top_selling_items']:
            self.report_text.insert(tk.END, "Top Selling Items:\n", "heading")
            for idx, item in enumerate(data['top_selling_items'], 1):
                self.report_text.insert(tk.END, f"  {idx}. {item['name']} ({item['sku']})\n", "subheading")
                self.report_text.insert(tk.END, f"     Quantity Sold: {item['total_sold']:,} | Revenue: ${item['revenue']:,.2f}\n", "normal")
            self.report_text.insert(tk.END, "\n")
        
        if data['top_customers']:
            self.report_text.insert(tk.END, "Top Customers:\n", "heading")
            for idx, customer in enumerate(data['top_customers'], 1):
                self.report_text.insert(tk.END, f"  {idx}. {customer['name']}\n", "subheading")
                self.report_text.insert(tk.END, f"     Orders: {customer['order_count']} | Total Spent: ${customer['total_spent']:,.2f}\n", "normal")
    
    def _display_purchase_report(self, start_date, end_date):
        """Display purchase report"""
        data = generate_purchase_report(self.current_user, start_date, end_date)
        self.current_report_data = {"type": "purchase_report", "data": data, "start_date": start_date, "end_date": end_date}
        
        self.report_text.insert(tk.END, "PURCHASE REPORT\n", "title")
        self.report_text.insert(tk.END, f"Period: {self.date_range_var.get().replace('_', ' ').title()}\n", "normal")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "normal")
        
        self.report_text.insert(tk.END, "Purchase Summary:\n", "heading")
        self.report_text.insert(tk.END, f"  Total Orders: {data['total_orders']}\n", "metric")
        self.report_text.insert(tk.END, f"  Total Quantity Purchased: {data['total_quantity_purchased']:,}\n", "metric")
        self.report_text.insert(tk.END, f"  Total Cost: ${data['total_cost']:,.2f}\n", "metric")
        self.report_text.insert(tk.END, f"  Average Order Cost: ${data['average_order_cost']:.2f}\n\n", "metric")
        
        if data['most_purchased_items']:
            self.report_text.insert(tk.END, "Most Purchased Items:\n", "heading")
            for idx, item in enumerate(data['most_purchased_items'], 1):
                self.report_text.insert(tk.END, f"  {idx}. {item['name']} ({item['sku']})\n", "subheading")
                self.report_text.insert(tk.END, f"     Quantity: {item['total_purchased']:,} | Cost: ${item['total_cost']:,.2f}\n", "normal")
            self.report_text.insert(tk.END, "\n")
        
        if data['top_suppliers']:
            self.report_text.insert(tk.END, "Top Suppliers:\n", "heading")
            for idx, supplier in enumerate(data['top_suppliers'], 1):
                self.report_text.insert(tk.END, f"  {idx}. {supplier['name']}\n", "subheading")
                self.report_text.insert(tk.END, f"     Orders: {supplier['order_count']} | Total Cost: ${supplier['total_cost']:,.2f}\n", "normal")
    
    def _display_stock_movement(self, start_date, end_date):
        """Display stock movement report"""
        data = generate_stock_movement_report(self.current_user, start_date, end_date)
        self.current_report_data = {"type": "stock_movement", "data": data, "start_date": start_date, "end_date": end_date}
        
        self.report_text.insert(tk.END, "STOCK MOVEMENT REPORT\n", "title")
        self.report_text.insert(tk.END, f"Period: {self.date_range_var.get().replace('_', ' ').title()}\n", "normal")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "normal")
        
        if data:
            self.report_text.insert(tk.END, f"Items with Activity ({len(data)} items):\n\n", "heading")
            for item in data:
                self.report_text.insert(tk.END, f"{item['name']} ({item['sku']})\n", "subheading")
                self.report_text.insert(tk.END, f"  Current Stock: {item['current_stock']:,}\n", "normal")
                self.report_text.insert(tk.END, f"  Purchased: +{item['total_purchased']:,} | Sold: -{item['total_sold']:,}\n", "normal")
                self.report_text.insert(tk.END, f"  Net Change: {item['net_change']:+,}\n\n", "metric")
        else:
            self.report_text.insert(tk.END, "No stock movement in selected period.\n", "normal")
    
    def _display_low_stock_report(self):
        """Display low stock report"""
        data = generate_low_stock_report(self.current_user)
        self.current_report_data = {"type": "low_stock", "data": data}
        
        self.report_text.insert(tk.END, "LOW STOCK ALERT REPORT\n", "title")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "normal")
        
        self.report_text.insert(tk.END, f"Total Critical Items: {data['total_critical']}\n\n", "warning" if data['total_critical'] > 0 else "metric")
        
        if data['out_of_stock']:
            self.report_text.insert(tk.END, f"🔴 OUT OF STOCK ({len(data['out_of_stock'])} items):\n", "warning")
            for item in data['out_of_stock']:
                self.report_text.insert(tk.END, f"  • {item['name']} ({item['sku']})\n", "normal")
                self.report_text.insert(tk.END, f"    Min Level: {item['min_stock_level']} | Price: ${item['price']:.2f}\n", "normal")
            self.report_text.insert(tk.END, "\n")
        
        if data['low_stock']:
            self.report_text.insert(tk.END, f"🟡 LOW STOCK ({len(data['low_stock'])} items):\n", "warning")
            for item in data['low_stock']:
                self.report_text.insert(tk.END, f"  • {item['name']} ({item['sku']})\n", "normal")
                self.report_text.insert(tk.END, f"    Current: {item['quantity']} | Min Level: {item['min_stock_level']} | Price: ${item['price']:.2f}\n", "normal")
            self.report_text.insert(tk.END, "\n")
        
        if data['reorder_needed']:
            self.report_text.insert(tk.END, f"⚠️  REORDER NEEDED ({len(data['reorder_needed'])} items):\n", "heading")
            for item in data['reorder_needed']:
                self.report_text.insert(tk.END, f"  • {item['name']} ({item['sku']})\n", "normal")
                self.report_text.insert(tk.END, f"    Current: {item['quantity']} | Reorder Point: {item['reorder_point']} | Price: ${item['price']:.2f}\n", "normal")
        
        if not data['out_of_stock'] and not data['low_stock'] and not data['reorder_needed']:
            self.report_text.insert(tk.END, "✓ All items have adequate stock levels!\n", "metric")
    
    def _display_profit_analysis(self, start_date, end_date):
        """Display profit analysis report"""
        data = generate_profit_analysis(self.current_user, start_date, end_date)
        self.current_report_data = {"type": "profit_analysis", "data": data, "start_date": start_date, "end_date": end_date}
        
        self.report_text.insert(tk.END, "PROFIT & LOSS ANALYSIS\n", "title")
        self.report_text.insert(tk.END, f"Period: {self.date_range_var.get().replace('_', ' ').title()}\n", "normal")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "normal")
        
        self.report_text.insert(tk.END, "Financial Summary:\n", "heading")
        self.report_text.insert(tk.END, f"  Total Revenue (Sales): ${data['total_revenue']:,.2f}\n", "metric")
        self.report_text.insert(tk.END, f"  Total Cost (Purchases): ${data['total_cost']:,.2f}\n", "metric")
        self.report_text.insert(tk.END, f"  Gross Profit: ${data['gross_profit']:,.2f}\n", "metric")
        self.report_text.insert(tk.END, f"  Profit Margin: {data['profit_margin_percent']:.2f}%\n\n", "metric")
        
        self.report_text.insert(tk.END, "Order Statistics:\n", "heading")
        self.report_text.insert(tk.END, f"  Sales Orders Completed: {data['total_sales_orders']}\n", "normal")
        self.report_text.insert(tk.END, f"  Purchase Orders Completed: {data['total_purchase_orders']}\n", "normal")
    
    def _export_report(self):
        """Export current report to CSV"""
        from tkinter import filedialog
        import csv
        
        if not self.current_report_data:
            messagebox.showwarning("No Report", "Please generate a report first.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{self.current_report_data['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            report_type = self.current_report_data['type']
            data = self.current_report_data['data']
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if report_type == "inventory_summary":
                    writer = csv.writer(csvfile)
                    writer.writerow(["Metric", "Value"])
                    writer.writerow(["Total Items", data['total_items']])
                    writer.writerow(["Total Quantity", data['total_quantity']])
                    writer.writerow(["Total Value", f"${data['total_value']:.2f}"])
                    writer.writerow(["Out of Stock Count", data['out_of_stock_count']])
                    writer.writerow(["Low Stock Count", data['low_stock_count']])
                    writer.writerow(["Average Price", f"${data['average_price']:.2f}"])
                
                elif report_type in ["sales_report", "purchase_report"]:
                    if report_type == "sales_report":
                        writer = csv.writer(csvfile)
                        writer.writerow(["Sales Report"])
                        writer.writerow(["Total Orders", data['total_orders']])
                        writer.writerow(["Total Quantity Sold", data['total_quantity_sold']])
                        writer.writerow(["Total Revenue", f"${data['total_revenue']:.2f}"])
                        writer.writerow(["Average Order Value", f"${data['average_order_value']:.2f}"])
                        writer.writerow([])
                        writer.writerow(["Top Selling Items"])
                        writer.writerow(["Name", "SKU", "Quantity Sold", "Revenue"])
                        for item in data['top_selling_items']:
                            writer.writerow([item['name'], item['sku'], item['total_sold'], f"${item['revenue']:.2f}"])
                    else:
                        writer = csv.writer(csvfile)
                        writer.writerow(["Purchase Report"])
                        writer.writerow(["Total Orders", data['total_orders']])
                        writer.writerow(["Total Quantity Purchased", data['total_quantity_purchased']])
                        writer.writerow(["Total Cost", f"${data['total_cost']:.2f}"])
                        writer.writerow(["Average Order Cost", f"${data['average_order_cost']:.2f}"])
                        writer.writerow([])
                        writer.writerow(["Most Purchased Items"])
                        writer.writerow(["Name", "SKU", "Quantity", "Cost"])
                        for item in data['most_purchased_items']:
                            writer.writerow([item['name'], item['sku'], item['total_purchased'], f"${item['total_cost']:.2f}"])
                
                elif report_type == "stock_movement":
                    writer = csv.DictWriter(csvfile, fieldnames=['Name', 'SKU', 'Current Stock', 'Purchased', 'Sold', 'Net Change'])
                    writer.writeheader()
                    for item in data:
                        writer.writerow({
                            'Name': item['name'],
                            'SKU': item['sku'],
                            'Current Stock': item['current_stock'],
                            'Purchased': item['total_purchased'],
                            'Sold': item['total_sold'],
                            'Net Change': item['net_change']
                        })
                
                elif report_type == "low_stock":
                    writer = csv.writer(csvfile)
                    writer.writerow(["Low Stock Report"])
                    writer.writerow([])
                    writer.writerow(["OUT OF STOCK"])
                    writer.writerow(["Name", "SKU", "Min Level", "Price"])
                    for item in data['out_of_stock']:
                        writer.writerow([item['name'], item['sku'], item['min_stock_level'], f"${item['price']:.2f}"])
                    writer.writerow([])
                    writer.writerow(["LOW STOCK"])
                    writer.writerow(["Name", "SKU", "Quantity", "Min Level", "Price"])
                    for item in data['low_stock']:
                        writer.writerow([item['name'], item['sku'], item['quantity'], item['min_stock_level'], f"${item['price']:.2f}"])
                
                elif report_type == "profit_analysis":
                    writer = csv.writer(csvfile)
                    writer.writerow(["Profit & Loss Analysis"])
                    writer.writerow(["Total Revenue", f"${data['total_revenue']:.2f}"])
                    writer.writerow(["Total Cost", f"${data['total_cost']:.2f}"])
                    writer.writerow(["Gross Profit", f"${data['gross_profit']:.2f}"])
                    writer.writerow(["Profit Margin", f"{data['profit_margin_percent']:.2f}%"])
                    writer.writerow(["Sales Orders", data['total_sales_orders']])
                    writer.writerow(["Purchase Orders", data['total_purchase_orders']])
            
            messagebox.showinfo("Export Successful", f"Report exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export report:\n{str(e)}")
    
    def _on_barcode_lookup(self):
        """Open barcode lookup dialog"""
        from utils.barcode_utils import search_item_by_barcode, get_barcode_tk_image
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Barcode Lookup")
        dialog.configure(bg="#f5f3ff")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg="#059669")
        header.pack(fill="x")
        tk.Label(
            header, text="📷 Barcode Lookup",
            font=("Segoe UI", 16, "bold"),
            bg="#059669", fg="white"
        ).pack(pady=15)
        
        # Form
        form = tk.Frame(dialog, bg="#f5f3ff")
        form.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            form, text="Enter Barcode Number:",
            font=("Segoe UI", 11, "bold"),
            bg="#f5f3ff", fg="#6b21a8"
        ).pack(anchor="w", pady=(0, 5))
        
        barcode_entry = tk.Entry(
            form,
            font=("Segoe UI", 12),
            bg="#ddd6fe", fg="#1f2937",
            relief="flat", bd=0,
            insertbackground="#6b21a8"
        )
        barcode_entry.pack(fill="x", ipady=10, ipadx=10, pady=(0, 15))
        barcode_entry.focus()
        
        # Result frame
        result_frame = tk.Frame(form, bg="white", relief="solid", bd=1)
        result_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        result_label = tk.Label(
            result_frame,
            text="Enter a barcode and click Search",
            font=("Segoe UI", 10),
            bg="white", fg="#6b7280",
            wraplength=400
        )
        result_label.pack(pady=20)
        
        def do_search():
            barcode = barcode_entry.get().strip()
            if not barcode:
                messagebox.showwarning("Input Required", "Please enter a barcode number.")
                return
            
            # Search for item
            item = search_item_by_barcode(barcode)
            
            # Clear result frame
            for widget in result_frame.winfo_children():
                widget.destroy()
            
            if item:
                # Display item info
                info_text = f"""
✓ Item Found!

Name: {item['name']}
SKU: {item['sku']}
Quantity: {item['quantity']}
Price: ${item['price']:.2f}
Barcode: {item['barcode']}

Min Stock: {item['min_stock_level']}
Reorder Point: {item['reorder_point']}
                """.strip()
                
                tk.Label(
                    result_frame,
                    text=info_text,
                    font=("Segoe UI", 10),
                    bg="white", fg="#059669",
                    justify="left",
                    anchor="w"
                ).pack(pady=15, padx=15, anchor="w")
                
                # Show barcode image if available
                try:
                    barcode_img = get_barcode_tk_image(item['barcode'], item['name'], width=350)
                    if barcode_img:
                        img_label = tk.Label(result_frame, image=barcode_img, bg="white")
                        img_label.image = barcode_img  # Keep reference
                        img_label.pack(pady=10)
                except Exception as e:
                    print(f"Error displaying barcode image: {e}")
                
                # Add button to view in inventory
                tk.Button(
                    result_frame,
                    text="View in Inventory",
                    font=("Segoe UI", 10, "bold"),
                    bg="#7c3aed", fg="white",
                    activebackground="#6b21a8",
                    relief="flat", cursor="hand2",
                    command=lambda: self._highlight_item(item['id'], dialog)
                ).pack(pady=10, ipady=8, ipadx=20)
            else:
                tk.Label(
                    result_frame,
                    text=f"❌ No item found with barcode:\n{barcode}",
                    font=("Segoe UI", 11),
                    bg="white", fg="#dc2626"
                ).pack(pady=40)
        
        # Search button
        tk.Button(
            form, text="🔍 Search",
            font=("Segoe UI", 11, "bold"),
            bg="#059669", fg="white",
            activebackground="#047857",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=do_search
        ).pack(pady=(15, 0), ipady=10, ipadx=40)
        
        barcode_entry.bind("<Return>", lambda e: do_search())
        
        # Close button
        tk.Button(
            form, text="Close",
            font=("Segoe UI", 10),
            bg="#9ca3af", fg="white",
            activebackground="#6b7280",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=dialog.destroy
        ).pack(pady=(10, 0), ipady=8, ipadx=30)
    
    def _highlight_item(self, item_id, dialog=None):
        """Highlight an item in the inventory table"""
        if dialog:
            dialog.destroy()
        
        # Switch to inventory tab
        self.notebook.select(0)  # Inventory is first tab
        
        # Search for the item in the table
        for item in self.table.get_children():
            values = self.table.item(item)["values"]
            if values and int(values[0]) == item_id:
                self.table.selection_set(item)
                self.table.focus(item)
                self.table.see(item)
                break
    
    def _regenerate_barcode(self, item_id, barcode_frame, parent_dialog):
        """Regenerate barcode for an item"""
        from utils.barcode_utils import generate_barcode_number, update_item_barcode, get_barcode_tk_image
        from models.inventory_model import get_item
        
        try:
            # Get current item data
            result = get_item(item_id)
            if not result.get("success"):
                messagebox.showerror("Error", "Item not found")
                return
            
            item = result.get("item")
            
            # Generate new barcode
            new_barcode = generate_barcode_number(item_id, item['sku'])
            
            # Update in database
            update_item_barcode(item_id, new_barcode)
            
            # Clear and update the barcode frame
            for widget in barcode_frame.winfo_children():
                widget.destroy()
            
            tk.Label(
                barcode_frame, text="Barcode",
                font=("Segoe UI", 10, "bold"),
                bg="white", fg="#6b21a8"
            ).pack(anchor="w", padx=10, pady=(10, 5))
            
            tk.Label(
                barcode_frame, text=new_barcode,
                font=("Consolas", 12),
                bg="white", fg="#1f2937"
            ).pack(anchor="w", padx=10, pady=(0, 10))
            
            # Show new barcode image
            try:
                barcode_img = get_barcode_tk_image(new_barcode, item['name'], width=400)
                if barcode_img:
                    img_label = tk.Label(barcode_frame, image=barcode_img, bg="white")
                    img_label.image = barcode_img  # Keep reference
                    img_label.pack(pady=10)
            except Exception as e:
                print(f"Error displaying barcode: {e}")
            
            # Regenerate button
            tk.Button(
                barcode_frame, text="🔄 Regenerate Barcode",
                font=("Segoe UI", 9),
                bg="#6b7280", fg="white",
                activebackground="#4b5563",
                relief="flat", cursor="hand2",
                command=lambda: self._regenerate_barcode(item_id, barcode_frame, parent_dialog)
            ).pack(pady=(0, 10), ipady=5, ipadx=15)
            
            messagebox.showinfo("Success", f"Barcode generated:\n{new_barcode}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate barcode:\n{str(e)}")
    
    def _open_email_settings(self):
        """Open email configuration dialog (Admin only)"""
        from utils.email_notifications import EMAIL_CONFIG, is_email_configured
        
        # Create scrollable dialog
        dialog, form_frame = self._create_scrollable_dialog("📧 Email Settings", width=600, height=600)
        
        # Form content
        form_content = tk.Frame(form_frame, bg="#f5f3ff")
        form_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        tk.Label(
            form_content,
            text="Configure email notifications for inventory alerts and order updates.",
            font=("Segoe UI", 10),
            bg="#f5f3ff", fg="#6b7280",
            wraplength=500
        ).pack(anchor="w", pady=(0, 20))
        
        # Status indicator
        status_frame = tk.Frame(form_content, bg="white", relief="solid", bd=1)
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_text = "✅ Enabled" if is_email_configured() else "⚠️ Not Configured"
        status_color = "#059669" if is_email_configured() else "#d97706"
        
        tk.Label(
            status_frame,
            text=f"Status: {status_text}",
            font=("Segoe UI", 11, "bold"),
            bg="white", fg=status_color
        ).pack(pady=15)
        
        # Form fields
        entries = {}
        fields = [
            ("smtp_server", "SMTP Server", EMAIL_CONFIG.get("smtp_server", "")),
            ("smtp_port", "SMTP Port", str(EMAIL_CONFIG.get("smtp_port", "587"))),
            ("sender_email", "Sender Email", EMAIL_CONFIG.get("sender_email", "")),
            ("sender_password", "Password", EMAIL_CONFIG.get("sender_password", "")),
        ]
        
        for field, label, default_value in fields:
            tk.Label(
                form_content, text=label,
                font=("Segoe UI", 10, "bold"),
                bg="#f5f3ff", fg="#6b21a8"
            ).pack(anchor="w", pady=(10, 5))
            
            if field == "sender_password":
                entry = tk.Entry(
                    form_content,
                    font=("Segoe UI", 11),
                    bg="#ddd6fe", fg="#1f2937",
                    relief="flat", bd=0,
                    show="*"
                )
            else:
                entry = tk.Entry(
                    form_content,
                    font=("Segoe UI", 11),
                    bg="#ddd6fe", fg="#1f2937",
                    relief="flat", bd=0
                )
            
            entry.pack(fill="x", ipady=10, ipadx=10)
            if default_value:
                entry.insert(0, str(default_value))
            entries[field] = entry
        
        # TLS checkbox
        use_tls_var = tk.BooleanVar(value=EMAIL_CONFIG.get("use_tls", True))
        tk.Checkbutton(
            form_content,
            text="Use TLS Encryption",
            variable=use_tls_var,
            font=("Segoe UI", 10),
            bg="#f5f3ff", fg="#1f2937",
            selectcolor="#ddd6fe"
        ).pack(anchor="w", pady=10)
        
        # Enabled checkbox
        enabled_var = tk.BooleanVar(value=EMAIL_CONFIG.get("enabled", False))
        tk.Checkbutton(
            form_content,
            text="Enable Email Notifications",
            variable=enabled_var,
            font=("Segoe UI", 10, "bold"),
            bg="#f5f3ff", fg="#6b21a8",
            selectcolor="#ddd6fe"
        ).pack(anchor="w", pady=10)
        
        # Info box
        info_frame = tk.Frame(form_content, bg="#fef3c7", relief="solid", bd=1)
        info_frame.pack(fill="x", pady=20)
        
        tk.Label(
            info_frame,
            text="💡 Tip: For Gmail, use 'smtp.gmail.com' and port 587.\nYou may need to enable 'App Passwords' in your Google Account.",
            font=("Segoe UI", 9),
            bg="#fef3c7", fg="#92400e",
            justify="left"
        ).pack(padx=15, pady=15)
        
        def test_email():
            """Test email configuration"""
            test_email = entries["sender_email"].get().strip()
            if not test_email:
                messagebox.showwarning("Test Email", "Please enter sender email first")
                return
            
            try:
                from utils.email_notifications import send_email
                result = send_email(
                    test_email,
                    "Test Email - Inventory System",
                    "<h2>Test Successful!</h2><p>Your email configuration is working correctly.</p>",
                    "Test Successful! Your email configuration is working correctly."
                )
                if result.get("success"):
                    messagebox.showinfo("Success", "Test email sent successfully!")
                else:
                    messagebox.showerror("Error", result.get("message"))
            except Exception as e:
                messagebox.showerror("Error", f"Test failed: {str(e)}")
        
        def save_settings():
            """Save email settings to config file"""
            try:
                # Create .env file with settings
                env_content = f"""# Email Configuration for Inventory Management System
SMTP_SERVER={entries["smtp_server"].get().strip()}
SMTP_PORT={entries["smtp_port"].get().strip()}
SENDER_EMAIL={entries["sender_email"].get().strip()}
SENDER_PASSWORD={entries["sender_password"].get().strip()}
USE_TLS={'True' if use_tls_var.get() else 'False'}
EMAIL_ENABLED={'True' if enabled_var.get() else 'False'}
"""
                with open(".env", "w") as f:
                    f.write(env_content)
                
                # Update in-memory config
                EMAIL_CONFIG.update({
                    "smtp_server": entries["smtp_server"].get().strip(),
                    "smtp_port": int(entries["smtp_port"].get().strip() or 587),
                    "sender_email": entries["sender_email"].get().strip(),
                    "sender_password": entries["sender_password"].get().strip(),
                    "use_tls": use_tls_var.get(),
                    "enabled": enabled_var.get()
                })
                
                messagebox.showinfo("Success", "Email settings saved successfully!\n\nNote: Changes will take full effect after restarting the application.")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
        
        def send_test_alerts():
            """Send test low stock alert"""
            try:
                from models.stock_alert_model import send_low_stock_email_alerts
                result = send_low_stock_email_alerts()
                if result.get("success"):
                    messagebox.showinfo("Success", result.get("message"))
                else:
                    messagebox.showwarning("No Alerts", result.get("message"))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send alerts: {str(e)}")
        
        # Buttons
        btn_frame = tk.Frame(form_content, bg="#f5f3ff")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        tk.Button(
            btn_frame, text="💾 Save Settings",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6b21a8",
            relief="flat", cursor="hand2",
            command=save_settings
        ).pack(side="left", ipady=8, ipadx=20)
        
        tk.Button(
            btn_frame, text="✉️ Send Test Email",
            font=("Segoe UI", 10, "bold"),
            bg="#059669", fg="white",
            activebackground="#047857",
            relief="flat", cursor="hand2",
            command=test_email
        ).pack(side="left", padx=10, ipady=8, ipadx=20)
        
        tk.Button(
            btn_frame, text="📧 Send Stock Alerts",
            font=("Segoe UI", 10),
            bg="#d97706", fg="white",
            activebackground="#b45309",
            relief="flat", cursor="hand2",
            command=send_test_alerts
        ).pack(side="left", ipady=8, ipadx=20)
        
        tk.Button(
            btn_frame, text="Close",
            font=("Segoe UI", 10),
            bg="#9ca3af", fg="white",
            activebackground="#6b7280",
            relief="flat", cursor="hand2",
            command=dialog.destroy
        ).pack(side="right", ipady=8, ipadx=20)

    # ==================== Import/Export Methods ====================
    
    def _export_inventory(self):
        """Export inventory items to CSV or Excel"""
        from tkinter import filedialog, messagebox
        from utils.import_export import (export_inventory_to_csv, export_inventory_to_excel, 
                                          EXCEL_AVAILABLE)
        from models.inventory_model import get_items
        
        # Get all items (returns list directly)
        items = get_items(limit=10000)
        if not items:
            messagebox.showwarning("No Data", "No inventory items to export")
            return
        
        # Ask for file type
        file_types = [("CSV files", "*.csv")]
        if EXCEL_AVAILABLE:
            file_types.insert(0, ("Excel files", "*.xlsx"))
        
        filepath = filedialog.asksaveasfilename(
            title="Export Inventory",
            defaultextension=".xlsx" if EXCEL_AVAILABLE else ".csv",
            filetypes=file_types
        )
        
        if not filepath:
            return
        
        # Export based on file extension
        if filepath.endswith('.xlsx') and EXCEL_AVAILABLE:
            result = export_inventory_to_excel(items, filepath)
        else:
            result = export_inventory_to_csv(items, filepath)
        
        if result.get("success"):
            messagebox.showinfo("Export Successful", result.get("message"))
        else:
            messagebox.showerror("Export Failed", result.get("message"))
    
    def _import_inventory(self):
        """Import inventory items from CSV or Excel"""
        from tkinter import filedialog, messagebox
        from utils.import_export import (import_inventory_from_csv, import_inventory_from_excel, 
                                          EXCEL_AVAILABLE)
        from models.inventory_model import add_item
        
        # Ask for file
        file_types = [("CSV files", "*.csv")]
        if EXCEL_AVAILABLE:
            file_types.insert(0, ("Excel files", "*.xlsx"))
        
        filepath = filedialog.askopenfilename(
            title="Import Inventory",
            filetypes=file_types
        )
        
        if not filepath:
            return
        
        # Import based on file extension
        if filepath.endswith('.xlsx') and EXCEL_AVAILABLE:
            result = import_inventory_from_excel(filepath)
        else:
            result = import_inventory_from_csv(filepath)
        
        if not result.get("success"):
            messagebox.showerror("Import Failed", result.get("message"))
            return
        
        items = result.get("data", [])
        if not items:
            messagebox.showwarning("No Data", "No items found in file")
            return
        
        # Confirm import
        if not messagebox.askyesno("Confirm Import", 
                                   f"Import {len(items)} items?\nThis will add new items to the inventory."):
            return
        
        # Import items
        success_count = 0
        errors = []
        
        for item in items:
            try:
                # Prepare payload for add_item (match actual database schema)
                payload = {
                    'sku': item.get('sku'),
                    'name': item.get('name'),
                    'quantity': item.get('quantity'),
                    'price': item.get('price'),
                    'min_stock_level': item.get('min_stock_level', 10),
                    'reorder_point': item.get('reorder_point', 20),
                    'barcode': item.get('barcode', '')
                }
                
                add_item(payload)
                success_count += 1
            except Exception as e:
                errors.append(f"SKU {item.get('sku')}: {str(e)}")
        
        # Show results
        if errors:
            error_msg = f"Imported {success_count} items.\n\nErrors:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more errors"
            messagebox.showwarning("Import Completed with Errors", error_msg)
        else:
            messagebox.showinfo("Import Successful", f"Successfully imported {success_count} items")
        
        # Refresh table
        self._on_search()
    
    def _export_suppliers(self):
        """Export suppliers to CSV or Excel"""
        from tkinter import filedialog, messagebox
        from utils.import_export import (export_suppliers_to_csv, export_suppliers_to_excel, 
                                          EXCEL_AVAILABLE)
        from models.supplier_model import search_suppliers
        
        result = search_suppliers("")  # Empty query returns all
        if not result.get("success"):
            messagebox.showerror("Export Error", result.get("message", "Failed to retrieve suppliers"))
            return
        
        suppliers = result.get("suppliers", [])
        if not suppliers:
            messagebox.showwarning("No Data", "No suppliers to export")
            return
        
        file_types = [("CSV files", "*.csv")]
        if EXCEL_AVAILABLE:
            file_types.insert(0, ("Excel files", "*.xlsx"))
        
        filepath = filedialog.asksaveasfilename(
            title="Export Suppliers",
            defaultextension=".xlsx" if EXCEL_AVAILABLE else ".csv",
            filetypes=file_types
        )
        
        if not filepath:
            return
        
        if filepath.endswith('.xlsx') and EXCEL_AVAILABLE:
            result = export_suppliers_to_excel(suppliers, filepath)
        else:
            result = export_suppliers_to_csv(suppliers, filepath)
        
        if result.get("success"):
            messagebox.showinfo("Export Successful", result.get("message"))
        else:
            messagebox.showerror("Export Failed", result.get("message"))
    
    def _import_suppliers(self):
        """Import suppliers from CSV or Excel"""
        from tkinter import filedialog, messagebox
        from utils.import_export import (import_suppliers_from_csv, import_suppliers_from_excel, 
                                          EXCEL_AVAILABLE)
        from models.supplier_model import create_supplier
        
        file_types = [("CSV files", "*.csv")]
        if EXCEL_AVAILABLE:
            file_types.insert(0, ("Excel files", "*.xlsx"))
        
        filepath = filedialog.askopenfilename(
            title="Import Suppliers",
            filetypes=file_types
        )
        
        if not filepath:
            return
        
        if filepath.endswith('.xlsx') and EXCEL_AVAILABLE:
            result = import_suppliers_from_excel(filepath)
        else:
            result = import_suppliers_from_csv(filepath)
        
        if not result.get("success"):
            messagebox.showerror("Import Failed", result.get("message"))
            return
        
        suppliers = result.get("data", [])
        if not suppliers:
            messagebox.showwarning("No Data", "No suppliers found in file")
            return
        
        if not messagebox.askyesno("Confirm Import", 
                                   f"Import {len(suppliers)} suppliers?"):
            return
        
        success_count = 0
        errors = []
        
        for supplier in suppliers:
            try:
                supplier_result = create_supplier(
                    name=supplier.get('name'),
                    contact_person=supplier.get('contact_person', ''),
                    email=supplier.get('email'),
                    phone=supplier.get('phone'),
                    address=supplier.get('address', '')
                )
                
                if supplier_result.get("success"):
                    success_count += 1
                else:
                    errors.append(f"{supplier.get('name')}: {supplier_result.get('message')}")
            except Exception as e:
                errors.append(f"{supplier.get('name')}: {str(e)}")
        
        if errors:
            error_msg = f"Imported {success_count} suppliers.\n\nErrors:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more errors"
            messagebox.showwarning("Import Completed with Errors", error_msg)
        else:
            messagebox.showinfo("Import Successful", f"Successfully imported {success_count} suppliers")
        
        self._on_search_suppliers()
    
    def _export_customers(self):
        """Export customers to CSV or Excel"""
        from tkinter import filedialog, messagebox
        from utils.import_export import (export_customers_to_csv, export_customers_to_excel, 
                                          EXCEL_AVAILABLE)
        from models.customer_model import search_customers
        
        result = search_customers("")  # Empty query returns all
        if not result.get("success"):
            messagebox.showerror("Export Error", result.get("message", "Failed to retrieve customers"))
            return
        
        customers = result.get("customers", [])
        if not customers:
            messagebox.showwarning("No Data", "No customers to export")
            return
        
        file_types = [("CSV files", "*.csv")]
        if EXCEL_AVAILABLE:
            file_types.insert(0, ("Excel files", "*.xlsx"))
        
        filepath = filedialog.asksaveasfilename(
            title="Export Customers",
            defaultextension=".xlsx" if EXCEL_AVAILABLE else ".csv",
            filetypes=file_types
        )
        
        if not filepath:
            return
        
        if filepath.endswith('.xlsx') and EXCEL_AVAILABLE:
            result = export_customers_to_excel(customers, filepath)
        else:
            result = export_customers_to_csv(customers, filepath)
        
        if result.get("success"):
            messagebox.showinfo("Export Successful", result.get("message"))
        else:
            messagebox.showerror("Export Failed", result.get("message"))
    
    def _import_customers(self):
        """Import customers from CSV or Excel"""
        from tkinter import filedialog, messagebox
        from utils.import_export import (import_customers_from_csv, import_customers_from_excel, 
                                          EXCEL_AVAILABLE)
        from models.customer_model import create_customer
        
        file_types = [("CSV files", "*.csv")]
        if EXCEL_AVAILABLE:
            file_types.insert(0, ("Excel files", "*.xlsx"))
        
        filepath = filedialog.askopenfilename(
            title="Import Customers",
            filetypes=file_types
        )
        
        if not filepath:
            return
        
        if filepath.endswith('.xlsx') and EXCEL_AVAILABLE:
            result = import_customers_from_excel(filepath)
        else:
            result = import_customers_from_csv(filepath)
        
        if not result.get("success"):
            messagebox.showerror("Import Failed", result.get("message"))
            return
        
        customers = result.get("data", [])
        if not customers:
            messagebox.showwarning("No Data", "No customers found in file")
            return
        
        if not messagebox.askyesno("Confirm Import", 
                                   f"Import {len(customers)} customers?"):
            return
        
        success_count = 0
        errors = []
        
        for customer in customers:
            try:
                customer_result = create_customer(
                    name=customer.get('name'),
                    email=customer.get('email'),
                    phone=customer.get('phone'),
                    address=customer.get('address', '')
                )
                
                if customer_result.get("success"):
                    success_count += 1
                else:
                    errors.append(f"{customer.get('name')}: {customer_result.get('message')}")
            except Exception as e:
                errors.append(f"{customer.get('name')}: {str(e)}")
        
        if errors:
            error_msg = f"Imported {success_count} customers.\n\nErrors:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more errors"
            messagebox.showwarning("Import Completed with Errors", error_msg)
        else:
            messagebox.showinfo("Import Successful", f"Successfully imported {success_count} customers")
        
        self._on_search_customers()



