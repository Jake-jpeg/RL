#!/usr/bin/env python3
"""
DivorceGPT NJ - Certification of Verification and Non-Collusion

Jake's template format:
- Pro se header: name (bold), Plaintiff, Pro-Se (italic), address, city/state/zip, phone
- 3-column caption: parties | colons | court info (centered except docket)
- Box 1: top/left/bottom borders only. Box 2: no borders.
- Body: "I, [Name], of full age, certify as follows:"
- Numbered paragraphs 1-3, double-spaced, flush left, justified
- R. 1:4-4(b) certification language
- Signature line right, Dated left
- Page numbers bottom center
- US Letter, 1-inch margins
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN_LEFT = 72
MARGIN_RIGHT = 72
MARGIN_TOP = 72
MARGIN_BOTTOM = 72
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

LINE_HEIGHT = 14.5
DOUBLE_SPACE = 24
FONT_SIZE = 12
FONT = "Times-Roman"
FONT_BOLD = "Times-Bold"
FONT_ITALIC = "Times-Italic"


def draw_wrapped_justified(c, text, x, y, max_width, font_name=FONT, font_size=FONT_SIZE, line_height=DOUBLE_SPACE):
    """Draw justified wrapped text. Returns final Y position after last line."""
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
                lines.append(current_line)
            current_line = [word]
            current_width = word_width
    if current_line:
        lines.append(current_line)

    for i, line_words in enumerate(lines):
        is_last = (i == len(lines) - 1)
        if is_last or len(line_words) == 1:
            c.drawString(x, y, ' '.join(line_words))
        else:
            text_width = sum(c.stringWidth(w, font_name, font_size) for w in line_words)
            total_space = max_width - text_width
            gap = total_space / (len(line_words) - 1)
            cx = x
            for word in line_words:
                c.drawString(cx, y, word)
                cx += c.stringWidth(word, font_name, font_size) + gap
        y -= line_height

    return y


def draw_page_number(c, page_num, total_pages):
    """Draw page number centered at bottom."""
    c.setFont(FONT, 10)
    text = f"Page {page_num} of {total_pages}"
    w = c.stringWidth(text, FONT, 10)
    c.drawString((PAGE_WIDTH - w) / 2, MARGIN_BOTTOM - 24, text)


def generate_nj_verification(data, output_path):
    """
    Generate NJ Certification of Verification and Non-Collusion.

    Required data:
    - plaintiffName
    - plaintiffAddress
    - plaintiffCityStateZip
    - plaintiffPhone
    - defendantName
    - filingCounty
    - docketNumber (optional)
    """

    c = canvas.Canvas(output_path, pagesize=letter)

    p_name = data.get('plaintiffName', '').strip()
    p_address = data.get('plaintiffAddress', '').strip()
    p_city_state_zip = data.get('plaintiffCityStateZip', '').strip()
    p_phone = data.get('plaintiffPhone', '').strip()
    d_name = data.get('defendantName', '').strip()
    filing_county = data.get('filingCounty', '').strip().upper()
    docket = data.get('docketNumber', '').strip()
    if not docket:
        docket = 'FM-'

    total_pages = 1  # single page form

    y = PAGE_HEIGHT - MARGIN_TOP

    # =====================================================================
    # PRO SE HEADER BLOCK
    # =====================================================================
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, p_name)
    y -= LINE_HEIGHT

    c.setFont(FONT_ITALIC, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "Plaintiff, Pro-Se")
    y -= LINE_HEIGHT

    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, p_address)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, p_city_state_zip)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"Phone: {p_phone}")
    y -= LINE_HEIGHT * 0.5

    # =====================================================================
    # CAPTION TABLE
    # =====================================================================
    caption_top_y = y

    col1_x = MARGIN_LEFT
    col1_width = 220
    col2_x = col1_x + col1_width
    col2_width = 14
    col3_x = col2_x + col2_width

    # Left column
    left_lines = [
        "",
        f"{p_name.upper()},",
        "Plaintiff,",
        "",
        "     vs.",
        "",
        "",
        f"{d_name.upper()},",
        "Defendant.",
        "",
    ]

    # Right column (blank line between county and docket)
    right_lines = [
        "",
        "SUPERIOR COURT OF NEW JERSEY",
        "CHANCERY DIVISION- FAMILY PART",
        f"{filing_county} COUNTY",
        "",
        f"DOCKET NO.:  {docket}",
        "",
        "CERTIFICATION OF VERIFICATION",
        "AND NON-COLLUSION",
    ]

    num_lines = max(len(left_lines), len(right_lines))
    caption_bottom_y = caption_top_y - (num_lines * LINE_HEIGHT) + (LINE_HEIGHT * 0.5)

    # Lines to center in right column (all except docket)
    docket_line_text = f"DOCKET NO.:  {docket}"

    c.setFont(FONT, FONT_SIZE)
    for i in range(num_lines):
        row_y = caption_top_y - (i * LINE_HEIGHT)

        if i < len(left_lines) and left_lines[i]:
            c.drawString(col1_x + 4, row_y, left_lines[i])

        # Only draw colons within the border lines
        if row_y < caption_top_y and row_y > caption_bottom_y:
            c.drawString(col2_x + 2, row_y, ":")

        if i < len(right_lines) and right_lines[i]:
            text = right_lines[i]
            # Title lines come after the blank line after docket (index 7+)
            is_title = (i >= 7)
            draw_font = FONT_BOLD if is_title else FONT
            c.setFont(draw_font, FONT_SIZE)
            if text == docket_line_text:
                c.drawString(col3_x + 4, row_y, text)
            else:
                text_w = c.stringWidth(text, draw_font, FONT_SIZE)
                box2_right = MARGIN_LEFT + CONTENT_WIDTH
                center_x = col3_x + (box2_right - col3_x - text_w) / 2
                c.drawString(center_x, row_y, text)
            c.setFont(FONT, FONT_SIZE)

    # Borders — Box 1 only: top, left, bottom
    c.setLineWidth(0.5)
    c.line(col1_x, caption_top_y, col1_x + col1_width, caption_top_y)
    c.line(col1_x, caption_top_y, col1_x, caption_bottom_y)
    c.line(col1_x, caption_bottom_y, col1_x + col1_width, caption_bottom_y)

    y = caption_bottom_y - LINE_HEIGHT * 2

    # =====================================================================
    # BODY
    # =====================================================================
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, f"I, {p_name}, of full age, certify as follows:")
    y -= DOUBLE_SPACE * 1.2

    # Numbered paragraphs — flush left, double-spaced
    num_w = c.stringWidth("1.  ", FONT, FONT_SIZE)

    c.drawString(MARGIN_LEFT, y, "1.  ")
    y = draw_wrapped_justified(c, "I am the plaintiff in the foregoing complaint.",
                                MARGIN_LEFT + num_w, y, CONTENT_WIDTH - num_w,
                                line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.1

    c.drawString(MARGIN_LEFT, y, "2.  ")
    y = draw_wrapped_justified(c,
        "The allegations of the complaint are true to the best of my knowledge, "
        "information, and belief. The complaint is made in truth and good faith and "
        "without collusion for the causes set forth therein.",
        MARGIN_LEFT + num_w, y, CONTENT_WIDTH - num_w,
        line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.1

    c.drawString(MARGIN_LEFT, y, "3.  ")
    y = draw_wrapped_justified(c,
        "The matter in controversy in the within action is not the subject of any other "
        "action pending in any court or of a pending arbitration proceeding, nor is any "
        "such court action or arbitration proceeding presently contemplated. There are "
        "no other persons who should be joined in this action at this time.",
        MARGIN_LEFT + num_w, y, CONTENT_WIDTH - num_w,
        line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.5

    # =====================================================================
    # CERTIFICATION LANGUAGE
    # =====================================================================
    y = draw_wrapped_justified(c,
        "I certify that the foregoing statements made by me are true. I am aware "
        "that if any of the foregoing statements made by me are willfully false, I am "
        "subject to punishment.",
        MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)

    # =====================================================================
    # SIGNATURE BLOCK
    # =====================================================================
    y -= DOUBLE_SPACE * 2.5

    sig_x = PAGE_WIDTH / 2 + 20
    c.setLineWidth(0.5)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)

    y -= LINE_HEIGHT

    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "Dated: _______________")
    c.drawString(sig_x, y, p_name)
    y -= LINE_HEIGHT

    c.setFont(FONT_ITALIC, FONT_SIZE)
    c.drawString(sig_x, y, "Plaintiff, Pro-Se")

    # =====================================================================
    # PAGE NUMBER
    # =====================================================================
    draw_page_number(c, 1, total_pages)

    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "plaintiffName": "John Doe",
        "plaintiffAddress": "2460 Lemoine Avenue",
        "plaintiffCityStateZip": "Fort Lee, NJ 07024",
        "plaintiffPhone": "(201) 800-4564",
        "defendantName": "Jane Doe",
        "filingCounty": "Bergen",
        "docketNumber": "",
    }

    output = generate_nj_verification(test_data, "/tmp/test_nj_verification.pdf")
    print(f"Generated: {output}")
