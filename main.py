# main.py
import tkinter as tk
from views.login_view import LoginView
from views.dashboard_view import DashboardView


class InventoryApp:
    """Main application flow controller."""

    def __init__(self):
        self.user_role = None
        self.run_app()

    def run_app(self):
        # Step 1: Show Login Window
        login_window = LoginView()
        login_window.mainloop()

        # After login window closes, check login result
        if login_window.authenticated_user:
            self.user_role = login_window.user_role
            self.show_dashboard()

    def show_dashboard(self):
        dashboard = DashboardView(self.user_role)
        dashboard.mainloop()


if __name__ == "__main__":
    InventoryApp()
