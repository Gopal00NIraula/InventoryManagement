#!/usr/bin/env python3
"""
Generate PDF Test Report for Inventory Management System
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import subprocess
import sys

def run_tests():
    """Run tests and capture output"""
    result = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr, result.returncode

def generate_pdf_report(filename="test_report.pdf"):
    """Generate PDF test report"""
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title = Paragraph("Inventory Management System<br/>Unit Test Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Test execution date
    date_text = Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                         styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 20))
    
    # Run tests
    test_output, return_code = run_tests()
    
    # Parse test results
    lines = test_output.split('\n')
    test_count = 0
    status = "FAILED"
    
    for line in lines:
        if line.startswith("Ran "):
            test_count = int(line.split()[1])
        if line == "OK":
            status = "PASSED"
    
    # Summary Section
    elements.append(Paragraph("Test Summary", heading_style))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Tests', str(test_count)],
        ['Status', status],
        ['Exit Code', str(return_code)]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Test Files Section
    elements.append(Paragraph("Test Modules", heading_style))
    
    test_modules = [
        ['Test Module', 'Description', 'Tests'],
        ['test_user_model.py', 'User authentication & management', '4'],
        ['test_inventory_model.py', 'Inventory CRUD operations', '7'],
        ['test_supplier_model.py', 'Supplier management', '5'],
        ['test_customer_model.py', 'Customer management', '5'],
        ['test_encryption.py', 'Password hashing & verification', '6'],
        ['test_barcode_utils.py', 'Barcode generation', '2'],
        ['test_import_export.py', 'CSV/Excel import/export', '4'],
        ['test_purchase_order_model.py', 'Purchase orders', '3'],
        ['test_sales_order_model.py', 'Sales orders', '3'],
        ['test_audit_log_model.py', 'Audit logging', '3'],
        ['test_stock_alert_model.py', 'Stock alerts', '3'],
        ['test_dashboard_stats.py', 'Dashboard statistics', '2'],
        ['test_email_notifications.py', 'Email system', '3'],
        ['test_login_controller.py', 'Login controller', '3'],
    ]
    
    modules_table = Table(test_modules, colWidths=[2.2*inch, 3*inch, 0.8*inch])
    modules_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(modules_table)
    elements.append(PageBreak())
    
    # Detailed Test Output
    elements.append(Paragraph("Detailed Test Output", heading_style))
    elements.append(Spacer(1, 12))
    
    # Add test output as preformatted text
    for line in lines[:100]:  # Limit to first 100 lines
        if line.strip():
            p = Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), styles['Code'])
            elements.append(p)
    
    # Build PDF
    doc.build(elements)
    print(f"PDF report generated: {filename}")

if __name__ == "__main__":
    generate_pdf_report()
