# controllers/inventory_controller.py
from models.inventory_model import add_item, get_all_items

def create_item(data):
    name = data.get("name")
    sku = data.get("sku")
    category = data.get("category")
    quantity = int(data.get("quantity", 0))
    price = float(data.get("price", 0.0))
    add_item(name, sku, category, quantity, price)
    print(f"[ITEM ADDED] {name}")

def fetch_items():
    return get_all_items()

from models.inventory_model import update_item, delete_item

def edit_item(item_id, data):
    name = data.get("name")
    category = data.get("category")
    quantity = int(data.get("quantity", 0))
    price = float(data.get("price", 0.0))
    update_item(item_id, name, category, quantity, price)
    print(f"[ITEM UPDATED] {name}")

def remove_item(item_id):
    delete_item(item_id)
    print(f"[ITEM DELETED] ID={item_id}")

from models.inventory_model import search_items

def find_items(query):
    return search_items(query)

