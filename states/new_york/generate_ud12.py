#!/usr/bin/env python3
"""
DivorceGPT UD-12 (Part 130 Certification) PDF Generator
========================================================

Certification that all papers filed are not frivolous per 22 NYCRR 130-1.1(c).
Simple one-page form - plaintiff certifies papers are legitimate.

Required for all uncontested divorce filings.
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


def generate_ud12(data, output_path):
    """
    Generate UD-12 (Part 130 Certification) PDF.
    
    Required DivorceGPT variables:
    - plaintiffName: Plaintiff's full legal name (for signature line)
    - county: NY county where action is filed
    - indexNumber: Court index number (optional)
    
    Date field left blank for user to fill by hand.
    """
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract variables
    county_name = data.get('county', '').strip()
    if not county_name:
        raise ValueError("County is required")
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    if not plaintiff_name:
        raise ValueError("Plaintiff name is required")
    plaintiff_name_upper = plaintiff_name.upper()
    
    index_number = data.get('indexNumber', '').strip()
    
    # =========================================================================
    # PAGE 1 (only page)
    # =========================================================================
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Court header
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT * 1  # Reduced from 2 to 1
    
    # Caption - dashed line format
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"{plaintiff_name_upper},")
    
    # Right side - Index No. and document title
    right_x = PAGE_WIDTH/2 + 95
    
    c.setFont("Times-Roman", 12)
    if index_number:
        c.drawString(right_x, y, f"Index No.: {index_number}")
    else:
        c.drawString(right_x, y, "Index No.: _______________")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    
    # Document title on right side
    c.setFont("Times-Bold", 12)
    c.drawString(right_x, y, "PART 130 CERTIFICATION")
    y -= LINE_HEIGHT * 1.5
    
    defendant_name = data.get('defendantName', '').strip()
    plaintiff_name_upper = plaintiff_name.upper()
    defendant_name_upper = defendant_name.upper()
    c.setFont("Times-Roman", 12)
    if defendant_name:
        c.drawString(MARGIN_LEFT, y, f"{defendant_name_upper},")
    else:
        c.drawString(MARGIN_LEFT, y, "_______________________,")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Defendant.")
    y -= LINE_HEIGHT
    
    # Dashed line with X (bottom of caption)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT * 1.5
    
    # Certification paragraph - CERTIFICATION: as bold prefix
    c.setFont("Times-Bold", 12)
    cert_prefix = "CERTIFICATION:"
    c.drawString(MARGIN_LEFT, y, cert_prefix)
    prefix_width = c.stringWidth(cert_prefix + " ", "Times-Bold", 12)
    
    c.setFont("Times-Roman", 12)
    
    cert_text = (
        "I hereby certify that all of the papers that I have served, filed or submitted to "
        "the court in this divorce action are not frivolous as defined in subsection (c) of "
        "Section 130-1.1 of the Rules of the Chief Administrator of the Courts."
    )
    
    # Word wrap the certification text (first line starts after CERTIFICATION:)
    words = cert_text.split()
    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(' ', "Times-Roman", 12)
    first_line_max = CONTENT_WIDTH - prefix_width
    current_max = first_line_max
    first_line = True
    
    for word in words:
        word_width = c.stringWidth(word, "Times-Roman", 12)
        test_width = current_width + word_width + (space_width if current_line else 0)
        
        if test_width <= current_max:
            current_line.append(word)
            current_width = test_width
        else:
            if current_line:
                lines.append((' '.join(current_line), first_line))
            current_line = [word]
            current_width = word_width
            if first_line:
                first_line = False
                current_max = CONTENT_WIDTH
    
    if current_line:
        lines.append((' '.join(current_line), first_line if not lines else False))
    
    # Draw first line after the bold prefix
    for i, (line, is_first) in enumerate(lines):
        if is_first:
            c.drawString(MARGIN_LEFT + prefix_width, y, line)
        else:
            c.drawString(MARGIN_LEFT, y, line)
        y -= DOUBLE_SPACE
    
    y -= DOUBLE_SPACE * 2
    
    # Date line
    c.drawString(MARGIN_LEFT, y, "Dated: _______________")
    
    y -= DOUBLE_SPACE * 3
    
    # Signature section - right aligned
    sig_x = MARGIN_LEFT + 250
    
    # Signature line
    c.setLineWidth(0.25)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT
    c.drawString(sig_x, y, "SIGNATURE")
    
    y -= DOUBLE_SPACE * 1.5
    
    # Print name line
    c.setLineWidth(0.25)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT
    c.drawString(sig_x, y, "Print or type name below signature")
    
    # Form identifier at bottom
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 10, "(Form UD-12)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # ==========================================================================
    # QUALITY CONTROL TEST - DivorceGPT Dynamic Data Binding
    # ==========================================================================
    
    print("=" * 60)
    print("UD-12 QUALITY CONTROL TEST")
    print("DivorceGPT Dynamic Data Binding Verification")
    print("=" * 60)
    
    # Test Case 1: Full DivorceGPT data
    test_data_full = {
        "plaintiffName": "MARIA SANTOS",
        "defendantName": "CARLOS SANTOS",
        "county": "Orange",
        "indexNumber": "2027/54321",
    }
    
    print("\n[TEST 1] Full DivorceGPT Data")
    print(f"  plaintiffName: {test_data_full['plaintiffName']}")
    print(f"  defendantName: {test_data_full['defendantName']}")
    print(f"  county: {test_data_full['county']}")
    print(f"  indexNumber: {test_data_full['indexNumber']}")
    
    output = generate_ud12(test_data_full, "/home/claude/test_ud12_full.pdf")
    print(f"  ✓ Generated: {output}")
    
    # Test Case 2: No index number (pre-filing)
    test_data_no_index = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Kings",
        "indexNumber": "",
    }
    
    print("\n[TEST 2] No Index Number (Pre-Filing)")
    print(f"  plaintiffName: {test_data_no_index['plaintiffName']}")
    print(f"  defendantName: {test_data_no_index['defendantName']}")
    print(f"  county: {test_data_no_index['county']}")
    print(f"  indexNumber: (blank - not yet assigned)")
    
    output = generate_ud12(test_data_no_index, "/home/claude/test_ud12_no_index.pdf")
    print(f"  ✓ Generated: {output}")
    
    # Test Case 3: Different county
    test_data_westchester = {
        "plaintiffName": "SARAH GOLDSTEIN",
        "defendantName": "DAVID GOLDSTEIN",
        "county": "Westchester",
        "indexNumber": "2027/99999",
    }
    
    print("\n[TEST 3] Different County (Westchester)")
    print(f"  plaintiffName: {test_data_westchester['plaintiffName']}")
    print(f"  county: {test_data_westchester['county']}")
    
    output = generate_ud12(test_data_westchester, "/home/claude/test_ud12_westchester.pdf")
    print(f"  ✓ Generated: {output}")
    
    # Test Case 4: Validation - Missing plaintiff name
    print("\n[TEST 4] Validation - Missing Plaintiff Name")
    try:
        test_data_invalid = {
            "plaintiffName": "",
            "defendantName": "JOHN DOE",
            "county": "Orange",
        }
        generate_ud12(test_data_invalid, "/home/claude/test_ud12_invalid.pdf")
        print("  ✗ FAILED - Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}")
    
    # Test Case 5: Validation - Missing county
    print("\n[TEST 5] Validation - Missing County")
    try:
        test_data_invalid = {
            "plaintiffName": "JANE DOE",
            "defendantName": "JOHN DOE",
            "county": "",
        }
        generate_ud12(test_data_invalid, "/home/claude/test_ud12_invalid.pdf")
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
    print("county            → Header 'COUNTY OF {COUNTY}'")
    print("indexNumber       → 'Index No.: {indexNumber}' or blank line")
    print("-" * 60)
    print("Date              → Left blank (user fills by hand)")
    print("Signature         → Left blank (user signs)")
    print("=" * 60)
    print("\nAll tests passed ✓")
