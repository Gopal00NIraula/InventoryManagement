"""
Reports Controller for handling report generation with permissions
"""
from models.reports_model import (
    get_inventory_summary,
    get_sales_report,
    get_purchase_report,
    get_stock_movement_report,
    get_low_stock_report,
    get_profit_analysis
)
from utils.permissions import require_permission


def generate_inventory_summary(user):
    """
    Generate inventory summary report
    Requires view_inventory permission
    """
    require_permission(user, "view_inventory")
    return get_inventory_summary()


def generate_sales_report(user, start_date=None, end_date=None):
    """
    Generate sales report for date range
    Requires view_inventory permission
    """
    require_permission(user, "view_inventory")
    return get_sales_report(start_date, end_date)


def generate_purchase_report(user, start_date=None, end_date=None):
    """
    Generate purchase report for date range
    Requires view_inventory permission
    """
    require_permission(user, "view_inventory")
    return get_purchase_report(start_date, end_date)


def generate_stock_movement_report(user, start_date=None, end_date=None):
    """
    Generate stock movement report
    Requires view_inventory permission
    """
    require_permission(user, "view_inventory")
    return get_stock_movement_report(start_date, end_date)


def generate_low_stock_report(user):
    """
    Generate low stock report
    Requires view_inventory permission
    """
    require_permission(user, "view_inventory")
    return get_low_stock_report()


def generate_profit_analysis(user, start_date=None, end_date=None):
    """
    Generate profit/loss analysis
    Requires view_inventory permission (ADMIN/STAFF only for financial data)
    """
    require_permission(user, "view_inventory")
    return get_profit_analysis(start_date, end_date)
