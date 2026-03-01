#!/usr/bin/env python3
"""
DivorceGPT UD-1 (Summons with Notice) PDF Generator
=====================================================

Ported from TypeScript/pdf-lib to Python/ReportLab for unified pipeline.

TWO-BOX LAYOUT:
- BOX 1 (Caption): TOP, RIGHT, BOTTOM borders (no left)
- BOX 2 (Metadata): LEFT border only
- Header: Left-aligned, Bold

County Logic:
- Accepts both 'county' and 'filingCounty' field names
- Automatically strips " County" suffix if present
- Uses qualifying party's county (plaintiff's if both apply)
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import re

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


def title_case(s):
    """Convert string to title case."""
    return ' '.join(word.capitalize() for word in s.split())


def format_address_lines(address):
    """Split address into street line and city/state/zip line."""
    address = address.strip()
    
    # Try: street, City, ST ZIP
    match1 = re.search(r',\s*([^,]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)$', address)
    if match1:
        city_state_zip = match1.group(1).strip()
        street = address[:match1.start()].strip()
        return [street, city_state_zip]
    
    # Try: street, City ST ZIP (no comma before state)
    match2 = re.search(r',\s*([A-Z]{2}\s+\d{5}(?:-\d{4})?)$', address)
    if match2:
        before_state = address[:match2.start()]
        last_comma = before_state.rfind(',')
        if last_comma > 0:
            street = before_state[:last_comma].strip()
            city_state_zip = before_state[last_comma + 1:].strip() + ', ' + match2.group(1).strip()
            return [street, city_state_zip]
    
    return [address]


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


def draw_underlined_text(c, text, x, y, font_name="Times-Roman", font_size=12):
    """Draw text with underline. Returns width of text drawn."""
    c.setFont(font_name, font_size)
    c.drawString(x, y, text)
    width = c.stringWidth(text, font_name, font_size)
    c.line(x, y - 2, x + width, y - 2)
    return width


def generate_ud1(data, output_path):
    """
    Generate UD-1 (Summons with Notice) PDF.
    
    Required DivorceGPT variables:
    - plaintiffName: Plaintiff's full legal name
    - defendantName: Defendant's full legal name
    - county OR filingCounty: NY county where action is filed
    - qualifyingParty: 'plaintiff' or 'defendant'
    - qualifyingAddress: Full address with ZIP code
    - plaintiffAddress: Plaintiff's mailing address with ZIP
    - plaintiffPhone: Phone number (optional)
    
    Date field auto-populated with current date if not provided.
    """
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract and validate variables
    county_name = (data.get('county', '') or data.get('filingCounty', '')).strip()
    # Strip " County" suffix if present
    county_name = re.sub(r'\s+County$', '', county_name, flags=re.IGNORECASE).strip()
    if not county_name:
        raise ValueError("County is required")
    county_upper = county_name.upper()
    county_title = title_case(county_name)
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    if not plaintiff_name:
        raise ValueError("Plaintiff name is required")
    plaintiff_name_upper = plaintiff_name.upper()
    
    defendant_name = data.get('defendantName', '').strip()
    if not defendant_name:
        raise ValueError("Defendant name is required")
    defendant_name_upper = defendant_name.upper()
    
    qualifying_party = data.get('qualifyingParty', '').strip().lower()
    if not qualifying_party:
        raise ValueError("Qualifying party is required")
    qualifying_party_label = 'Plaintiff' if qualifying_party == 'plaintiff' else 'Defendant'
    
    qualifying_address = data.get('qualifyingAddress', '').strip()
    if not qualifying_address:
        raise ValueError("Qualifying address is required")
    
    plaintiff_address = data.get('plaintiffAddress', '').strip()
    if not plaintiff_address:
        raise ValueError("Plaintiff address is required")
    
    plaintiff_phone = data.get('plaintiffPhone', '').strip()
    
    date_filed = data.get('dateFiled', '').strip()
    if not date_filed:
        date_filed = datetime.now().strftime('%B %d, %Y')
    
    qual_addr_lines = format_address_lines(qualifying_address)
    plaintiff_addr_lines = format_address_lines(plaintiff_address)
    
    # =========================================================================
    # PAGE 1
    # =========================================================================
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Header - Bold, left aligned
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT * 0.5
    
    # =========================================================================
    # TWO-BOX CAPTION
    # =========================================================================
    boxes_top_y = y
    
    # --- BOX 2 CONTENT (right side - drives box height) ---
    box2_content_x = BOX2_LEFT_X + 8
    box2_max_width = BOX2_RIGHT_X - box2_content_x - 8
    y2 = boxes_top_y - LINE_HEIGHT
    
    c.setFont("Times-Roman", 12)
    c.drawString(box2_content_x, y2, "Index No.:")
    y2 -= LINE_HEIGHT * 2
    
    c.drawString(box2_content_x, y2, "Date Summons filed:")
    y2 -= LINE_HEIGHT * 2
    
    # "Plaintiff designates [County] County as the place of trial"
    part1 = "Plaintiff designates "
    county_display = f"{county_title} County"
    part1b = " as the place of trial"
    
    full_width1 = (c.stringWidth(part1, "Times-Roman", 12) +
                   c.stringWidth(county_display, "Times-Roman", 12) +
                   c.stringWidth(part1b, "Times-Roman", 12))
    
    if full_width1 <= box2_max_width:
        c.drawString(box2_content_x, y2, part1)
        x_pos = box2_content_x + c.stringWidth(part1, "Times-Roman", 12)
        w = draw_underlined_text(c, county_display, x_pos, y2)
        c.setFont("Times-Roman", 12)
        c.drawString(x_pos + w, y2, part1b)
    else:
        c.drawString(box2_content_x, y2, part1)
        x_pos = box2_content_x + c.stringWidth(part1, "Times-Roman", 12)
        draw_underlined_text(c, county_display, x_pos, y2)
        y2 -= LINE_HEIGHT
        c.setFont("Times-Roman", 12)
        c.drawString(box2_content_x, y2, "as the place of trial")
    y2 -= LINE_HEIGHT
    
    # "The basis of the venue is: [Party]'s address"
    venue_p1 = "The basis of the venue is: "
    venue_p2 = f"{qualifying_party_label}'s address"
    
    full_width2 = (c.stringWidth(venue_p1, "Times-Roman", 12) +
                   c.stringWidth(venue_p2, "Times-Roman", 12))
    
    if full_width2 <= box2_max_width:
        c.drawString(box2_content_x, y2, venue_p1)
        x_pos = box2_content_x + c.stringWidth(venue_p1, "Times-Roman", 12)
        draw_underlined_text(c, venue_p2, x_pos, y2)
    else:
        c.drawString(box2_content_x, y2, venue_p1)
        y2 -= LINE_HEIGHT
        draw_underlined_text(c, venue_p2, box2_content_x, y2)
    y2 -= LINE_HEIGHT * 2
    
    # SUMMONS WITH NOTICE (centered, bold, underlined)
    c.setFont("Times-Bold", 12)
    summons_text = "SUMMONS WITH NOTICE"
    summons_width = c.stringWidth(summons_text, "Times-Bold", 12)
    box2_center = BOX2_LEFT_X + (BOX2_RIGHT_X - BOX2_LEFT_X) / 2
    draw_underlined_text(c, summons_text, box2_center - summons_width / 2, y2, "Times-Bold")
    y2 -= LINE_HEIGHT * 2
    
    # "[Party] resides at:" + address
    c.setFont("Times-Roman", 12)
    c.drawString(box2_content_x, y2, f"{qualifying_party_label} resides at:")
    y2 -= LINE_HEIGHT
    
    c.drawString(box2_content_x, y2, qual_addr_lines[0] if qual_addr_lines else '')
    if len(qual_addr_lines) > 1:
        y2 -= LINE_HEIGHT
        c.drawString(box2_content_x, y2, qual_addr_lines[1])
    
    boxes_bottom_y = y2 - 8
    
    # --- BOX 1 CONTENT (left side - caption, vertically distributed) ---
    box1_content_x = BOX1_LEFT_X + 8
    box_height = boxes_top_y - boxes_bottom_y
    
    # Equal spacing: plaintiff at 20%, -against- at 50%, defendant at 80%
    plaintiff_y = boxes_top_y - box_height * 0.2
    against_y = boxes_top_y - box_height * 0.5
    defendant_y = boxes_top_y - box_height * 0.8
    
    c.setFont("Times-Roman", 12)
    c.drawString(box1_content_x, plaintiff_y, plaintiff_name_upper + ',')
    c.drawString(box1_content_x + 40, against_y, '-against-')
    c.drawString(box1_content_x, defendant_y, defendant_name_upper + '.')
    
    # --- DRAW BOX BORDERS ---
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    
    # BOX 1: TOP, RIGHT, BOTTOM (no left)
    c.line(BOX1_LEFT_X, boxes_top_y, BOX1_RIGHT_X, boxes_top_y)       # top
    c.line(BOX1_RIGHT_X, boxes_top_y, BOX1_RIGHT_X, boxes_bottom_y)   # right
    c.line(BOX1_LEFT_X, boxes_bottom_y, BOX1_RIGHT_X, boxes_bottom_y) # bottom
    
    # BOX 2: LEFT only
    c.line(BOX2_LEFT_X, boxes_top_y, BOX2_LEFT_X, boxes_bottom_y)     # left
    
    # =========================================================================
    # ACTION FOR A DIVORCE
    # =========================================================================
    y = boxes_bottom_y - LINE_HEIGHT * 1.5
    
    c.setFont("Times-Bold", 12)
    action_text = "ACTION FOR A DIVORCE"
    action_width = c.stringWidth(action_text, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - action_width) / 2, y, action_text)
    
    y -= LINE_HEIGHT * 1.5
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT, y, "To the above named Defendant:")
    y -= LINE_HEIGHT * 1.5
    
    # =========================================================================
    # YOU ARE HEREBY SUMMONED + body paragraph
    # =========================================================================
    bold_part = "YOU ARE HEREBY SUMMONED "
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT + 36, y, bold_part)
    bold_width = c.stringWidth(bold_part, "Times-Bold", 12)
    
    rest_text = (
        "to serve a notice of appearance on the Plaintiff within twenty (20) days "
        "after the service of this summons, exclusive of the day of service (or within "
        "thirty (30) days after the service is complete if this summons is not personally "
        "delivered to you within the State of New York); and in case of your failure to "
        "appear, judgment will be taken against you by default for the relief demanded "
        "in the notice set forth below."
    )
    
    # Word wrap the rest text, starting after the bold part on first line
    c.setFont("Times-Roman", 12)
    words = rest_text.split()
    current_line = ''
    first_line = True
    start_x = MARGIN_LEFT + 36 + bold_width
    max_width = CONTENT_WIDTH - 36 - bold_width
    
    for word in words:
        test_line = (current_line + ' ' + word) if current_line else word
        test_width = c.stringWidth(test_line, "Times-Roman", 12)
        
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                c.drawString(start_x, y, current_line)
                y -= LINE_HEIGHT
            current_line = word
            if first_line:
                first_line = False
                start_x = MARGIN_LEFT
                max_width = CONTENT_WIDTH
    
    if current_line:
        c.drawString(start_x, y, current_line)
        y -= LINE_HEIGHT
    
    # =========================================================================
    # Dated: and Signature Block
    # =========================================================================
    y -= LINE_HEIGHT * 2
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"Dated: {date_filed}")
    
    sig_x = BOX2_LEFT_X + 8
    c.setLineWidth(0.5)
    c.line(sig_x, y - 3, PAGE_WIDTH - MARGIN_RIGHT, y - 3)
    
    # Name below signature line (title case, not all caps)
    y -= LINE_HEIGHT
    plaintiff_name_title = title_case(plaintiff_name)
    c.drawString(sig_x, y, plaintiff_name_title)
    
    y -= LINE_HEIGHT
    c.drawString(sig_x, y, plaintiff_addr_lines[0] if plaintiff_addr_lines else '')
    y -= LINE_HEIGHT
    
    if len(plaintiff_addr_lines) > 1:
        c.drawString(sig_x, y, plaintiff_addr_lines[1])
        y -= LINE_HEIGHT
    
    if plaintiff_phone:
        c.drawString(sig_x, y, plaintiff_phone)
    
    # =========================================================================
    # NOTICE Section
    # =========================================================================
    y -= LINE_HEIGHT * 2
    
    c.setFont("Times-Bold", 12)
    draw_underlined_text(c, "NOTICE:", MARGIN_LEFT, y, "Times-Bold")
    
    notice_indent = MARGIN_LEFT + 72
    c.setFont("Times-Roman", 12)
    c.drawString(notice_indent, y, "The nature of this action is to dissolve the marriage between the parties, on the")
    
    y -= LINE_HEIGHT
    c.drawString(notice_indent, y, "grounds: DRL§170 subd.7 – ")
    
    grounds_x = notice_indent + c.stringWidth("grounds: DRL§170 subd.7 – ", "Times-Roman", 12)
    grounds_text = "irretrievable breakdown in relationship for a"
    c.setFont("Times-Bold", 12)
    c.drawString(grounds_x, y, grounds_text)
    grounds_width = c.stringWidth(grounds_text, "Times-Bold", 12)
    c.line(grounds_x, y - 2, grounds_x + grounds_width, y - 2)
    
    y -= LINE_HEIGHT
    grounds_text2 = "period at least six months"
    c.drawString(notice_indent, y, grounds_text2)
    grounds_width2 = c.stringWidth(grounds_text2, "Times-Bold", 12)
    c.line(notice_indent, y - 2, notice_indent + grounds_width2, y - 2)
    
    # =========================================================================
    # Relief Sought
    # =========================================================================
    y -= LINE_HEIGHT * 2
    
    c.setFont("Times-Roman", 12)
    relief_text = (
        "The relief sought is a judgment of absolute divorce in favor of the Plaintiff "
        "dissolving the marriage between the parties in this action."
    )
    y = draw_wrapped_text(c, relief_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    
    # =========================================================================
    # Ancillary Relief
    # =========================================================================
    y -= LINE_HEIGHT
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "The nature of any ancillary or additional relief requested is:")
    y -= LINE_HEIGHT * 2
    
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "NONE")
    none_width = c.stringWidth("NONE", "Times-Bold", 12)
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + none_width + 4, y, "– I am not requesting any ancillary relief.")
    
    # =========================================================================
    # FOOTER
    # =========================================================================
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 20, "UD-1 (Summons with Notice)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "plaintiffName": "JAKE KIM",
        "defendantName": "JANE DOE",
        "county": "Orange",
        "qualifyingParty": "plaintiff",
        "qualifyingAddress": "74 Fitzgerald Court, Monroe, NY 10950",
        "plaintiffAddress": "74 Fitzgerald Court, Monroe, NY 10950",
        "plaintiffPhone": "(201) 917-2944",
    }
    
    output = generate_ud1(test_data, "/tmp/test_ud1.pdf")
    print(f"Generated: {output}")
