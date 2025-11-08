# views/dashboard_view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from controllers.inventory_controller import create_item, edit_item, remove_item, find_items
from models.user_model import create_user, delete_user, list_team_employees  # delete_user used by manager panel

class DashboardPage(ttk.Frame):
    def __init__(self, master, current_user: dict):
        super().__init__(master, padding=12)
        self.current_user = current_user

        # Header
        hdr = ttk.Frame(self)
        hdr.pack(fill="x")
        ttk.Label(
            hdr,
            text=f"Inventory Dashboard — {current_user['username']} [{current_user['role']}]",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        # Right-side header actions
        actions = ttk.Frame(hdr)
        actions.pack(side="right")
        self.btn_user_mgmt = ttk.Button(actions, text="User Management", command=self._open_user_mgmt)
        self.btn_user_mgmt.pack(side="right", padx=(0,6))
        ttk.Button(actions, text="Log out", command=self._logout).pack(side="right")

        # Toolbar
        bar = ttk.Frame(self); bar.pack(fill="x", pady=(8, 4))
        self.btn_add = ttk.Button(bar, text="Add Item", command=self._on_add_item)
        self.btn_edit = ttk.Button(bar, text="Edit Item", command=self._on_edit_item)
        self.btn_delete = ttk.Button(bar, text="Delete Item", command=self._on_delete_item)
        self.btn_add.pack(side="left", padx=4)
        self.btn_edit.pack(side="left", padx=4)
        self.btn_delete.pack(side="left", padx=4)

        # Search + Table
        body = ttk.Frame(self); body.pack(fill="both", expand=True)
        top = ttk.Frame(body); top.pack(fill="x")
        ttk.Label(top, text="Search:").pack(side="left")
        self.ent_q = ttk.Entry(top, width=40); self.ent_q.pack(side="left", padx=6)
        ttk.Button(top, text="Go", command=self._on_search).pack(side="left")
        ttk.Button(top, text="Refresh", command=self._on_search).pack(side="left", padx=(6,0))

        cols = ("id","name","sku","quantity","location")
        self.table = ttk.Treeview(body, columns=cols, show="headings")
        for c, h, w in (("id","ID",80), ("name","Name",220), ("sku","SKU",150), ("quantity","Qty",100), ("location","Location",150)):
            self.table.heading(c, text=h)
            self.table.column(c, width=w, anchor="w")
        self.table.pack(fill="both", expand=True, pady=8)

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
                b.configure(state="disabled")

    # ---- inventory handlers ----
    def _on_search(self):
        q = self.ent_q.get().strip()
        rows = find_items(q)
        for i in self.table.get_children():
            self.table.delete(i)
        for r in rows:
            self.table.insert("", "end", values=(r["id"], r["name"], r["sku"], r["quantity"], r.get("location","")))

    def _selected_item_id(self):
        sel = self.table.focus()
        if not sel:
            return None
        vals = self.table.item(sel)["values"]
        return int(vals[0]) if vals else None

    def _on_add_item(self):
        try:
            name = simpledialog.askstring("Add Item", "Name:", parent=self)
            if not name: return
            sku  = simpledialog.askstring("Add Item", "SKU:", parent=self)
            if not sku: return
            qty  = int(simpledialog.askstring("Add Item", "Quantity:", parent=self) or "0")
            loc  = simpledialog.askstring("Add Item", "Location:", parent=self)
            create_item(self.current_user, {"name": name, "sku": sku, "quantity": qty, "location": loc})
            messagebox.showinfo("Success", "Item created.")
            self._on_search()
        except PermissionError as e:
            messagebox.showerror("Forbidden", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_edit_item(self):
        try:
            vid = self._selected_item_id()
            if vid is None: return
            qty = simpledialog.askstring("Edit Item", "New Quantity:", parent=self)
            if qty is None: return
            edit_item(self.current_user, vid, {"quantity": int(qty)})
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
        win = tk.Toplevel(self); win.title("User Management"); win.resizable(False, False)

        frm = ttk.Frame(win, padding=10); frm.pack(fill="x")
        def row(r, label, show=None):
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="w", pady=3)
            e = ttk.Entry(frm, width=32, show=show); e.grid(row=r, column=1, pady=3)
            return e
        ent_first = row(0, "First Name")
        ent_last  = row(1, "Last Name")
        ent_email = row(2, "Email")
        ent_phone = row(3, "Phone")
        ent_pass  = row(4, "Temp Password", show="*")
        ent_pass2 = row(5, "Confirm Password", show="*")

        def strong(p): return len(p) >= 8 and any(c.isalpha() for c in p) and any(c.isdigit() for c in p)

        def do_create():
            p1, p2 = ent_pass.get(), ent_pass2.get()
            if p1 != p2:
                messagebox.showwarning("Mismatch", "Passwords do not match."); return
            if not strong(p1):
                messagebox.showwarning("Weak", "Use ≥8 chars with letters and numbers."); return
            try:
                res = create_user(
                    password=p1,
                    role="employee",
                    manager_id=self.current_user["id"],
                    first_name=ent_first.get().strip(),
                    last_name=ent_last.get().strip(),
                    email=ent_email.get().strip() or None,
                    phone=ent_phone.get().strip() or None,
                    business_name=None,
                    username=None,  # auto-generate
                )
                messagebox.showinfo("OK", f"Employee created.\nAssigned username: {res['username']}")
                refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(frm, text="Create Employee", command=do_create)\
            .grid(row=6, column=0, columnspan=2, pady=6, sticky="ew")

        lst = tk.Listbox(win, width=40, height=10); lst.pack(fill="both", expand=True, padx=8, pady=8)

        def refresh():
            lst.delete(0, "end")
            for emp in list_team_employees(self.current_user["id"]):
                lst.insert("end", f"{emp['id']}  —  {emp['username']}")
        refresh()
