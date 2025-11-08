# views/auth_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.login_controller import login, create_manager_account

class AuthPage(ttk.Frame):
    """
    Single master page containing:
      - Login panel (left)
      - Create Manager Account panel (right)
    """
    def __init__(self, master, on_authenticated):
        super().__init__(master, padding=16)
        self.on_authenticated = on_authenticated

        # 2-column responsive grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        title = ttk.Label(self, text="Inventory Management", font=("Segoe UI", 22, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Login panel
        login_card = ttk.LabelFrame(self, text="Sign in")
        login_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=8)
        for r in range(6):
            login_card.rowconfigure(r, weight=0)
        login_card.columnconfigure(1, weight=1)

        ttk.Label(login_card, text="Username or Email").grid(row=0, column=0, sticky="w", padx=10, pady=(12, 6))
        self.ent_user = ttk.Entry(login_card, width=36)
        self.ent_user.grid(row=0, column=1, sticky="ew", padx=10, pady=(12, 6))

        ttk.Label(login_card, text="Password").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.ent_pass = ttk.Entry(login_card, width=36, show="*")
        self.ent_pass.grid(row=1, column=1, sticky="ew", padx=10, pady=6)

        btn_signin = ttk.Button(login_card, text="Sign in", command=self._attempt_login)
        btn_signin.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(6, 12))

        # Create Manager panel
        create_card = ttk.LabelFrame(self, text="Create Manager Account")
        create_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=8)
        for r in range(10):
            create_card.rowconfigure(r, weight=0)
        create_card.columnconfigure(1, weight=1)

        def row(r, label, show=None):
            ttk.Label(create_card, text=label).grid(row=r, column=0, sticky="w", padx=10, pady=4)
            e = ttk.Entry(create_card, width=36, show=show)
            e.grid(row=r, column=1, sticky="ew", padx=10, pady=4)
            return e

        self.ent_first = row(0, "First Name")
        self.ent_last  = row(1, "Last Name")
        self.ent_phone = row(2, "Phone")
        self.ent_email = row(3, "Email")
        self.ent_biz   = row(4, "Business Name")
        self.ent_pass1 = row(5, "Password", show="*")
        self.ent_pass2 = row(6, "Confirm Password", show="*")

        btns = ttk.Frame(create_card)
        btns.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=(6, 12))
        ttk.Button(btns, text="Create Account", command=self._create_manager).pack(side="left")
        ttk.Button(btns, text="Clear", command=self._clear_create_form).pack(side="right")

        # convenience: Enter key logs in
        self.bind_all("<Return>", lambda e: self._attempt_login())

    # -------- Actions --------
    def _attempt_login(self):
        identifier = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        ok, current_user = login(identifier, pwd)
        if not ok:
            messagebox.showerror("Login failed", "Invalid credentials or account not found.")
            return
        self.on_authenticated(current_user)

    def _strong(self, p: str) -> bool:
        return len(p) >= 8 and any(c.isalpha() for c in p) and any(c.isdigit() for c in p)

    def _create_manager(self):
        p1, p2 = self.ent_pass1.get(), self.ent_pass2.get()
        if p1 != p2:
            messagebox.showwarning("Mismatch", "Passwords do not match.")
            return
        if not self._strong(p1):
            messagebox.showwarning("Weak password", "Use ≥8 characters with letters and numbers.")
            return

        form = {
            "first_name": self.ent_first.get().strip(),
            "last_name":  self.ent_last.get().strip(),
            "phone":      self.ent_phone.get().strip(),
            "email":      self.ent_email.get().strip(),
            "business_name": self.ent_biz.get().strip(),
            "password":   p1
        }
        try:
            res = create_manager_account(form)
            uname = res["username"]
            messagebox.showinfo(
                "Account created",
                f"Manager account created.\nYour username is: {uname}"
            )
            # Pre-fill login with the new username so they can sign in immediately
            self.ent_user.delete(0, "end"); self.ent_user.insert(0, uname)
            self.ent_pass.delete(0, "end"); self.ent_pass.insert(0, p1)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear_create_form(self):
        for w in (self.ent_first, self.ent_last, self.ent_phone, self.ent_email, self.ent_biz, self.ent_pass1, self.ent_pass2):
            w.delete(0, "end")
