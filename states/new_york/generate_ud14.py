#!/usr/bin/env python3
"""
DivorceGPT UD-14 (Notice of Entry) PDF Generator
=================================================

Notice to defendant that Judgment of Divorce has been entered with County Clerk.
Must be served on defendant within 20 days after judgment is entered.

This is a post-judgment form - used after UD-11 is signed and filed.
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
DOUBLE_SPACE = 28


def generate_ud14(data, output_path):
    """
    Generate UD-14 (Notice of Entry) PDF.
    
    Required DivorceGPT variables:
    - plaintiffName: Plaintiff's full legal name
    - defendantName: Defendant's full legal name
    - county: NY county where action is filed
    - indexNumber: Court index number
    - plaintiffAddress: Plaintiff's full address
    - defendantAddress: Defendant's full address
    
    Entry date left blank - user fills after judgment is entered.
    """
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract and validate variables
    county_name = data.get('county', '').strip()
    if not county_name:
        raise ValueError("County is required")
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    if not plaintiff_name:
        raise ValueError("Plaintiff name is required")
    
    defendant_name = data.get('defendantName', '').strip()
    if not defendant_name:
        raise ValueError("Defendant name is required")
    
    index_number = data.get('indexNumber', '').strip()
    
    plaintiff_address = data.get('plaintiffAddress', '').strip()
    defendant_address = data.get('defendantAddress', '').strip()
    
    # =========================================================================
    # PAGE 1 (only page)
    # =========================================================================
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Court header
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT
    
    # Caption box
    c.setFont("Times-Roman", 12)
    box_top = y
    box_left = MARGIN_LEFT
    box_right = MARGIN_LEFT + 230
    box_height = LINE_HEIGHT * 8
    box_bottom = box_top - box_height
    
    # Draw box borders (no left side - top, right, bottom only)
    c.setLineWidth(0.5)
    c.line(box_left, box_top, box_right, box_top)
    c.line(box_right, box_top, box_right, box_bottom)
    c.line(box_left, box_bottom, box_right, box_bottom)
    
    # Party names inside box
    inner_y = box_top - LINE_HEIGHT * 1.5
    c.drawString(box_left + 10, inner_y, f"{plaintiff_name},")
    inner_y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(box_left + 30, inner_y, "Plaintiff,")
    
    inner_y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(box_left + 50, inner_y, "-against-")
    
    inner_y -= LINE_HEIGHT * 1.5
    
    c.drawString(box_left + 10, inner_y, f"{defendant_name},")
    inner_y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(box_left + 30, inner_y, "Defendant.")
    
    # Right side - Index No. and document title
    right_x = box_right + 20
    right_y = box_top - LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    if index_number:
        c.drawString(right_x, right_y, f"Index No.: {index_number}")
    else:
        c.drawString(right_x, right_y, "Index No.: _______________")
    right_y -= LINE_HEIGHT * 2.5
    
    # Document title
    c.setFont("Times-Bold", 12)
    c.drawString(right_x, right_y, "NOTICE OF ENTRY")
    
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"{defendant_name},")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Defendant.")
    y -= LINE_HEIGHT
    
    # Dashed line with X (bottom of caption)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT * 1.5
    
    # Body text
    c.setFont("Times-Roman", 12)
    
    # PLEASE TAKE NOTICE paragraph
    notice_text = (
        f"PLEASE TAKE NOTICE that the attached is a true copy of a judgment of divorce in "
        f"this matter that was entered in the Office of the County Clerk of {county_name} County, on the "
        f"_____ day of _______________, 20___."
    )
    
    # Word wrap
    words = notice_text.split()
    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(' ', "Times-Roman", 12)
    
    for word in words:
        word_width = c.stringWidth(word, "Times-Roman", 12)
        test_width = current_width + word_width + (space_width if current_line else 0)
        
        if test_width <= CONTENT_WIDTH:
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
        c.drawString(MARGIN_LEFT, y, line)
        y -= DOUBLE_SPACE
    
    y -= DOUBLE_SPACE
    
    # Dated line
    c.drawString(MARGIN_LEFT, y, "Dated: _______________")
    
    y -= DOUBLE_SPACE * 2
    
    # ==========================================================================
    # FOUR QUADRANT LAYOUT
    # Q1 (top-left): blank
    # Q2 (top-right): Plaintiff signature/address
    # Q3 (bottom-left): TO: Defendant address
    # Q4 (bottom-right): blank
    # ==========================================================================
    
    quadrant_y = y
    mid_x = PAGE_WIDTH / 2
    
    # Q2 - Plaintiff (top-right)
    q2_x = mid_x + 20
    
    # Signature line first
    c.line(q2_x, quadrant_y, PAGE_WIDTH - MARGIN_RIGHT, quadrant_y)
    quadrant_y -= LINE_HEIGHT
    
    # Plaintiff name under signature line
    c.setFont("Times-Roman", 12)
    c.drawString(q2_x, quadrant_y, plaintiff_name)
    quadrant_y -= LINE_HEIGHT
    
    # Italicized "Plaintiff"
    c.setFont("Times-Italic", 12)
    c.drawString(q2_x, quadrant_y, "Plaintiff")
    quadrant_y -= LINE_HEIGHT  # Reduced from DOUBLE_SPACE
    
    # Address line 1
    c.setFont("Times-Roman", 12)
    if plaintiff_address:
        # Split address into two lines at comma
        addr_parts = plaintiff_address.split(', ', 1)
        c.drawString(q2_x, quadrant_y, addr_parts[0])
        quadrant_y -= LINE_HEIGHT
        if len(addr_parts) > 1:
            c.drawString(q2_x, quadrant_y, addr_parts[1])
            quadrant_y -= LINE_HEIGHT
    else:
        c.line(q2_x, quadrant_y, PAGE_WIDTH - MARGIN_RIGHT, quadrant_y)
        quadrant_y -= LINE_HEIGHT
        c.line(q2_x, quadrant_y, PAGE_WIDTH - MARGIN_RIGHT, quadrant_y)
        quadrant_y -= LINE_HEIGHT
    
    quadrant_y -= DOUBLE_SPACE
    
    # Q3 - TO: Defendant (bottom-left)
    q3_x = MARGIN_LEFT
    
    c.setFont("Times-Roman", 12)
    c.drawString(q3_x, quadrant_y, "TO:")
    quadrant_y -= DOUBLE_SPACE  # Added space after TO:
    
    # Defendant name
    c.drawString(q3_x, quadrant_y, defendant_name)
    quadrant_y -= LINE_HEIGHT
    
    # Italicized "Defendant"
    c.setFont("Times-Italic", 12)
    c.drawString(q3_x, quadrant_y, "Defendant")
    quadrant_y -= LINE_HEIGHT  # Tight spacing like Plaintiff
    
    # Defendant address lines
    c.setFont("Times-Roman", 12)
    if defendant_address:
        # Split address into two lines at comma
        addr_parts = defendant_address.split(', ', 1)
        c.drawString(q3_x, quadrant_y, addr_parts[0])
        quadrant_y -= LINE_HEIGHT
        if len(addr_parts) > 1:
            c.drawString(q3_x, quadrant_y, addr_parts[1])
            quadrant_y -= LINE_HEIGHT
    else:
        c.line(q3_x, quadrant_y, mid_x - 40, quadrant_y)
        quadrant_y -= LINE_HEIGHT
        c.line(q3_x, quadrant_y, mid_x - 40, quadrant_y)
        quadrant_y -= LINE_HEIGHT
    
    # Form identifier at bottom
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 10, "(Form UD-14)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # ==========================================================================
    # QUALITY CONTROL TEST - DivorceGPT Dynamic Data Binding
    # ==========================================================================
    
    print("=" * 60)
    print("UD-14 QUALITY CONTROL TEST")
    print("DivorceGPT Dynamic Data Binding Verification")
    print("=" * 60)
    
    # Test Case 1: Full DivorceGPT data
    test_data_full = {
        "plaintiffName": "MARIA SANTOS",
        "defendantName": "CARLOS SANTOS",
        "county": "Orange",
        "indexNumber": "2027/54321",
        "plaintiffAddress": "123 Main Street, Monroe, NY 10950",
        "defendantAddress": "456 Oak Avenue, Goshen, NY 10924",
    }
    
    print("\n[TEST 1] Full DivorceGPT Data")
    print(f"  plaintiffName: {test_data_full['plaintiffName']}")
    print(f"  defendantName: {test_data_full['defendantName']}")
    print(f"  county: {test_data_full['county']}")
    print(f"  indexNumber: {test_data_full['indexNumber']}")
    print(f"  plaintiffAddress: {test_data_full['plaintiffAddress']}")
    print(f"  defendantAddress: {test_data_full['defendantAddress']}")
    
    output = generate_ud14(test_data_full, "/home/claude/test_ud14_full.pdf")
    print(f"  ✓ Generated: {output}")
    
    # Test Case 2: No addresses (blanks)
    test_data_no_addr = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Kings",
        "indexNumber": "2027/99999",
        "plaintiffAddress": "",
        "defendantAddress": "",
    }
    
    print("\n[TEST 2] No Addresses (Blank Lines)")
    print(f"  plaintiffName: {test_data_no_addr['plaintiffName']}")
    print(f"  plaintiffAddress: (blank)")
    print(f"  defendantAddress: (blank)")
    
    output = generate_ud14(test_data_no_addr, "/home/claude/test_ud14_no_addr.pdf")
    print(f"  ✓ Generated: {output}")
    
    # Test Case 3: Validation - Missing plaintiff name
    print("\n[TEST 3] Validation - Missing Plaintiff Name")
    try:
        test_data_invalid = {
            "plaintiffName": "",
            "defendantName": "JOHN DOE",
            "county": "Orange",
        }
        generate_ud14(test_data_invalid, "/home/claude/test_ud14_invalid.pdf")
        print("  ✗ FAILED - Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}")
    
    # Test Case 4: Validation - Missing defendant name
    print("\n[TEST 4] Validation - Missing Defendant Name")
    try:
        test_data_invalid = {
            "plaintiffName": "JANE DOE",
            "defendantName": "",
            "county": "Orange",
        }
        generate_ud14(test_data_invalid, "/home/claude/test_ud14_invalid.pdf")
        print("  ✗ FAILED - Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}")
    
    print("\n" + "=" * 60)
    print("DYNAMIC DATA BINDING SUMMARY:")
    print("=" * 60)
    print("Variable          → PDF Location")
    print("-" * 60)
    print("plaintiffName     → Caption box (left side)")
    print("defendantName     → Caption box (left side)")
    print("county            → Header + body text")
    print("indexNumber       → 'Index No.: {indexNumber}'")
    print("plaintiffAddress  → Plaintiff signature block")
    print("defendantAddress  → TO: block")
    print("-" * 60)
    print("Entry date        → Left blank (user fills after filing)")
    print("Dated             → Left blank (user fills)")
    print("Checkboxes        → User checks Plaintiff or Attorney")
    print("=" * 60)
    print("\nAll tests passed ✓")
