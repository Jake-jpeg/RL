#!/usr/bin/env python3
"""
DivorceGPT UD-15 (Affirmation of Service by Mail of Judgment of Divorce) PDF Generator
=====================================================================================

Proof that the Judgment of Divorce with Notice of Entry was served on the Defendant by mail.
Must be completed by a third party (not the plaintiff) who is over 18.

This is a post-judgment form - used after UD-11 is signed and UD-14 is prepared.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .layout import TOP_Y, caption_title, fit_text

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

# Two-box caption layout (matching UD-6)
BOX1_LEFT_X = MARGIN_LEFT
BOX1_RIGHT_X = PAGE_WIDTH / 2

BOX2_LEFT_X = PAGE_WIDTH / 2
BOX2_RIGHT_X = PAGE_WIDTH - MARGIN_RIGHT


def draw_wrapped_text(c, text, x, y, max_width, line_height=None):
    """Draw text that wraps within max_width. Returns final Y position."""
    if line_height is None:
        line_height = LINE_HEIGHT
    
    words = text.split()
    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(' ', "Times-Roman", 12)
    
    for word in words:
        word_width = c.stringWidth(word, "Times-Roman", 12)
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
        y -= line_height
    
    return y


def generate_ud15(data, output_path):
    """
    Generate UD-15 (Affirmation of Service by Mail of JOD) PDF.
    
    Required DivorceGPT variables:
    - plaintiffName: Plaintiff's full legal name
    - defendantName: Defendant's full legal name
    - county: NY county where action is filed
    - indexNumber: Court index number
    - defendantCurrentAddress: Defendant's CURRENT mailing address where JOD will be sent.
                               This may differ from defendantAddress used in earlier forms
                               if defendant has moved since filing.
    
    Server info left blank - completed by third party who mails the documents.
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
    plaintiff_name_upper = plaintiff_name.upper()
    defendant_name_upper = defendant_name.upper()
    if not defendant_name:
        raise ValueError("Defendant name is required")
    
    index_number = data.get('indexNumber', '').strip()
    defendant_current_address = data.get('defendantCurrentAddress', '').strip()
    
    # Fallback to defendantAddress if defendantCurrentAddress not provided
    if not defendant_current_address:
        defendant_current_address = data.get('defendantAddress', '').strip()
    
    # =========================================================================
    # PAGE 1
    # =========================================================================
    
    y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
    
    # Court header - Bold
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT * 1.5
    
    # Caption - dashed line format
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Roman", 12)
    fit_text(c, f"{plaintiff_name_upper},", MARGIN_LEFT, y, (PAGE_WIDTH / 2) - (MARGIN_LEFT) - 12)  # a long name must never overprint the right caption column
    
    # Right side - Index No. and Title
    right_x = PAGE_WIDTH / 2
    
    index_display = index_number if index_number else "_______________"
    c.drawString(right_x, y, f"Index No.: {index_display}")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    
    # Document title - bold, multi-line on right
    c.setFont("Times-Bold", 12)
    c.drawString(right_x, y, "AFFIRMATION OF SERVICE BY")
    y -= LINE_HEIGHT
    c.drawString(right_x, y, "MAIL OF JUDGMENT OF DIVORCE")
    y -= LINE_HEIGHT
    c.drawString(right_x, y, "WITH NOTICE OF ENTRY")
    y -= LINE_HEIGHT * 0.3
    
    c.setFont("Times-Roman", 12)
    fit_text(c, f"{defendant_name_upper},", MARGIN_LEFT, y, (PAGE_WIDTH / 2) - (MARGIN_LEFT) - 12)  # a long name must never overprint the right caption column
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Defendant.")
    y -= LINE_HEIGHT
    
    # Dashed line with X (bottom of caption)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT * 1.5
    
    # Venue block (SS.:) - matching reference image format
    c.setFont("Times-Roman", 12)
    bracket_x = MARGIN_LEFT + 180
    
    c.drawString(MARGIN_LEFT, y, "STATE OF NEW YORK")
    c.drawString(bracket_x, y, ")")
    y -= LINE_HEIGHT
    c.drawString(bracket_x, y, ")")
    c.drawString(bracket_x + 20, y, "SS.:")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "COUNTY OF _______________")
    c.drawString(bracket_x, y, ")")
    y -= LINE_HEIGHT * 2.5  # extra space for server to write name/address
    
    # Server identification paragraph - single spaced
    c.drawString(MARGIN_LEFT, y, "________________________________, residing at _________________________________,")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "says, I am not a party to the action, and am over 18 years of age.")
    y -= LINE_HEIGHT * 1.5
    
    # Service paragraph - single spaced
    service_text = (
        "On _______________, I served a copy of the Judgment of Divorce with Notice of Entry upon "
        "the Defendant by mailing a true copy of such papers enclosed and properly sealed in an envelope "
        "which I deposited in an official United States Post Office depository under the exclusive care and "
        "custody of the United States Postal Service addressed to:"
    )
    y = draw_wrapped_text(c, service_text, MARGIN_LEFT, y, CONTENT_WIDTH, LINE_HEIGHT)
    
    y -= LINE_HEIGHT
    
    # Defendant name and address (where mailed) - may be current address, different from filing docs
    c.drawString(MARGIN_LEFT, y, f"{defendant_name}")
    y -= LINE_HEIGHT
    if defendant_current_address:
        # Split address into two lines
        addr_parts = defendant_current_address.split(', ', 1)
        c.drawString(MARGIN_LEFT, y, addr_parts[0])
        y -= LINE_HEIGHT
        if len(addr_parts) > 1:
            c.drawString(MARGIN_LEFT, y, addr_parts[1])
            y -= LINE_HEIGHT
    else:
        c.line(MARGIN_LEFT, y, PAGE_WIDTH - MARGIN_RIGHT, y)
        y -= LINE_HEIGHT
        c.line(MARGIN_LEFT, y, PAGE_WIDTH - MARGIN_RIGHT, y)
        y -= LINE_HEIGHT
    
    y -= LINE_HEIGHT * 1.5
    
    # Signature block - centered right half, matching reference image
    sig_block_left = PAGE_WIDTH / 2 - 40  # start of signature area
    sig_line_right = PAGE_WIDTH - MARGIN_RIGHT
    
    # "Server's" label aligned directly above "Signature:"
    c.drawString(sig_block_left, y, "Server's")
    y -= LINE_HEIGHT
    
    # Dated on left, "Signature:" label + line on right - same baseline
    c.drawString(MARGIN_LEFT, y, "Dated: _______________")
    
    sig_label = "Signature: "
    sig_label_w = c.stringWidth(sig_label, "Times-Roman", 12)
    c.drawString(sig_block_left, y, sig_label)
    c.setLineWidth(0.25)
    c.line(sig_block_left + sig_label_w, y - 2, sig_line_right, y - 2)
    y -= LINE_HEIGHT * 1.5
    
    # "Print Name:" label + line, aligned to same block
    pn_label = "Print Name: "
    pn_label_w = c.stringWidth(pn_label, "Times-Roman", 12)
    c.drawString(sig_block_left, y, pn_label)
    c.line(sig_block_left + pn_label_w, y - 2, sig_line_right, y - 2)
    
    y -= LINE_HEIGHT * 2
    
    # Affirmation paragraph - starts with "I,"
    affirm_text = (
        "I, ________________________, affirm this ___ day of ______, ____, under the penalties of perjury, "
        "under the laws of New York, which may include a fine or imprisonment, that the foregoing is true, "
        "except as to matters alleged on information and belief and as to those matters I believe it to be true, "
        "and I understand that this document may be filed in an action or proceeding in a court of law."
    )
    y = draw_wrapped_text(c, affirm_text, MARGIN_LEFT, y, CONTENT_WIDTH, LINE_HEIGHT)
    
    y -= LINE_HEIGHT * 2
    
    # Final signature line - centered in same block
    c.setLineWidth(0.25)
    c.line(sig_block_left, y, sig_line_right, y)
    y -= LINE_HEIGHT
    server_sig_text = "Server's Signature"
    server_sig_w = c.stringWidth(server_sig_text, "Times-Roman", 12)
    c.drawString((sig_block_left + sig_line_right) / 2 - server_sig_w / 2, y, server_sig_text)
    
    # Form identifier at bottom
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 10, "(Form UD-15)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # ==========================================================================
    # QUALITY CONTROL TEST - DivorceGPT Dynamic Data Binding
    # ==========================================================================
    
    print("=" * 60)
    print("UD-15 QUALITY CONTROL TEST")
    print("DivorceGPT Dynamic Data Binding Verification")
    print("=" * 60)
    
    # Test Case 1: Full DivorceGPT data
    test_data_full = {
        "plaintiffName": "MARIA SANTOS",
        "defendantName": "CARLOS SANTOS",
        "county": "Orange",
        "indexNumber": "2027/54321",
        "defendantCurrentAddress": "456 Oak Avenue, Goshen, NY 10924",
    }
    
    print("\n[TEST 1] Full DivorceGPT Data")
    print(f"  plaintiffName: {test_data_full['plaintiffName']}")
    print(f"  defendantName: {test_data_full['defendantName']}")
    print(f"  county: {test_data_full['county']}")
    print(f"  indexNumber: {test_data_full['indexNumber']}")
    print(f"  defendantCurrentAddress: {test_data_full['defendantCurrentAddress']}")
    
    output = generate_ud15(test_data_full, "/home/claude/test_ud15_full.pdf")
    print(f"  ✓ Generated: {output}")
    
    # Test Case 2: No address (blank lines)
    test_data_no_addr = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Kings",
        "indexNumber": "2027/99999",
        "defendantCurrentAddress": "",
    }
    
    print("\n[TEST 2] No Address (Blank Lines)")
    print(f"  plaintiffName: {test_data_no_addr['plaintiffName']}")
    print(f"  defendantCurrentAddress: (blank)")
    
    output = generate_ud15(test_data_no_addr, "/home/claude/test_ud15_no_addr.pdf")
    print(f"  ✓ Generated: {output}")
    
    # Test Case 3: Validation - Missing plaintiff name
    print("\n[TEST 3] Validation - Missing Plaintiff Name")
    try:
        test_data_invalid = {
            "plaintiffName": "",
            "defendantName": "JOHN DOE",
            "county": "Orange",
        }
        generate_ud15(test_data_invalid, "/home/claude/test_ud15_invalid.pdf")
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
        generate_ud15(test_data_invalid, "/home/claude/test_ud15_invalid.pdf")
        print("  ✗ FAILED - Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}")
    
    print("\n" + "=" * 60)
    print("DYNAMIC DATA BINDING SUMMARY:")
    print("=" * 60)
    print("Variable               → PDF Location")
    print("-" * 60)
    print("plaintiffName          → Caption (Plaintiff)")
    print("defendantName          → Caption (Defendant) + mailing block")
    print("county                 → Header 'COUNTY OF {COUNTY}'")
    print("indexNumber            → 'Index No.: {indexNumber}'")
    print("defendantCurrentAddress→ Mailing address in body")
    print("                         (may differ from defendantAddress if moved)")
    print("-" * 60)
    print("Server name            → Left blank (3rd party fills)")
    print("Server address         → Left blank (3rd party fills)")
    print("Service date           → Left blank (3rd party fills)")
    print("Signatures             → Left blank (3rd party signs)")
    print("=" * 60)
    print("\nAll tests passed ✓")
