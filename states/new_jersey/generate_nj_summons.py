#!/usr/bin/env python3
"""
DivorceGPT NJ - Summons

Standardized summons language per Appendix XII-A / R. 4:4-2.
Clerk: Michelle M. Smith, Esq.
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

INDENT = 36


def draw_indented_justified(c, text, x, y, max_width, font_name=FONT, font_size=FONT_SIZE, line_height=DOUBLE_SPACE):
    c.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(' ', font_name, font_size)
    first_line = True

    for word in words:
        word_width = c.stringWidth(word, font_name, font_size)
        line_max = (max_width - INDENT) if first_line else max_width
        test_width = current_width + word_width + (space_width if current_line else 0)
        if test_width <= line_max:
            current_line.append(word)
            current_width = test_width
        else:
            if current_line:
                lines.append((current_line, first_line))
                first_line = False
            current_line = [word]
            current_width = word_width
    if current_line:
        lines.append((current_line, first_line))

    for i, (line_words, is_indented) in enumerate(lines):
        is_last = (i == len(lines) - 1)
        lx = (x + INDENT) if is_indented else x
        lw = (max_width - INDENT) if is_indented else max_width

        if is_last or len(line_words) == 1:
            c.drawString(lx, y, ' '.join(line_words))
        else:
            text_width = sum(c.stringWidth(w, font_name, font_size) for w in line_words)
            total_space = lw - text_width
            gap = total_space / (len(line_words) - 1)
            cx = lx
            for word in line_words:
                c.drawString(cx, y, word)
                cx += c.stringWidth(word, font_name, font_size) + gap
        y -= line_height
    return y


def draw_justified(c, text, x, y, max_width, font_name=FONT, font_size=FONT_SIZE, line_height=LINE_HEIGHT):
    """Draw paragraph justified, no indent."""
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


def generate_nj_summons(data, output_path):
    """
    Generate NJ Summons.

    Required data:
    - plaintiffName, plaintiffAddress, plaintiffCityStateZip, plaintiffPhone
    - defendantName, defendantAddress, defendantCityStateZip
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
    d_address = data.get('defendantAddress', '').strip()
    d_city_state_zip = data.get('defendantCityStateZip', '').strip()
    filing_county = data.get('filingCounty', '').strip().upper()
    docket = data.get('docketNumber', '').strip()
    if not docket:
        docket = 'FM-'

    total_pages = 2

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
        "CIVIL ACTION",
        "",
        "SUMMONS",
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

    y = caption_bottom_y - LINE_HEIGHT * 1.5

    SINGLE_SPACE = LINE_HEIGHT  # single-spaced body for summons

    # =====================================================================
    # "STATE OF NEW JERSEY / TO THE DEFENDANT(S)..."
    # =====================================================================
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "STATE OF NEW JERSEY")
    y -= SINGLE_SPACE
    c.drawString(MARGIN_LEFT, y, f"TO THE DEFENDANT(S) NAMED ABOVE:")
    # Defendant name on same line, regular weight
    prefix = "TO THE DEFENDANT(S) NAMED ABOVE:"
    prefix_w = c.stringWidth(prefix, FONT_BOLD, FONT_SIZE)
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT + prefix_w + 20, y, d_name_upper)
    y -= SINGLE_SPACE * 1.5

    c.setFont(FONT, FONT_SIZE)

    # =====================================================================
    # BODY — Verbatim Appendix XII-A, single-spaced
    # =====================================================================

    # Paragraph 1: Notice + 35-day + directory reference
    para1 = (
        "The plaintiff, named above, has filed a lawsuit against you in the "
        "Superior Court of New Jersey. The complaint attached to this summons "
        "states the basis for this lawsuit. If you dispute this complaint, you "
        "or your attorney must file a written answer or motion and proof of "
        "service with the deputy clerk of the Superior Court in the county "
        "listed above within 35 days from the date you received this summons, "
        "not counting the date you received it. (A directory of the addresses "
        "of each deputy clerk of the Superior Court is available in the Civil "
        "Division Management Office in the county listed above and online at "
        "http://www.njcourts.gov.)"
    )
    y = draw_justified(c, para1, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=SINGLE_SPACE)
    y -= SINGLE_SPACE * 0.8

    # Paragraph 2: Foreclosure + filing fee + CIS
    para2 = (
        "If the complaint is one in foreclosure, then you must file your "
        "written answer or motion and proof of service with the Clerk of the "
        "Superior Court, Hughes Justice Complex, P.O. Box 971, Trenton, NJ "
        "08625-0971. A filing fee payable to the Treasurer, State of New "
        "Jersey and a completed Case Information Statement (available from the "
        "deputy clerk of the Superior Court) must accompany your answer or "
        "motion when it is filed. You must also send a copy of your answer or "
        "motion to plaintiff's attorney whose name and address appear above, "
        "or to plaintiff, if no attorney is named above. A telephone call will "
        "not protect your rights; you must file and serve a written answer or "
        "motion (with fee of $175.00 and completed Case Information Statement) "
        "if you want the court to hear your defense."
    )
    y = draw_justified(c, para2, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=SINGLE_SPACE)
    y -= SINGLE_SPACE * 0.8

    # Paragraph 3: Default warning
    para3 = (
        "If you do not file and serve a written answer or motion within 35 "
        "days, the court may enter a judgment against you for the relief "
        "plaintiff demands, plus interest and costs of suit. If judgment is "
        "entered against you, the Sheriff may seize your money, wages or "
        "property to pay all or part of the judgment."
    )
    y = draw_justified(c, para3, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=SINGLE_SPACE)

    # =====================================================================
    # PAGE BREAK
    # =====================================================================
    draw_page_number(c, 1, total_pages)
    c.showPage()
    y = PAGE_HEIGHT - MARGIN_TOP
    c.setFont(FONT, FONT_SIZE)

    # Paragraph 4: Legal services / lawyer referral + URL (page 2)
    para4 = (
        "If you cannot afford an attorney, you may call the Legal Services "
        "office in the county where you live or the Legal Services of New "
        "Jersey Statewide Hotline at 1-888-LSNJ-LAW (1-888-576-5529). If you "
        "do not have an attorney and are not eligible for free legal "
        "assistance, you may obtain a referral to an attorney by calling one "
        "of the Lawyer Referral Services. A directory with contact information "
        "for local Legal Services Offices and Lawyer Referral Services is "
        "available in the Civil Division Management Office in the county "
        "listed above and online at "
        "http://www.njcourts.gov."
    )
    y = draw_justified(c, para4, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=SINGLE_SPACE)
    y -= DOUBLE_SPACE * 1.5

    # =====================================================================
    # CLERK SIGNATURE BLOCK — /s/ above line, name below
    # =====================================================================
    sig_x = PAGE_WIDTH / 2 + 20
    sig_width = PAGE_WIDTH - MARGIN_RIGHT - sig_x

    c.setFont(FONT_ITALIC, FONT_SIZE)
    c.drawString(sig_x, y, "/s/ Michelle M. Smith")
    y -= LINE_HEIGHT * 0.8

    c.setLineWidth(0.5)
    c.line(sig_x, y, sig_x + sig_width, y)
    y -= LINE_HEIGHT

    c.setFont(FONT, FONT_SIZE)
    c.drawString(sig_x, y, "Michelle M. Smith, Esq.")
    y -= LINE_HEIGHT
    c.drawString(sig_x, y, "Clerk of the Superior Court")
    y -= DOUBLE_SPACE

    c.drawString(MARGIN_LEFT, y, "Dated: _______________")
    y -= DOUBLE_SPACE * 2

    # =====================================================================
    # DEFENDANT SERVICE INFORMATION — v1 style
    # =====================================================================
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "Name of defendant to be served:")
    y -= LINE_HEIGHT
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, d_name)
    y -= DOUBLE_SPACE

    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, "Address of defendant to be served:")
    y -= LINE_HEIGHT
    c.setFont(FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y, d_address)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, d_city_state_zip)

    draw_page_number(c, 2, total_pages)
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "plaintiffName": "John Doe",
        "plaintiffAddress": "81 East Crescent Avenue",
        "plaintiffCityStateZip": "Mahwah, NJ 07430",
        "plaintiffPhone": "(201) 800-4564",
        "defendantName": "Jane Doe",
        "defendantAddress": "425 Main Street, Apt 3B",
        "defendantCityStateZip": "Hackensack, NJ 07601",
        "filingCounty": "Bergen",
        "docketNumber": "",
    }
    output = generate_nj_summons(test_data, "/tmp/test_nj_summons.pdf")
    print(f"Generated: {output}")
