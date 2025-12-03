"""
Email Notification System
Handles sending email notifications for inventory events
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os


EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL", ""),
    "sender_password": os.getenv("SENDER_PASSWORD", ""),
    "use_tls": os.getenv("USE_TLS", "True").lower() == "true",
    "enabled": os.getenv("EMAIL_ENABLED", "False").lower() == "true"
}


def is_email_configured():
    """Check if email is properly configured"""
    return (EMAIL_CONFIG["enabled"] and 
            EMAIL_CONFIG["sender_email"] and 
            EMAIL_CONFIG["sender_password"])


def send_email(to_email, subject, body_html, body_text=None):
    """
    Send an email notification
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body_html (str): HTML body content
        body_text (str): Plain text body (optional fallback)
        
    Returns:
        dict: {"success": bool, "message": str}
    """
    if not is_email_configured():
        return {"success": False, "message": "Email notifications are not configured"}
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_CONFIG["sender_email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        
        # Attach both plain text and HTML versions
        if body_text:
            part1 = MIMEText(body_text, "plain")
            msg.attach(part1)
        
        part2 = MIMEText(body_html, "html")
        msg.attach(part2)
        
        # Send email
        if EMAIL_CONFIG["use_tls"]:
            server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        server.send_message(msg)
        server.quit()
        
        return {"success": True, "message": "Email sent successfully"}
        
    except Exception as e:
        print(f"Email error: {e}")
        return {"success": False, "message": f"Failed to send email: {str(e)}"}


def send_low_stock_alert(user_email, items):
    """
    Send low stock alert email
    
    Args:
        user_email (str): Recipient email
        items (list): List of low stock items
        
    Returns:
        dict: {"success": bool, "message": str}
    """
    if not items:
        return {"success": False, "message": "No items to notify"}
    
    subject = f"🔴 Low Stock Alert - {len(items)} Items Need Attention"
    
    # Build HTML content
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #dc2626; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .item {{ background-color: #fee2e2; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .item-name {{ font-weight: bold; color: #991b1b; }}
            .footer {{ padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>⚠️ Low Stock Alert</h2>
        </div>
        <div class="content">
            <p>The following items are running low and need to be restocked:</p>
    """
    
    for item in items:
        status = ""
        if item['quantity'] == 0:
            status = "🔴 OUT OF STOCK"
        elif item['quantity'] <= item.get('min_stock_level', 10):
            status = "🟡 LOW STOCK"
        else:
            status = "⚠️ REORDER SOON"
        
        html_body += f"""
            <div class="item">
                <div class="item-name">{item['name']} ({item['sku']})</div>
                <div>Status: {status}</div>
                <div>Current Quantity: {item['quantity']}</div>
                <div>Min Stock Level: {item.get('min_stock_level', 10)}</div>
                <div>Price: ${item['price']:.2f}</div>
            </div>
        """
    
    html_body += """
        </div>
        <div class="footer">
            <p>This is an automated notification from your Inventory Management System.</p>
            <p>Please log in to the system to take action.</p>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_body = f"Low Stock Alert - {len(items)} Items\n\n"
    for item in items:
        text_body += f"- {item['name']} ({item['sku']}): {item['quantity']} units\n"
    
    return send_email(user_email, subject, html_body, text_body)


def send_order_completion_notification(user_email, order_type, order_id, items_count):
    """
    Send order completion notification
    
    Args:
        user_email (str): Recipient email
        order_type (str): "purchase" or "sales"
        order_id (int): Order ID
        items_count (int): Number of items in order
        
    Returns:
        dict: {"success": bool, "message": str}
    """
    order_label = "Purchase Order" if order_type == "purchase" else "Sales Order"
    subject = f"✅ {order_label} #{order_id} Completed"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #059669; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .info {{ background-color: #d1fae5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .footer {{ padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>✅ Order Completed Successfully</h2>
        </div>
        <div class="content">
            <div class="info">
                <p><strong>Order Type:</strong> {order_label}</p>
                <p><strong>Order ID:</strong> #{order_id}</p>
                <p><strong>Items:</strong> {items_count}</p>
                <p><strong>Completed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <p>The order has been processed and inventory has been updated accordingly.</p>
        </div>
        <div class="footer">
            <p>This is an automated notification from your Inventory Management System.</p>
        </div>
    </body>
    </html>
    """
    
    text_body = f"{order_label} #{order_id} completed with {items_count} items."
    
    return send_email(user_email, subject, html_body, text_body)


def send_welcome_email(user_email, username, temporary_password=None):
    """
    Send welcome email to new user
    
    Args:
        user_email (str): New user's email
        username (str): Username
        temporary_password (str): Temporary password (optional)
        
    Returns:
        dict: {"success": bool, "message": str}
    """
    subject = "Welcome to Inventory Management System"
    
    password_info = ""
    if temporary_password:
        password_info = f"""
            <div style="background-color: #fef3c7; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <p><strong>Temporary Password:</strong> {temporary_password}</p>
                <p style="color: #92400e;">Please change your password after first login.</p>
            </div>
        """
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #7c3aed; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .footer {{ padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Welcome to Inventory Management System!</h2>
        </div>
        <div class="content">
            <p>Hello {username},</p>
            <p>Your account has been created successfully.</p>
            <p><strong>Username:</strong> {username}</p>
            {password_info}
            <p>You can now log in and start managing your inventory.</p>
        </div>
        <div class="footer">
            <p>If you have any questions, please contact your system administrator.</p>
        </div>
    </body>
    </html>
    """
    
    text_body = f"Welcome {username}! Your account has been created."
    
    return send_email(user_email, subject, html_body, text_body)


def send_stock_alert_summary(user_email, alert_counts):
    """
    Send daily stock alert summary
    
    Args:
        user_email (str): Recipient email
        alert_counts (dict): {"out_of_stock": int, "low_stock": int, "reorder": int}
        
    Returns:
        dict: {"success": bool, "message": str}
    """
    total = sum(alert_counts.values())
    if total == 0:
        return {"success": False, "message": "No alerts to send"}
    
    subject = f"📊 Daily Stock Alert Summary - {total} Total Alerts"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #6b21a8; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .summary {{ background-color: #f5f3ff; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .alert-stat {{ margin: 10px 0; padding: 10px; border-left: 4px solid #7c3aed; }}
            .footer {{ padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>📊 Daily Stock Alert Summary</h2>
        </div>
        <div class="content">
            <p>Here's your daily inventory alert summary:</p>
            <div class="summary">
                <div class="alert-stat">
                    <strong>🔴 Out of Stock:</strong> {alert_counts.get('out_of_stock', 0)} items
                </div>
                <div class="alert-stat">
                    <strong>🟡 Low Stock:</strong> {alert_counts.get('low_stock', 0)} items
                </div>
                <div class="alert-stat">
                    <strong>⚠️ Reorder Needed:</strong> {alert_counts.get('reorder', 0)} items
                </div>
            </div>
            <p><strong>Total Items Needing Attention: {total}</strong></p>
            <p>Please log in to the system to review and take action.</p>
        </div>
        <div class="footer">
            <p>This is an automated daily summary from your Inventory Management System.</p>
        </div>
    </body>
    </html>
    """
    
    text_body = f"Daily Summary: {alert_counts.get('out_of_stock', 0)} out of stock, {alert_counts.get('low_stock', 0)} low stock, {alert_counts.get('reorder', 0)} need reordering."
    
    return send_email(user_email, subject, html_body, text_body)
