# views/dashboard_view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from controllers.inventory_controller import create_item, edit_item, remove_item, find_items
from models.user_model import create_user, delete_user, list_team_employees  # delete_user used by manager panel

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

        # Main content area
        content = tk.Frame(self, bg="#f5f3ff")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Toolbar with modern buttons
        toolbar = tk.Frame(content, bg="#f5f3ff")
        toolbar.pack(fill="x", pady=(0, 15))
        
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

        # Search bar
        search_frame = tk.Frame(content, bg="white", bd=0)
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

        # Table with purple theme
        table_frame = tk.Frame(content, bg="white", bd=0)
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
        
        cols = ("id","name","sku","quantity","price")
        self.table = ttk.Treeview(table_frame, columns=cols, show="headings", style="Purple.Treeview")
        for c, h, w in (("id","ID",80), ("name","Name",220), ("sku","SKU",150), ("quantity","Qty",100), ("price","Price",120)):
            self.table.heading(c, text=h)
            self.table.column(c, width=w, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True, padx=2, pady=2)

        self._apply_role_locks()
        self._on_search()

    # ---- session / nav ----
    def _logout(self):
        if messagebox.askyesno("Log out", "Log out and return to sign-in?"):
            app = self.winfo_toplevel()   # the root App()
            app.show_auth()               # swap back to AuthPage

    def _is_manager(self):
        return self.current_user.get("role") == "manager"

    def _apply_role_locks(self):
        if not self._is_manager():
            self.btn_user_mgmt.pack_forget()
            for b in (self.btn_add, self.btn_edit, self.btn_delete):
                b.configure(state="disabled", bg="#d1d5db")

    # ---- inventory handlers ----
    def _on_search(self):
        q = self.ent_q.get().strip()
        rows = find_items(q)
        for i in self.table.get_children():
            self.table.delete(i)
        for r in rows:
            price_display = f"${r.get('price', 0.0):.2f}"
            self.table.insert("", "end", values=(r["id"], r["name"], r["sku"], r["quantity"], price_display))

    def _selected_item_id(self):
        sel = self.table.focus()
        if not sel:
            return None
        vals = self.table.item(sel)["values"]
        return int(vals[0]) if vals else None
    
    def _get_selected_item_data(self):
        """Get the full data for the selected item"""
        sel = self.table.focus()
        if not sel:
            return None
        vals = self.table.item(sel)["values"]
        if not vals:
            return None
        # vals = (id, name, sku, quantity, price_display)
        price_str = vals[4].replace("$", "").replace(",", "")
        return {
            "id": int(vals[0]),
            "name": vals[1],
            "sku": vals[2],
            "quantity": int(vals[3]),
            "price": float(price_str) if price_str else 0.0
        }

    def _on_add_item(self):
        try:
            # Create custom dialog
            dialog = tk.Toplevel(self)
            dialog.title("Add Item")
            dialog.configure(bg="#f5f3ff")
            dialog.geometry("400x450")
            dialog.transient(self)
            dialog.grab_set()
            
            # Header
            header = tk.Frame(dialog, bg="#7c3aed")
            header.pack(fill="x")
            tk.Label(
                header, text="Add New Item",
                font=("Segoe UI", 16, "bold"),
                bg="#7c3aed", fg="white"
            ).pack(pady=15)
            
            # Form
            form = tk.Frame(dialog, bg="#f5f3ff")
            form.pack(fill="both", expand=True, padx=30, pady=30)
            
            def create_field(label_text):
                tk.Label(
                    form, text=label_text,
                    font=("Segoe UI", 10, "bold"),
                    bg="#f5f3ff", fg="#6b21a8"
                ).pack(anchor="w", pady=(10, 5))
                
                entry = tk.Entry(
                    form,
                    font=("Segoe UI", 11),
                    bg="#ddd6fe", fg="#1f2937",
                    relief="flat", bd=0,
                    insertbackground="#6b21a8"
                )
                entry.pack(fill="x", ipady=10, ipadx=10)
                return entry
            
            ent_name = create_field("Item Name")
            ent_sku = create_field("SKU")
            ent_qty = create_field("Quantity")
            ent_price = create_field("Price ($)")
            
            result = {"cancelled": True}
            
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
            
            # Buttons
            btn_frame = tk.Frame(form, bg="#f5f3ff")
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
            
            # Create custom dialog
            dialog = tk.Toplevel(self)
            dialog.title("Edit Item")
            dialog.configure(bg="#f5f3ff")
            dialog.geometry("400x500")
            dialog.transient(self)
            dialog.grab_set()
            
            # Header
            header = tk.Frame(dialog, bg="#7c3aed")
            header.pack(fill="x")
            tk.Label(
                header, text="Edit Item",
                font=("Segoe UI", 16, "bold"),
                bg="#7c3aed", fg="white"
            ).pack(pady=15)
            
            # Form
            form = tk.Frame(dialog, bg="#f5f3ff")
            form.pack(fill="both", expand=True, padx=30, pady=30)
            
            # Track original values to detect changes
            original_values = {
                "name": item_data["name"],
                "sku": item_data["sku"],
                "quantity": str(item_data["quantity"]),
                "price": f"{item_data['price']:.2f}"
            }
            
            def create_field(label_text, initial_value=""):
                tk.Label(
                    form, text=label_text,
                    font=("Segoe UI", 10, "bold"),
                    bg="#f5f3ff", fg="#6b21a8"
                ).pack(anchor="w", pady=(10, 5))
                
                entry = tk.Entry(
                    form,
                    font=("Segoe UI", 11),
                    bg="#ddd6fe", fg="#1f2937",
                    relief="flat", bd=0,
                    insertbackground="#6b21a8"
                )
                entry.pack(fill="x", ipady=10, ipadx=10)
                if initial_value:
                    entry.insert(0, initial_value)
                return entry
            
            ent_name = create_field("Item Name", item_data["name"])
            ent_sku = create_field("SKU", item_data["sku"])
            ent_qty = create_field("Quantity", str(item_data["quantity"]))
            ent_price = create_field("Price ($)", f"{item_data['price']:.2f}")
            
            result = {"cancelled": True}
            
            # Save button (initially disabled)
            btn_frame = tk.Frame(form, bg="#f5f3ff")
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
            messagebox.showerror("Error", str(e))

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

    # ---- manager: user management ----
    def _open_user_mgmt(self):
        if not self._is_manager():
            messagebox.showerror("Forbidden","Managers only."); return
        
        win = tk.Toplevel(self)
        win.title("User Management")
        win.configure(bg="#f5f3ff")
        win.geometry("500x600")
        
        # Header
        header = tk.Frame(win, bg="#7c3aed")
        header.pack(fill="x")
        tk.Label(
            header, text="User Management",
            font=("Segoe UI", 18, "bold"),
            bg="#7c3aed", fg="white"
        ).pack(pady=20, padx=20)
        
        # Form container
        form_container = tk.Frame(win, bg="white")
        form_container.pack(fill="x", padx=20, pady=20)
        
        form_inner = tk.Frame(form_container, bg="white")
        form_inner.pack(padx=20, pady=20)
        
        tk.Label(
            form_inner, text="Create New Employee",
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
            
            try:
                res = create_user(
                    password=p1,
                    role="employee",
                    manager_id=self.current_user["id"],
                    first_name=first,
                    last_name=last,
                    email=email,
                    phone=phone,
                    business_name=None,
                    username=None,  # auto-generate
                )
                messagebox.showinfo("OK", f"Employee created.\nAssigned username: {res['username']}")
                refresh()
                # Clear form
                for e in [ent_first, ent_last, ent_email, ent_phone, ent_pass, ent_pass2]:
                    e.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            form_inner, text="Create Employee",
            font=("Segoe UI", 12, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=do_create
        ).pack(fill="x", pady=(15, 0), ipady=10)
        
        # Employee list
        list_container = tk.Frame(win, bg="white")
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        tk.Label(
            list_container, text="Current Employees",
            font=("Segoe UI", 12, "bold"),
            bg="white", fg="#6b21a8"
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        list_frame = tk.Frame(list_container, bg="white")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        lst = tk.Listbox(
            list_frame,
            font=("Segoe UI", 10),
            bg="#f3f4f6", fg="#1f2937",
            selectbackground="#ddd6fe",
            selectforeground="#1f2937",
            relief="flat", bd=0
        )
        lst.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=lst.yview)
        lst.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def refresh():
            lst.delete(0, "end")
            for emp in list_team_employees(self.current_user["id"]):
                lst.insert("end", f"{emp['id']}  —  {emp['username']}")
        refresh()
