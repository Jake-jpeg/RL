#!/usr/bin/env python3
"""
DivorceGPT NJ - Acknowledgment of Service

Per R. 4:4-6. Defendant acknowledges receipt of the Summons, Complaint,
and all accompanying documents. Has the same effect as personal service.

Signed by the Defendant.
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


def generate_nj_acknowledgment(data, output_path):
    """
    Generate NJ Acknowledgment of Service.

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
        "ACKNOWLEDGMENT OF SERVICE",
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
    # BODY
    # =====================================================================
    c.setFont(FONT, FONT_SIZE)

    para_indent = 36
    para_x = MARGIN_LEFT + para_indent
    para_width = CONTENT_WIDTH - para_indent

    # 1. Identity
    c.drawString(MARGIN_LEFT, y, "1.")
    y = draw_wrapped_justified(c,
        f"I, {d_name}, am the Defendant in the above captioned matter.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 2. Acknowledge receipt
    c.drawString(MARGIN_LEFT, y, "2.")
    y = draw_wrapped_justified(c,
        "I hereby acknowledge that I have received a copy of the Summons and "
        "Complaint for Divorce, together with all accompanying documents filed "
        "in this action.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 3. Understand right to respond
    c.drawString(MARGIN_LEFT, y, "3.")
    y = draw_wrapped_justified(c,
        "I understand that I have thirty-five (35) days from the date of this "
        "Acknowledgment to file an Answer, Counterclaim, or Appearance with "
        "the court.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 4. Waive formal service
    c.drawString(MARGIN_LEFT, y, "4.")
    y = draw_wrapped_justified(c,
        "I waive formal service of process by the Sheriff or other authorized "
        "process server, and I accept service of the above documents voluntarily.",
        para_x, y, para_width, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.2

    # 5. Understand effect
    c.drawString(MARGIN_LEFT, y, "5.")
    y = draw_wrapped_justified(c,
        "I understand that this Acknowledgment of Service has the same legal "
        "effect as if I had been personally served with these documents, pursuant "
        "to R. 4:4-6.",
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
    y -= DOUBLE_SPACE * 2.5

    sig_x = PAGE_WIDTH / 2 + 20
    c.setLineWidth(0.5)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT

    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "Dated: _______________")
    c.drawString(sig_x, y, d_name)
    y -= LINE_HEIGHT

    c.setFont(FONT_ITALIC, FONT_SIZE)
    c.drawString(sig_x, y, "Defendant")

    draw_page_number(c, 1, 2)

    # =====================================================================
    # PAGE 2 — VERIFICATION (Notary Jurat)
    # =====================================================================
    c.showPage()
    y = PAGE_HEIGHT - MARGIN_TOP

    # Title — centered, bold, underlined
    c.setFont(FONT_BOLD, FONT_SIZE)
    title = "NOTARIZATION"
    title_w = c.stringWidth(title, FONT_BOLD, FONT_SIZE)
    title_x = (PAGE_WIDTH - title_w) / 2
    c.drawString(title_x, y, title)
    # Underline
    c.setLineWidth(0.5)
    c.line(title_x, y - 1.5, title_x + title_w, y - 1.5)
    y -= DOUBLE_SPACE * 2

    # State / SS / County block with brackets
    bracket_x = MARGIN_LEFT + 250
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "STATE OF ________________________")
    c.drawString(bracket_x, y, ")")
    y -= LINE_HEIGHT
    c.drawString(bracket_x, y, ") SS.")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "COUNTY OF ________________________")
    c.drawString(bracket_x, y, ")")
    y -= DOUBLE_SPACE * 1.5

    # BE IT REMEMBERED paragraph
    y = draw_wrapped_justified(c,
        f"BE IT REMEMBERED that on this ________ day of ________________________, "
        f"20____, before me, the subscriber, a Notary Public, personally appeared "
        f"{d_name_upper}, who, I am satisfied, is the person named in the foregoing "
        f"Acknowledgment of Service, to whom I first made known the contents thereof, "
        f"and thereupon the party acknowledged that the party signed, sealed, and "
        f"delivered the same as the party's voluntary act and deed, for the uses and "
        f"purposes therein expressed.",
        MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)

    y -= DOUBLE_SPACE * 3

    # All notary elements — right side
    sig_x = PAGE_WIDTH / 2 + 20

    # "Subscribed and sworn to before me"
    c.setFont(FONT, FONT_SIZE)
    c.drawString(sig_x, y, "Subscribed and sworn to before me")
    y -= LINE_HEIGHT
    c.drawString(sig_x, y, "on:")

    y -= DOUBLE_SPACE * 2

    # Notary signature line
    c.setLineWidth(0.5)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT

    c.setFont(FONT, FONT_SIZE)
    c.drawString(sig_x, y, "Notary Public")
    y -= DOUBLE_SPACE

    # Commission expires with line
    c.drawString(sig_x, y, "My Commission Expires:")
    y -= LINE_HEIGHT * 0.5
    c.setLineWidth(0.5)
    c.line(sig_x + c.stringWidth("My Commission Expires: ", FONT, FONT_SIZE), y + LINE_HEIGHT * 0.5, PAGE_WIDTH - MARGIN_RIGHT, y + LINE_HEIGHT * 0.5)

    y -= DOUBLE_SPACE * 2.5

    # Notary stamp area — right side
    c.setFont(FONT_ITALIC, 10)
    c.drawString(sig_x, y, "(Notary Stamp / Seal)")
    y -= LINE_HEIGHT * 4

    # Box for stamp — right side
    c.setLineWidth(0.3)
    c.setDash(3, 3)
    c.rect(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT - sig_x, 80)
    c.setDash()

    draw_page_number(c, 2, 2)
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
    output = generate_nj_acknowledgment(test_data, "/tmp/test_nj_acknowledgment.pdf")
    print(f"Generated: {output}")
