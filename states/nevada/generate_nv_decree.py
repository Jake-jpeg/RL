#!/usr/bin/env python3
"""
DivorceGPT NV - Decree of Divorce (No Children) PDF Generator
==============================================================

Generates the Nevada Joint Petition Decree of Divorce (No Children) — 3 pages.
Based on the 2022 Nevada Supreme Court standardized form from selfhelp.nvcourts.gov.

NV Decree has line numbers (1-28) on the left margin — standard NV court format.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN_LEFT = 72
MARGIN_RIGHT = 72
MARGIN_TOP = 72
MARGIN_BOTTOM = 72
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
LINE_HEIGHT = 14
INDENT = MARGIN_LEFT + 36

# Line number column
LINE_NUM_X = MARGIN_LEFT - 30
BODY_LEFT = MARGIN_LEFT  # Text starts at left margin (line numbers are in the gutter)


def draw_wrapped_text(c, text, x, y, max_width, font_name="Times-Roman", font_size=12, line_height=LINE_HEIGHT):
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
        y -= line_height
    return y


def draw_underline(c, x, y, width):
    c.setLineWidth(0.5)
    c.line(x, y - 2, x + width, y - 2)


def draw_checkbox(c, x, y, checked=False, size=10):
    c.setLineWidth(0.5)
    c.rect(x, y - 2, size, size, stroke=1, fill=0)
    if checked:
        c.setLineWidth(1)
        c.line(x + 2, y + 2, x + 4, y)
        c.line(x + 4, y, x + 8, y + 7)
        c.setLineWidth(0.5)


def draw_line_numbers(c, start_num, end_num, top_y, line_spacing=24.2):
    """Draw NV court line numbers in the left gutter."""
    c.setFont("Times-Roman", 8)
    y = top_y
    for num in range(start_num, end_num + 1):
        c.drawRightString(LINE_NUM_X + 12, y, str(num))
        y -= line_spacing
    return y


def draw_footer(c, page_num, total_pages=3):
    c.setFont("Times-Roman", 9)
    copyright_text = "\u00a9 2022 Nevada Supreme Court"
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 30, copyright_text)
    page_text = f"Page {page_num} of {total_pages} - Joint Petition Decree of Divorce (No Children)"
    page_width = c.stringWidth(page_text, "Times-Roman", 9)
    c.drawString((PAGE_WIDTH - page_width) / 2, MARGIN_BOTTOM - 45, page_text)


def draw_header_block(c, data, y):
    """Draw self-represented header block."""
    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse1_address = data.get('firstSpouseAddress', '').strip()
    spouse1_csz = data.get('firstSpouseCityStateZip', '').strip()
    spouse1_phone = data.get('firstSpousePhone', '').strip()
    spouse1_email = data.get('firstSpouseEmail', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()
    spouse2_address = data.get('secondSpouseAddress', '').strip()
    spouse2_csz = data.get('secondSpouseCityStateZip', '').strip()
    spouse2_phone = data.get('secondSpousePhone', '').strip()
    spouse2_email = data.get('secondSpouseEmail', '').strip()

    c.setFont("Times-Roman", 10)
    label_x = MARGIN_LEFT
    value_x = MARGIN_LEFT + 90

    c.drawString(label_x, y, "FILING CODE:")
    draw_underline(c, value_x, y, 100)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "Spouse\u2019s Name:")
    c.drawString(value_x, y, spouse1_name)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "Address:")
    c.drawString(value_x, y, spouse1_address)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "City, State, Zip:")
    c.drawString(value_x, y, spouse1_csz)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "Phone:")
    c.drawString(value_x, y, spouse1_phone)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "Email:")
    c.drawString(value_x, y, spouse1_email)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT * 1.2

    c.drawString(label_x, y, "Spouse\u2019s Name:")
    c.drawString(value_x, y, spouse2_name)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "Address:")
    c.drawString(value_x, y, spouse2_address)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "City, State, Zip:")
    c.drawString(value_x, y, spouse2_csz)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "Phone:")
    c.drawString(value_x, y, spouse2_phone)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(label_x, y, "Email:")
    c.drawString(value_x, y, spouse2_email)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Self-Represented")
    y -= LINE_HEIGHT * 1.5
    return y


def generate_nv_decree(data, output_path):
    """
    Generate NV Decree of Divorce (No Children) PDF.

    Uses same data keys as Joint Petition plus:
    - nameChange1, nameChange1MarriedName, nameChange1MaidenName
    - nameChange2, nameChange2MarriedName, nameChange2MaidenName
    """

    c = canvas.Canvas(output_path, pagesize=letter)

    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()
    county = data.get('county', '').strip()
    marriage_date = data.get('marriageDate', '').strip()
    marriage_city = data.get('marriageCity', '').strip()
    marriage_state = data.get('marriageState', '').strip()
    resident_spouse = data.get('residentSpouseName', '').strip()
    name_change1 = data.get('nameChange1', 'none').strip()
    name_change1_married = data.get('nameChange1MarriedName', '').strip()
    name_change1_maiden = data.get('nameChange1MaidenName', '').strip()
    name_change2 = data.get('nameChange2', 'none').strip()
    name_change2_married = data.get('nameChange2MarriedName', '').strip()
    name_change2_maiden = data.get('nameChange2MaidenName', '').strip()

    # =========================================================================
    # PAGE 1
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # Header block
    y = draw_header_block(c, data, y)

    # Caption
    c.setFont("Times-Bold", 12)
    dc_text = "DISTRICT COURT"
    c.drawString((PAGE_WIDTH - c.stringWidth(dc_text, "Times-Bold", 12)) / 2, y, dc_text)
    y -= LINE_HEIGHT * 1.2
    county_text = f"{county.upper()} COUNTY, NEVADA"
    c.drawString((PAGE_WIDTH - c.stringWidth(county_text, "Times-Bold", 12)) / 2, y, county_text)
    y -= LINE_HEIGHT * 2

    # Party names and case info
    caption_mid = PAGE_WIDTH / 2
    box_top = y + LINE_HEIGHT * 0.5

    c.setFont("Times-Roman", 12)
    draw_underline(c, MARGIN_LEFT, y, 240)
    c.drawString(MARGIN_LEFT, y, spouse1_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "First Joint Petitioner (")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth("First Joint Petitioner (", "Times-Roman", 12), y, "Spouse Name")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth("First Joint Petitioner (Spouse Name", "Times-Roman", 12), y, "),")

    # Right side
    right_x = caption_mid + 20
    c.drawString(right_x, y + LINE_HEIGHT, "CASE NO.: ")
    draw_underline(c, right_x + c.stringWidth("CASE NO.: ", "Times-Roman", 12), y + LINE_HEIGHT, 120)
    c.drawString(right_x, y, "DEPT:")
    draw_underline(c, right_x + c.stringWidth("DEPT: ", "Times-Roman", 12), y, 130)

    y -= LINE_HEIGHT * 1.5
    c.drawString(MARGIN_LEFT, y, "And")
    y -= LINE_HEIGHT * 1.5

    draw_underline(c, MARGIN_LEFT, y, 240)
    c.drawString(MARGIN_LEFT, y, spouse2_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Second Joint Petitioner (")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth("Second Joint Petitioner (", "Times-Roman", 12), y, "Spouse Name")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth("Second Joint Petitioner (Spouse Name", "Times-Roman", 12), y, ").")

    box_bottom = y - LINE_HEIGHT * 0.5
    c.setLineWidth(0.5)
    c.line(caption_mid, box_top, caption_mid, box_bottom)

    y = box_bottom - LINE_HEIGHT * 1.5

    # DECREE OF DIVORCE title
    c.setFont("Times-Bold", 12)
    title = "DECREE OF DIVORCE"
    c.drawString((PAGE_WIDTH - c.stringWidth(title, "Times-Bold", 12)) / 2, y, title)
    y -= LINE_HEIGHT * 1.5

    # Draw line numbers for this page
    draw_line_numbers(c, 1, 28, PAGE_HEIGHT - MARGIN_TOP - 12 * LINE_HEIGHT)

    # Body text
    c.setFont("Times-Roman", 12)
    intro = (
        "The above entitled cause, having been submitted to this Court for decision pursuant to Chapter "
        "125 of the Nevada Revised Statutes, and based upon the Joint Petition by the Petitioners, and all "
        "of the papers and pleadings on file, the Court finds as follows:"
    )
    y = draw_wrapped_text(c, intro, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 0.5

    # Numbered findings
    c.drawString(INDENT, y, "1. All of the allegations contained in the documents on file are true;")
    y -= LINE_HEIGHT * 1.2

    c.drawString(INDENT, y, "2. All of the requirements of NRS 125.181 and NRS 125.182 have been met;")
    y -= LINE_HEIGHT * 1.2

    c.drawString(INDENT, y, "3. That (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + c.stringWidth("3. That (", "Times-Roman", 12), y, "name of person who lives in Nevada")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + c.stringWidth("3. That (name of person who lives in Nevada", "Times-Roman", 12), y, ") ")
    name_x = INDENT + c.stringWidth("3. That (name of person who lives in Nevada) ", "Times-Roman", 12)
    c.drawString(name_x, y, resident_spouse)
    draw_underline(c, name_x, y, max(c.stringWidth(resident_spouse, "Times-Roman", 12), 180))
    y -= LINE_HEIGHT
    c.drawString(INDENT + 18, y, "has been a resident of the State of Nevada for at least six weeks immediately prior to the")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 18, y, "commencement of this action.")

    draw_footer(c, 1)
    c.showPage()

    # =========================================================================
    # PAGE 2
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    draw_line_numbers(c, 1, 28, y)

    c.setFont("Times-Roman", 12)

    # 4. Marriage info
    c.drawString(INDENT, y, "4. Petitioners were married on (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + c.stringWidth("4. Petitioners were married on (", "Times-Roman", 12), y, "date")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + c.stringWidth("4. Petitioners were married on (date", "Times-Roman", 12), y, ") ")
    date_x = INDENT + c.stringWidth("4. Petitioners were married on (date) ", "Times-Roman", 12)
    c.drawString(date_x, y, marriage_date)
    draw_underline(c, date_x, y, max(c.stringWidth(marriage_date, "Times-Roman", 12), 130))
    c.drawString(date_x + max(c.stringWidth(marriage_date, "Times-Roman", 12), 130) + 4, y, " in the city of")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 18, y, marriage_city)
    draw_underline(c, INDENT + 18, y, max(c.stringWidth(marriage_city, "Times-Roman", 12), 140))
    c.drawString(INDENT + 18 + max(c.stringWidth(marriage_city, "Times-Roman", 12), 140) + 4, y, ", State of ")
    state_x = INDENT + 18 + max(c.stringWidth(marriage_city, "Times-Roman", 12), 140) + 4 + c.stringWidth(", State of ", "Times-Roman", 12)
    c.drawString(state_x, y, marriage_state)
    draw_underline(c, state_x, y, max(c.stringWidth(marriage_state, "Times-Roman", 12), 100))
    c.drawString(state_x + max(c.stringWidth(marriage_state, "Times-Roman", 12), 100) + 4, y, " and have since remained")
    y -= LINE_HEIGHT
    remain_text = (
        "married. The parties have become, and continue to be, incompatible in marriage, and no "
        "reconciliation is possible. The Petitioners are entitled to a Decree of Divorce."
    )
    y = draw_wrapped_text(c, remain_text, INDENT + 18, y, CONTENT_WIDTH - 54)
    y -= LINE_HEIGHT * 0.5

    # 5. Pregnancy
    c.drawString(INDENT, y, "5. ")
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT + c.stringWidth("5. ", "Times-Roman", 12), y, "Pregnancy.")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + c.stringWidth("5. Pregnancy. ", "Times-Roman", 12), y, "(\u2612 check one)")
    y -= LINE_HEIGHT * 1.5

    draw_checkbox(c, INDENT + 18, y - 2, checked=True)
    c.drawString(INDENT + 32, y, "Neither spouse is pregnant.")
    y -= LINE_HEIGHT * 1.2

    draw_checkbox(c, INDENT + 18, y - 2, checked=False)
    c.drawString(INDENT + 32, y, "One spouse is pregnant. The following spouse is pregnant: ")
    y -= LINE_HEIGHT * 2.5

    # 6. Children
    c.drawString(INDENT, y, "6. ")
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT + c.stringWidth("6. ", "Times-Roman", 12), y, "Children.")
    c.setFont("Times-Roman", 12)
    child_text = " The Petitioners have no minor children in common born to or adopted by the"
    c.drawString(INDENT + c.stringWidth("6. Children.", "Times-Roman", 12), y, child_text)
    y -= LINE_HEIGHT
    c.drawString(INDENT + 18, y, "parties.")
    y -= LINE_HEIGHT * 1.2

    # 7. Property agreement
    text_7 = (
        "7. The Petitioners have entered into an equitable agreement settling all issues regarding the "
        "division and distribution of assets and debts which is outlined in the Joint Petition, a "
        "filed copy of which is attached as Exhibit A. The Petitioners request that this agreement "
        "be ratified, confirmed, and incorporated into this Decree as though fully set forth."
    )
    y = draw_wrapped_text(c, text_7, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 0.3

    # 8. Spousal support agreement
    text_8 = (
        "8. The Petitioners have entered into an equitable agreement settling the issue of spousal "
        "support which is outlined in the Joint Petition, a filed copy of which is attached as "
        "Exhibit A. The Petitioners request that this agreement be ratified, confirmed, and "
        "incorporated into this Decree as though fully set forth."
    )
    y = draw_wrapped_text(c, text_8, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 0.3

    # 9. Jurisdiction
    text_9 = (
        "9. This Court has complete jurisdiction to enter this Decree and the orders regarding the "
        "distribution of assets and debts."
    )
    y = draw_wrapped_text(c, text_9, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 0.3

    # 10. Waiver
    text_10 = (
        "10. The Petitioners waive their rights to a written notice of entry of decree or judgment, to "
        "request findings of fact and conclusions of law, to appeal, and to move for a new trial."
    )
    y = draw_wrapped_text(c, text_10, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 0.3

    # 11. Other findings
    c.drawString(INDENT, y, "11. Any other necessary findings of fact are attached and incorporated herein.")
    y -= LINE_HEIGHT * 1.5

    # NOW THEREFORE
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT, y, "NOW THEREFORE, IT IS HEREBY ORDERED ")
    c.setFont("Times-Roman", 12)
    order_text = (
        "that the bonds of matrimony now "
        "existing between the parties are hereby wholly dissolved, and an absolute Decree of Divorce is "
        "hereby granted to the parties, and each of the parties are hereby restored to the status of a single, "
        "unmarried person."
    )
    bold_w = c.stringWidth("NOW THEREFORE, IT IS HEREBY ORDERED ", "Times-Bold", 12)
    # First line continues after bold
    words = order_text.split()
    first_line_max = CONTENT_WIDTH - 36 - bold_w
    current_line = ''
    remaining_words = []
    c.setFont("Times-Roman", 12)
    for i, word in enumerate(words):
        test = (current_line + ' ' + word).strip()
        if c.stringWidth(test, "Times-Roman", 12) <= first_line_max:
            current_line = test
        else:
            remaining_words = words[i:]
            break
    c.drawString(INDENT + bold_w, y, current_line)
    y -= LINE_HEIGHT
    if remaining_words:
        y = draw_wrapped_text(c, ' '.join(remaining_words), MARGIN_LEFT, y, CONTENT_WIDTH)

    draw_footer(c, 2)
    c.showPage()

    # =========================================================================
    # PAGE 3
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    draw_line_numbers(c, 1, 28, y)

    c.setFont("Times-Roman", 12)

    # IT IS FURTHER ORDERED - property
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT, y, "IT IS FURTHER ORDERED ")
    c.setFont("Times-Roman", 12)
    further1 = (
        "that the terms, as stated in the Petitioner\u2019s Joint Petition, "
        "regarding the division of assets and debts are hereby ratified, confirmed and incorporated into "
        "this Decree as though fully set forth."
    )
    bold_w = c.stringWidth("IT IS FURTHER ORDERED ", "Times-Bold", 12)
    y = draw_wrapped_text(c, further1, INDENT + bold_w, y, CONTENT_WIDTH - 36 - bold_w)
    # Continue wrapping from left margin
    y -= LINE_HEIGHT * 0.5

    # IT IS FURTHER ORDERED - support
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT, y, "IT IS FURTHER ORDERED ")
    c.setFont("Times-Roman", 12)
    further2 = (
        "that the terms, as stated in the Petitioner\u2019s Joint Petition, "
        "regarding the issue of spousal support are hereby ratified, confirmed and incorporated into this "
        "Decree as though fully set forth."
    )
    y = draw_wrapped_text(c, further2, INDENT + bold_w, y, CONTENT_WIDTH - 36 - bold_w)
    y -= LINE_HEIGHT * 0.5

    # IT IS FURTHER ORDERED - name change
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT, y, "IT IS FURTHER ORDERED that ")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + c.stringWidth("IT IS FURTHER ORDERED that ", "Times-Bold", 12), y, "(\u2612 check all that apply)")
    y -= LINE_HEIGHT * 1.5

    neither_name_change = (name_change1 == 'none' and name_change2 == 'none')

    draw_checkbox(c, INDENT + 10, y - 2, checked=neither_name_change)
    c.drawString(INDENT + 24, y, "Neither spouse changed their name or neither spouse wishes to have a former or")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 24, y, "maiden name restored.")
    y -= LINE_HEIGHT * 1.5

    draw_checkbox(c, INDENT + 10, y - 2, checked=(name_change1 == 'restore'))
    c.drawString(INDENT + 24, y, "The name of (spouse\u2019s married name) ")
    mx = INDENT + 24 + c.stringWidth("The name of (spouse\u2019s married name) ", "Times-Roman", 12)
    c.drawString(mx, y, name_change1_married)
    draw_underline(c, mx, y, max(c.stringWidth(name_change1_married, "Times-Roman", 12), 180))
    y -= LINE_HEIGHT
    c.drawString(INDENT + 24, y, "should be restored to his / her former or maiden name of (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 24 + c.stringWidth("should be restored to his / her former or maiden name of (", "Times-Roman", 12), y, "write full name the spouse")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 24, y, "wants to go back to")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 24 + c.stringWidth("wants to go back to", "Times-Italic", 12), y, ") ")
    maiden_x = INDENT + 24 + c.stringWidth("wants to go back to", "Times-Italic", 12) + c.stringWidth(") ", "Times-Roman", 12)
    c.drawString(maiden_x, y, name_change1_maiden)
    draw_underline(c, maiden_x, y, max(c.stringWidth(name_change1_maiden, "Times-Roman", 12), 180))
    y -= LINE_HEIGHT * 1.5

    draw_checkbox(c, INDENT + 10, y - 2, checked=(name_change2 == 'restore'))
    c.drawString(INDENT + 24, y, "The name of (spouse\u2019s married name) ")
    mx = INDENT + 24 + c.stringWidth("The name of (spouse\u2019s married name) ", "Times-Roman", 12)
    c.drawString(mx, y, name_change2_married)
    draw_underline(c, mx, y, max(c.stringWidth(name_change2_married, "Times-Roman", 12), 180))
    y -= LINE_HEIGHT
    c.drawString(INDENT + 24, y, "should be restored to his / her former or maiden name of (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 24 + c.stringWidth("should be restored to his / her former or maiden name of (", "Times-Roman", 12), y, "write full name the spouse")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 24, y, "wants to go back to")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 24 + c.stringWidth("wants to go back to", "Times-Italic", 12), y, ") ")
    maiden_x = INDENT + 24 + c.stringWidth("wants to go back to", "Times-Italic", 12) + c.stringWidth(") ", "Times-Roman", 12)
    c.drawString(maiden_x, y, name_change2_maiden)
    draw_underline(c, maiden_x, y, max(c.stringWidth(name_change2_maiden, "Times-Roman", 12), 180))
    y -= LINE_HEIGHT * 1.5

    # NRS 125.130 order
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT, y, "IT IS FURTHER ORDERED ")
    c.setFont("Times-Roman", 12)
    nrs_text = (
        "that each party shall submit the information required in NRS "
        "125.130 on a separate form to the Court. Such information shall be maintained by the Clerk in a "
        "confidential manner and not part of the public record."
    )
    y = draw_wrapped_text(c, nrs_text, INDENT + c.stringWidth("IT IS FURTHER ORDERED ", "Times-Bold", 12), y, CONTENT_WIDTH - 36 - c.stringWidth("IT IS FURTHER ORDERED ", "Times-Bold", 12))
    y -= LINE_HEIGHT * 1.5

    # DATED
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "DATED (month) ")
    draw_underline(c, MARGIN_LEFT + c.stringWidth("DATED (month) ", "Times-Roman", 12), y, 140)
    c.drawString(MARGIN_LEFT + c.stringWidth("DATED (month) ", "Times-Roman", 12) + 144, y, " (day) ")
    draw_underline(c, MARGIN_LEFT + c.stringWidth("DATED (month) ", "Times-Roman", 12) + 144 + c.stringWidth(" (day) ", "Times-Roman", 12), y, 30)
    c.drawString(MARGIN_LEFT + c.stringWidth("DATED (month) ", "Times-Roman", 12) + 144 + c.stringWidth(" (day) ", "Times-Roman", 12) + 34, y, ", 20")
    draw_underline(c, MARGIN_LEFT + c.stringWidth("DATED (month) ", "Times-Roman", 12) + 144 + c.stringWidth(" (day) , 20", "Times-Roman", 12) + 34, y, 30)
    c.drawString(MARGIN_LEFT + c.stringWidth("DATED (month) ", "Times-Roman", 12) + 144 + c.stringWidth(" (day) , 20", "Times-Roman", 12) + 68, y, ".")
    y -= LINE_HEIGHT * 3

    # Judge signature
    judge_x = PAGE_WIDTH / 2 + 18
    draw_underline(c, judge_x, y, 180)
    y -= LINE_HEIGHT
    c.drawString(judge_x, y, "DISTRICT COURT JUDGE")
    y -= LINE_HEIGHT * 3

    # Respectfully Submitted By
    c.drawString(MARGIN_LEFT, y, "Respectfully Submitted By:")
    y -= LINE_HEIGHT * 2

    sig_left = MARGIN_LEFT + 10
    sig_right = PAGE_WIDTH / 2 + 18
    sig_w = 180

    # Arrow + signature lines
    c.drawString(sig_left - 10, y, "\u25b8")
    draw_underline(c, sig_left, y, sig_w)
    c.drawString(sig_right - 10, y, "\u25b8")
    draw_underline(c, sig_right, y, sig_w)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(sig_left, y, "(First Spouse\u2019s signature)")
    c.drawString(sig_right, y, "(Second Spouse\u2019s signature)")
    y -= LINE_HEIGHT * 1.5

    c.setFont("Times-Roman", 12)
    draw_underline(c, sig_left, y, sig_w)
    draw_underline(c, sig_right, y, sig_w)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(sig_left, y, "(First Spouse\u2019s printed name)")
    c.drawString(sig_right, y, "(Second Spouse\u2019s printed name)")
    y -= LINE_HEIGHT * 1.5

    c.setFont("Times-Bold", 10)
    attach_text = "(Attach a filed copy of the Petitioner\u2019s Joint Petition for Divorce as Exhibit A)"
    attach_w = c.stringWidth(attach_text, "Times-Bold", 10)
    c.drawString((PAGE_WIDTH - attach_w) / 2, y, attach_text)

    draw_footer(c, 3)
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "firstSpouseName": "JOHN DOE",
        "firstSpouseAddress": "1234 Las Vegas Blvd S",
        "firstSpouseCityStateZip": "Las Vegas, NV 89109",
        "firstSpousePhone": "(702) 555-1234",
        "firstSpouseEmail": "john@example.com",
        "secondSpouseName": "JANE DOE",
        "secondSpouseAddress": "1234 Las Vegas Blvd S",
        "secondSpouseCityStateZip": "Las Vegas, NV 89109",
        "secondSpousePhone": "(702) 555-5678",
        "secondSpouseEmail": "jane@example.com",
        "county": "Clark",
        "marriageDate": "June 15, 2020",
        "marriageCity": "Las Vegas",
        "marriageState": "Nevada",
        "residentSpouseName": "JOHN DOE",
        "nameChange1": "none",
        "nameChange2": "restore",
        "nameChange2MarriedName": "JANE DOE",
        "nameChange2MaidenName": "JANE SMITH",
    }
    output = generate_nv_decree(test_data, "/tmp/test_nv_decree.pdf")
    print(f"Generated: {output}")
