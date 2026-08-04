#!/usr/bin/env python3
"""
DivorceGPT UD-4 (Sworn Statement of Removal of Barriers to Remarriage) PDF Generator
=====================================================================================

Two pages:
- Page 1: UD-4 Sworn Statement
- Page 2: UD-4a Affirmation of Service

ONLY generated for religious ceremonies where Defendant has provided written waiver.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .layout import TOP_Y, caption_title, fit_text
from datetime import datetime

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


def generate_ud4(data, output_path):
    """Generate UD-4 form PDF with UD-4a on page 2."""
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract variables
    county_name = data.get('county', '').strip()
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    defendant_name = data.get('defendantName', '').strip()
    plaintiff_name_upper = plaintiff_name.upper()
    defendant_name_upper = defendant_name.upper()
    
    # For the ss: line - default to New York if not provided
    state_signed = data.get('stateSigned', 'NEW YORK').strip().upper()
    county_signed = data.get('countySigned', county_name).strip().upper()
    
    # Service method for UD-4a: "personal" or "mail"
    service_method = data.get('serviceMethod', '').lower()
    
    # UD-4a fill-in fields (optional - blank if not provided)
    server_name = data.get('serverName', '').strip()
    server_address = data.get('serverAddress', '').strip()
    service_date = data.get('serviceDate', '').strip()
    service_address = data.get('serviceAddress', '').strip()
    
    # Determine if we're filling in or leaving blank
    manual_fill = data.get('manualFill', False)
    
    # =========================================================================
    # PAGE 1: UD-4 Sworn Statement
    # =========================================================================
    
    y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
    
    # Header
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT
    
    # Dashed line with X (top of caption)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT
    
    # Plaintiff name
    c.setFont("Times-Roman", 12)
    fit_text(c, f"{plaintiff_name_upper},", MARGIN_LEFT, y, (PAGE_WIDTH/2 + 95) - (MARGIN_LEFT) - 12)  # a long name must never overprint the right caption column
    
    # Index No. (right side)
    index_number = data.get('indexNumber', '').strip()
    index_display = index_number if index_number else "_______________"
    c.drawString(PAGE_WIDTH/2 + 95, y, f"Index No.: {index_display}")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    
    # Document title — wrapped INSIDE the caption column. The hand-split
    # "REMOVAL OF BARRIERS" line was wider than the column and ran to x=544
    # (QA 2026-08-04); caption_title re-splits to fit.
    after = caption_title(c, "SWORN STATEMENT OF REMOVAL OF BARRIERS TO REMARRIAGE", y)
    y = after + LINE_HEIGHT * 0.7  # preserve the old left-column flow position
    
    # Defendant name
    c.setFont("Times-Roman", 12)
    fit_text(c, f"{defendant_name_upper},", MARGIN_LEFT, y, (PAGE_WIDTH/2 + 95) - (MARGIN_LEFT) - 12)  # a long name must never overprint the right caption column
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Defendant.")
    y -= LINE_HEIGHT
    
    # Dashed line with X (bottom of caption)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT * 1.5
    
    # State/County line
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"STATE OF {state_signed}, COUNTY OF {county_signed}, ss:")
    y -= LINE_HEIGHT * 2
    
    # Deponent line
    c.drawString(MARGIN_LEFT, y, f"{plaintiff_name}, being duly sworn, deposes and says:")
    y -= LINE_HEIGHT * 2
    
    # Paragraph 1
    c.drawString(MARGIN_LEFT, y, "1.  I am the Plaintiff in this action.")
    y -= LINE_HEIGHT * 2
    
    # Paragraph 2
    c.drawString(MARGIN_LEFT, y, "2.  The parties to this action were married in a religious ceremony.")
    y -= LINE_HEIGHT * 2
    
    # Paragraph 3 - waiver statement
    para3_text = "3.  The Defendant has waived in writing the requirements of DRL §253."
    y = draw_wrapped_text(c, para3_text, MARGIN_LEFT, y, CONTENT_WIDTH, "Times-Italic", 12)
    y -= LINE_HEIGHT * 2
    
    # Affirmation under penalty of perjury
    affirm_text = "I, ________________________ (print or type name), affirm this ___ day of ______, ____, under the penalties of perjury, under the laws of New York, which may include a fine or imprisonment, that the foregoing is true, except as to matters alleged on information and belief and as to those matters I believe it to be true, and I understand that this document may be filed in an action or proceeding in a court of law."
    y = draw_wrapped_text(c, affirm_text, MARGIN_LEFT, y, CONTENT_WIDTH, "Times-Roman", 12)
    y -= LINE_HEIGHT * 3
    
    # Signature line - right side
    sig_x = PAGE_WIDTH / 2 + 20
    c.setLineWidth(0.25)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(sig_x, y, plaintiff_name)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 10)
    c.drawString(sig_x, y, "Plaintiff's Signature")
    
    # Footer
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 20, "(Form UD-4)")
    
    # =========================================================================
    # PAGE 2: UD-4a Affirmation of Service
    # =========================================================================
    
    c.showPage()
    y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
    
    # Header
    c.setFont("Times-Bold", 12)
    center_x = PAGE_WIDTH / 2
    title = "Affirmation of Service"
    c.drawString(center_x - c.stringWidth(title, "Times-Bold", 12)/2, y, title)
    y -= LINE_HEIGHT * 2
    
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT * 1.5
    
    # Caption reference
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"{plaintiff_name} v. {defendant_name}")
    y -= LINE_HEIGHT * 2
    
    # Server declaration - fill in or blank
    server_name_display = server_name if server_name else "_____________________________"
    server_address_display = server_address if server_address else "_____________________________________________________"
    
    server_text = f"{server_name_display} being sworn, says, I am not a party to the action, and am over 18 years of age. I reside at {server_address_display}."
    y = draw_wrapped_text(c, server_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    # Service statement - fill in date or blank
    service_date_display = service_date if service_date else "___________________"
    service_text = f"On {service_date_display}, I served a true copy of the within Sworn Statement of Removal of Barriers to Remarriage on the Defendant:"
    y = draw_wrapped_text(c, service_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    # Service address display
    # 58 underscores: an underscore is 6.2pt in Times 12, and this default is
    # also drawn after "[ ]  personally at " — 58 is the longest run that stays
    # inside the right margin from that deepest indent (174 + 58*6.2 = 534).
    service_address_display = service_address if service_address else "_" * 58
    
    # Option 1 - Personal service
    personal_box = "[X]" if service_method == "personal" else "[ ]"
    if service_method == "personal" and service_address:
        c.drawString(MARGIN_LEFT + 20, y, f"{personal_box}  personally at {service_address_display}")
    else:
        # 58 underscores (see service_address_display above) — the 62-run ended at x=546
        c.drawString(MARGIN_LEFT + 20, y, f"{personal_box}  personally at " + "_" * 58)
    y -= LINE_HEIGHT * 1.5
    
    # OR
    c.setFont("Times-Bold", 12)
    c.drawString(center_x - c.stringWidth("OR", "Times-Bold", 12)/2, y, "OR")
    y -= LINE_HEIGHT * 1.5
    
    # Option 2 - Mail service
    mail_box = "[X]" if service_method == "mail" else "[ ]"
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 20, y, f"{mail_box}  by depositing a true copy thereof enclosed in a post-paid wrapper, in an official")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 35, y, "depository under the exclusive care and custody of the U.S. Postal Service within")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 35, y, "New York State, to the address designated by the Defendant at:")
    y -= LINE_HEIGHT
    if service_method == "mail" and service_address:
        c.drawString(MARGIN_LEFT + 35, y, service_address_display)
    else:
        c.drawString(MARGIN_LEFT + 35, y, "_" * 70)  # 73 ran to x=545, past the margin
    y -= LINE_HEIGHT * 2
    
    # Affirmation - fill in server name or blank
    server_name_affirm = server_name if server_name else "________________________"
    affirm_text = f"I, {server_name_affirm} (print or type name), affirm this ___ day of ______, ____, under the penalties of perjury, under the laws of New York, which may include a fine or imprisonment, that the foregoing is true, except as to matters alleged on information and belief and as to those matters I believe it to be true, and I understand that this document may be filed in an action or proceeding in a court of law."
    y = draw_wrapped_text(c, affirm_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 2
    
    # Server signature - right side
    sig_x = PAGE_WIDTH / 2 + 20
    c.setLineWidth(0.25)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT
    c.drawString(sig_x, y, "Server's Signature")
    y -= LINE_HEIGHT * 2
    
    # OR - Acknowledgment
    c.setFont("Times-Bold", 12)
    c.drawString(center_x - c.stringWidth("OR", "Times-Bold", 12)/2, y, "OR")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Service of the within document is hereby acknowledged.")
    y -= LINE_HEIGHT * 4
    
    # Defendant signature - right side
    sig_x = PAGE_WIDTH / 2 + 20
    c.setLineWidth(0.25)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT
    c.drawString(sig_x, y, "Defendant's Signature")
    
    # Footer
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 20, "(Form UD-4a)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # Test with AI-filled fields
    test_data = {
        "plaintiffName": "JOHN DOE",
        "defendantName": "JANE DOE",
        "county": "Orange",
        "stateSigned": "New York",
        "countySigned": "Orange",
        "indexNumber": "12345/2026",
        "serviceMethod": "mail",
        # AI-filled fields (optional)
        "serverName": "Robert Smith",
        "serverAddress": "789 Elm Street, Newburgh, NY 12550",
        "serviceAddress": "74 Fitzgerald Court, Monroe, NY 10950",
        # "serviceDate": "",  # Leave blank - server fills in when they actually serve
    }
    
    output = generate_ud4(test_data, "/home/claude/test_ud4_output.pdf")
    print(f"Generated: {output}")
