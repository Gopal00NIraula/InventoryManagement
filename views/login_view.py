# views/login_view.py

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.login_controller import login

class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Inventory System")
        self.geometry("400x300")
        self.configure(bg="#f2f2f2")
        self.resizable(False, False)

        self.authenticated_user = False
        self.user_role = None

        ttk.Label(self, text="User Login", font=("Segoe UI", 16, "bold")).pack(pady=20)

        # Username
        ttk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        # Password
        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self, text="Login", command=self.handle_login).pack(pady=20)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        success, role = login(username, password)
        if success:
            self.authenticated_user = True
            self.user_role = role
            messagebox.showinfo("Login Success", f"Welcome {username} ({role})")
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

if __name__ == "__main__":
    app = LoginView()
    app.mainloop()

