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
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Header
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT * 1.5
    
    # Caption box
    boxes_top_y = y
    box_height = LINE_HEIGHT * 8
    boxes_bottom_y = boxes_top_y - box_height
    
    # Draw box borders
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    
    # Left box (caption) - top, right, bottom borders
    c.line(BOX1_LEFT_X, boxes_top_y, BOX1_RIGHT_X, boxes_top_y)
    c.line(BOX1_RIGHT_X, boxes_top_y, BOX1_RIGHT_X, boxes_bottom_y)
    c.line(BOX1_LEFT_X, boxes_bottom_y, BOX1_RIGHT_X, boxes_bottom_y)
    
    # Right box - left border only (creates divider)
    c.line(BOX2_LEFT_X, boxes_top_y, BOX2_LEFT_X, boxes_bottom_y)
    
    # Left box content - Caption
    box1_x = BOX1_LEFT_X + 8
    caption_y = boxes_top_y - LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(box1_x, caption_y, f"{plaintiff_name},")
    caption_y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(box1_x + 40, caption_y, "Plaintiff,")
    caption_y -= LINE_HEIGHT * 1.5
    c.setFont("Times-Roman", 12)
    c.drawString(box1_x + 40, caption_y, "-against-")
    caption_y -= LINE_HEIGHT * 1.5
    c.drawString(box1_x, caption_y, f"{defendant_name}.")
    caption_y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(box1_x + 40, caption_y, "Defendant.")
    
    # Right box content - Title
    box2_x = BOX2_LEFT_X + 8
    title_y = boxes_top_y - LINE_HEIGHT * 1.5
    
    # Index Number - required at this phase
    index_number = data.get('indexNumber', '').strip()
    c.setFont("Times-Roman", 12)
    if index_number:
        c.drawString(box2_x, title_y, f"Index No.: {index_number}")
    else:
        c.drawString(box2_x, title_y, "Index No.: _______________")
    title_y -= LINE_HEIGHT * 2
    
    c.setFont("Times-Bold", 12)
    # Center the title in the right box
    title_text = "SWORN STATEMENT OF"
    title_width = c.stringWidth(title_text, "Times-Bold", 12)
    box2_center = BOX2_LEFT_X + (BOX2_RIGHT_X - BOX2_LEFT_X) / 2
    c.drawString(box2_center - title_width/2, title_y, title_text)
    title_y -= LINE_HEIGHT
    
    title_text2 = "REMOVAL OF BARRIERS"
    title_width2 = c.stringWidth(title_text2, "Times-Bold", 12)
    c.drawString(box2_center - title_width2/2, title_y, title_text2)
    title_y -= LINE_HEIGHT
    
    title_text3 = "TO REMARRIAGE"
    title_width3 = c.stringWidth(title_text3, "Times-Bold", 12)
    c.drawString(box2_center - title_width3/2, title_y, title_text3)
    
    # Body content
    y = boxes_bottom_y - LINE_HEIGHT * 2
    
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
    para3_text = "3.  The Defendant has waived in writing the requirements of DRL §253 (Barriers to Remarriage). A copy of said waiver is attached."
    y = draw_wrapped_text(c, para3_text, MARGIN_LEFT, y, CONTENT_WIDTH, "Times-Italic", 12)
    y -= LINE_HEIGHT * 2
    
    # Affirmation under penalty of perjury
    affirm_text = "I, ________________________ (print or type name), affirm this ___ day of ______, ____, under the penalties of perjury, under the laws of New York, which may include a fine or imprisonment, that the foregoing is true, except as to matters alleged on information and belief and as to those matters I believe it to be true, and I understand that this document may be filed in an action or proceeding in a court of law."
    y = draw_wrapped_text(c, affirm_text, MARGIN_LEFT, y, CONTENT_WIDTH, "Times-Roman", 12)
    y -= LINE_HEIGHT * 3
    
    # Signature line
    c.line(MARGIN_LEFT, y, MARGIN_LEFT + 250, y)
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, plaintiff_name)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 10)
    c.drawString(MARGIN_LEFT, y, "Plaintiff's Signature")
    
    # Footer
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 20, "Form UD-4 (Rev. 02/2026)")
    
    # =========================================================================
    # PAGE 2: UD-4a Affirmation of Service
    # =========================================================================
    
    c.showPage()
    y = PAGE_HEIGHT - MARGIN_TOP
    
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
    service_address_display = service_address if service_address else "______________________________________________________________"
    
    # Option 1 - Personal service
    personal_box = "[X]" if service_method == "personal" else "[ ]"
    if service_method == "personal" and service_address:
        c.drawString(MARGIN_LEFT + 20, y, f"{personal_box}  personally at {service_address_display}")
    else:
        c.drawString(MARGIN_LEFT + 20, y, f"{personal_box}  personally at ______________________________________________________________")
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
        c.drawString(MARGIN_LEFT + 35, y, "_________________________________________________________________________")
    y -= LINE_HEIGHT * 2
    
    # Affirmation - fill in server name or blank
    server_name_affirm = server_name if server_name else "________________________"
    affirm_text = f"I, {server_name_affirm} (print or type name), affirm this ___ day of ______, ____, under the penalties of perjury, under the laws of New York, which may include a fine or imprisonment, that the foregoing is true, except as to matters alleged on information and belief and as to those matters I believe it to be true, and I understand that this document may be filed in an action or proceeding in a court of law."
    y = draw_wrapped_text(c, affirm_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 2
    
    # Server signature
    c.line(MARGIN_LEFT, y, MARGIN_LEFT + 250, y)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Server's Signature")
    y -= LINE_HEIGHT * 2
    
    # OR - Acknowledgment
    c.setFont("Times-Bold", 12)
    c.drawString(center_x - c.stringWidth("OR", "Times-Bold", 12)/2, y, "OR")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Service of the within document is hereby acknowledged.")
    y -= LINE_HEIGHT * 4
    
    # Defendant signature
    c.line(MARGIN_LEFT, y, MARGIN_LEFT + 250, y)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Defendant's Signature")
    
    # Footer
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 20, "Form UD-4a (Rev. 02/2026)")
    
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
