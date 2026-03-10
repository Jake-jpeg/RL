#!/usr/bin/env python3
"""
DivorceGPT NV - Affidavit of Resident Witness PDF Generator
=============================================================

Generates the Nevada Affidavit of Resident Witness — 2 pages.
Based on the 2017 Nevada Supreme Court standardized form from selfhelp.nvcourts.gov.

This form is signed by a third-party Nevada resident (NOT a spouse) who can attest
to the filing spouse's 6-week residency in Nevada.
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


def draw_wrapped_text(c, text, x, y, max_width, font_name="Times-Roman", font_size=12, line_height=LINE_HEIGHT):
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


def draw_footer(c, page_label="Affidavit of Resident Witness"):
    c.setFont("Times-Roman", 9)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 30, "\u00a9 2017 Nevada Supreme Court")
    c.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, MARGIN_BOTTOM - 30, page_label)


def generate_nv_affidavit(data, output_path):
    """
    Generate NV Affidavit of Resident Witness PDF.

    Required data keys:
    - firstSpouseName: First Joint Petitioner name (for caption)
    - secondSpouseName: Second Joint Petitioner name (for caption)
    - county: Nevada county
    - witnessName: Full name of the resident witness
    - witnessAddress: Witness's street address
    - witnessCityStateZip: Witness's city, state, zip
    - witnessPhone: Witness's phone number
    - witnessEmail: Witness's email
    - witnessYearsInNV: How many years witness has lived in NV
    - witnessStreetCityState: Witness's address (street, city, state format)
    - residentSpouseName: Name of spouse whose residency is being established
    - residentSpouseAddress: Address of that spouse (street, city, state)
    - residencySinceDate: Date the spouse has lived in NV since
    - witnessTimesPerWeek: How many times per week witness sees the spouse
    - witnessRelationship: How the witness knows the spouse
    """

    c = canvas.Canvas(output_path, pagesize=letter)

    witness_name = data.get('witnessName', '').strip()
    witness_address = data.get('witnessAddress', '').strip()
    witness_csz = data.get('witnessCityStateZip', '').strip()
    witness_phone = data.get('witnessPhone', '').strip()
    witness_email = data.get('witnessEmail', '').strip()
    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()
    county = data.get('county', '').strip()
    witness_years = data.get('witnessYearsInNV', '').strip()
    witness_street_city_state = data.get('witnessStreetCityState', '').strip()
    resident_spouse = data.get('residentSpouseName', '').strip()
    resident_address = data.get('residentSpouseAddress', '').strip()
    residency_since = data.get('residencySinceDate', '').strip()
    times_per_week = data.get('witnessTimesPerWeek', '').strip()
    relationship = data.get('witnessRelationship', '').strip()

    # =========================================================================
    # PAGE 1
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # Header block (witness info, not spouse)
    c.setFont("Times-Roman", 10)
    label_x = MARGIN_LEFT
    value_x = MARGIN_LEFT + 90

    c.drawString(label_x, y, "Your Name:")
    c.drawString(value_x, y, witness_name)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Address:")
    c.drawString(value_x, y, witness_address)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "City, State, Zip")
    c.drawString(value_x, y, witness_csz)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Telephone:")
    c.drawString(value_x, y, witness_phone)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Email Address:")
    c.drawString(value_x, y, witness_email)
    draw_underline(c, value_x, y, 180)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Self-Represented")
    y -= LINE_HEIGHT * 2

    # Caption
    c.setFont("Times-Bold", 12)
    dc = "DISTRICT COURT"
    c.drawString((PAGE_WIDTH - c.stringWidth(dc, "Times-Bold", 12)) / 2, y, dc)
    y -= LINE_HEIGHT * 1.2
    county_text = f"{county.upper()} COUNTY, NEVADA"
    c.drawString((PAGE_WIDTH - c.stringWidth(county_text, "Times-Bold", 12)) / 2, y, county_text)
    y -= LINE_HEIGHT * 2

    # Party caption with case number
    caption_mid = PAGE_WIDTH / 2
    box_top = y + LINE_HEIGHT * 0.5

    c.setFont("Times-Roman", 12)
    draw_underline(c, MARGIN_LEFT, y, 200)
    c.drawString(MARGIN_LEFT, y, spouse1_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Plaintiff / Joint Petitioner,")

    right_x = caption_mid + 20
    c.drawString(right_x, y + LINE_HEIGHT, "CASE NO.: ")
    draw_underline(c, right_x + c.stringWidth("CASE NO.: ", "Times-Roman", 12), y + LINE_HEIGHT, 120)
    c.drawString(right_x, y, "DEPT:")
    draw_underline(c, right_x + c.stringWidth("DEPT: ", "Times-Roman", 12), y, 130)

    y -= LINE_HEIGHT * 1.2
    c.drawString(MARGIN_LEFT, y, "vs.")
    y -= LINE_HEIGHT * 1.2

    draw_underline(c, MARGIN_LEFT, y, 200)
    c.drawString(MARGIN_LEFT, y, spouse2_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Defendant / Joint Petitioner.")

    box_bottom = y - LINE_HEIGHT * 0.5
    c.setLineWidth(0.5)
    c.line(caption_mid, box_top, caption_mid, box_bottom)

    y = box_bottom - LINE_HEIGHT * 1.5

    # Title
    c.setFont("Times-Bold", 12)
    title = "AFFIDAVIT OF RESIDENT WITNESS"
    title_w = c.stringWidth(title, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - title_w) / 2, y, title)
    y -= LINE_HEIGHT * 2

    # Body
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT, y, "I, (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + c.stringWidth("I, (", "Times-Roman", 12), y, "resident witness\u2019 name")
    c.setFont("Times-Roman", 12)
    rw_x = INDENT + c.stringWidth("I, (resident witness\u2019 name", "Times-Roman", 12)
    c.drawString(rw_x, y, ") ")
    name_x = rw_x + c.stringWidth(") ", "Times-Roman", 12)
    c.drawString(name_x, y, witness_name)
    draw_underline(c, name_x, y, max(c.stringWidth(witness_name, "Times-Roman", 12), 200))
    end_x = name_x + max(c.stringWidth(witness_name, "Times-Roman", 12), 200)
    c.drawString(end_x + 4, y, ", swear under")
    y -= LINE_HEIGHT

    c.drawString(MARGIN_LEFT, y, "penalty of perjury that the following statements are true and correct.")
    y -= LINE_HEIGHT * 1.5

    # 1.
    c.drawString(INDENT, y, "1.")
    text1 = "I am over the age of eighteen (18) and competent to testify of my own knowledge to"
    c.drawString(INDENT + 18, y, text1)
    y -= LINE_HEIGHT
    c.drawString(INDENT + 18, y, "the following.")
    y -= LINE_HEIGHT * 1.5

    # 2.
    c.drawString(INDENT, y, "2.")
    c.drawString(INDENT + 18, y, "I have lived in the State of Nevada for (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("I have lived in the State of Nevada for (", "Times-Roman", 12), y, "number")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("I have lived in the State of Nevada for (number", "Times-Roman", 12), y, ") ")
    num_x = INDENT + 18 + c.stringWidth("I have lived in the State of Nevada for (number) ", "Times-Roman", 12)
    c.drawString(num_x, y, witness_years)
    draw_underline(c, num_x, y, max(c.stringWidth(witness_years, "Times-Roman", 12), 50))
    c.drawString(num_x + max(c.stringWidth(witness_years, "Times-Roman", 12), 50) + 4, y, " years and currently")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, "live at (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("live at (", "Times-Roman", 12), y, "street, city, state")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("live at (street, city, state", "Times-Roman", 12), y, ") ")
    addr_x = INDENT + 18 + c.stringWidth("live at (street, city, state) ", "Times-Roman", 12)
    c.drawString(addr_x, y, witness_street_city_state)
    draw_underline(c, addr_x, y, max(c.stringWidth(witness_street_city_state, "Times-Roman", 12), 200))
    c.drawString(addr_x + max(c.stringWidth(witness_street_city_state, "Times-Roman", 12), 200) + 2, y, ".")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, "I intend to live in the State of Nevada for the foreseeable future.")
    y -= LINE_HEIGHT * 1.5

    # 3.
    c.drawString(INDENT, y, "3.")
    c.drawString(INDENT + 18, y, "To my personal knowledge, (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("To my personal knowledge, (", "Times-Roman", 12), y, "name of spouse whose residency is being established")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("To my personal knowledge, (name of spouse whose residency is being established", "Times-Roman", 12), y, ")")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, resident_spouse)
    draw_underline(c, INDENT + 18, y, max(c.stringWidth(resident_spouse, "Times-Roman", 12), 250))
    c.drawString(INDENT + 18 + max(c.stringWidth(resident_spouse, "Times-Roman", 12), 250) + 4, y, " lives at (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + max(c.stringWidth(resident_spouse, "Times-Roman", 12), 250) + 4 + c.stringWidth(" lives at (", "Times-Roman", 12), y, "street, city, state")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + max(c.stringWidth(resident_spouse, "Times-Roman", 12), 250) + 4 + c.stringWidth(" lives at (street, city, state", "Times-Roman", 12), y, ")")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, resident_address)
    draw_underline(c, INDENT + 18, y, max(c.stringWidth(resident_address, "Times-Roman", 12), 400))
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, "and has been physically living within the State of Nevada on a daily basis for at least")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 18, y, "six (6) weeks prior to the filing of this action.")

    draw_footer(c)
    c.showPage()

    # =========================================================================
    # PAGE 2
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    c.setFont("Times-Roman", 12)

    # 4.
    c.drawString(INDENT, y, "4.")
    c.drawString(INDENT + 18, y, "To my personal knowledge, (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("To my personal knowledge, (", "Times-Roman", 12), y, "name of spouse whose residency is being established")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("To my personal knowledge, (name of spouse whose residency is being established", "Times-Roman", 12), y, ")")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, resident_spouse)
    draw_underline(c, INDENT + 18, y, max(c.stringWidth(resident_spouse, "Times-Roman", 12), 250))
    c.drawString(INDENT + 18 + max(c.stringWidth(resident_spouse, "Times-Roman", 12), 250) + 4, y, " has physically lived in the State of")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, "Nevada since (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("Nevada since (", "Times-Roman", 12), y, "date")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("Nevada since (date", "Times-Roman", 12), y, ") ")
    date_x = INDENT + 18 + c.stringWidth("Nevada since (date) ", "Times-Roman", 12)
    c.drawString(date_x, y, residency_since)
    draw_underline(c, date_x, y, max(c.stringWidth(residency_since, "Times-Roman", 12), 120))
    c.drawString(date_x + max(c.stringWidth(residency_since, "Times-Roman", 12), 120) + 2, y, ".")
    y -= LINE_HEIGHT * 1.5

    # 5.
    c.drawString(INDENT, y, "5.")
    c.drawString(INDENT + 18, y, "I see the named party an average of (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("I see the named party an average of (", "Times-Roman", 12), y, "number")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("I see the named party an average of (number", "Times-Roman", 12), y, ") ")
    num_x = INDENT + 18 + c.stringWidth("I see the named party an average of (number) ", "Times-Roman", 12)
    c.drawString(num_x, y, times_per_week)
    draw_underline(c, num_x, y, max(c.stringWidth(times_per_week, "Times-Roman", 12), 60))
    c.drawString(num_x + max(c.stringWidth(times_per_week, "Times-Roman", 12), 60) + 4, y, " times per week.")
    y -= LINE_HEIGHT * 1.5

    # 6.
    c.drawString(INDENT, y, "6.")
    c.drawString(INDENT + 18, y, "I know the named party because (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("I know the named party because (", "Times-Roman", 12), y, "explain how you know the spouse")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("I know the named party because (explain how you know the spouse", "Times-Roman", 12), y, ")")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, relationship)
    draw_underline(c, INDENT + 18, y, 400)
    y -= LINE_HEIGHT
    draw_underline(c, INDENT + 18, y, 400)
    c.drawString(INDENT + 18 + 402, y, ".")
    y -= LINE_HEIGHT * 1.5

    # 7.
    c.drawString(INDENT, y, "7.")
    c.drawString(INDENT + 18, y, "I know of my own personal knowledge that (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + 18 + c.stringWidth("I know of my own personal knowledge that (", "Times-Roman", 12), y, "name of person whose residency is")
    y -= LINE_HEIGHT
    c.drawString(INDENT + 18, y, "being established")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + 18 + c.stringWidth("being established", "Times-Italic", 12), y, ") ")
    name_x = INDENT + 18 + c.stringWidth("being established) ", "Times-Roman", 12)
    c.drawString(name_x, y, resident_spouse)
    draw_underline(c, name_x, y, max(c.stringWidth(resident_spouse, "Times-Roman", 12), 200))
    c.drawString(name_x + max(c.stringWidth(resident_spouse, "Times-Roman", 12), 200) + 4, y, " is a bona fide resident")
    y -= LINE_HEIGHT

    c.drawString(INDENT + 18, y, "of the State of Nevada.")
    y -= LINE_HEIGHT * 2.5

    # Declaration
    c.setFont("Times-Bold", 12)
    decl = "Pursuant to NRS 53.045, I declare under penalty of perjury that the foregoing is"
    c.drawString(INDENT, y, decl)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "true and correct.")
    y -= LINE_HEIGHT * 2

    c.setFont("Times-Roman", 12)
    c.drawString(INDENT, y, "Executed on (")
    c.setFont("Times-Italic", 12)
    c.drawString(INDENT + c.stringWidth("Executed on (", "Times-Roman", 12), y, "date")
    c.setFont("Times-Roman", 12)
    c.drawString(INDENT + c.stringWidth("Executed on (date", "Times-Roman", 12), y, ") ")
    draw_underline(c, INDENT + c.stringWidth("Executed on (date) ", "Times-Roman", 12), y, 200)
    c.drawString(INDENT + c.stringWidth("Executed on (date) ", "Times-Roman", 12) + 202, y, ".")
    y -= LINE_HEIGHT * 3

    # Signature
    sig_x = PAGE_WIDTH / 2
    c.setFont("Times-Italic", 12)
    c.drawString(sig_x, y, "(Signature)")
    c.drawString(sig_x + c.stringWidth("(Signature) ", "Times-Italic", 12), y, "\u25b8")
    draw_underline(c, sig_x + c.stringWidth("(Signature) \u25b8 ", "Times-Roman", 12), y, 180)
    y -= LINE_HEIGHT * 1.5

    c.drawString(sig_x, y, "(Printed Name)")
    draw_underline(c, sig_x + c.stringWidth("(Printed Name) ", "Times-Italic", 12), y, 180)

    draw_footer(c)
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "firstSpouseName": "JOHN DOE",
        "secondSpouseName": "JANE DOE",
        "county": "Clark",
        "witnessName": "ROBERT SMITH",
        "witnessAddress": "5678 Sahara Ave",
        "witnessCityStateZip": "Las Vegas, NV 89102",
        "witnessPhone": "(702) 555-9999",
        "witnessEmail": "robert@example.com",
        "witnessYearsInNV": "15",
        "witnessStreetCityState": "5678 Sahara Ave, Las Vegas, Nevada",
        "residentSpouseName": "JOHN DOE",
        "residentSpouseAddress": "1234 Las Vegas Blvd S, Las Vegas, Nevada",
        "residencySinceDate": "January 1, 2026",
        "witnessTimesPerWeek": "3-4",
        "witnessRelationship": "We are coworkers at the same company and have been friends for 5 years",
    }
    output = generate_nv_affidavit(test_data, "/tmp/test_nv_affidavit.pdf")
    print(f"Generated: {output}")
