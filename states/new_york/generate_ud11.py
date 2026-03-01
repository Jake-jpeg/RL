#!/usr/bin/env python3
"""
DivorceGPT UD-11 (Judgment of Divorce) PDF Generator
=====================================================

The actual judgment signed by the court dissolving the marriage.
Simplified for DivorceGPT scope: no children, no assets, no maintenance.
Grounds: DRL §170(7) - irretrievable breakdown for 6+ months.

This is the court's official judgment - prepared by plaintiff, signed by judge.
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
DOUBLE_SPACE = 28  # Double spaced for body text


def draw_wrapped_text(c, text, x, y, max_width, font_name="Times-Roman", font_size=12, line_height=None):
    """Draw text that wraps within max_width. Returns final Y position."""
    if line_height is None:
        line_height = DOUBLE_SPACE
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
        y -= line_height
    
    return y


def draw_bold_prefix_text(c, bold_text, regular_text, x, y, max_width, line_height=None):
    """Draw text with bold prefix followed by regular text, wrapping properly."""
    if line_height is None:
        line_height = DOUBLE_SPACE
    
    # Calculate bold prefix width
    c.setFont("Times-Bold", 12)
    bold_width = c.stringWidth(bold_text + " ", "Times-Bold", 12)
    
    # Draw bold prefix
    c.drawString(x, y, bold_text)
    
    # Now wrap the regular text
    c.setFont("Times-Roman", 12)
    words = regular_text.split()
    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(' ', "Times-Roman", 12)
    
    # First line has less space (after bold prefix)
    first_line_max = max_width - bold_width
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
                current_max = max_width
    
    if current_line:
        lines.append((' '.join(current_line), first_line if not lines else False))
    
    # Draw lines
    for i, (line, is_first) in enumerate(lines):
        if is_first:
            c.drawString(x + bold_width, y, line)
        else:
            c.drawString(x, y, line)
        y -= line_height
    
    return y


def check_page_break(c, y, needed_space):
    """Check if page break needed, return new y position."""
    if y < MARGIN_BOTTOM + needed_space:
        c.showPage()
        c.setFont("Times-Roman", 12)
        return PAGE_HEIGHT - MARGIN_TOP
    return y


def generate_ud11(data, output_path):
    """
    Generate UD-11 (Judgment of Divorce) PDF.
    
    Required DivorceGPT variables:
    - plaintiffName: Plaintiff's full legal name
    - defendantName: Defendant's full legal name  
    - county: NY county where action is filed
    - indexNumber: Court index number (optional, blank if not yet assigned)
    - religiousCeremony: Boolean - True if religious, False if civil
    - plaintiffAddress: Plaintiff's full address
    - defendantAddress: Defendant's full address
    
    SSN fields are left blank - user fills in by hand (privacy protection).
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
    
    # Marriage info - determines DRL §253 language
    religious_ceremony = data.get('religiousCeremony', False)
    
    # Addresses - filled in from user input
    plaintiff_address = data.get('plaintiffAddress', '').strip()
    if not plaintiff_address:
        plaintiff_address = "_________________________"
    
    defendant_address = data.get('defendantAddress', '').strip()
    if not defendant_address:
        defendant_address = "_________________________"
    
    # =========================================================================
    # PAGE 1
    # =========================================================================
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Header - match edited docx format
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "At the Matrimonial/IAS Part _____ of")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "New York State Supreme Court at")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"the Courthouse, {county_name} County,")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "on ____________________________.")
    y -= LINE_HEIGHT * 1.5
    
    c.drawString(MARGIN_LEFT, y, "Present:")
    y -= LINE_HEIGHT
    hon_text = "Hon. "
    c.drawString(MARGIN_LEFT, y, hon_text)
    hon_width = c.stringWidth(hon_text, "Times-Roman", 12)
    c.setLineWidth(0.5)  # Thinner line
    c.line(MARGIN_LEFT + hon_width, y - 2, MARGIN_LEFT + 180, y - 2)  # Shorter line
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 50, y, "Justice/Referee")
    y -= LINE_HEIGHT * 2
    
    # Court header - Bold (matches UD-10)
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
    c.drawString(MARGIN_LEFT, y, f"{plaintiff_name},")
    
    # Right side - Index No., Calendar No., and Document Title
    right_x = PAGE_WIDTH/2 + 95
    
    c.setFont("Times-Roman", 12)
    if index_number:
        c.drawString(right_x, y, f"Index No.: {index_number}")
    else:
        c.drawString(right_x, y, "Index No.: _______________")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    c.setFont("Times-Roman", 12)
    c.drawString(right_x, y, "Calendar No.: ___________")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    
    # Document title on right side
    c.setFont("Times-Bold", 12)
    c.drawString(right_x, y, "JUDGMENT OF DIVORCE")
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
    
    # Body - double spaced
    c.setFont("Times-Roman", 12)
    
    # Intro paragraph 1
    intro1 = "This action was submitted to this court for consideration this _____ day of _______________ ."
    y = draw_wrapped_text(c, intro1, MARGIN_LEFT, y, CONTENT_WIDTH)
    
    # Intro paragraph 2
    intro2 = "Plaintiff presented a Summons With Notice and Affidavit of Plaintiff constituting the facts of the matter."
    y = draw_wrapped_text(c, intro2, MARGIN_LEFT, y, CONTENT_WIDTH)
    
    # Intro paragraph 3
    intro3 = "The Defendant has appeared and waived his or her right to answer."
    y = draw_wrapped_text(c, intro3, MARGIN_LEFT, y, CONTENT_WIDTH)
    
    # Military status
    intro4 = "The Court accepted written proof of non-military status."
    y = draw_wrapped_text(c, intro4, MARGIN_LEFT, y, CONTENT_WIDTH)
    
    # Addresses (filled in) and SSN (blank for user to fill by hand)
    addr_text = f"The Plaintiff's address is {plaintiff_address}, and social security number is ___________. The Defendant's address is {defendant_address}, and social security number is ___________."
    y = draw_wrapped_text(c, addr_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y -= DOUBLE_SPACE * 0.5
    
    # NOW paragraph - NOW is bold
    y = draw_bold_prefix_text(c, "NOW,", "on motion of the Plaintiff, it is", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - Referee's Report
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED", "that the Referee's Report, if any, is hereby confirmed; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - Marriage dissolved
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", f"that the marriage between {plaintiff_name}, Plaintiff, and {defendant_name}, Defendant, is hereby dissolved by reason of the Irretrievable Breakdown of the marriage relationship for a period of at least six (6) months pursuant to DRL §170(7); and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - No children
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that there are no children of the marriage; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - No maintenance
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that no award of maintenance is made to either party, neither party having requested maintenance; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - No equitable distribution
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that equitable distribution of marital property is not in issue, there being no marital property to distribute; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - Barriers to remarriage
    if religious_ceremony:
        y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that Plaintiff has complied with DRL §253 by filing a sworn statement that Plaintiff has taken all steps within his or her power to remove all barriers to Defendant's remarriage; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    else:
        y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that compliance with DRL §253 regarding removal of barriers to remarriage is not required as the parties were married in a civil ceremony; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - Applications for modification
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that any applications to enforce or modify the provisions of this Judgment shall be brought in a County wherein one of the parties resides; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # ORDERED AND ADJUDGED - DRL 255 compliance
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that the parties have been provided notice pursuant to DRL §255 regarding health care coverage continuation, tax consequences, and other rights affected by this judgment; and it is further", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y = check_page_break(c, y, DOUBLE_SPACE * 3)
    
    # Final ORDERED AND ADJUDGED
    y = draw_bold_prefix_text(c, "ORDERED AND ADJUDGED,", "that this judgment shall be entered and that the marriage of the parties is dissolved as of the date of entry of this judgment.", MARGIN_LEFT, y, CONTENT_WIDTH)
    
    y -= DOUBLE_SPACE
    
    y = check_page_break(c, y, DOUBLE_SPACE * 4)
    
    # Signature section - cleaner layout
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Dated: _______________________")
    y -= DOUBLE_SPACE * 1.5
    
    # ENTER label - right aligned above signature
    c.setFont("Times-Bold", 12)
    enter_x = PAGE_WIDTH / 2 + 20
    c.drawString(enter_x, y, "ENTER:")
    y -= DOUBLE_SPACE * 1.5
    
    # Signature line - right-aligned, proper spacing
    sig_line_start = PAGE_WIDTH / 2 + 20
    sig_line_end = PAGE_WIDTH - MARGIN_RIGHT
    c.setLineWidth(0.25)
    c.line(sig_line_start, y, sig_line_end, y)
    y -= LINE_HEIGHT * 1.2
    
    # Title centered under signature line
    c.setFont("Times-Roman", 12)
    title_text = "Justice of the Supreme Court / Referee"
    title_width = c.stringWidth(title_text, "Times-Roman", 12)
    title_center = sig_line_start + (sig_line_end - sig_line_start) / 2
    c.drawString(title_center - title_width / 2, y, title_text)
    
    # Form identifier and revision date at bottom
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 10, "(Form UD-11)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # ==========================================================================
    # QUALITY CONTROL TEST
    # ==========================================================================
    
    print("=" * 60)
    print("UD-11 QUALITY CONTROL TEST")
    print("=" * 60)
    
    # Test Case 1: Civil Ceremony - Full DivorceGPT data
    test_data_civil = {
        "plaintiffName": "MARIA SANTOS",
        "defendantName": "CARLOS SANTOS",
        "county": "Orange",
        "indexNumber": "2027/54321",
        "religiousCeremony": False,
        "plaintiffAddress": "123 Main Street, Monroe, NY 10950",
        "defendantAddress": "456 Oak Avenue, Goshen, NY 10924",
    }
    
    print("\n[TEST 1] Civil Ceremony")
    print(f"  Plaintiff: {test_data_civil['plaintiffName']}")
    print(f"  Defendant: {test_data_civil['defendantName']}")
    print(f"  County: {test_data_civil['county']}")
    print(f"  Index No: {test_data_civil['indexNumber']}")
    print(f"  Ceremony: CIVIL")
    print(f"  Plaintiff Address: {test_data_civil['plaintiffAddress']}")
    print(f"  Defendant Address: {test_data_civil['defendantAddress']}")
    
    output = generate_ud11(test_data_civil, "/home/claude/test_ud11_civil.pdf")
    print(f"  Generated: {output}")
    
    # Test Case 2: Religious Ceremony
    test_data_religious = {
        "plaintiffName": "SARAH GOLDSTEIN",
        "defendantName": "DAVID GOLDSTEIN",
        "county": "Kings",
        "indexNumber": "2027/98765",
        "religiousCeremony": True,
        "plaintiffAddress": "789 Brooklyn Ave, Brooklyn, NY 11213",
        "defendantAddress": "321 Crown Street, Brooklyn, NY 11225",
    }
    
    print("\n[TEST 2] Religious Ceremony")
    print(f"  Plaintiff: {test_data_religious['plaintiffName']}")
    print(f"  Defendant: {test_data_religious['defendantName']}")
    print(f"  County: {test_data_religious['county']}")
    print(f"  Index No: {test_data_religious['indexNumber']}")
    print(f"  Ceremony: RELIGIOUS")
    print(f"  Plaintiff Address: {test_data_religious['plaintiffAddress']}")
    print(f"  Defendant Address: {test_data_religious['defendantAddress']}")
    
    output = generate_ud11(test_data_religious, "/home/claude/test_ud11_religious.pdf")
    print(f"  Generated: {output}")
    
    # Test Case 3: No Index Number (not yet assigned)
    test_data_no_index = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Westchester",
        "indexNumber": "",  # Not yet assigned
        "religiousCeremony": False,
        "plaintiffAddress": "100 Court Street, White Plains, NY 10601",
        "defendantAddress": "200 Main Street, Yonkers, NY 10701",
    }
    
    print("\n[TEST 3] No Index Number")
    print(f"  Plaintiff: {test_data_no_index['plaintiffName']}")
    print(f"  Index No: (blank - not yet assigned)")
    
    output = generate_ud11(test_data_no_index, "/home/claude/test_ud11_no_index.pdf")
    print(f"  Generated: {output}")
    
    print("\n" + "=" * 60)
    print("QUALITY CONTROL CHECKLIST:")
    print("=" * 60)
    print("[ ] County appears in header AND in COUNTY OF line")
    print("[ ] Plaintiff name appears in caption AND marriage dissolution paragraph")
    print("[ ] Defendant name appears in caption AND marriage dissolution paragraph")
    print("[ ] Index number appears (or blank if not provided)")
    print("[ ] Addresses are filled in (not blank)")
    print("[ ] SSN fields are BLANK (for user to fill by hand)")
    print("[ ] Civil ceremony -> DRL §253 NOT required language")
    print("[ ] Religious ceremony -> DRL §253 compliance language")
    print("[ ] NOW is BOLD")
    print("[ ] ORDERED AND ADJUDGED is BOLD (all instances)")
    print("[ ] ENTER: is BOLD")
    print("[ ] Double-spaced body text")
    print("[ ] Form UD-11 at bottom")
    print("=" * 60)
