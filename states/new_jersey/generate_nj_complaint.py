#!/usr/bin/env python3
"""
DivorceGPT NJ - Complaint for Divorce
Based on Irreconcilable Differences (N.J.S.A. 2A:34-2)

Same caption format as Verification Cert:
- Pro se header, 3-column caption, Box 1 borders only
- Title: "COMPLAINT FOR DIVORCE" (centered in Box 2)
- Body: numbered paragraphs with legal allegations
- WHEREFORE relief block
- Signature line right, Dated left
- Page numbers bottom center
- US Letter, 1-inch margins, justified, double-spaced
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


def draw_mixed_text(c, segments, x, y, font_size=FONT_SIZE):
    """
    Draw text with mixed formatting on a single line.
    segments = [(text, font_name), (text, font_name), ...]
    Returns x position after last segment.
    """
    cx = x
    for text, font_name in segments:
        c.setFont(font_name, font_size)
        c.drawString(cx, y, text)
        cx += c.stringWidth(text, font_name, font_size)
    return cx


def draw_underlined_text(c, text, x, y, font_name=FONT, font_size=FONT_SIZE):
    """Draw underlined text. Returns x after text."""
    c.setFont(font_name, font_size)
    c.drawString(x, y, text)
    w = c.stringWidth(text, font_name, font_size)
    c.setLineWidth(0.4)
    c.line(x, y - 1.5, x + w, y - 1.5)
    return x + w


def draw_page_number(c, page_num, total_pages):
    """Draw page number centered at bottom."""
    c.setFont(FONT, 10)
    text = f"Page {page_num} of {total_pages}"
    w = c.stringWidth(text, FONT, 10)
    c.drawString((PAGE_WIDTH - w) / 2, MARGIN_BOTTOM - 24, text)


def check_page_break(c, y, needed, page_num, total_pages):
    """Check if we need a page break. Returns new y and page_num."""
    if y - needed < MARGIN_BOTTOM + 30:
        draw_page_number(c, page_num, total_pages)
        c.showPage()
        page_num += 1
        y = PAGE_HEIGHT - MARGIN_TOP - 10  # cap tops ON the margin line (same fix as NY layout.py)
    return y, page_num


def generate_nj_complaint(data, output_path):
    """
    Generate NJ Complaint for Divorce.

    Required data:
    - plaintiffName
    - plaintiffAddress (street)
    - plaintiffCityStateZip (abbreviated for header: "Mahwah, NJ 07430")
    - plaintiffPhone
    - plaintiffFullCityState (for body text: "Mahwah, New Jersey")
    - defendantName
    - defendantAddress (street)
    - defendantCityStateZip (abbreviated for header)
    - defendantFullCityState (for body text: "Mahwah, New Jersey")
    - filingCounty
    - docketNumber (optional)
    - marriageDate
    - ceremonyType ("civil" or "religious")
    - ceremonyLocation (e.g., "the Borough of Fort Lee, State of New Jersey")
    - residencyParty ("plaintiff", "defendant", or "both")
    """

    c = canvas.Canvas(output_path, pagesize=letter)

    # Extract data
    p_name = data.get('plaintiffName', '').strip()
    p_name_upper = p_name.upper()
    p_address = data.get('plaintiffAddress', '').strip()
    p_city_state_zip = data.get('plaintiffCityStateZip', '').strip()
    p_phone = data.get('plaintiffPhone', '').strip()
    p_full_city_state = data.get('plaintiffFullCityState', '').strip()

    d_name = data.get('defendantName', '').strip()
    d_name_upper = d_name.upper()
    d_address = data.get('defendantAddress', '').strip()
    d_city_state_zip = data.get('defendantCityStateZip', '').strip()
    d_full_city_state = data.get('defendantFullCityState', '').strip()

    filing_county = data.get('filingCounty', '').strip().upper()
    docket = data.get('docketNumber', '').strip()
    if not docket:
        docket = 'FM-'

    marriage_date = data.get('marriageDate', '').strip()
    ceremony_type = data.get('ceremonyType', 'civil').strip().lower()
    ceremony_location = data.get('ceremonyLocation', '').strip()

    residency_party = data.get('residencyParty', 'plaintiff').strip().lower()

    total_pages = 2  # complaint + signature
    page_num = 1

    y = PAGE_HEIGHT - MARGIN_TOP - 10  # cap tops ON the margin line (same fix as NY layout.py)

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

    left_lines = [
        "",
        f"{p_name_upper},",
        "Plaintiff,",
        "",
        "     vs.",
        "",
        "",
        f"{d_name_upper},",
        "Defendant.",
        "",
    ]

    right_lines = [
        "",
        "SUPERIOR COURT OF NEW JERSEY",
        "CHANCERY DIVISION- FAMILY PART",
        f"{filing_county} COUNTY",
        "",
        f"DOCKET NO.:  {docket}",
        "",
        "COMPLAINT FOR DIVORCE",
    ]

    num_lines = max(len(left_lines), len(right_lines))
    caption_bottom_y = caption_top_y - (num_lines * LINE_HEIGHT) + (LINE_HEIGHT * 0.5)

    docket_line_text = f"DOCKET NO.:  {docket}"

    c.setFont(FONT, FONT_SIZE)
    for i in range(num_lines):
        row_y = caption_top_y - (i * LINE_HEIGHT)

        if i < len(left_lines) and left_lines[i]:
            c.drawString(col1_x + 4, row_y, left_lines[i])

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

    # Borders — Box 1 only
    c.setLineWidth(0.5)
    c.line(col1_x, caption_top_y, col1_x + col1_width, caption_top_y)
    c.line(col1_x, caption_top_y, col1_x, caption_bottom_y)
    c.line(col1_x, caption_bottom_y, col1_x + col1_width, caption_bottom_y)

    y = caption_bottom_y - LINE_HEIGHT * 2

    # =====================================================================
    # BODY — Opening paragraph
    # =====================================================================
    c.setFont(FONT, FONT_SIZE)

    # Build address strings
    # Header uses abbreviated: "Mahwah, NJ 07430"
    # Body uses full: "81 East Crescent Avenue, Mahwah, New Jersey"
    p_body_address = f"{p_address}, {p_full_city_state}"
    d_body_address = f"{d_address}, {d_full_city_state}"

    opening = (
        f"The Plaintiff, {p_name_upper}, currently residing at {p_body_address}, "
        f"by way of Complaint against the Defendant, {d_name_upper}, says:"
    )
    y = draw_wrapped_justified(c, opening, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.3

    # =====================================================================
    # NUMBERED PARAGRAPHS — hanging indent: number at margin, text at 0.5"
    # =====================================================================
    para_indent = 36  # 0.5 inch from left margin
    para_x = MARGIN_LEFT + para_indent
    para_width = CONTENT_WIDTH - para_indent

    # Helper to draw a numbered paragraph with hanging indent
    def draw_numbered_para(num, text):
        nonlocal y, page_num
        y, page_num = check_page_break(c, y, DOUBLE_SPACE * 3, page_num, total_pages)
        c.setFont(FONT, FONT_SIZE)
        c.drawString(MARGIN_LEFT, y, f"{num}.")
        y_new = draw_wrapped_justified(c, text, para_x, y, para_width, line_height=DOUBLE_SPACE)
        return y_new

    # 1. Marriage
    ceremony_label = "religious" if ceremony_type == "religious" else "civil"
    y = draw_numbered_para(1,
        f"The Plaintiff was lawfully married to Defendant on {marriage_date} "
        f"in a {ceremony_label} ceremony in {ceremony_location}.")
    y -= DOUBLE_SPACE * 0.1

    # 2. Residency — adapts based on who satisfies the requirement
    if residency_party == 'both':
        residency_text = (
            "Both the Plaintiff and the Defendant were bona fide residents of the "
            "State of New Jersey when this cause of action arose and have ever since "
            "and for more than one year next preceding the commencement of this action "
            "continued to be such bona fide residents.")
    elif residency_party == 'defendant':
        residency_text = (
            "The Defendant was a bona fide resident of the State of New Jersey when "
            "this cause of action arose and has ever since and for more than one year "
            "next preceding the commencement of this action continued to be such bona "
            "fide resident.")
    else:
        residency_text = (
            "The Plaintiff was a bona fide resident of the State of New Jersey when "
            "this cause of action arose and has ever since and for more than one year "
            "next preceding the commencement of this action continued to be such bona "
            "fide resident.")
    y = draw_numbered_para(2, residency_text)
    y -= DOUBLE_SPACE * 0.1

    # 3. Plaintiff address
    y = draw_numbered_para(3,
        f"The Plaintiff presently resides at {p_body_address}.")
    y -= DOUBLE_SPACE * 0.1

    # 4. Defendant address
    y = draw_numbered_para(4,
        f"The Defendant presently resides at {d_body_address}.")
    y -= DOUBLE_SPACE * 0.1

    # 5. Venue — per R. 5:7-1, filed in county where plaintiff was domiciled
    #    when cause of action arose
    y = draw_numbered_para(5,
        "At the time the within cause of action arose, the Plaintiff resided in "
        f"the State of New Jersey and, therefore, venue is properly situated in the "
        f"County of {data.get('filingCounty', '').strip()}.")
    y -= DOUBLE_SPACE * 0.1

    # 6. Irreconcilable differences
    y = draw_numbered_para(6,
        "Irreconcilable differences have arisen between the parties, which have caused "
        "the breakdown of the marriage for a period of six (6) months or more and which "
        "make it appear that the marriage should be dissolved. There is no reasonable "
        "prospect of reconciliation.")
    y -= DOUBLE_SPACE * 0.1

    # 7. No assets
    y = draw_numbered_para(7,
        "During the course of the marriage, the Plaintiff and Defendant have NOT "
        "legally and / or beneficially acquired assets, both real and personal, which "
        "may be subject to equitable distribution, pursuant to N.J.S.A. 2A:34-23.1.")
    y -= DOUBLE_SPACE * 0.1

    # 8. No previous proceedings
    y = draw_numbered_para(8,
        "There have been no previous proceedings between the parties hereto respecting "
        "the dissolution of the marriage, or the support or maintenance of either party "
        "in any Court in any State.")
    y -= DOUBLE_SPACE * 0.5

    # =====================================================================
    # WHEREFORE
    # =====================================================================
    y, page_num = check_page_break(c, y, DOUBLE_SPACE * 5, page_num, total_pages)

    c.setFont(FONT, FONT_SIZE)
    y = draw_wrapped_justified(c,
        "WHEREFORE, the Plaintiff demands judgment as follows:",
        MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.3

    # a. Dissolving
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "a.")
    y = draw_wrapped_justified(c,
        "Dissolving the marriage between the parties pursuant to N.J.S.A. 2A:34-2;",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.1

    # b. Other relief
    c.drawString(MARGIN_LEFT, y, "b.")
    y = draw_wrapped_justified(c,
        "Granting such other relief as this Court deems equitable and just.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)

    # =====================================================================
    # SIGNATURE BLOCK
    # =====================================================================
    y -= DOUBLE_SPACE * 2.5

    y, page_num = check_page_break(c, y, DOUBLE_SPACE * 4, page_num, total_pages)

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
    draw_page_number(c, page_num, total_pages)

    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "plaintiffName": "John Doe",
        "plaintiffAddress": "81 East Crescent Avenue",
        "plaintiffCityStateZip": "Mahwah, NJ 07430",
        "plaintiffFullCityState": "Mahwah, New Jersey",
        "plaintiffPhone": "(201) 800-4564",
        "defendantName": "Jane Doe",
        "defendantAddress": "81 East Crescent Avenue",
        "defendantCityStateZip": "Mahwah, NJ 07430",
        "defendantFullCityState": "Mahwah, New Jersey",
        "filingCounty": "Bergen",
        "docketNumber": "",
        "marriageDate": "July 11, 2006",
        "ceremonyType": "civil",
        "ceremonyLocation": "the Borough of Fort Lee, State of New Jersey",
        "residencyParty": "plaintiff",
    }

    output = generate_nj_complaint(test_data, "/tmp/test_nj_complaint.pdf")
    print(f"Generated: {output}")
