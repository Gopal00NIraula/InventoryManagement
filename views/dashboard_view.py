import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk


class DashboardView(tk.Tk):
    def __init__(self, user_role=None):
        super().__init__()
        self.title("Inventory Dashboard")
        self.geometry("1100x700")
        self.configure(bg="#F9FAFB")
        self.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Theme colors
        self.primary = "#7C3AED"
        self.card_bg = "#FFFFFF"
        self.header_color = "#6D28D9"
        self.text_color = "#111827"

        self.create_header()
        self.create_top_cards()
        self.create_search_add_section()
        self.create_table_section()

    # ----------------- HEADER -----------------
    def create_header(self):
        header_frame = tk.Frame(self, bg="#F9FAFB")
        header_frame.pack(fill="x", pady=(25, 5))

        title = tk.Label(
            header_frame,
            text="Inventory Dashboard",
            font=("Inter", 26, "bold"),
            fg=self.header_color,
            bg="#F9FAFB",
            anchor="w"
        )
        title.pack(fill="x", padx=30)

        subtitle = tk.Label(
            header_frame,
            text="Manage your stock efficiently",
            font=("Inter", 12),
            fg="#6B7280",
            bg="#F9FAFB",
            anchor="w"
        )
        subtitle.pack(fill="x", padx=30)

    # ----------------- TOP CARDS -----------------
    def create_top_cards(self):
        card_data = [
            ("📦", "Total Items", "225", "+12%"),
            ("💲", "Total Value", "$6397.75", "+8%"),
            ("⚠️", "Low Stock", "1", ""),
            ("📈", "Out of Stock", "1", "")
        ]

        cards_frame = tk.Frame(self, bg="#F9FAFB")
        cards_frame.pack(fill="x", padx=30, pady=20)

        for i, (icon, title, value, subtext) in enumerate(card_data):
            card = tk.Frame(
                cards_frame,
                bg=self.card_bg,
                width=230,
                height=100,
                highlightbackground="#E5E7EB",
                highlightthickness=1
            )
            card.grid(row=0, column=i, padx=10)
            card.grid_propagate(False)

            tk.Label(card, text=icon, font=("Inter", 24), fg=self.primary, bg=self.card_bg).pack(anchor="w", padx=15, pady=(10, 0))
            tk.Label(card, text=title, font=("Inter", 11, "bold"), fg="#6B7280", bg=self.card_bg).pack(anchor="w", padx=15)
            tk.Label(card, text=value, font=("Inter", 16, "bold"), fg="#111827", bg=self.card_bg).pack(anchor="w", padx=15)
            if subtext:
                tk.Label(card, text=subtext, font=("Inter", 10), fg="#059669", bg=self.card_bg).pack(anchor="w", padx=15)

    # ----------------- SEARCH + ADD -----------------
        # ----------------- SEARCH + ADD -----------------
    def create_search_add_section(self):
        action_frame = tk.Frame(self, bg="#F9FAFB")
        action_frame.pack(fill="x", padx=30, pady=(5, 15))

        # Search bar
        search_icon = tk.Label(action_frame, text="🔍", bg="#FFFFFF")
        search_icon.pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)

        self.search_entry = tk.Entry(
            action_frame,
            textvariable=self.search_var,
            font=("Inter", 11),
            width=45,
            bg="#FFFFFF",
            fg="#111827",
            relief="flat",
            highlightbackground="#E5E7EB",
            highlightthickness=1
        )
        self.search_entry.insert(0, "Search by name, SKU, or category...")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.pack(side="left", padx=(5, 20), ipady=6)

        # Add Item button
        add_btn = tk.Button(
            action_frame,
            text="+ Add Item",
            bg=self.primary,
            fg="#FFFFFF",
            font=("Inter", 10, "bold"),
            relief="flat",
            padx=20,
            pady=6,
            cursor="hand2",
            activebackground="#6D28D9",
            activeforeground="#FFFFFF",
            borderwidth=0,
            command=self.open_add_item_window
        )
        add_btn.pack(side="right")


    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search by name, SKU, or category...":
            self.search_entry.delete(0, tk.END)

    # ----------------- TABLE -----------------
    def create_table_section(self):
        table_frame = tk.Frame(self, bg="#F9FAFB")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        title_label = tk.Label(
            table_frame,
            text="📦 Inventory Items",
            font=("Inter", 14, "bold"),
            fg=self.text_color,
            bg="#F9FAFB"
        )
        title_label.pack(anchor="w", pady=(0, 10))

        # --- Create a frame to hold the table and scrollbar ---
        tree_container = tk.Frame(table_frame, bg="#F9FAFB")
        tree_container.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container)
        scrollbar.pack(side="right", fill="y")

        # Treeview setup
        columns = ("Product", "SKU", "Category", "Quantity", "Price", "Status", "Actions")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=12,
            yscrollcommand=scrollbar.set
        )
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Define columns
        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=130, anchor="w")

        # Load data
        from controllers.inventory_controller import fetch_items
        items = fetch_items()
        for item in items:
            _, name, sku, category, quantity, price = item
            status = (
                "Out of Stock" if quantity == 0 else
                "Low Stock" if quantity < 5 else
                "In Stock"
            )
            self.tree.insert("", "end", values=(name, sku, category, quantity, f"${price}", status, ""))

        # --- Delete Button Section ---
        button_frame = tk.Frame(table_frame, bg="#F9FAFB")
        button_frame.pack(fill="x", pady=(15, 10), anchor="e")

        delete_btn = tk.Button(
            button_frame,
            text="🗑️  Delete Selected",
            bg="#DC2626",
            fg="#FFFFFF",
            font=("Inter", 10, "bold"),
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2",
            activebackground="#B91C1C",
            activeforeground="#FFFFFF",
            borderwidth=0,
            command=self.delete_selected_item
        )
        delete_btn.pack(anchor="e", padx=10)

        # Hover effect
        def on_enter(e):
            delete_btn.config(bg="#B91C1C")

        def on_leave(e):
            delete_btn.config(bg="#DC2626")

        delete_btn.bind("<Enter>", on_enter)
        delete_btn.bind("<Leave>", on_leave)

        # Bind double-click for edit
        self.tree.bind("<Double-1>", self.on_double_click)

        # Status colors
        self.tree.tag_configure("In Stock", foreground="#16A34A")
        self.tree.tag_configure("Low Stock", foreground="#F59E0B")
        self.tree.tag_configure("Out of Stock", foreground="#DC2626")

    # ----------------- ADD ITEM POPUP -----------------
    def open_add_item_window(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Item")
        popup.geometry("400x400")
        popup.configure(bg="#FFFFFF")
        popup.resizable(False, False)

        fields = ["Product Name", "SKU", "Category", "Quantity", "Price"]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(popup, text=field, font=("Inter", 10), bg="#FFFFFF", fg="#111827").pack(pady=(15 if i == 0 else 5, 2))
            entry = tk.Entry(popup, font=("Inter", 10), relief="solid", bd=1, width=30)
            entry.pack(pady=2)
            entries[field] = entry

        def save_item():
            from controllers.inventory_controller import create_item, fetch_items
            data = {
                "name": entries["Product Name"].get(),
                "sku": entries["SKU"].get(),
                "category": entries["Category"].get(),
                "quantity": entries["Quantity"].get(),
                "price": entries["Price"].get()
            }
            create_item(data)
            popup.destroy()
            self.refresh_table()

        tk.Button(
            popup,
            text="Save Item",
            bg=self.primary,
            fg="#FFFFFF",
            font=("Inter", 10, "bold"),
            relief="flat",
            padx=20,
            pady=6,
            command=save_item
        ).pack(pady=25)

    # ----------------- REFRESH TABLE -----------------
    def refresh_table(self):
        from controllers.inventory_controller import fetch_items
        for row in self.tree.get_children():
            self.tree.delete(row)
        items = fetch_items()
        for item in items:
            _, name, sku, category, quantity, price = item
            status = (
                "Out of Stock" if quantity == 0 else
                "Low Stock" if quantity < 5 else
                "In Stock"
            )
            self.tree.insert("", "end", values=(name, sku, category, quantity, f"${price}", status, ""))

    # ----------------- DOUBLE CLICK TO EDIT -----------------
    def on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], "values")
        product_name, _, category, quantity, price, _, _ = item_values
        price = price.replace("$", "")
        self.open_edit_item_window(selected[0], product_name, category, quantity, price)

    def open_edit_item_window(self, item_id, name, category, quantity, price):
        popup = tk.Toplevel(self)
        popup.title("Edit Item")
        popup.geometry("400x400")
        popup.configure(bg="#FFFFFF")

        fields = ["Product Name", "Category", "Quantity", "Price"]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(popup, text=field, font=("Inter", 10), bg="#FFFFFF", fg="#111827").pack(pady=(15 if i == 0 else 5, 2))
            entry = tk.Entry(popup, font=("Inter", 10), relief="solid", bd=1, width=30)
            entry.pack(pady=2)
            if field == "Product Name":
                entry.insert(0, name)
            elif field == "Category":
                entry.insert(0, category)
            elif field == "Quantity":
                entry.insert(0, quantity)
            elif field == "Price":
                entry.insert(0, price)
            entries[field] = entry

        def update_item_in_db():
            from controllers.inventory_controller import edit_item
            data = {
                "name": entries["Product Name"].get(),
                "category": entries["Category"].get(),
                "quantity": entries["Quantity"].get(),
                "price": entries["Price"].get()
            }
            # Find actual DB id based on selected name
            db_id = self.get_item_db_id(name)
            if db_id:
                edit_item(db_id, data)
                popup.destroy()
                self.refresh_table()

        tk.Button(
            popup,
            text="Save Changes",
            bg=self.primary,
            fg="#FFFFFF",
            font=("Inter", 10, "bold"),
            relief="flat",
            padx=20,
            pady=6,
            command=update_item_in_db
        ).pack(pady=25)

    # ----------------- DELETE ITEM -----------------
    def get_item_db_id(self, name):
        # Find the database ID by matching item_name
        from database.db_connection import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM inventory WHERE item_name = ?", (name,))
        result = cur.fetchone()
        conn.close()
        return result[0] if result else None

    def delete_selected_item(self):
        from tkinter import messagebox
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        item_values = self.tree.item(selected[0], "values")
        product_name = item_values[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?")
        if confirm:
            from controllers.inventory_controller import remove_item
            db_id = self.get_item_db_id(product_name)
            if db_id:
                remove_item(db_id)
                self.refresh_table()

    # ----------------- SEARCH FILTER -----------------
    def on_search_change(self, *args):
        from controllers.inventory_controller import find_items, fetch_items
        query = self.search_var.get().strip()
        if query == "" or query == "Search by name, SKU, or category...":
            results = fetch_items()
        else:
            results = find_items(query)

        # Clear and repopulate table
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in results:
            _, name, category, quantity, price = item
            status = (
                "Out of Stock" if quantity == 0 else
                "Low Stock" if quantity < 5 else
                "In Stock"
            )
            self.tree.insert("", "end", values=(name, "", category, quantity, f"${price}", status, ""))



if __name__ == "__main__":
    app = DashboardView()
    app.mainloop()
