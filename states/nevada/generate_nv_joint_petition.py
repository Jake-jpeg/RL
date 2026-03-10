#!/usr/bin/env python3
"""
DivorceGPT NV - Joint Petition for Divorce (No Children) PDF Generator
=======================================================================

Generates the Nevada Joint Petition for Divorce (No Children) — 7 pages.
Based on the 2022 Nevada Supreme Court standardized form from selfhelp.nvcourts.gov.

Layout:
- Page 1: Header block, caption, title, Marriage (§1), Residency (§2)
- Page 2: Addresses (§3), Pregnancy (§4), Children (§5), Community Property (§6)
- Page 3: Community Property cont'd, Community Debt (§7)
- Page 4: Community Debt cont'd, Certification (§8), Spousal Support (§9), Name Change (§10)
- Page 5: §11-13 boilerplate, Prayer for Relief, Signature blocks
- Page 6: First Petitioner's Verification (notary)
- Page 7: Second Petitioner's Verification (notary)
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points
MARGIN_LEFT = 72
MARGIN_RIGHT = 72
MARGIN_TOP = 72
MARGIN_BOTTOM = 72
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 468 points
LINE_HEIGHT = 14
INDENT = MARGIN_LEFT + 36  # For numbered paragraphs


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
    """Draw a blank underline."""
    c.setLineWidth(0.5)
    c.line(x, y - 2, x + width, y - 2)


def draw_checkbox(c, x, y, checked=False, size=10):
    """Draw a checkbox square, optionally checked."""
    c.setLineWidth(0.5)
    c.rect(x, y - 2, size, size, stroke=1, fill=0)
    if checked:
        # Draw checkmark
        c.setLineWidth(1)
        c.line(x + 2, y + 2, x + 4, y)
        c.line(x + 4, y, x + 8, y + 7)
        c.setLineWidth(0.5)


def draw_footer(c, page_num, total_pages=7):
    """Draw the standard NV footer."""
    c.setFont("Times-Roman", 9)
    copyright_text = "\u00a9 2022 Nevada Supreme Court"
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 30, copyright_text)
    page_text = f"Page {page_num} of {total_pages} \u2013 Joint Petition for Divorce (No Children)"
    page_width = c.stringWidth(page_text, "Times-Roman", 9)
    c.drawString((PAGE_WIDTH - page_width) / 2, MARGIN_BOTTOM - 45, page_text)


def check_page_break(c, y, needed=80, page_num_ref=None):
    """Check if we need a page break. Returns (new_y, new_page_num)."""
    if y < MARGIN_BOTTOM + needed:
        if page_num_ref is not None:
            draw_footer(c, page_num_ref[0])
            page_num_ref[0] += 1
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
    return y


def draw_header_block(c, data, y):
    """Draw the self-represented header block with both spouses' info."""
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

    # First spouse info
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

    # Second spouse info
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


def draw_caption(c, data, y):
    """Draw DISTRICT COURT / COUNTY, NEVADA caption and party names."""
    county = data.get('county', '').strip()
    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()

    # DISTRICT COURT centered bold
    c.setFont("Times-Bold", 12)
    dc_text = "DISTRICT COURT"
    dc_width = c.stringWidth(dc_text, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - dc_width) / 2, y, dc_text)
    y -= LINE_HEIGHT * 1.2

    county_text = f"{county.upper()} COUNTY, NEVADA"
    county_width = c.stringWidth(county_text, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - county_width) / 2, y, county_text)
    y -= LINE_HEIGHT * 2

    # Caption box - left side: party names, right side: case no/dept
    box_top = y + LINE_HEIGHT * 0.5
    caption_left = MARGIN_LEFT
    caption_mid = PAGE_WIDTH / 2
    caption_right = PAGE_WIDTH - MARGIN_RIGHT

    # Left side - party names
    c.setFont("Times-Roman", 12)
    draw_underline(c, caption_left, y, 240)
    y -= LINE_HEIGHT
    c.drawString(caption_left, y, f"First Joint Petitioner (")
    c.setFont("Times-Italic", 12)
    c.drawString(caption_left + c.stringWidth("First Joint Petitioner (", "Times-Roman", 12), y, "Spouse Name")
    c.setFont("Times-Roman", 12)
    c.drawString(caption_left + c.stringWidth("First Joint Petitioner (Spouse Name", "Times-Roman", 12), y, "),")

    # Fill in the name on the line above
    c.setFont("Times-Roman", 12)
    c.drawString(caption_left, y + LINE_HEIGHT, spouse1_name)

    y -= LINE_HEIGHT * 1.5
    c.drawString(caption_left, y, "And")
    y -= LINE_HEIGHT * 1.5

    draw_underline(c, caption_left, y, 240)
    y -= LINE_HEIGHT
    c.drawString(caption_left, y, f"Second Joint Petitioner (")
    c.setFont("Times-Italic", 12)
    c.drawString(caption_left + c.stringWidth("Second Joint Petitioner (", "Times-Roman", 12), y, "Spouse Name")
    c.setFont("Times-Roman", 12)
    c.drawString(caption_left + c.stringWidth("Second Joint Petitioner (Spouse Name", "Times-Roman", 12), y, ").")

    # Fill in the name on the line above
    c.drawString(caption_left, y + LINE_HEIGHT, spouse2_name)

    # Right side - CASE NO and DEPT
    right_x = caption_mid + 20
    right_y = box_top - LINE_HEIGHT * 2
    c.drawString(right_x, right_y, "CASE NO.: ")
    draw_underline(c, right_x + c.stringWidth("CASE NO.: ", "Times-Roman", 12), right_y, 120)
    right_y -= LINE_HEIGHT * 1.5
    c.drawString(right_x, right_y, "DEPT:")
    draw_underline(c, right_x + c.stringWidth("DEPT: ", "Times-Roman", 12), right_y, 130)

    box_bottom = y - LINE_HEIGHT * 0.5

    # Draw vertical separator line
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    c.line(caption_mid, box_top, caption_mid, box_bottom)

    y = box_bottom - LINE_HEIGHT
    return y


