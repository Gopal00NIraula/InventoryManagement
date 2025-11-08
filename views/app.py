# views/app.py
import tkinter as tk
from tkinter import ttk
from views.auth_view import AuthPage
from views.dashboard_view import DashboardPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management")
        try:
            self.state("zoomed")  # windowed-fullscreen
        except Exception:
            self.attributes("-zoomed", True)
        self.minsize(960, 600)

        # Root uses pack; pages use grid INSIDE this container
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self._current_page = None
        self.show_auth()

    def show_auth(self):
        if self._current_page:
            self._current_page.destroy()
        # IMPORTANT: parent is self.container (not self)
        self._current_page = AuthPage(self.container, on_authenticated=self.show_dashboard)
        self._current_page.grid(row=0, column=0, sticky="nsew")

    def show_dashboard(self, current_user: dict):
        if self._current_page:
            self._current_page.destroy()
        # IMPORTANT: parent is self.container (not self)
        self._current_page = DashboardPage(self.container, current_user=current_user)
        self._current_page.grid(row=0, column=0, sticky="nsew")

    def run(self):
        self.mainloop()
