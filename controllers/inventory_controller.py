# controllers/inventory_controller.py
from models.inventory_model import get_items, add_item, update_item, delete_item, search_items

def _require_manager(current_user: dict):
    if not current_user or current_user.get("role") != "manager":
        raise PermissionError("Managers only.")

def list_items():
    return get_items()

def find_items(query: str):
    return search_items(query)

def create_item(current_user: dict, payload: dict):
    _require_manager(current_user)
    return add_item(payload)

def edit_item(current_user: dict, item_id: int, payload: dict):
    _require_manager(current_user)
    return update_item(item_id, payload)

def remove_item(current_user: dict, item_id: int):
    _require_manager(current_user)
    return delete_item(item_id)
