from database.db_setup import setup_database
from views.app import App

def InventoryApp():
    setup_database()
    app = App()
    app.run()

if __name__ == "__main__":
    InventoryApp()
