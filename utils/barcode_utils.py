"""
Barcode and QR Code Utilities
"""
import os
import io
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image

try:
    from PIL import ImageTk
    HAS_IMAGETK = True
except ImportError:
    HAS_IMAGETK = False
    print("Warning: ImageTk not available. GUI barcode display will be limited.")

from database.db_connection import get_connection


def generate_barcode_number(item_id, sku):
    """
    Generate a unique barcode number from item ID and SKU
    Uses EAN13 format (13 digits)
    
    Args:
        item_id (int): Item database ID
        sku (str): Item SKU
        
    Returns:
        str: 12-digit barcode number (13th digit is checksum, auto-added by library)
    """
    # Use item_id padded to 6 digits + first 6 chars of SKU hash
    sku_hash = str(abs(hash(sku)))[:6]
    item_part = str(item_id).zfill(6)
    barcode_num = item_part + sku_hash
    return barcode_num[:12]  # EAN13 needs 12 digits (13th is checksum)


def generate_barcode_image(barcode_number, item_name=""):
    """
    Generate EAN13 barcode image
    
    Args:
        barcode_number (str): 12-digit barcode number
        item_name (str): Item name for display
        
    Returns:
        PIL.Image: Barcode image
    """
    try:
        # Create EAN13 barcode
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(barcode_number, writer=ImageWriter())
        
        # Generate to BytesIO
        buffer = io.BytesIO()
        ean.write(buffer, options={
            'module_width': 0.3,
            'module_height': 10.0,
            'quiet_zone': 6.5,
            'font_size': 10,
            'text_distance': 5.0,
            'text': item_name[:30] if item_name else ''
        })
        
        buffer.seek(0)
        img = Image.open(buffer)
        return img
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None


def generate_qr_code(data, size=200):
    """
    Generate QR code image
    
    Args:
        data (str): Data to encode in QR code
        size (int): Image size in pixels
        
    Returns:
        PIL.Image: QR code image
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


def save_barcode_image(barcode_number, item_name, output_dir="barcodes"):
    """
    Save barcode image to file
    
    Args:
        barcode_number (str): Barcode number
        item_name (str): Item name
        output_dir (str): Directory to save images
        
    Returns:
        str: Path to saved image or None
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate and save
        img = generate_barcode_image(barcode_number, item_name)
        if img:
            filename = f"{output_dir}/barcode_{barcode_number}.png"
            img.save(filename)
            return filename
        return None
    except Exception as e:
        print(f"Error saving barcode: {e}")
        return None


def save_qr_code(data, item_id, output_dir="qrcodes"):
    """
    Save QR code image to file
    
    Args:
        data (str): Data to encode
        item_id (int): Item ID
        output_dir (str): Directory to save images
        
    Returns:
        str: Path to saved image or None
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate and save
        img = generate_qr_code(data)
        if img:
            filename = f"{output_dir}/qr_{item_id}.png"
            img.save(filename)
            return filename
        return None
    except Exception as e:
        print(f"Error saving QR code: {e}")
        return None


def search_item_by_barcode(barcode_number):
    """
    Search for item by barcode number
    
    Args:
        barcode_number (str): Barcode to search for
        
    Returns:
        dict: Item data or None if not found
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, name, sku, quantity, price, min_stock_level, reorder_point, barcode
        FROM items
        WHERE barcode = ?
    """, (barcode_number,))
    
    row = cur.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'sku': row[2],
            'quantity': row[3],
            'price': row[4],
            'min_stock_level': row[5],
            'reorder_point': row[6],
            'barcode': row[7]
        }
    return None


def update_item_barcode(item_id, barcode_number):
    """
    Update item's barcode in database
    
    Args:
        item_id (int): Item ID
        barcode_number (str): Barcode number to set
        
    Returns:
        bool: Success status
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE items
            SET barcode = ?
            WHERE id = ?
        """, (barcode_number, item_id))
        conn.commit()
        success = cur.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        conn.close()
        print(f"Error updating barcode: {e}")
        return False


def generate_and_save_item_barcode(item_id, item_name, sku):
    """
    Generate barcode number, save it to database, and create image
    
    Args:
        item_id (int): Item ID
        item_name (str): Item name
        sku (str): Item SKU
        
    Returns:
        tuple: (barcode_number, image_path) or (None, None) on error
    """
    try:
        # Generate barcode number
        barcode_number = generate_barcode_number(item_id, sku)
        
        # Save to database
        if update_item_barcode(item_id, barcode_number):
            # Generate and save image
            img_path = save_barcode_image(barcode_number, item_name)
            return (barcode_number, img_path)
        
        return (None, None)
    except Exception as e:
        print(f"Error in generate_and_save_item_barcode: {e}")
        return (None, None)


def get_barcode_tk_image(barcode_number, item_name="", width=300):
    """
    Generate barcode as Tkinter PhotoImage for display in GUI
    
    Args:
        barcode_number (str): Barcode number
        item_name (str): Item name
        width (int): Desired width in pixels
        
    Returns:
        ImageTk.PhotoImage: Image ready for Tkinter display, or None if ImageTk unavailable
    """
    if not HAS_IMAGETK:
        return None
    
    try:
        img = generate_barcode_image(barcode_number, item_name)
        if img:
            # Resize to desired width while maintaining aspect ratio
            aspect_ratio = img.height / img.width
            new_height = int(width * aspect_ratio)
            img = img.resize((width, new_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None
    except Exception as e:
        print(f"Error creating Tk image: {e}")
        return None


def get_qr_tk_image(data, size=150):
    """
    Generate QR code as Tkinter PhotoImage for display in GUI
    
    Args:
        data (str): Data to encode
        size (int): Image size in pixels
        
    Returns:
        ImageTk.PhotoImage: Image ready for Tkinter display, or None if ImageTk unavailable
    """
    if not HAS_IMAGETK:
        return None
    
    try:
        img = generate_qr_code(data, size)
        if img:
            return ImageTk.PhotoImage(img)
        return None
    except Exception as e:
        print(f"Error creating QR Tk image: {e}")
        return None
