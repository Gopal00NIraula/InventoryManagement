# views/auth_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.login_controller import login, create_admin_account

class AuthPage(tk.Frame):
    """
    Modern centered login/signup page with purple theme
    """
    def __init__(self, master, on_authenticated):
        super().__init__(master, bg="#f5f3ff")
        self.on_authenticated = on_authenticated
        self.showing_login = True
        
        # Center the form
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main container - centered
        container = tk.Frame(self, bg="#f5f3ff")
        container.grid(row=0, column=0)
        
        # Logo/Title
        title = tk.Label(container, text="Inventory Management", 
                        font=("Segoe UI", 28, "bold"), 
                        bg="#f5f3ff", fg="#6b21a8")
        title.pack(pady=(40, 30))
        
        # Card frame with rounded appearance
        self.card = tk.Frame(container, bg="white", bd=0, relief="flat")
        self.card.pack(padx=40, pady=20)
        
        # Add shadow effect with borders
        shadow_frame = tk.Frame(self.card, bg="#e9d5ff", bd=0)
        shadow_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        self.content_frame = tk.Frame(shadow_frame, bg="white", bd=0)
        self.content_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Show login form initially
        self._show_login_form()
    
    def _show_login_form(self):
        """Display the login form"""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.showing_login = True
        
        # Form container
        form = tk.Frame(self.content_frame, bg="white")
        form.pack(padx=60, pady=40)
        
        # Username field
        self.ent_user = tk.Entry(form, font=("Segoe UI", 14), 
                                 bg="#ddd6fe", fg="#1f2937",
                                 relief="flat", bd=0,
                                 insertbackground="#6b21a8")
        self.ent_user.pack(pady=(0, 20), ipady=12, ipadx=15, fill="x")
        self.ent_user.insert(0, "Username")
        self.ent_user.bind("<FocusIn>", lambda e: self._clear_placeholder(self.ent_user, "Username"))
        self.ent_user.bind("<FocusOut>", lambda e: self._restore_placeholder(self.ent_user, "Username"))
        
        # Password field
        self.ent_pass = tk.Entry(form, font=("Segoe UI", 14), 
                                bg="#ddd6fe", fg="#1f2937",
                                relief="flat", bd=0, show="*",
                                insertbackground="#6b21a8")
        self.ent_pass.pack(pady=(0, 15), ipady=12, ipadx=15, fill="x")
        self.ent_pass.insert(0, "Password")
        self.ent_pass.bind("<FocusIn>", lambda e: self._clear_placeholder(self.ent_pass, "Password", True))
        self.ent_pass.bind("<FocusOut>", lambda e: self._restore_placeholder(self.ent_pass, "Password", True))
        
        # Toggle link
        toggle_link = tk.Label(form, text="Create account?", 
                              font=("Segoe UI", 11), 
                              bg="white", fg="#6b21a8",
                              cursor="hand2")
        toggle_link.pack(pady=(0, 20))
        toggle_link.bind("<Button-1>", lambda e: self._show_create_form())
        
        # Login button
        login_btn = tk.Button(form, text="Login", 
                            font=("Segoe UI", 14, "bold"),
                            bg="#7c3aed", fg="white",
                            activebackground="#6d28d9",
                            activeforeground="white",
                            relief="flat", bd=0,
                            cursor="hand2",
                            command=self._attempt_login)
        login_btn.pack(ipady=12, ipadx=80, fill="x")
        
        # Bind Enter key
        self.ent_user.bind("<Return>", lambda e: self._attempt_login())
        self.ent_pass.bind("<Return>", lambda e: self._attempt_login())
    
    def _show_create_form(self):
        """Display the create account form"""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.showing_login = False
        
        # Form container
        form = tk.Frame(self.content_frame, bg="white")
        form.pack(padx=60, pady=40)
        
        # Form title
        form_title = tk.Label(form, text="Create Manager Account", 
                            font=("Segoe UI", 18, "bold"),
                            bg="white", fg="#6b21a8")
        form_title.pack(pady=(0, 20))
        
        # Helper function to create entry fields
        def create_entry(placeholder, show=None):
            entry = tk.Entry(form, font=("Segoe UI", 12), 
                           bg="#ddd6fe", fg="#1f2937",
                           relief="flat", bd=0,
                           insertbackground="#6b21a8")
            if show:
                entry.config(show=show)
            entry.pack(pady=8, ipady=10, ipadx=12, fill="x")
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e: self._clear_placeholder(entry, placeholder, show is not None))
            entry.bind("<FocusOut>", lambda e: self._restore_placeholder(entry, placeholder, show is not None))
            return entry
        
        self.ent_first = create_entry("First Name")
        self.ent_last = create_entry("Last Name")
        self.ent_phone = create_entry("Phone")
        self.ent_email = create_entry("Email")
        self.ent_biz = create_entry("Business Name")
        self.ent_pass1 = create_entry("Password", show="*")
        self.ent_pass2 = create_entry("Confirm Password", show="*")
        
        # Toggle link
        toggle_link = tk.Label(form, text="Already have an account? Login", 
                              font=("Segoe UI", 11), 
                              bg="white", fg="#6b21a8",
                              cursor="hand2")
        toggle_link.pack(pady=(15, 20))
        toggle_link.bind("<Button-1>", lambda e: self._show_login_form())
        
        # Create button
        create_btn = tk.Button(form, text="Create Account", 
                             font=("Segoe UI", 14, "bold"),
                             bg="#7c3aed", fg="white",
                             activebackground="#6d28d9",
                             activeforeground="white",
                             relief="flat", bd=0,
                             cursor="hand2",
                             command=self._create_manager)
        create_btn.pack(ipady=12, ipadx=60, fill="x")
    
    def _clear_placeholder(self, entry, placeholder, is_password=False):
        """Clear placeholder text on focus"""
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg="#1f2937")
            if is_password:
                entry.config(show="*")
    
    def _restore_placeholder(self, entry, placeholder, is_password=False):
        """Restore placeholder if field is empty"""
        if not entry.get():
            if is_password:
                entry.config(show="")
            entry.insert(0, placeholder)
            entry.config(fg="#9ca3af")
    
    # -------- Actions --------
    def _attempt_login(self):
        identifier = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        
        # Check for placeholders
        if identifier == "Username" or not identifier:
            messagebox.showerror("Login failed", "Please enter your username or email.")
            return
        if pwd == "Password" or not pwd:
            messagebox.showerror("Login failed", "Please enter your password.")
            return
            
        ok, current_user = login(identifier, pwd)
        if not ok:
            messagebox.showerror("Login failed", "Invalid credentials or account not found.")
            return
        self.on_authenticated(current_user)

    def _strong(self, p: str) -> bool:
        return len(p) >= 8 and any(c.isalpha() for c in p) and any(c.isdigit() for c in p)

    def _create_manager(self):
        # Get values and check for placeholders
        first = self.ent_first.get().strip()
        last = self.ent_last.get().strip()
        phone = self.ent_phone.get().strip()
        email = self.ent_email.get().strip()
        biz = self.ent_biz.get().strip()
        p1 = self.ent_pass1.get()
        p2 = self.ent_pass2.get()
        
        # Validate not placeholders
        if first == "First Name" or not first:
            messagebox.showwarning("Validation", "Please enter your first name.")
            return
        if last == "Last Name" or not last:
            messagebox.showwarning("Validation", "Please enter your last name.")
            return
        if email == "Email" or not email:
            messagebox.showwarning("Validation", "Please enter your email.")
            return
        if p1 == "Password" or not p1:
            messagebox.showwarning("Validation", "Please enter a password.")
            return
        if p2 == "Confirm Password" or not p2:
            messagebox.showwarning("Validation", "Please confirm your password.")
            return
            
        if p1 != p2:
            messagebox.showwarning("Mismatch", "Passwords do not match.")
            return
        if not self._strong(p1):
            messagebox.showwarning("Weak password", "Use ≥8 characters with letters and numbers.")
            return

        form = {
            "first_name": first,
            "last_name": last,
            "phone": phone if phone != "Phone" else "",
            "email": email,
            "business_name": biz if biz != "Business Name" else "",
            "password": p1
        }
        try:
            res = create_admin_account(form)
            uname = res["username"]
            messagebox.showinfo(
                "Account created",
                f"Manager account created.\nYour username is: {uname}\n\nYou can now log in."
            )
            # Switch back to login form
            self._show_login_form()
            # Pre-fill login with the new username
            self.ent_user.delete(0, "end")
            self.ent_user.insert(0, uname)
            self.ent_user.config(fg="#1f2937")
        except Exception as e:
            messagebox.showerror("Error", str(e))

