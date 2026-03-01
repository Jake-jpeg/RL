#!/usr/bin/env python3
"""
DivorceGPT UD-9 (Note of Issue) PDF Generator
==============================================

Puts the case on the court calendar.
For uncontested divorces - no children under 18.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points
MARGIN_LEFT = 72   # 1 inch
MARGIN_RIGHT = 72
MARGIN_TOP = 72
MARGIN_BOTTOM = 72

# Content area
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 468 points

# Line height
LINE_HEIGHT = 14

# Box layout positions
BOX1_LEFT_X = MARGIN_LEFT
BOX1_RIGHT_X = PAGE_WIDTH / 2

BOX2_LEFT_X = PAGE_WIDTH / 2
BOX2_RIGHT_X = PAGE_WIDTH - MARGIN_RIGHT


def draw_wrapped_text(c, text, x, y, max_width, font_name="Times-Roman", font_size=12):
    """Draw text that wraps within max_width. Returns final Y position."""
    c.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(' ', font_name, font_size)
    
    for word in words:
        word_width = c.stringWidth(word, font_name, font_size)
        test_width = current_width + word_width + (space_width if current_line else 0)
        
        if test_width <= max_width:
            current_line.append(word)
            current_width = test_width
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
    
    if current_line:
        lines.append(' '.join(current_line))
    
    for line in lines:
        c.drawString(x, y, line)
        y -= LINE_HEIGHT
    
    return y


def generate_ud9(data, output_path):
    """Generate UD-9 (Note of Issue) PDF."""
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract variables
    county_name = data.get('county', '').strip()
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    defendant_name = data.get('defendantName', '').strip()
    index_number = data.get('indexNumber', '').strip()
    
    # Dates
    date_summons_filed = data.get('dateSummonsFiled', '').strip()
    date_summons_served = data.get('dateSummonsServed', '').strip()
    
    # Plaintiff contact info (pro se)
    plaintiff_address = data.get('plaintiffAddress', '').strip()
    plaintiff_phone = data.get('plaintiffPhone', '').strip()
    
    # Defendant contact info
    defendant_address = data.get('defendantAddress', '').strip()
    defendant_phone = data.get('defendantPhone', '').strip()
    
    # ASCII checkbox characters
    CHECKBOX_EMPTY = "[ ]"
    CHECKBOX_CHECKED = "[X]"
    
    # =========================================================================
    # PAGE 1
    # =========================================================================
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Title - centered at top
    c.setFont("Times-Bold", 14)
    center_x = PAGE_WIDTH / 2
    title = "NOTE OF ISSUE - UNCONTESTED DIVORCE"
    c.drawString(center_x - c.stringWidth(title, "Times-Bold", 14)/2, y, title)
    y -= LINE_HEIGHT * 2
    
    # For Use of Clerk box (right side) - keep in same position
    clerk_box_x = PAGE_WIDTH - MARGIN_RIGHT - 140
    clerk_box_y = y
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    c.rect(clerk_box_x, clerk_box_y - 50, 140, 50)
    c.setFont("Times-Italic", 10)
    c.drawString(clerk_box_x + 5, clerk_box_y - 15, "For Use of Clerk")
    
    # Move down past the clerk box before starting court header
    y -= LINE_HEIGHT * 5
    
    # Court header
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    
    # County - Bold
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT
    
    # Dashed line with X
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "-" * 55 + "X")
    y -= LINE_HEIGHT
    
    # Plaintiff name
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, plaintiff_name + ",")
    
    # Index No. and Calendar No. (right side)
    c.setFont("Times-Roman", 12)
    index_display = index_number if index_number else "____________"
    c.drawString(PAGE_WIDTH/2 + 95, y, f"Index No.: {index_display}")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    c.setFont("Times-Roman", 12)
    c.drawString(PAGE_WIDTH/2 + 95, y, "Calendar No.: ____________")
    y -= LINE_HEIGHT * 1.2
    
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    y -= LINE_HEIGHT * 1.5
    
    # Defendant name
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, defendant_name + ".")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Defendant.")
    y -= LINE_HEIGHT
    
    # Dashed line with X
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "-" * 55 + "X")
    y -= LINE_HEIGHT * 1.5
    
    # NO TRIAL
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "NO TRIAL")
    y -= LINE_HEIGHT * 1.5
    
    # Filed by - Plaintiff only
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "FILED BY:")
    c.drawString(MARGIN_LEFT + 70, y, f"{CHECKBOX_CHECKED}")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 95, y, "Plaintiff")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 160, y, f"{CHECKBOX_EMPTY}")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 185, y, "Defendant")
    y -= LINE_HEIGHT * 1.5
    
    # Date Summons Filed
    c.setFont("Times-Roman", 12)
    date_filed_display = date_summons_filed if date_summons_filed else "____________________"
    c.drawString(MARGIN_LEFT, y, f"DATE SUMMONS FILED: {date_filed_display}")
    y -= LINE_HEIGHT * 1.3
    
    # Date Summons Served
    date_served_display = date_summons_served if date_summons_served else "____________________"
    c.drawString(MARGIN_LEFT, y, f"DATE SUMMONS SERVED: {date_served_display}")
    y -= LINE_HEIGHT * 1.3
    
    # Date Issue Joined - NOT JOINED with Waiver
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "DATE ISSUE JOINED:")
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT + 130, y, "NOT JOINED -")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 215, y, f"{CHECKBOX_CHECKED}")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 240, y, "Waiver")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 295, y, f"{CHECKBOX_EMPTY}")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 320, y, "Default")
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 215, y, f"{CHECKBOX_EMPTY}")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 240, y, "Stipulation/Separation Agreement")
    y -= LINE_HEIGHT * 1.3
    
    # Nature of Action
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "NATURE OF ACTION:")
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT + 130, y, "UNCONTESTED DIVORCE")
    y -= LINE_HEIGHT * 1.3
    
    # Relief
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "RELIEF:")
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT + 130, y, "ABSOLUTE DIVORCE")
    y -= LINE_HEIGHT * 1.5
    
    # Plaintiff info
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"{CHECKBOX_CHECKED}")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 25, y, "Plaintiff")
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Office and P.O. Address:")
    y -= LINE_HEIGHT
    
    # Plaintiff address - at margin
    if plaintiff_address:
        y = draw_wrapped_text(c, plaintiff_address, MARGIN_LEFT, y, CONTENT_WIDTH)
    else:
        c.drawString(MARGIN_LEFT, y, "N/A")
        y -= LINE_HEIGHT
    y -= LINE_HEIGHT * 0.3
    
    phone_display = plaintiff_phone if plaintiff_phone else "N/A"
    c.drawString(MARGIN_LEFT, y, f"Phone No.: {phone_display}")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Fax No.: N/A")
    y -= LINE_HEIGHT * 1.5
    
    # Defendant info
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"{CHECKBOX_CHECKED}")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 25, y, "Defendant")
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Office and P.O. Address:")
    y -= LINE_HEIGHT
    
    # Defendant address - at margin
    if defendant_address:
        y = draw_wrapped_text(c, defendant_address, MARGIN_LEFT, y, CONTENT_WIDTH)
    else:
        c.drawString(MARGIN_LEFT, y, "N/A")
        y -= LINE_HEIGHT
    y -= LINE_HEIGHT * 0.3
    
    defendant_phone_display = defendant_phone if defendant_phone else "N/A"
    c.drawString(MARGIN_LEFT, y, f"Phone No.: {defendant_phone_display}")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Fax No.: N/A")
    
    # Footer - Form ID in bottom margin
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, 36, "(Form UD-9)")
    
    c.save()
    return output_path
    
    c.save()
    return output_path
    
    c.save()
    return output_path


if __name__ == "__main__":
    # Test with waiver (UD-7 signed)
    test_data = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Orange",
        "indexNumber": "12345/2027",
        "dateSummonsFiled": "January 10, 2027",
        "dateSummonsServed": "January 15, 2027",
        "issueType": "waiver",  # UD-7 signed
        "plaintiffAddress": "74 Fitzgerald Court, Monroe, NY 10950",
        "plaintiffPhone": "(845) 555-1234",
        "defendantAddress": "123 Main Street, Newburgh, NY 12550",
        "defendantPhone": "",  # Unknown - will show N/A
    }
    
    output = generate_ud9(test_data, "/home/claude/test_ud9_waiver.pdf")
    print(f"Generated WAIVER: {output}")
    
    # Test with default
    test_data["issueType"] = "default"
    output = generate_ud9(test_data, "/home/claude/test_ud9_default.pdf")
    print(f"Generated DEFAULT: {output}")
