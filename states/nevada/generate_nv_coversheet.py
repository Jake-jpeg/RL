#!/usr/bin/env python3
"""
DivorceGPT NV - Family Court Cover Sheet PDF Generator
========================================================

Generates the Nevada Civil (Family/Juvenile-Related) Cover Sheet — 1 page.
Based on the Nevada AOC standardized form (Pursuant to NRS 3.275, Rev. P3.2).

For DivorceGPT scope: pre-checks "Joint Petition - Without Children" and fills party info.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN_LEFT = 54  # Tighter margins for coversheet (form is dense)
MARGIN_RIGHT = 54
MARGIN_TOP = 54
MARGIN_BOTTOM = 54
LINE_HEIGHT = 12
SMALL_LINE = 10


def draw_underline(c, x, y, width):
    c.setLineWidth(0.5)
    c.line(x, y - 2, x + width, y - 2)


def draw_checkbox(c, x, y, checked=False, size=8):
    c.setLineWidth(0.5)
    c.rect(x, y - 1, size, size, stroke=1, fill=0)
    if checked:
        c.setLineWidth(1)
        c.line(x + 1.5, y + 2, x + 3.5, y)
        c.line(x + 3.5, y, x + 6.5, y + 6)
        c.setLineWidth(0.5)


def generate_nv_coversheet(data, output_path):
    """
    Generate NV Family Court Cover Sheet PDF.

    Required data keys:
    - firstSpouseName, firstSpouseAddress, firstSpouseCityStateZip
    - firstSpousePhone, firstSpouseEmail, firstSpouseDOB
    - secondSpouseName, secondSpouseAddress, secondSpouseCityStateZip
    - secondSpousePhone, secondSpouseEmail, secondSpouseDOB
    - county: Nevada county
    """

    c = canvas.Canvas(output_path, pagesize=letter)

    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse1_address = data.get('firstSpouseAddress', '').strip()
    spouse1_csz = data.get('firstSpouseCityStateZip', '').strip()
    spouse1_phone = data.get('firstSpousePhone', '').strip()
    spouse1_email = data.get('firstSpouseEmail', '').strip()
    spouse1_dob = data.get('firstSpouseDOB', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()
    spouse2_address = data.get('secondSpouseAddress', '').strip()
    spouse2_csz = data.get('secondSpouseCityStateZip', '').strip()
    spouse2_phone = data.get('secondSpousePhone', '').strip()
    spouse2_email = data.get('secondSpouseEmail', '').strip()
    spouse2_dob = data.get('secondSpouseDOB', '').strip()
    county = data.get('county', '').strip()

    y = PAGE_HEIGHT - MARGIN_TOP

    # =========================================================================
    # TITLE
    # =========================================================================
    c.setFont("Times-Bold", 11)
    title = "CIVIL (FAMILY/JUVENILE-RELATED) COVER SHEET"
    title_w = c.stringWidth(title, "Times-Bold", 11)
    c.drawString((PAGE_WIDTH - title_w) / 2, y, title)
    y -= LINE_HEIGHT * 1.2

    # County and Case No
    c.setFont("Times-Roman", 10)
    draw_underline(c, PAGE_WIDTH / 2 - 40, y, 100)
    c.drawString(PAGE_WIDTH / 2 - 40, y, county)
    c.drawString(PAGE_WIDTH / 2 + 64, y, " County, Nevada")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT + 180, y, "Case No. ")
    draw_underline(c, MARGIN_LEFT + 230, y, 150)
    y -= SMALL_LINE
    c.setFont("Times-Italic", 8)
    c.drawString(MARGIN_LEFT + 260, y, "(Assigned by Clerk\u2019s Office)")
    y -= LINE_HEIGHT * 1.2

    # =========================================================================
    # SECTION I: PARTY INFORMATION
    # =========================================================================
    c.setFont("Times-Bold", 10)
    c.drawString(MARGIN_LEFT, y, "I. Party Information")
    c.setFont("Times-Italic", 8)
    c.drawString(MARGIN_LEFT + c.stringWidth("I. Party Information ", "Times-Bold", 10), y, "(provide both home and mailing addresses if different)")
    y -= LINE_HEIGHT * 1.2

    mid_x = PAGE_WIDTH / 2 + 10
    left_col = MARGIN_LEFT
    c.setFont("Times-Roman", 9)

    # Left column: Plaintiff/Petitioner
    c.drawString(left_col, y, "Plaintiff/Petitioner (name/address/phone):")
    c.drawString(mid_x, y, "Defendant/Respondent/Co-petitioner (name/address/phone):")
    y -= LINE_HEIGHT

    # Spouse 1 info
    spouse1_info = f"{spouse1_name}, {spouse1_address}, {spouse1_csz}"
    c.drawString(left_col, y, spouse1_info[:60])
    if len(spouse1_info) > 60:
        y -= SMALL_LINE
        c.drawString(left_col, y, spouse1_info[60:])

    # Spouse 2 info
    spouse2_info = f"{spouse2_name}, {spouse2_address}, {spouse2_csz}"
    c.drawString(mid_x, y + (SMALL_LINE if len(spouse1_info) > 60 else 0), spouse2_info[:60])

    y -= LINE_HEIGHT * 2

    # DOB
    c.drawString(left_col, y, "D.O.B.")
    c.drawString(left_col + 40, y, spouse1_dob)
    draw_underline(c, left_col + 40, y, 100)
    c.drawString(mid_x, y, "D.O.B.")
    c.drawString(mid_x + 40, y, spouse2_dob)
    draw_underline(c, mid_x + 40, y, 100)
    y -= LINE_HEIGHT

    # Email
    c.drawString(left_col, y, "E-mail address:")
    c.drawString(left_col + 72, y, spouse1_email)
    draw_underline(c, left_col + 72, y, 160)
    c.drawString(mid_x, y, "E-mail address:")
    c.drawString(mid_x + 72, y, spouse2_email)
    draw_underline(c, mid_x + 72, y, 160)
    y -= LINE_HEIGHT

    # Attorney (Self-Represented — left blank)
    c.drawString(left_col, y, "Attorney (name/address/phone): Self-Represented")
    c.drawString(mid_x, y, "Attorney (name/address/phone): Self-Represented")
    y -= LINE_HEIGHT * 2

    # Interpreter
    c.drawString(left_col, y, "Will an Interpreter be required for court hearings?")
    draw_checkbox(c, left_col + c.stringWidth("Will an Interpreter be required for court hearings? ", "Times-Roman", 9), y - 1, checked=False)
    c.drawString(left_col + c.stringWidth("Will an Interpreter be required for court hearings? ", "Times-Roman", 9) + 12, y, "Yes")
    draw_checkbox(c, left_col + c.stringWidth("Will an Interpreter be required for court hearings? Yes ", "Times-Roman", 9) + 12, y - 1, checked=True)
    c.drawString(left_col + c.stringWidth("Will an Interpreter be required for court hearings? Yes ", "Times-Roman", 9) + 24, y, "No")
    y -= LINE_HEIGHT * 1.5

    # =========================================================================
    # SECTION II: NATURE OF CONTROVERSY
    # =========================================================================
    c.setFont("Times-Bold", 10)
    c.drawString(MARGIN_LEFT, y, "II. Nature of Controversy")
    c.setFont("Times-Italic", 8)
    c.drawString(MARGIN_LEFT + c.stringWidth("II. Nature of Controversy ", "Times-Bold", 10), y, "(Please check the most appropriate case type listed below)")
    y -= LINE_HEIGHT

    c.setFont("Times-Bold", 9)
    c.drawString((PAGE_WIDTH - c.stringWidth("Family-Juvenile Related Cases", "Times-Bold", 9)) / 2, y, "Family-Juvenile Related Cases")
    y -= LINE_HEIGHT * 1.2

    # Two columns
    c.setFont("Times-Bold", 9)
    c.drawString(left_col + 20, y, "Domestic Relations Case Filing Types")
    c.drawString(mid_x, y, "Other Family Related Case Filing Types")
    y -= LINE_HEIGHT * 1.2

    c.setFont("Times-Bold", 9)
    c.drawString(left_col, y, "Marriage Dissolution Case")
    y -= LINE_HEIGHT

    # Checkboxes for case types
    c.setFont("Times-Roman", 9)
    case_types_left = [
        ("Annulment", False),
        ("Divorce - With Children", False),
        ("Divorce - Without Children", False),
        ("Foreign Decree", False),
        ("Joint Petition - With Children", False),
        ("Joint Petition - Without Children", True),  # <-- CHECKED
        ("Separate Maintenance", False),
    ]

    for label, checked in case_types_left:
        draw_checkbox(c, left_col + 10, y - 1, checked=checked, size=7)
        c.drawString(left_col + 22, y, label)
        y -= SMALL_LINE

    y -= LINE_HEIGHT * 2

    # Children section (none)
    c.setFont("Times-Bold", 9)
    c.drawString(left_col, y, "Children involved in this case:")
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 9)
    c.drawString(left_col, y, "Name:")
    draw_underline(c, left_col + 36, y, 200)
    c.drawString(left_col + 280, y, "DOB:")
    draw_underline(c, left_col + 306, y, 100)
    y -= LINE_HEIGHT * 3

    # Date and Signature
    draw_underline(c, left_col, y, 180)
    c.drawString(mid_x + 50, y, "Signature of initiating party or representative")
    draw_underline(c, mid_x + 50, y + LINE_HEIGHT, 200)
    y -= LINE_HEIGHT
    c.drawString(left_col, y, "Date")

    y -= LINE_HEIGHT * 2

    # Clark/Washoe note
    c.setFont("Times-BoldItalic", 8)
    note = "For Clark and Washoe Counties, please use their Family Court Cover Sheet for family-related case filings."
    note_w = c.stringWidth(note, "Times-BoldItalic", 8)
    c.drawString((PAGE_WIDTH - note_w) / 2, y, note)
    y -= SMALL_LINE
    note2 = "Please see the Family Court Clerk in those counties for copies of their forms."
    note2_w = c.stringWidth(note2, "Times-BoldItalic", 8)
    c.drawString((PAGE_WIDTH - note2_w) / 2, y, note2)

    # Bottom reference
    c.setFont("Times-Roman", 7)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 10, "Nevada AOC - Research Statistics Unit")
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 18, "Pursuant to NRS 3.275")
    c.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, MARGIN_BOTTOM - 18, "Rev. P3.2")

    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "firstSpouseName": "JOHN DOE",
        "firstSpouseAddress": "1234 Las Vegas Blvd S",
        "firstSpouseCityStateZip": "Las Vegas, NV 89109",
        "firstSpousePhone": "(702) 555-1234",
        "firstSpouseEmail": "john@example.com",
        "firstSpouseDOB": "01/15/1985",
        "secondSpouseName": "JANE DOE",
        "secondSpouseAddress": "1234 Las Vegas Blvd S",
        "secondSpouseCityStateZip": "Las Vegas, NV 89109",
        "secondSpousePhone": "(702) 555-5678",
        "secondSpouseEmail": "jane@example.com",
        "secondSpouseDOB": "03/22/1987",
        "county": "Clark",
    }
    output = generate_nv_coversheet(test_data, "/tmp/test_nv_coversheet.pdf")
    print(f"Generated: {output}")