def generate_nv_joint_petition(data, output_path):
    """
    Generate NV Joint Petition for Divorce (No Children) PDF.

    Required data keys:
    - firstSpouseName, firstSpouseAddress, firstSpouseCityStateZip, firstSpousePhone, firstSpouseEmail
    - secondSpouseName, secondSpouseAddress, secondSpouseCityStateZip, secondSpousePhone, secondSpouseEmail
    - county: Nevada county
    - marriageDate, marriageCity, marriageState
    - residentSpouseName: name of spouse who meets 6-week NV residency
    - communityPropertyOption: 'none' | 'already_divided'
    - communityDebtOption: 'none' | 'already_divided'
    - nameChange1: 'none' | 'restore'
    - nameChange1MarriedName, nameChange1MaidenName (if restore)
    - nameChange2: 'none' | 'restore'
    - nameChange2MarriedName, nameChange2MaidenName (if restore)
    """

    c = canvas.Canvas(output_path, pagesize=letter)
    page_num = [1]  # Mutable reference for page tracking

    # Extract variables
    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()
    spouse1_address = data.get('firstSpouseAddress', '').strip()
    spouse1_csz = data.get('firstSpouseCityStateZip', '').strip()
    spouse2_address = data.get('secondSpouseAddress', '').strip()
    spouse2_csz = data.get('secondSpouseCityStateZip', '').strip()
    county = data.get('county', '').strip()
    marriage_date = data.get('marriageDate', '').strip()
    marriage_city = data.get('marriageCity', '').strip()
    marriage_state = data.get('marriageState', '').strip()
    resident_spouse = data.get('residentSpouseName', '').strip()
    community_prop = data.get('communityPropertyOption', 'none').strip()
    community_debt = data.get('communityDebtOption', 'none').strip()
    name_change1 = data.get('nameChange1', 'none').strip()
    name_change1_married = data.get('nameChange1MarriedName', '').strip()
    name_change1_maiden = data.get('nameChange1MaidenName', '').strip()
    name_change2 = data.get('nameChange2', 'none').strip()
    name_change2_married = data.get('nameChange2MarriedName', '').strip()
    name_change2_maiden = data.get('nameChange2MaidenName', '').strip()

    if not spouse1_name:
        raise ValueError("First spouse name is required")
    if not spouse2_name:
        raise ValueError("Second spouse name is required")
    if not county:
        raise ValueError("County is required")

    # =========================================================================
    # PAGE 1
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # Header block
    y = draw_header_block(c, data, y)

    # Caption
    y = draw_caption(c, data, y)

    # Title
    y -= LINE_HEIGHT * 0.5
    c.setFont("Times-Bold", 12)
    title = "JOINT PETITION FOR DIVORCE (No Children)"
    title_width = c.stringWidth(title, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - title_width) / 2, y, title)
    y -= LINE_HEIGHT * 1.5

    # Intro paragraph
    c.setFont("Times-Roman", 12)
    intro = (
        "Petitioners request this Court to grant them a divorce pursuant to the terms of Chapter 125 "
        "of the Nevada Revised Statutes. Petitioners respectfully show, under oath, and state to the "
        "Court that every condition of NRS 125.181 has been met and further state as follows:"
    )
    y = draw_wrapped_text(c, intro, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 0.5

    # 1. Marriage
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "1.")
    c.drawString(INDENT, y, "Marriage.")
    bold_w = c.stringWidth("Marriage. ", "Times-Bold", 12)
    c.setFont("Times-Roman", 12)
    marriage_text = f"The parties were married on (date) "
    c.drawString(INDENT + bold_w, y, marriage_text)
    date_x = INDENT + bold_w + c.stringWidth(marriage_text, "Times-Roman", 12)
    c.drawString(date_x, y, marriage_date)
    draw_underline(c, date_x, y, max(c.stringWidth(marriage_date, "Times-Roman", 12), 150))
    c.drawString(date_x + max(c.stringWidth(marriage_date, "Times-Roman", 12), 150) + 4, y, " in")
    y -= LINE_HEIGHT

    city_text = f"(city) "
    c.drawString(INDENT, y, city_text)
    city_x = INDENT + c.stringWidth(city_text, "Times-Roman", 12)
    c.drawString(city_x, y, marriage_city)
    draw_underline(c, city_x, y, max(c.stringWidth(marriage_city, "Times-Roman", 12), 100))
    state_start = city_x + max(c.stringWidth(marriage_city, "Times-Roman", 12), 100) + 4
    c.drawString(state_start, y, ", (state) ")
    state_x = state_start + c.stringWidth(", (state) ", "Times-Roman", 12)
    c.drawString(state_x, y, marriage_state)
    draw_underline(c, state_x, y, max(c.stringWidth(marriage_state, "Times-Roman", 12), 100))
    end_x = state_x + max(c.stringWidth(marriage_state, "Times-Roman", 12), 100)
    c.drawString(end_x + 4, y, ". The parties are incompatible.")
    y -= LINE_HEIGHT * 1.5

    # 2. Residency
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "2.")
    c.drawString(INDENT, y, "Residency.")
    bold_w = c.stringWidth("Residency. ", "Times-Bold", 12)
    c.setFont("Times-Roman", 12)
    res_text = "The following spouse has been a resident of the State of Nevada for at least"
    c.drawString(INDENT + bold_w, y, res_text)
    y -= LINE_HEIGHT
    res_text2 = "six weeks prior to filing this Joint Petition: "
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT, y, res_text2)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT, y, "(write the name of the spouse who is a")
    y -= LINE_HEIGHT
    c.drawString(INDENT, y, "Nevada resident) ")
    c.setFont("Times-Roman", 12)
    name_x = INDENT + c.stringWidth("Nevada resident) ", "Times-Italic", 12)
    c.drawString(name_x, y, resident_spouse)
    draw_underline(c, name_x, y, max(c.stringWidth(resident_spouse, "Times-Roman", 12), 200))
    c.drawString(name_x + max(c.stringWidth(resident_spouse, "Times-Roman", 12), 200) + 2, y, ".")

    draw_footer(c, page_num[0])
    c.showPage()
    page_num[0] += 1

    # =========================================================================
    # PAGE 2
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # 3. Address
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "3.")
    c.drawString(INDENT, y, "Address.")
    bold_w = c.stringWidth("Address. ", "Times-Bold", 12)
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + bold_w, y, "The mailing addresses of the petitioners are:")
    y -= LINE_HEIGHT * 1.5

    # Two-column address layout
    col1_x = MARGIN_LEFT + 18
    col2_x = PAGE_WIDTH / 2 + 18

    c.setFont("Times-Roman", 12)
    c.drawString(col1_x, y, "First Spouse:")
    c.drawString(col2_x, y, "Second Spouse:")
    y -= LINE_HEIGHT * 1.2

    c.drawString(col1_x, y, "Name: ")
    c.drawString(col1_x + 40, y, spouse1_name)
    draw_underline(c, col1_x + 40, y, 180)
    c.drawString(col2_x, y, "Name: ")
    c.drawString(col2_x + 40, y, spouse2_name)
    draw_underline(c, col2_x + 40, y, 180)
    y -= LINE_HEIGHT * 1.2

    c.drawString(col1_x, y, "Address: ")
    c.drawString(col1_x + 52, y, spouse1_address)
    draw_underline(c, col1_x + 52, y, 168)
    c.drawString(col2_x, y, "Address: ")
    c.drawString(col2_x + 52, y, spouse2_address)
    draw_underline(c, col2_x + 52, y, 168)
    y -= LINE_HEIGHT * 1.2

    c.drawString(col1_x, y, "City, State, Zip: ")
    csz_offset = c.stringWidth("City, State, Zip: ", "Times-Roman", 12)
    c.drawString(col1_x + csz_offset, y, spouse1_csz)
    draw_underline(c, col1_x + csz_offset, y, 220 - csz_offset)
    c.drawString(col2_x, y, "City, State, Zip: ")
    c.drawString(col2_x + csz_offset, y, spouse2_csz)
    draw_underline(c, col2_x + csz_offset, y, 220 - csz_offset)
    y -= LINE_HEIGHT * 2

    # 4. Pregnancy
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "4.")
    c.drawString(INDENT, y, "Pregnancy.")
    bold_w = c.stringWidth("Pregnancy. ", "Times-Bold", 12)
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + bold_w, y, "Is either spouse pregnant? (\u2612 check one)")
    y -= LINE_HEIGHT * 1.5

    # Checkbox: No, neither spouse is pregnant (always checked for our scope)
    draw_checkbox(c, INDENT + 10, y - 2, checked=True)
    c.drawString(INDENT + 24, y, "No, neither spouse is pregnant.")
    y -= LINE_HEIGHT * 1.2

    # Checkbox: Yes (always unchecked)
    draw_checkbox(c, INDENT + 10, y - 2, checked=False)
    c.drawString(INDENT + 24, y, "Yes, this spouse is pregnant: (name of pregnant spouse) ")
    draw_underline(c, INDENT + 24 + c.stringWidth("Yes, this spouse is pregnant: (name of pregnant spouse) ", "Times-Roman", 12), y, 100)
    y -= LINE_HEIGHT * 2.5

    # 5. Children
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "5.")
    c.drawString(INDENT, y, "Children.")
    bold_w = c.stringWidth("Children. ", "Times-Bold", 12)
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + bold_w, y, "There are no minor children in common born to or adopted by the parties.")
    y -= LINE_HEIGHT * 2

    # 6. Community Property
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "6.")
    c.drawString(INDENT, y, "Community Property.")
    y -= LINE_HEIGHT * 1.5

    # Info box
    box_top_y = y + 4
    c.setFont("Times-Bold", 10)
    box_title = "Community Property:"
    box_title_w = c.stringWidth(box_title, "Times-Bold", 10)
    c.drawString((PAGE_WIDTH - box_title_w) / 2, y, box_title)
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 9)
    info_text = (
        "Community property includes but is not limited to: checking, savings, and other "
        "investment accounts, real property / houses, vehicles, pensions, 401(k)s, deferred "
        "compensation, IRAs, and personal property."
    )
    y = draw_wrapped_text(c, info_text, MARGIN_LEFT + 36, y, CONTENT_WIDTH - 72, "Times-Roman", 9, 12)
    c.setFont("Times-Roman", 9)
    c.drawString(MARGIN_LEFT + 36, y, "Make sure the list of property below is complete.")
    y -= 12
    box_bottom_y = y
    # Draw box border
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.5)
    c.rect(MARGIN_LEFT + 30, box_bottom_y - 4, CONTENT_WIDTH - 60, box_top_y - box_bottom_y + 8, stroke=1, fill=0)
    c.setStrokeColorRGB(0, 0, 0)
    y -= LINE_HEIGHT * 1.5

    # Checkboxes
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "(\u2612 check one)")
    y -= LINE_HEIGHT * 1.2

    is_no_prop = community_prop == 'none'
    is_already_div = community_prop == 'already_divided'

    draw_checkbox(c, INDENT, y - 2, checked=is_no_prop)
    c.drawString(INDENT + 14, y, "There is no community property to divide.")
    y -= LINE_HEIGHT * 1.2

    draw_checkbox(c, INDENT, y - 2, checked=is_already_div)
    c.drawString(INDENT + 14, y, "Any community property has already been divided.")
    y -= LINE_HEIGHT * 1.2

    draw_checkbox(c, INDENT, y - 2, checked=False)
    c.drawString(INDENT + 14, y, "The community property should be divided as follows:")

    draw_footer(c, page_num[0])
    c.showPage()
    page_num[0] += 1

    # =========================================================================
    # PAGE 3 - Property cont'd + Community Debt
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # Property division lines (left blank — not applicable for our scope)
    c.setFont("Times-Bold", 12)
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 36, y, "(Name of spouse)")
    c.setFont("Times-Roman", 12)
    draw_underline(c, INDENT + 36 + c.stringWidth("(Name of spouse) ", "Times-Italic", 12), y, 180)
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT + 36 + c.stringWidth("(Name of spouse) ", "Times-Italic", 12) + 184, y, "shall receive:")
    y -= LINE_HEIGHT * 1.5

    for i in range(1, 7):
        c.setFont("Times-Roman", 12)
        c.drawString(INDENT + 54, y, f"{i}.")
        draw_underline(c, INDENT + 72, y, 300)
        y -= LINE_HEIGHT * 1.2

    y -= LINE_HEIGHT * 0.5
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Attach additional sheets if more property needs to be listed.")
    y -= LINE_HEIGHT * 2

    # 7. Community Debt
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "7.")
    c.drawString(INDENT, y, "Community Debt.")
    y -= LINE_HEIGHT * 1.5

    # Debt info box
    box_top_y = y + 4
    c.setFont("Times-Bold", 10)
    box_title = "Community Debt:"
    box_title_w = c.stringWidth(box_title, "Times-Bold", 10)
    c.drawString((PAGE_WIDTH - box_title_w) / 2, y, box_title)
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 9)
    debt_info = (
        "Community debt includes but is not limited to: mortgages, car loans, credit cards, & tax debt. "
        "The division of debt does not affect creditors\u2019 rights to collect the debt. The parties may "
        "be required to restructure the debts per creditors\u2019 requirements."
    )
    y = draw_wrapped_text(c, debt_info, MARGIN_LEFT + 36, y, CONTENT_WIDTH - 72, "Times-Roman", 9, 12)
    box_bottom_y = y
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.5)
    c.rect(MARGIN_LEFT + 30, box_bottom_y - 4, CONTENT_WIDTH - 60, box_top_y - box_bottom_y + 8, stroke=1, fill=0)
    c.setStrokeColorRGB(0, 0, 0)
    y -= LINE_HEIGHT * 1.5

    # Debt checkboxes
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "(\u2612 check one)")
    y -= LINE_HEIGHT * 1.2

    is_no_debt = community_debt == 'none'
    is_debt_divided = community_debt == 'already_divided'

    draw_checkbox(c, INDENT, y - 2, checked=is_no_debt)
    c.drawString(INDENT + 14, y, "There is no community debt to divide.")
    y -= LINE_HEIGHT * 1.2

    draw_checkbox(c, INDENT, y - 2, checked=is_debt_divided)
    c.drawString(INDENT + 14, y, "Any community debt has already been divided.")
    y -= LINE_HEIGHT * 1.2

    draw_checkbox(c, INDENT, y - 2, checked=False)
    c.drawString(INDENT + 14, y, "The community debt should be divided as follows:")

    draw_footer(c, page_num[0])
    c.showPage()
    page_num[0] += 1

    # =========================================================================
    # PAGE 4 - Debt cont'd + Certification + Spousal Support + Name Change
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # Debt division lines (left blank)
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 36, y, "(Name of spouse)")
    c.setFont("Times-Roman", 12)
    draw_underline(c, INDENT + 36 + c.stringWidth("(Name of spouse) ", "Times-Italic", 12), y, 180)
    c.setFont("Times-Bold", 12)
    c.drawString(INDENT + 36 + c.stringWidth("(Name of spouse) ", "Times-Italic", 12) + 184, y, "shall be liable for:")
    y -= LINE_HEIGHT * 1.5

    for i in range(1, 7):
        c.setFont("Times-Roman", 12)
        c.drawString(INDENT + 54, y, f"{i}.")
        draw_underline(c, INDENT + 72, y, 300)
        y -= LINE_HEIGHT * 1.2

    y -= LINE_HEIGHT * 0.5
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Attach additional sheets if more debts need to be listed.")
    y -= LINE_HEIGHT * 2

    # 8. Certification
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "8.")
    c.setFont("Times-Roman", 12)
    cert_text = (
        "Petitioners certify that they have disclosed all community assets and debts and that there "
        "are no other community assets or debts for this Court to divide."
    )
    y = draw_wrapped_text(c, cert_text, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 1

    # 9. Spousal Support/Alimony
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "9.")
    c.drawString(INDENT, y, "Spousal Support/Alimony.")
    bold_w = c.stringWidth("Spousal Support/Alimony. ", "Times-Bold", 12)
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + bold_w, y, "(\u2612 check one)")
    y -= LINE_HEIGHT * 1.5

    # Always "neither" for our scope
    draw_checkbox(c, INDENT + 10, y - 2, checked=True)
    c.drawString(INDENT + 24, y, "Neither spouse should be awarded alimony.")
    y -= LINE_HEIGHT * 1.2

    draw_checkbox(c, INDENT + 10, y - 2, checked=False)
    c.drawString(INDENT + 24, y, "(Name of spouse who will pay alimony) ")
    draw_underline(c, INDENT + 24 + c.stringWidth("(Name of spouse who will pay alimony) ", "Times-Roman", 12), y, 140)
    y -= LINE_HEIGHT
    c.drawString(INDENT + 24, y, "should pay (amount) $")
    draw_underline(c, INDENT + 24 + c.stringWidth("should pay (amount) $", "Times-Roman", 12), y, 60)
    c.drawString(INDENT + 24 + c.stringWidth("should pay (amount) $", "Times-Roman", 12) + 64, y, " per month in alimony for the next (number)")
    y -= LINE_HEIGHT
    draw_underline(c, INDENT + 24, y, 60)
    c.drawString(INDENT + 88, y, " years. Spousal support will be due the 1st of the month and should")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 24, y, "begin on (start date) ")
    draw_underline(c, INDENT + 24 + c.stringWidth("begin on (start date) ", "Times-Roman", 12), y, 90)
    c.drawString(INDENT + 24 + c.stringWidth("begin on (start date) ", "Times-Roman", 12) + 94, y, " and end on (end date) ")
    draw_underline(c, INDENT + 24 + c.stringWidth("begin on (start date) ", "Times-Roman", 12) + 94 + c.stringWidth(" and end on (end date) ", "Times-Roman", 12), y, 90)
    c.drawString(INDENT + 24 + c.stringWidth("begin on (start date) ", "Times-Roman", 12) + 94 + c.stringWidth(" and end on (end date) ", "Times-Roman", 12) + 92, y, ".")
    y -= LINE_HEIGHT * 2

    # 10. Name Change
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "10. Name Change.")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth("10. Name Change. ", "Times-Bold", 12), y, "(\u2612 check all that apply)")
    y -= LINE_HEIGHT * 1.5

    neither_name_change = (name_change1 == 'none' and name_change2 == 'none')

    draw_checkbox(c, INDENT, y - 2, checked=neither_name_change)
    name_none_text = "Neither spouse changed their name or neither spouse wishes to have a former or"
    c.drawString(INDENT + 14, y, name_none_text)
    y -= LINE_HEIGHT
    c.drawString(INDENT + 14, y, "maiden name restored.")
    y -= LINE_HEIGHT * 1.5

    # First name change option
    draw_checkbox(c, INDENT, y - 2, checked=(name_change1 == 'restore'))
    c.drawString(INDENT + 14, y, "The name of (spouse\u2019s married name) ")
    married_x = INDENT + 14 + c.stringWidth("The name of (spouse\u2019s married name) ", "Times-Roman", 12)
    c.drawString(married_x, y, name_change1_married)
    draw_underline(c, married_x, y, max(c.stringWidth(name_change1_married, "Times-Roman", 12), 180))
    y -= LINE_HEIGHT
    c.drawString(INDENT + 14, y, "should be restored to his / her former or maiden name of (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 14 + c.stringWidth("should be restored to his / her former or maiden name of (", "Times-Roman", 12), y, "write full name the spouse")
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 14, y, "wants to go back to")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 14 + c.stringWidth("wants to go back to", "Times-Italic", 12), y, ") ")
    maiden_x = INDENT + 14 + c.stringWidth("wants to go back to", "Times-Italic", 12) + c.stringWidth(") ", "Times-Roman", 12)
    c.drawString(maiden_x, y, name_change1_maiden)
    draw_underline(c, maiden_x, y, max(c.stringWidth(name_change1_maiden, "Times-Roman", 12), 180))
    c.drawString(maiden_x + max(c.stringWidth(name_change1_maiden, "Times-Roman", 12), 180) + 2, y, ".")
    y -= LINE_HEIGHT * 1.5

    # Second name change option
    draw_checkbox(c, INDENT, y - 2, checked=(name_change2 == 'restore'))
    c.drawString(INDENT + 14, y, "The name of (spouse\u2019s married name) ")
    married_x = INDENT + 14 + c.stringWidth("The name of (spouse\u2019s married name) ", "Times-Roman", 12)
    c.drawString(married_x, y, name_change2_married)
    draw_underline(c, married_x, y, max(c.stringWidth(name_change2_married, "Times-Roman", 12), 180))
    y -= LINE_HEIGHT
    c.drawString(INDENT + 14, y, "should be restored to his / her former or maiden name of (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 14 + c.stringWidth("should be restored to his / her former or maiden name of (", "Times-Roman", 12), y, "write full name the spouse")
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 14, y, "wants to go back to")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 14 + c.stringWidth("wants to go back to", "Times-Italic", 12), y, ") ")
    maiden_x = INDENT + 14 + c.stringWidth("wants to go back to", "Times-Italic", 12) + c.stringWidth(") ", "Times-Roman", 12)
    c.drawString(maiden_x, y, name_change2_maiden)
    draw_underline(c, maiden_x, y, max(c.stringWidth(name_change2_maiden, "Times-Roman", 12), 180))
    c.drawString(maiden_x + max(c.stringWidth(name_change2_maiden, "Times-Roman", 12), 180) + 2, y, ".")

    draw_footer(c, page_num[0])
    c.showPage()
    page_num[0] += 1

    # =========================================================================
    # PAGE 5 - Boilerplate paragraphs + Prayer + Signatures
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # 11
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "11.")
    c.setFont("Times-Roman", 12)
    text_11 = (
        "Petitioners hereby request that this Court enter a Decree of Divorce, incorporating into "
        "that Decree the provisions made in this Joint Petition."
    )
    y = draw_wrapped_text(c, text_11, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 0.5

    # 12
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "12.")
    c.setFont("Times-Roman", 12)
    text_12 = (
        "It is understood by the Petitioners that entry of a Decree of Divorce constitutes a final "
        "adjudication of the rights and obligations of the parties with respect to the status of the "
        "marriage. Petitioners each expressly give up their respective rights to receive written "
        "notice of entry of any judgment or decree of divorce, and Petitioners give up their right "
        "to request formal findings of fact and conclusions of law. Petitioners waive their right to "
        "appeal the Decree of Divorce, and the right to move for a new trial."
    )
    y = draw_wrapped_text(c, text_12, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 0.5

    # 13
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "13.")
    c.setFont("Times-Roman", 12)
    text_13 = (
        "It is further understood by the Petitioners that a final Decree of Divorce entered by this "
        "summary procedure does not prejudice or prevent the rights of either Petitioner to bring "
        "an action to set aside the final decree for fraud, duress, accident, mistake, or the grounds "
        "recognized at law or in equity."
    )
    y = draw_wrapped_text(c, text_13, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 1.5

    # Prayer for Relief
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "Petitioners request:")
    y -= LINE_HEIGHT * 1.5

    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18, y, "1.")
    prayer1 = (
        "That they be granted a Decree of Divorce and that each of the Petitioners be "
        "restored to the status of a single, unmarried person;"
    )
    y = draw_wrapped_text(c, prayer1, INDENT + 36, y, CONTENT_WIDTH - 72)
    y -= LINE_HEIGHT * 0.3

    c.drawString(INDENT + 18, y, "2.")
    c.drawString(INDENT + 36, y, "That the terms agreed upon in this Joint Petition be included in the Decree.")
    y -= LINE_HEIGHT * 3

    # Signature blocks - side by side
    sig_left = MARGIN_LEFT
    sig_right = PAGE_WIDTH / 2 + 18
    sig_width = 190

    # Date lines
    draw_underline(c, sig_left, y, sig_width)
    draw_underline(c, sig_right, y, sig_width)
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(sig_left, y, "Date")
    c.drawString(sig_right, y, "Date")
    y -= LINE_HEIGHT * 2

    # Signature lines
    draw_underline(c, sig_left, y, sig_width)
    draw_underline(c, sig_right, y, sig_width)
    y -= LINE_HEIGHT
    c.drawString(sig_left, y, "First Spouse Signature")
    c.drawString(sig_right, y, "Second Spouse Signature")
    y -= LINE_HEIGHT * 2

    # Printed name lines
    draw_underline(c, sig_left, y, sig_width)
    draw_underline(c, sig_right, y, sig_width)
    y -= LINE_HEIGHT
    c.drawString(sig_left, y, "First Spouse Printed Name")
    c.drawString(sig_right, y, "Second Spouse Printed Name")

    draw_footer(c, page_num[0])
    c.showPage()
    page_num[0] += 1

    # =========================================================================
    # PAGE 6 - First Petitioner's Verification
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    c.setFont("Times-Bold", 12)
    title = "FIRST PETITIONER\u2019S VERIFICATION"
    title_w = c.stringWidth(title, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - title_w) / 2, y, title)
    # Underline the title
    c.setLineWidth(0.5)
    c.line((PAGE_WIDTH - title_w) / 2, y - 2, (PAGE_WIDTH + title_w) / 2, y - 2)
    y -= LINE_HEIGHT * 2.5

    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "STATE OF NEVADA")
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF ")
    c.drawString(MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, county)
    draw_underline(c, MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, max(c.stringWidth(county, "Times-Roman", 12), 80))
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT * 2

    # Verification text
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT, y, "(First spouse\u2019s name) ")
    c.setFont("Times-Roman", 12)
    name_x = INDENT + c.stringWidth("(First spouse\u2019s name) ", "Times-Italic", 12)
    c.drawString(name_x, y, spouse1_name)
    draw_underline(c, name_x, y, max(c.stringWidth(spouse1_name, "Times-Roman", 12), 200))
    end_x = name_x + max(c.stringWidth(spouse1_name, "Times-Roman", 12), 200)
    c.drawString(end_x + 4, y, " being first duly sworn")
    y -= LINE_HEIGHT

    c.drawString(MARGIN_LEFT, y, "under penalty of perjury, deposes and says:")
    y -= LINE_HEIGHT * 1.5

    verification_text = (
        "I am the Petitioner herein, and I have read the foregoing Joint Petition for Divorce and "
        "know the contents thereof; that the pleading is true to the best of my own knowledge, except as "
        "to those matters therein stated upon information and belief, and as to those matters, I believe "
        "them to be true."
    )
    y = draw_wrapped_text(c, verification_text, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 1.5

    # Signature
    sig_x = PAGE_WIDTH / 2 + 18
    c.drawString(sig_x - 14, y, "\u25b8")
    draw_underline(c, sig_x, y, 180)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(sig_x, y, "(First spouse\u2019s signature)")
    y -= LINE_HEIGHT * 2

    # Jurat
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Signed and sworn to (or affirmed) before me on")
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT, y, "(date)")
    c.setFont("Times-Roman", 12)
    draw_underline(c, MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12), y, 80)
    c.drawString(MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12) + 84, y, " by ")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12) + 84 + c.stringWidth(" by ", "Times-Roman", 12), y, "(name)")
    draw_underline(c, MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12) + 84 + c.stringWidth(" by (name) ", "Times-Roman", 12), y, 120)
    y -= LINE_HEIGHT * 3

    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Signature of notarial officer")
    draw_underline(c, MARGIN_LEFT, y + LINE_HEIGHT, 200)
    y -= LINE_HEIGHT * 3

    # Notary acknowledgment
    c.drawString(MARGIN_LEFT, y, "STATE OF NEVADA")
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF ")
    c.drawString(MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, county)
    draw_underline(c, MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, max(c.stringWidth(county, "Times-Roman", 12), 80))
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT * 2

    notary_text = (
        f"On this _________ day of _______________________ 20____, personally appeared "
        f"before me, a Notary Public, (first spouse\u2019s name) {spouse1_name}, "
        "known or proved to me to be the person who executed the foregoing Joint Petition for Divorce, "
        "and who acknowledged to me that he/she did so freely and voluntarily and for the uses and "
        "purposes herein stated."
    )
    y = draw_wrapped_text(c, notary_text, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 2

    c.drawString(MARGIN_LEFT, y, "Signature of notarial officer")
    draw_underline(c, MARGIN_LEFT, y + LINE_HEIGHT, 200)

    draw_footer(c, page_num[0])
    c.showPage()
    page_num[0] += 1

    # =========================================================================
    # PAGE 7 - Second Petitioner's Verification
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    c.setFont("Times-Bold", 12)
    title = "SECOND PETITIONER\u2019S VERIFICATION"
    title_w = c.stringWidth(title, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - title_w) / 2, y, title)
    c.setLineWidth(0.5)
    c.line((PAGE_WIDTH - title_w) / 2, y - 2, (PAGE_WIDTH + title_w) / 2, y - 2)
    y -= LINE_HEIGHT * 2.5

    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "STATE OF NEVADA")
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF ")
    c.drawString(MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, county)
    draw_underline(c, MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, max(c.stringWidth(county, "Times-Roman", 12), 80))
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT * 2

    c.setFont("Times-Italic", 12)
    c.drawString(INDENT, y, "(Second spouse\u2019s name) ")
    c.setFont("Times-Roman", 12)
    name_x = INDENT + c.stringWidth("(Second spouse\u2019s name) ", "Times-Italic", 12)
    c.drawString(name_x, y, spouse2_name)
    draw_underline(c, name_x, y, max(c.stringWidth(spouse2_name, "Times-Roman", 12), 200))
    end_x = name_x + max(c.stringWidth(spouse2_name, "Times-Roman", 12), 200)
    c.drawString(end_x + 4, y, " being first duly sworn")
    y -= LINE_HEIGHT

    c.drawString(MARGIN_LEFT, y, "under penalty of perjury, deposes and says:")
    y -= LINE_HEIGHT * 1.5

    y = draw_wrapped_text(c, verification_text, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 1.5

    # Signature
    sig_x = PAGE_WIDTH / 2 + 18
    c.drawString(sig_x - 14, y, "\u25b8")
    draw_underline(c, sig_x, y, 180)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(sig_x, y, "(Second spouse\u2019s signature)")
    y -= LINE_HEIGHT * 2

    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Signed and sworn to (or affirmed) before me on")
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT, y, "(date)")
    c.setFont("Times-Roman", 12)
    draw_underline(c, MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12), y, 80)
    c.drawString(MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12) + 84, y, " by ")
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12) + 84 + c.stringWidth(" by ", "Times-Roman", 12), y, "(name)")
    draw_underline(c, MARGIN_LEFT + c.stringWidth("(date) ", "Times-Italic", 12) + 84 + c.stringWidth(" by (name) ", "Times-Roman", 12), y, 120)
    y -= LINE_HEIGHT * 3

    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Signature of notarial officer")
    draw_underline(c, MARGIN_LEFT, y + LINE_HEIGHT, 200)
    y -= LINE_HEIGHT * 3

    # Notary acknowledgment
    c.drawString(MARGIN_LEFT, y, "STATE OF NEVADA")
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF ")
    c.drawString(MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, county)
    draw_underline(c, MARGIN_LEFT + c.stringWidth("COUNTY OF ", "Times-Roman", 12), y, max(c.stringWidth(county, "Times-Roman", 12), 80))
    c.drawString(MARGIN_LEFT + 180, y, ")")
    y -= LINE_HEIGHT * 2

    notary_text2 = (
        f"On this _________ day of _______________________ 20____, personally appeared "
        f"before me, a Notary Public, (second spouse\u2019s name) {spouse2_name}, "
        "known or proved to me to be the person who executed the foregoing Joint Petition for Divorce, "
        "and who acknowledged to me that he/she did so freely and voluntarily and for the uses and "
        "purposes herein stated."
    )
    y = draw_wrapped_text(c, notary_text2, INDENT, y, CONTENT_WIDTH - 36)
    y -= LINE_HEIGHT * 2

    c.drawString(MARGIN_LEFT, y, "Signature of notarial officer")
    draw_underline(c, MARGIN_LEFT, y + LINE_HEIGHT, 200)

    draw_footer(c, page_num[0])
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
        "communityPropertyOption": "none",
        "communityDebtOption": "none",
        "nameChange1": "none",
        "nameChange2": "restore",
        "nameChange2MarriedName": "JANE DOE",
        "nameChange2MaidenName": "JANE SMITH",
    }

    output = generate_nv_joint_petition(test_data, "/tmp/test_nv_joint_petition.pdf")
    print(f"Generated: {output}")
