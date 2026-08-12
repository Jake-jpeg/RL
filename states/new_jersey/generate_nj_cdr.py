#!/usr/bin/env python3
"""
DivorceGPT NJ - Self-Represented Litigant Certification of Notification
of Complementary Dispute Resolution (CDR) Alternatives

Per R. 5:4-2(h) / CN 10889.

Two versions generated:
- Plaintiff version: checkbox on Plaintiff, plaintiff name/signature
- Defendant version: checkbox on Defendant, defendant name/signature

Same caption format as other NJ forms.
Body text is verbatim from the official CN 10889 form.
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


def _draw_cdr_form(c, data, party_type):
    """
    Draw a single CDR certification form.
    party_type: "plaintiff" or "defendant"
    """

    p_name = data.get('plaintiffName', '').strip()
    p_name_upper = p_name.upper()
    p_address = data.get('plaintiffAddress', '').strip()
    p_city_state_zip = data.get('plaintiffCityStateZip', '').strip()
    p_phone = data.get('plaintiffPhone', '').strip()

    d_name = data.get('defendantName', '').strip()
    d_name_upper = d_name.upper()

    filing_county = data.get('filingCounty', '').strip().upper()
    docket = data.get('docketNumber', '').strip()
    if not docket:
        docket = 'FM-'

    # The certifying party
    if party_type == "plaintiff":
        certifying_name = p_name
    else:
        certifying_name = d_name

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
        "SELF-REPRESENTED LITIGANT",
        "CERTIFICATION OF NOTIFICATION",
        "OF COMPLEMENTARY DISPUTE",
        "RESOLUTION (CDR) ALTERNATIVES",
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
            if text == docket_line_text:
                c.drawString(col3_x + 4, row_y, text)
            else:
                text_w = c.stringWidth(text, FONT, FONT_SIZE)
                box2_right = MARGIN_LEFT + CONTENT_WIDTH
                center_x = col3_x + (box2_right - col3_x - text_w) / 2
                c.drawString(center_x, row_y, text)

    # Borders — Box 1 only
    c.setLineWidth(0.5)
    c.line(col1_x, caption_top_y, col1_x + col1_width, caption_top_y)
    c.line(col1_x, caption_top_y, col1_x, caption_bottom_y)
    c.line(col1_x, caption_bottom_y, col1_x + col1_width, caption_bottom_y)

    y = caption_bottom_y - LINE_HEIGHT * 2

    # =====================================================================
    # BODY — Opening line
    # =====================================================================
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, f"{certifying_name}, being of full age, hereby certifies as follows:")
    y -= DOUBLE_SPACE * 1.2

    # =====================================================================
    # NUMBERED PARAGRAPHS — hanging indent
    # =====================================================================
    para_indent = 36
    para_x = MARGIN_LEFT + para_indent
    para_width = CONTENT_WIDTH - para_indent

    # 1. Plaintiff/Defendant checkbox
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "1.")

    # Build the text with checkbox indicators
    if party_type == "plaintiff":
        checkbox_text = "I am the [X] Plaintiff / [  ] Defendant in the above captioned matter, and I am not represented by an attorney."
    else:
        checkbox_text = "I am the [  ] Plaintiff / [X] Defendant in the above captioned matter, and I am not represented by an attorney."

    y = draw_wrapped_justified(c, checkbox_text, para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.1

    # 2. Certification pursuant to rule
    c.drawString(MARGIN_LEFT, y, "2.")
    y = draw_wrapped_justified(c,
        "I make this Certification pursuant to New Jersey Court Rule 5:4-2(h).",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.1

    # 3. Read the document — with underlined title
    c.drawString(MARGIN_LEFT, y, "3.")

    # First part before the underlined title
    part1 = 'I have read the document titled, "'
    c.setFont(FONT, FONT_SIZE)
    c.drawString(para_x, y, part1)
    cx = para_x + c.stringWidth(part1, FONT, FONT_SIZE)

    # Underlined document title — may wrap
    underline_title = "Descriptive Material (R. 5:4-2(h)) Divorce or Dissolution - Dispute Resolution Alternatives to Conventional Litigation."
    closing = '"'

    # Draw the full paragraph as wrapped text since the underlined title is long
    full_para3 = (
        'I have read the document titled, "Descriptive Material (R. 5:4-2(h)) '
        'Divorce or Dissolution - Dispute Resolution Alternatives to Conventional '
        'Litigation." (CN 10888)'
    )
    y = draw_wrapped_justified(c, full_para3, para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.1

    # 4. Understand other options
    c.drawString(MARGIN_LEFT, y, "4.")
    y = draw_wrapped_justified(c,
        "I understand that there are other options available to resolve the issues "
        "in this case instead of going to trial.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
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
    y -= DOUBLE_SPACE * 2

    # Two signature lines side by side: Date left, Signature right
    date_line_x = MARGIN_LEFT
    date_line_width = 180
    sig_line_x = PAGE_WIDTH / 2 + 20
    sig_line_width = PAGE_WIDTH - MARGIN_RIGHT - sig_line_x

    c.setLineWidth(0.5)
    c.line(date_line_x, y, date_line_x + date_line_width, y)
    c.line(sig_line_x, y, sig_line_x + sig_line_width, y)

    y -= LINE_HEIGHT

    c.setFont(FONT, FONT_SIZE)
    c.drawString(date_line_x, y, "Date")
    c.drawString(sig_line_x, y, "Signature")

    # =====================================================================
    # PAGE NUMBER
    # =====================================================================
    draw_page_number(c, 1, 1)


def generate_nj_cdr_plaintiff(data, output_path):
    """Generate CDR Certification for the Plaintiff."""
    c = canvas.Canvas(output_path, pagesize=letter)
    _draw_cdr_form(c, data, "plaintiff")
    c.save()
    return output_path


def generate_nj_cdr_defendant(data, output_path):
    """Generate CDR Certification for the Defendant."""
    c = canvas.Canvas(output_path, pagesize=letter)
    _draw_cdr_form(c, data, "defendant")
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "plaintiffName": "John Doe",
        "plaintiffAddress": "81 East Crescent Avenue",
        "plaintiffCityStateZip": "Mahwah, NJ 07430",
        "plaintiffPhone": "(201) 800-4564",
        "defendantName": "Jane Doe",
        "filingCounty": "Bergen",
        "docketNumber": "",
    }

    output1 = generate_nj_cdr_plaintiff(test_data, "/tmp/test_nj_cdr_plaintiff.pdf")
    print(f"Generated Plaintiff: {output1}")

    output2 = generate_nj_cdr_defendant(test_data, "/tmp/test_nj_cdr_defendant.pdf")
    print(f"Generated Defendant: {output2}")
