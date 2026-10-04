"""
Sample PDF Dataset Generator for Hotel Food Inventory Management System
Generates professional, multi-page PDF datasets with:
- A formal cover page (title, description, metadata)
- 10 realistic food items with distinct units (kg, litres, dozen)
- Weekly consumption (Week 1, Week 2, Week 3, Week 4) for every month
- Strict mathematical consistency: Week 1 + Week 2 + Week 3 + Week 4 == Monthly Total
- Opening stock + Purchased - Monthly Total == Closing stock
- Creates both a 4-month dataset (Sep-Dec) and a 3-month dataset (Sep-Nov) for validation.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 10 Hotel Food Items with realistic units: kg, litres, dozen
FOOD_ITEMS_INFO = [
    {"id": "F001", "name": "Basmati Rice", "category": "Grains", "unit": "kg"},
    {"id": "F002", "name": "Wheat Flour", "category": "Grains", "unit": "kg"},
    {"id": "F003", "name": "Fresh Chicken", "category": "Meat & Poultry", "unit": "kg"},
    {"id": "F004", "name": "Whole Milk", "category": "Dairy", "unit": "litres"},
    {"id": "F005", "name": "Fresh Eggs", "category": "Dairy & Eggs", "unit": "dozen"},
    {"id": "F006", "name": "Cooking Oil", "category": "Oils & Fats", "unit": "litres"},
    {"id": "F007", "Onions": "Onions", "name": "Onions", "category": "Vegetables", "unit": "kg"},
    {"id": "F008", "name": "Tomatoes", "category": "Vegetables", "unit": "kg"},
    {"id": "F009", "name": "Potatoes", "category": "Vegetables", "unit": "kg"},
    {"id": "F010", "name": "Paneer", "category": "Dairy", "unit": "kg"},
]

# Month-by-month verified data: W1 + W2 + W3 + W4 == Monthly Total
DATA_BY_MONTH = {
    "September": [
        # id, name, category, unit, opening, purchased, w1, w2, w3, w4, monthly_total, closing
        ["F001", "Basmati Rice", "Grains", "kg", 200, 300, 95, 110, 105, 120, 430, 70],
        ["F002", "Wheat Flour", "Grains", "kg", 150, 250, 80, 85, 90, 85, 340, 60],
        ["F003", "Fresh Chicken", "Meat & Poultry", "kg", 100, 450, 110, 125, 130, 115, 480, 70],
        ["F004", "Whole Milk", "Dairy", "litres", 120, 500, 130, 145, 140, 150, 565, 55],
        ["F005", "Fresh Eggs", "Dairy & Eggs", "dozen", 100, 350, 85, 90, 95, 90, 360, 90],
        ["F006", "Cooking Oil", "Oils & Fats", "litres", 80, 150, 45, 50, 52, 48, 195, 35],
        ["F007", "Onions", "Vegetables", "kg", 150, 300, 90, 95, 100, 95, 380, 70],
        ["F008", "Tomatoes", "Vegetables", "kg", 100, 250, 75, 80, 85, 70, 310, 40],
        ["F009", "Potatoes", "Vegetables", "kg", 160, 320, 95, 105, 110, 100, 410, 70],
        ["F010", "Paneer", "Dairy", "kg", 60, 180, 50, 55, 58, 52, 215, 25],
    ],
    "October": [
        ["F001", "Basmati Rice", "Grains", "kg", 70, 450, 100, 115, 115, 115, 445, 75],
        ["F002", "Wheat Flour", "Grains", "kg", 60, 350, 85, 90, 90, 90, 355, 55],
        ["F003", "Fresh Chicken", "Meat & Poultry", "kg", 70, 500, 115, 125, 130, 125, 495, 75],
        ["F004", "Whole Milk", "Dairy", "litres", 55, 600, 140, 150, 145, 150, 585, 70],
        ["F005", "Fresh Eggs", "Dairy & Eggs", "dozen", 90, 380, 90, 95, 100, 95, 380, 90],
        ["F006", "Cooking Oil", "Oils & Fats", "litres", 35, 200, 48, 52, 55, 50, 205, 30],
        ["F007", "Onions", "Vegetables", "kg", 70, 380, 95, 100, 100, 95, 390, 60],
        ["F008", "Tomatoes", "Vegetables", "kg", 40, 320, 80, 80, 85, 80, 325, 35],
        ["F009", "Potatoes", "Vegetables", "kg", 70, 400, 100, 105, 110, 100, 415, 55],
        ["F010", "Paneer", "Dairy", "kg", 25, 220, 52, 58, 60, 55, 225, 20],
    ],
    "November": [
        ["F001", "Basmati Rice", "Grains", "kg", 75, 520, 120, 130, 135, 125, 510, 85],
        ["F002", "Wheat Flour", "Grains", "kg", 55, 400, 95, 100, 105, 95, 395, 60],
        ["F003", "Fresh Chicken", "Meat & Poultry", "kg", 75, 580, 135, 145, 150, 140, 570, 85],
        ["F004", "Whole Milk", "Dairy", "litres", 70, 650, 155, 165, 160, 160, 640, 80],
        ["F005", "Fresh Eggs", "Dairy & Eggs", "dozen", 90, 420, 100, 105, 110, 105, 420, 90],
        ["F006", "Cooking Oil", "Oils & Fats", "litres", 30, 230, 52, 58, 60, 55, 225, 35],
        ["F007", "Onions", "Vegetables", "kg", 60, 440, 105, 110, 110, 105, 430, 70],
        ["F008", "Tomatoes", "Vegetables", "kg", 35, 360, 85, 90, 90, 85, 350, 45],
        ["F009", "Potatoes", "Vegetables", "kg", 55, 460, 110, 115, 115, 110, 450, 65],
        ["F010", "Paneer", "Dairy", "kg", 20, 260, 60, 65, 68, 62, 255, 25],
    ],
    "December": [
        ["F001", "Basmati Rice", "Grains", "kg", 85, 600, 140, 150, 155, 145, 590, 95],
        ["F002", "Wheat Flour", "Grains", "kg", 60, 450, 105, 115, 115, 105, 440, 70],
        ["F003", "Fresh Chicken", "Meat & Poultry", "kg", 85, 660, 155, 165, 170, 160, 650, 95],
        ["F004", "Whole Milk", "Dairy", "litres", 80, 720, 170, 185, 180, 175, 710, 90],
        ["F005", "Fresh Eggs", "Dairy & Eggs", "dozen", 90, 470, 115, 120, 125, 115, 475, 85],
        ["F006", "Cooking Oil", "Oils & Fats", "litres", 35, 260, 60, 65, 68, 62, 255, 40],
        ["F007", "Onions", "Vegetables", "kg", 70, 490, 115, 125, 125, 115, 480, 80],
        ["F008", "Tomatoes", "Vegetables", "kg", 45, 400, 95, 100, 100, 95, 390, 55],
        ["F009", "Potatoes", "Vegetables", "kg", 65, 510, 120, 130, 130, 120, 500, 75],
        ["F010", "Paneer", "Dairy", "kg", 25, 300, 70, 75, 75, 70, 290, 35],
    ],
}

def validate_dataset_math():
    """Verify that W1+W2+W3+W4 == Total Consumed and Opening+Purchased-Consumed == Closing."""
    for month, rows in DATA_BY_MONTH.items():
        for r in rows:
            name = r[1]
            opening, purchased = r[4], r[5]
            w1, w2, w3, w4 = r[6], r[7], r[8], r[9]
            total, closing = r[10], r[11]
            
            calc_total = w1 + w2 + w3 + w4
            assert calc_total == total, f"Math mismatch in {month} for {name}: {w1}+{w2}+{w3}+{w4} = {calc_total} != {total}"
            
            calc_closing = opening + purchased - total
            assert calc_closing == closing, f"Closing stock mismatch in {month} for {name}: {opening}+{purchased}-{total} = {calc_closing} != {closing}"
    print("All dataset mathematical relationships verified successfully!")

def build_pdf_document(output_path: str, months_to_include: list):
    """Generates a landscape PDF dataset with Cover Page and monthly tables."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=25,
        bottomMargin=25
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=12
    )
    
    cover_subtitle_style = ParagraphStyle(
        'CoverSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=25
    )
    
    cover_body_style = ParagraphStyle(
        'CoverBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=20
    )
    
    page_title_style = ParagraphStyle(
        'PageTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=3
    )
    
    page_sub_style = ParagraphStyle(
        'PageSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    
    story = []
    
    # ================= COVER PAGE =================
    story.append(Spacer(1, 60))
    story.append(Paragraph("🏨 Grand Heritage Hotel & Suites", cover_title_style))
    story.append(Paragraph("Food Inventory & Consumption Official Report", ParagraphStyle('SubSub', parent=cover_title_style, fontSize=18, textColor=colors.HexColor('#1E293B'))))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Food & Beverage Operations Department • Inventory Control Dataset", cover_subtitle_style))
    
    months_str = ", ".join(months_to_include)
    desc_text = (
        f"This document provides verified monthly food inventory and weekly consumption records for "
        f"<b>{len(months_to_include)} months: {months_str}</b>.<br/><br/>"
        "It tracks <b>10 key kitchen food items</b> categorized into Grains, Meat & Poultry, Dairy, Oils, and Vegetables. "
        "Each month contains item-wise opening stock, purchased stock, consumption broken down into "
        "<b>Week 1, Week 2, Week 3, and Week 4</b>, the monthly consumption total, and the ending closing stock.<br/>"
        "All quantities are recorded in realistic hospitality units: <b>kg, litres, and dozen</b>."
    )
    story.append(Paragraph(desc_text, cover_body_style))
    story.append(Spacer(1, 30))
    
    # Cover page metadata box
    meta_data = [
        ["Report Identifier", f"GH-FNB-{len(months_to_include)}M-2025"],
        ["Client", "Grand Heritage Hotel F&B Department"],
        ["Prepared By", "Inventory Operations Engineering Team"],
        ["Monitored Commodities", "10 Primary Hotel Food Staples"],
        ["Reporting Period", months_str],
    ]
    meta_table = Table(meta_data, colWidths=[180, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#475569')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0F172A')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(PageBreak())
    
    # ================= MONTHLY TABLES =================
    table_headers = [
        "Item ID", "Food Item", "Category", "Unit",
        "Opening Stock", "Purchased", "Week 1", "Week 2", "Week 3", "Week 4",
        "Monthly Total", "Closing Stock"
    ]
    col_widths = [50, 100, 85, 45, 60, 60, 52, 52, 52, 52, 68, 56]
    
    for month in months_to_include:
        story.append(Paragraph(f"Monthly Food Inventory & Consumption: {month}", page_title_style))
        story.append(Paragraph(f"Detailed weekly consumption breakdown (Weeks 1 to 4) and inventory balances for {month}.", page_sub_style))
        
        table_rows = [table_headers]
        for row in DATA_BY_MONTH[month]:
            table_rows.append([str(c) for c in row])
            
        t = Table(table_rows, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TEXTCOLOR', (6, 1), (9, -1), colors.HexColor('#0369A1')),   # Highlight weekly columns
            ('FONTNAME', (10, 1), (10, -1), 'Helvetica-Bold'),             # Bold Monthly Total
            ('TEXTCOLOR', (10, 1), (10, -1), colors.HexColor('#0F172A')),
        ]))
        story.append(t)
        story.append(PageBreak())
        
    doc.build(story)
    print(f"Generated PDF with months [{', '.join(months_to_include)}] at: {output_path}")

if __name__ == "__main__":
    validate_dataset_math()
    out_dir = Path(__file__).resolve().parent
    
    # 1. 4-Month Sample PDF (September, October, November, December)
    sample_4m = out_dir / "hotel_food_inventory_sample.pdf"
    build_pdf_document(str(sample_4m), ["September", "October", "November", "December"])
    
    # 2. 3-Month Test PDF (September, October, November)
    sample_3m = out_dir / "hotel_food_inventory_3months_sample.pdf"
    build_pdf_document(str(sample_3m), ["September", "October", "November"])
