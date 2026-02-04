#!/usr/bin/env python3
"""
DivorceGPT UD-5 (Affirmation of Regularity) PDF Generator
==========================================================

Confirms proper service on defendant and case status.
Pro se plaintiff version (no attorney option per DivorceGPT non-lawyer platform).
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


def generate_ud5(data, output_path):
    """Generate UD-5 (Affirmation of Regularity) PDF."""
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract variables
    county_name = data.get('county', '').strip()
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    defendant_name = data.get('defendantName', '').strip()
    index_number = data.get('indexNumber', '').strip()
    
    # Service details
    service_within_ny = data.get('serviceWithinNY', True)  # True = within NY, False = outside NY
    defendant_appeared = data.get('defendantAppeared', True)  # True = appeared, False = default
    
    # For affirmation
    state_signed = data.get('stateSigned', 'NEW YORK').strip().upper()
    county_signed = data.get('countySigned', county_name).strip().upper()
    
    # =========================================================================
    # PAGE 1: UD-5 Affirmation of Regularity
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
    
    # Right box - left border only
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
    
    c.setFont("Times-Roman", 12)
    if index_number:
        c.drawString(box2_x, title_y, f"Index No.: {index_number}")
    else:
        c.drawString(box2_x, title_y, "Index No.: _______________")
    title_y -= LINE_HEIGHT * 2.5
    
    c.setFont("Times-Bold", 12)
    box2_center = BOX2_LEFT_X + (BOX2_RIGHT_X - BOX2_LEFT_X) / 2
    title_text = "AFFIRMATION OF REGULARITY"
    title_width = c.stringWidth(title_text, "Times-Bold", 12)
    c.drawString(box2_center - title_width/2, title_y, title_text)
    
    # Body content
    y = boxes_bottom_y - LINE_HEIGHT * 2
    
    # State/County line
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"STATE OF {state_signed}, COUNTY OF {county_signed}, ss:")
    y -= LINE_HEIGHT * 2
    
    # Paragraph 1 - I am the Plaintiff (no attorney option - pro se platform)
    c.drawString(MARGIN_LEFT, y, "1.  I am the Plaintiff herein. This is a matrimonial action.")
    y -= LINE_HEIGHT * 2
    
    # Paragraph 2 - Service statement
    service_location = "within" if service_within_ny else "outside"
    para2_text = f"2.  The Summons with Notice and the Notice of Automatic Orders and the Notice of Guideline Maintenance were personally served upon the Defendant herein, {service_location} the State of New York as appears in the affidavit or affirmation of service submitted herewith."
    y = draw_wrapped_text(c, para2_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    # Paragraph 3 - Defendant status
    if defendant_appeared:
        para3_text = "3.  Defendant has appeared on his or her own behalf and executed an affidavit or affirmation that this matter be placed on the matrimonial calendar immediately."
    else:
        para3_text = "3.  Defendant is in default for failure to serve a notice of appearance or failure to answer the complaint served in this action in due time, and the time to answer has not been extended by stipulation, court order, or otherwise."
    y = draw_wrapped_text(c, para3_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    # Paragraph 4 - No other actions pending
    para4_text = "4.  No other action or proceeding for divorce, annulment, or dissolution of marriage has been commenced by or against either party in this or any other court."
    y = draw_wrapped_text(c, para4_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    # Paragraph 5 - Papers in order
    para5_text = "5.  The papers submitted herewith are in proper form."
    y = draw_wrapped_text(c, para5_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 2
    
    # Affirmation under penalty of perjury
    affirm_text = "I, ________________________ (print or type name), affirm this ___ day of ______, ____, under the penalties of perjury, under the laws of New York, which may include a fine or imprisonment, that the foregoing is true, except as to matters alleged on information and belief and as to those matters I believe it to be true, and I understand that this document may be filed in an action or proceeding in a court of law."
    y = draw_wrapped_text(c, affirm_text, MARGIN_LEFT, y, CONTENT_WIDTH)
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
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 20, "Form UD-5 (Rev. 02/2026)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Orange",
        "indexNumber": "12345/2027",
        "stateSigned": "New York",
        "countySigned": "Orange",
        "serviceWithinNY": True,
        "defendantAppeared": True,
        # Fill-in fields
        "affirmantName": "Jane Doe",
        "affirmDay": "6th",
        "affirmMonth": "March",
        "affirmYear": "2027",
    }
    
    output = generate_ud5(test_data, "/home/claude/test_ud5_output.pdf")
    print(f"Generated: {output}")
