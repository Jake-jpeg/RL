#!/usr/bin/env python3
"""
DivorceGPT NV - Request for Submission & Index of Exhibits PDF Generator
=========================================================================

Generates the Washoe County Request for Submission and Index of Exhibits — 2 pages.
Based on the Second Judicial District Court form (revised 10/24/2025, Code: 3860).

This form is ONLY required for Washoe County (Reno). Clark County does NOT use it.
In Washoe, this is filed together with the Index of Exhibits as one combined PDF.
The Exhibit Cover Page + Decree of Divorce is then attached as a continuation document.

Page 1: Request for Submission — asks the judge to review and decide the case
Page 2: Index of Exhibits — lists the exhibits (the Decree of Divorce)
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


def draw_underline(c, x, y, width):
    c.setLineWidth(0.5)
    c.line(x, y - 2, x + width, y - 2)


def draw_footer(c, page_num, total_pages):
    c.setFont("Times-Roman", 9)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 30,
                 "This Request for Submission was revised on 10/24/2025 by SB.")
    c.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, MARGIN_BOTTOM - 30,
                      f"Page {page_num} of {total_pages}")


def generate_nv_request_submission(data, output_path):
    """
    Generate NV Request for Submission & Index of Exhibits PDF (Washoe County only).

    Required data keys:
    - firstSpouseName: First Joint Petitioner name
    - secondSpouseName: Second Joint Petitioner name
    - firstSpouseAddress: Petitioner street address
    - firstSpouseCityStateZip: Petitioner city, state, zip
    - firstSpousePhone: Petitioner phone
    - firstSpouseEmail: Petitioner email
    - filingDate: Date the Joint Petition was filed with the court (may be blank)

    Optional data keys (auto-populated for DivorceGPT):
    - documentName: Name of document filed (defaults to "Joint Petition for Summary Decree of Divorce")
    - exhibitDescription: Description of exhibit (defaults to "Decree of Divorce")
    - exhibitPages: Number of pages in decree exhibit (defaults to blank for user to fill)
    """

    c = canvas.Canvas(output_path, pagesize=letter)

    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()
    spouse1_address = data.get('firstSpouseAddress', '').strip()
    spouse1_csz = data.get('firstSpouseCityStateZip', '').strip()
    spouse1_phone = data.get('firstSpousePhone', '').strip()
    spouse1_email = data.get('firstSpouseEmail', '').strip()
    filing_date = data.get('filingDate', '').strip()
    document_name = data.get('documentName',
                             'Joint Petition for Summary Decree of Divorce').strip()
    exhibit_desc = data.get('exhibitDescription', 'Decree of Divorce').strip()
    exhibit_pages = data.get('exhibitPages', '').strip()

    # =========================================================================
    # PAGE 1 — Request for Submission
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    # Code reference (top right)
    c.setFont("Times-Roman", 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, y, "Code: 3860")
    y -= LINE_HEIGHT * 1.5

    # Header block — petitioner contact info
    c.setFont("Times-Roman", 10)
    label_x = MARGIN_LEFT
    value_x = MARGIN_LEFT + 90

    c.drawString(label_x, y, "Name:")
    c.drawString(value_x, y, spouse1_name)
    draw_underline(c, value_x, y, 200)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Address:")
    c.drawString(value_x, y, spouse1_address)
    draw_underline(c, value_x, y, 200)
    y -= LINE_HEIGHT

    c.drawString(value_x, y, spouse1_csz)
    draw_underline(c, value_x, y, 200)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Telephone:")
    c.drawString(value_x, y, spouse1_phone)
    draw_underline(c, value_x, y, 200)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Email:")
    c.drawString(value_x, y, spouse1_email)
    draw_underline(c, value_x, y, 200)
    y -= LINE_HEIGHT

    c.drawString(label_x, y, "Self-Represented Litigant")
    y -= LINE_HEIGHT * 2

    # Court header
    c.setFont("Times-Bold", 11)
    header1 = "IN THE FAMILY DIVISION"
    c.drawString((PAGE_WIDTH - c.stringWidth(header1, "Times-Bold", 11)) / 2, y, header1)
    y -= LINE_HEIGHT
    header2 = "OF THE SECOND JUDICIAL DISTRICT COURT OF THE STATE OF NEVADA"
    c.drawString((PAGE_WIDTH - c.stringWidth(header2, "Times-Bold", 11)) / 2, y, header2)
    y -= LINE_HEIGHT
    header3 = "IN AND FOR THE COUNTY OF WASHOE"
    c.drawString((PAGE_WIDTH - c.stringWidth(header3, "Times-Bold", 11)) / 2, y, header3)
    y -= LINE_HEIGHT * 2

    # Caption block
    caption_mid = PAGE_WIDTH / 2
    box_top = y + LINE_HEIGHT * 0.5

    c.setFont("Times-Roman", 12)
    draw_underline(c, MARGIN_LEFT, y, 200)
    c.drawString(MARGIN_LEFT, y, spouse1_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Plaintiff / Petitioner / Joint Petitioner,")

    # Right side: Case No. and Dept.
    right_x = caption_mid + 20
    c.drawString(right_x, y + LINE_HEIGHT, "Case No. ")
    draw_underline(c, right_x + c.stringWidth("Case No. ", "Times-Roman", 12),
                   y + LINE_HEIGHT, 120)
    c.drawString(right_x, y, "Dept. No. ")
    draw_underline(c, right_x + c.stringWidth("Dept. No. ", "Times-Roman", 12),
                   y, 120)

    y -= LINE_HEIGHT * 1.2
    c.drawString(MARGIN_LEFT, y, "vs.")
    y -= LINE_HEIGHT * 1.2

    draw_underline(c, MARGIN_LEFT, y, 200)
    c.drawString(MARGIN_LEFT, y, spouse2_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Defendant / Respondent / Joint Petitioner.")

    box_bottom = y - LINE_HEIGHT * 0.5
    c.setLineWidth(0.5)
    c.line(caption_mid, box_top, caption_mid, box_bottom)

    # Separator line
    y = box_bottom - LINE_HEIGHT * 0.5
    c.line(MARGIN_LEFT, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT * 2

    # Title
    c.setFont("Times-Bold", 14)
    title = "REQUEST FOR SUBMISSION"
    c.drawString((PAGE_WIDTH - c.stringWidth(title, "Times-Bold", 14)) / 2, y, title)
    y -= LINE_HEIGHT * 2.5

    # Body text
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "I request that the (")
    c.setFont("Times-Italic", 10)
    c.drawString(MARGIN_LEFT + c.stringWidth("I request that the (", "Times-Roman", 12),
                 y, "Name of document that was filed with the Court")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth(
        "I request that the (Name of document that was filed with the Court",
        "Times-Roman", 12), y, ")")
    y -= LINE_HEIGHT * 1.2

    # Document name on underline
    c.drawString(MARGIN_LEFT, y, document_name)
    draw_underline(c, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.2

    c.drawString(MARGIN_LEFT, y, "that was filed on (")
    c.setFont("Times-Italic", 10)
    c.drawString(MARGIN_LEFT + c.stringWidth("that was filed on (", "Times-Roman", 12),
                 y, "Date the document was filed with the Court")
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + c.stringWidth(
        "that was filed on (Date the document was filed with the Court",
        "Times-Roman", 12), y, ") ")
    y -= LINE_HEIGHT * 1.2

    # Filing date on underline
    c.drawString(MARGIN_LEFT, y, filing_date)
    draw_underline(c, MARGIN_LEFT, y, 200)
    c.drawString(MARGIN_LEFT + 210, y, "be submitted to the")
    y -= LINE_HEIGHT * 1.2

    c.drawString(MARGIN_LEFT, y, "Court for decision.")
    y -= LINE_HEIGHT * 2.5

    # NRS disclaimer
    c.setFont("Times-Roman", 11)
    disclaimer = ("This document does not contain the Personal Information "
                  "of any person as defined by")
    c.drawString(MARGIN_LEFT, y, disclaimer)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "NRS 603A.040.")
    y -= LINE_HEIGHT * 3

    # Date and signature
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Date: ")
    draw_underline(c, MARGIN_LEFT + c.stringWidth("Date: ", "Times-Roman", 12),
                   y, 150)

    sig_x = PAGE_WIDTH / 2 + 10
    c.drawString(sig_x, y, "Signature:")
    draw_underline(c, sig_x + c.stringWidth("Signature: ", "Times-Roman", 12),
                   y, 160)
    y -= LINE_HEIGHT * 1.5

    c.drawString(sig_x, y, "Print Your Name:")
    draw_underline(c, sig_x + c.stringWidth("Print Your Name: ", "Times-Roman", 12),
                   y, 120)

    draw_footer(c, 1, 2)
    c.showPage()

    # =========================================================================
    # PAGE 2 — Index of Exhibits
    # =========================================================================
    y = PAGE_HEIGHT - MARGIN_TOP

    c.setFont("Times-Bold", 14)
    title2 = "INDEX OF EXHIBITS"
    c.drawString((PAGE_WIDTH - c.stringWidth(title2, "Times-Bold", 14)) / 2, y, title2)
    y -= LINE_HEIGHT * 3

    c.setFont("Times-Roman", 12)

    # For DivorceGPT no-children joint petition, there is exactly one exhibit:
    # the Decree of Divorce. We pre-fill line 1 and leave the rest blank.
    for i in range(9):
        # Exhibit Number
        c.drawString(MARGIN_LEFT, y, "Exhibit Number ")
        num_x = MARGIN_LEFT + c.stringWidth("Exhibit Number ", "Times-Roman", 12)
        if i == 0:
            c.drawString(num_x, y, "1")
        draw_underline(c, num_x, y, 60)

        # Number of Pages
        pages_label_x = num_x + 80
        c.drawString(pages_label_x, y, "Number of Pages ")
        pages_val_x = pages_label_x + c.stringWidth("Number of Pages ", "Times-Roman", 12)
        if i == 0:
            c.drawString(pages_val_x, y, exhibit_pages)
        draw_underline(c, pages_val_x, y, 60)
        y -= LINE_HEIGHT * 1.5

        # Exhibit Description
        c.drawString(MARGIN_LEFT, y, "Exhibit Description ")
        desc_x = MARGIN_LEFT + c.stringWidth("Exhibit Description ", "Times-Roman", 12)
        if i == 0:
            c.drawString(desc_x, y, exhibit_desc)
        draw_underline(c, desc_x, y, CONTENT_WIDTH - c.stringWidth(
            "Exhibit Description ", "Times-Roman", 12))
        y -= LINE_HEIGHT * 2

    draw_footer(c, 2, 2)
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "firstSpouseName": "JOHN DOE",
        "secondSpouseName": "JANE DOE",
        "firstSpouseAddress": "1234 Virginia St",
        "firstSpouseCityStateZip": "Reno, NV 89501",
        "firstSpousePhone": "(775) 555-1234",
        "firstSpouseEmail": "john@example.com",
        "filingDate": "",
        "documentName": "Joint Petition for Summary Decree of Divorce",
        "exhibitDescription": "Decree of Divorce",
        "exhibitPages": "",
    }
    output = generate_nv_request_submission(test_data, "/tmp/test_nv_request_submission.pdf")
    print(f"Generated: {output}")
