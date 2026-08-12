#!/usr/bin/env python3
"""
DivorceGPT NJ - Proposed Final Judgment of Divorce

Uncontested, dissolution only. No children, no property, no alimony,
no prior orders. Decided on the papers per Directive #01-25.

This is a PROPOSED judgment — submitted to the court for the judge's
signature. The judge signs it; the parties do not.
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


INDENT = 36  # 0.5 inch first-line indent


def draw_para_bold_prefix(c, bold_text, rest_text, x, y, max_width, line_height=DOUBLE_SPACE):
    """
    Draw a paragraph with:
    - 0.5" first-line indent
    - Bold prefix on first line, then regular text continues
    - All lines justified, subsequent lines at left margin (x)
    """
    indent_x = x + INDENT
    indent_width = max_width - INDENT

    # Build all words with font tags: ('word', font_name)
    bold_words = [(w, FONT_BOLD) for w in bold_text.split()]
    rest_words = [(w, FONT) for w in rest_text.split()]
    all_words = bold_words + rest_words

    # Word-wrap into lines
    lines = []
    current_line = []
    current_width = 0
    first_line = True

    for word, font in all_words:
        w_width = c.stringWidth(word, font, FONT_SIZE)
        space_w = c.stringWidth(' ', font, FONT_SIZE)
        test_width = current_width + w_width + (space_w if current_line else 0)
        line_max = indent_width if first_line else max_width

        if test_width <= line_max:
            current_line.append((word, font))
            current_width = test_width
        else:
            if current_line:
                lines.append(current_line)
                first_line = False
            current_line = [(word, font)]
            current_width = w_width
    if current_line:
        lines.append(current_line)

    # Draw lines
    for i, line_words in enumerate(lines):
        is_first = (i == 0)
        is_last = (i == len(lines) - 1)
        lx = indent_x if is_first else x
        lw = indent_width if is_first else max_width

        if is_last or len(line_words) == 1:
            cx = lx
            for word, font in line_words:
                c.setFont(font, FONT_SIZE)
                c.drawString(cx, y, word)
                cx += c.stringWidth(word, font, FONT_SIZE) + c.stringWidth(' ', font, FONT_SIZE)
        else:
            text_width = sum(c.stringWidth(w, f, FONT_SIZE) for w, f in line_words)
            total_space = lw - text_width
            gap = total_space / (len(line_words) - 1)
            cx = lx
            for word, font in line_words:
                c.setFont(font, FONT_SIZE)
                c.drawString(cx, y, word)
                cx += c.stringWidth(word, font, FONT_SIZE) + gap
        y -= line_height

    c.setFont(FONT, FONT_SIZE)
    return y


def draw_page_number(c, page_num, total_pages=None):
    """total_pages=None renders "Page N" — used by the dynamic flow, which
    cannot know the total while drawing. A wrong "of 2" is worse than none."""
    c.setFont(FONT, 10)
    text = (f"Page {page_num} of {total_pages}" if total_pages else f"Page {page_num}")
    w = c.stringWidth(text, FONT, 10)
    c.drawString((PAGE_WIDTH - w) / 2, MARGIN_BOTTOM - 36, text)


def generate_nj_jod(data, output_path):
    """
    Generate NJ Proposed Final Judgment of Divorce.

    Required data:
    - plaintiffName, plaintiffAddress, plaintiffCityStateZip, plaintiffPhone
    - defendantName
    - filingCounty
    - docketNumber (optional)
    - marriageDate
    - ceremonyType ("civil" or "religious")
    - ceremonyLocation
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
    marriage_date = data.get('marriageDate', '').strip()
    ceremony_type = data.get('ceremonyType', 'civil').strip().lower()
    ceremony_location = data.get('ceremonyLocation', '').strip()
    ceremony_label = "religious" if ceremony_type == "religious" else "civil"

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
        "FINAL JUDGMENT OF DIVORCE",
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

    # Opening recital — bold "THIS MATTER"
    recital_rest = (
        f"having been opened to the Court by Plaintiff, "
        f"{p_name_upper}, appearing pro se, and Defendant, {d_name_upper}, "
        f"appearing pro se; and the Court having considered the Complaint for "
        f"Divorce and the Certifications in Support of Judgment of Divorce "
        f"Without a Court Appearance filed by both parties; and it appearing "
        f"that the parties were married on {marriage_date} in a {ceremony_label} "
        f"ceremony in {ceremony_location}; and that the parties having proved "
        f"a cause of action for divorce under N.J.S.A. 2A:34-2; in such case "
        f"made and provided, entitling the parties to be granted a Judgment of "
        f"Divorce; and it further appearing that the parties have been a bona fide "
        f"resident of the State of New Jersey for more than one year next preceding "
        f"the commencement of this action, and jurisdiction having been acquired "
        f"over the parties pursuant to the Rules governing the Court; and for good "
        f"cause shown;"
    )
    _pg = [1]
    def _room(y, lines=3):
        """Page-break guard. The old flow drew page 1 with NO guard and a
        hard-coded 2-page total; the QA fixture's longer names wrapped the
        recital deeper and the ORDERED paragraph printed to y=787 — 25pt from
        the paper's edge, THROUGH the page number (QA 2026-08-05)."""
        if y < MARGIN_BOTTOM + lines * DOUBLE_SPACE:
            draw_page_number(c, _pg[0])
            c.showPage()
            _pg[0] += 1
            c.setFont(FONT, FONT_SIZE)
            return PAGE_HEIGHT - MARGIN_TOP - 10
        return y

    y = draw_para_bold_prefix(c, "THIS MATTER", recital_rest, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.5

    # "It is therefore..."
    therefore_rest = (
        f"on this __________ day of ________________________, "
        f"20____, by the Superior Court of New Jersey, Chancery Division, Family "
        f"Part, {filing_county} County, State of New Jersey;"
    )
    y = _room(y)
    y = draw_para_bold_prefix(c, "", f"It is therefore {therefore_rest.strip()}", MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.5

    # Dissolution order — bold "ORDERED and ADJUDGED"
    dissolution_rest = (
        f"that this Court, by virtue of the power and "
        f"authority of this Court and of the acts of the Legislature in such case "
        f"made and provided, does hereby order that the Plaintiff, {p_name_upper}, "
        f"and the Defendant, {d_name_upper}, be divorced from the bond of matrimony "
        f"for the cause aforesaid, and that the parties and each of them be freed "
        f"from the obligations thereof and that the marriage between the parties is "
        f"hereby dissolved; and it is further"
    )
    y = _room(y, 4)
    y = draw_para_bold_prefix(c, "ORDERED and ADJUDGED", dissolution_rest, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)

    # =====================================================================
    # PAGE BREAK
    # =====================================================================
    # The old hard page break lived here, with page totals fixed at 2.
    # Pagination is dynamic now — the remaining decrees start a fresh page
    # only when they need one.
    y = _room(y, 6)

    # No alimony
    alimony_rest = (
        "that neither party shall have an alimony "
        "obligation to the other; and it is further"
    )
    y = _room(y)
    y = draw_para_bold_prefix(c, "ORDERED AND ADJUDGED,", alimony_rest, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.5

    # No equitable distribution
    equitable_rest = (
        "that there is no equitable distribution between the parties "
        "in that there is no real property, personal property nor any debt to "
        "be divided between them; and it is further"
    )
    y = _room(y)
    y = draw_para_bold_prefix(c, "ORDERED", equitable_rest, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.5

    # On the papers
    papers_rest = (
        "that this case was decided based on the papers filed and "
        "without a court hearing; and it is further"
    )
    y = draw_para_bold_prefix(c, "ORDERED", papers_rest, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.5

    # Abandoned issues
    abandoned_rest = (
        "that all issues pleaded and not resolved in "
        "this Judgment are deemed abandoned; and it is further"
    )
    y = draw_para_bold_prefix(c, "ORDERED and ADJUDGED", abandoned_rest, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 0.5

    # Service of judgment
    service_rest = (
        "that a copy of the within Judgment shall be "
        "served upon all parties within seven (7) days of its receipt from "
        "the Court."
    )
    y = draw_para_bold_prefix(c, "ORDERED and ADJUDGED", service_rest, MARGIN_LEFT, y, CONTENT_WIDTH, line_height=DOUBLE_SPACE)
    y -= DOUBLE_SPACE * 3.5

    # =====================================================================
    # JUDGE SIGNATURE BLOCK
    # =====================================================================
    sig_x = PAGE_WIDTH / 2 + 20
    sig_width = PAGE_WIDTH - MARGIN_RIGHT - sig_x

    c.setLineWidth(0.5)
    c.line(sig_x, y, sig_x + sig_width, y)
    y -= LINE_HEIGHT

    c.setFont(FONT, FONT_SIZE)
    c.drawString(sig_x, y, "Hon. ________________________, J.S.C.")

    draw_page_number(c, _pg[0])
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
        "marriageDate": "July 11, 2006",
        "ceremonyType": "civil",
        "ceremonyLocation": "the Borough of Fort Lee, State of New Jersey",
    }
    output = generate_nj_jod(test_data, "/tmp/test_nj_jod.pdf")
    print(f"Generated: {output}")
