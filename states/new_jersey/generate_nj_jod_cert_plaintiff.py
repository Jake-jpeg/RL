#!/usr/bin/env python3
"""
DivorceGPT NJ - Plaintiff's Certification in Support of Judgment of Divorce
Without a Court Appearance

Per Directive #01-25 (03/19/2025), CN 12620.
Scoped for DivorceGPT: uncontested, no children, no property, no alimony.
Only applicable paragraphs included.
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
    c.setFont(FONT, 10)
    text = f"Page {page_num} of {total_pages}"
    w = c.stringWidth(text, FONT, 10)
    c.drawString((PAGE_WIDTH - w) / 2, MARGIN_BOTTOM - 24, text)


def generate_nj_jod_cert_plaintiff(data, output_path):
    """
    Generate Plaintiff's Certification in Support of JOD Without Court Appearance.

    Required data:
    - plaintiffName, plaintiffAddress, plaintiffCityStateZip, plaintiffPhone
    - defendantName
    - filingCounty
    - docketNumber (optional)
    """

    c = canvas.Canvas(output_path, pagesize=letter)

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

    total_pages = 2
    page_num = 1

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
    col3_x = col2_x + 14

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
        "PLAINTIFF'S CERTIFICATION IN",
        "SUPPORT OF JUDGMENT OF DIVORCE",
        "WITHOUT A COURT APPEARANCE",
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

    c.setLineWidth(0.5)
    c.line(col1_x, caption_top_y, col1_x + col1_width, caption_top_y)
    c.line(col1_x, caption_top_y, col1_x, caption_bottom_y)
    c.line(col1_x, caption_bottom_y, col1_x + col1_width, caption_bottom_y)

    y = caption_bottom_y - LINE_HEIGHT * 2

    # =====================================================================
    # BODY — Opening
    # =====================================================================
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, f"I, {p_name}, of full age, hereby certify:")
    y -= DOUBLE_SPACE * 1.2

    # =====================================================================
    # SECTION I: CAUSE OF ACTION
    # =====================================================================
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "I.  Cause of Action")
    y -= DOUBLE_SPACE

    para_indent = 36
    para_x = MARGIN_LEFT + para_indent
    para_width = CONTENT_WIDTH - para_indent

    # Sub-indent for lettered items under numbered paragraphs
    sub_indent = 54
    sub_x = MARGIN_LEFT + sub_indent
    sub_width = CONTENT_WIDTH - sub_indent

    c.setFont(FONT, FONT_SIZE)

    # 1. Plaintiff filing certification
    c.drawString(MARGIN_LEFT, y, "1.")
    y = draw_wrapped_justified(c,
        "I am the Plaintiff, and I am filing this Certification in support of my "
        "request for a Judgment of Divorce without appearing in court.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 1(a)
    c.drawString(para_x, y, "a.")
    y = draw_wrapped_justified(c,
        "I filed a Complaint for Divorce.",
        sub_x, y, sub_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 1(b)
    c.drawString(para_x, y, "b.")
    y = draw_wrapped_justified(c,
        "I certify to the truth of the Complaint.",
        sub_x, y, sub_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 1(c)
    c.drawString(para_x, y, "c.")
    y = draw_wrapped_justified(c,
        "The Defendant filed an Acknowledgment of Service.",
        sub_x, y, sub_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 1(e)
    c.drawString(para_x, y, "d.")
    y = draw_wrapped_justified(c,
        "I do not want to reconcile with the Defendant.",
        sub_x, y, sub_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.3

    # 2. Waive right to trial
    c.drawString(MARGIN_LEFT, y, "2.")
    y = draw_wrapped_justified(c,
        "I am aware that I have a right to a trial, and I am waiving that right.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 3. Aware outcome could differ
    c.drawString(MARGIN_LEFT, y, "3.")
    y = draw_wrapped_justified(c,
        "I am aware that if there is a trial, the outcome could be different.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 4. No other cases
    c.drawString(MARGIN_LEFT, y, "4.")
    y = draw_wrapped_justified(c,
        "There are no other closed or open cases in this court or any other court "
        "between me and the other party.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 5. No property to divide
    c.drawString(MARGIN_LEFT, y, "5.")
    y = draw_wrapped_justified(c,
        "No property was bought, owned, or received during the marriage that needs "
        "to be legally divided.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 6. Not seeking child support/custody
    c.drawString(MARGIN_LEFT, y, "6.")
    y = draw_wrapped_justified(c,
        "I am not seeking child support, custody, or parenting time.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)

    # =====================================================================
    # PAGE BREAK
    # =====================================================================
    draw_page_number(c, 1, total_pages)
    c.showPage()
    page_num = 2
    y = PAGE_HEIGHT - MARGIN_TOP

    c.setFont(FONT, FONT_SIZE)

    # 7. Further certifications
    c.drawString(MARGIN_LEFT, y, "7.")
    y = draw_wrapped_justified(c,
        "I further certify to the following:",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 7(a)
    c.drawString(para_x, y, "a.")
    y = draw_wrapped_justified(c,
        "There is no other property or debt to be divided.",
        sub_x, y, sub_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 7(b)
    c.drawString(para_x, y, "b.")
    y = draw_wrapped_justified(c,
        "There are no other issues between the Plaintiff and Defendant.",
        sub_x, y, sub_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 1.0

    # =====================================================================
    # CERTIFICATION LANGUAGE
    # =====================================================================
    c.setFont(FONT, FONT_SIZE)
    y = draw_wrapped_justified(c,
        "I certify that the statements made by me are true. I am aware that if any "
        "of the statements made by me are willfully false, I am subject to punishment "
        "by the court.",
        MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 1.0

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

    draw_page_number(c, page_num, total_pages)
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
    output = generate_nj_jod_cert_plaintiff(test_data, "/tmp/test_nj_jod_cert_plaintiff.pdf")
    print(f"Generated: {output}")
