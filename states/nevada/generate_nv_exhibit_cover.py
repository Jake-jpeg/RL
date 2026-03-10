#!/usr/bin/env python3
"""
DivorceGPT NV - Exhibit Cover Page PDF Generator
==================================================

Generates the Washoe County Exhibit Cover Page — 1 page.
This is a simple separator page that goes in front of the Decree of Divorce
when filed as a continuation/attachment to the Request for Submission in eFlex.

Washoe County eFlex filing instructions:
- Request for Submission + Index of Exhibits → uploaded as one PDF (Document Type: Request for Submission)
- Exhibit Cover Page + Decree of Divorce → uploaded as one PDF attached to the above (Document Type: **Continuation)

This generator creates ONLY the cover page. The Decree of Divorce follows it.
In production, the PDF server should merge this cover page with the Decree
into a single PDF for the user.
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


def draw_underline(c, x, y, width):
    c.setLineWidth(0.5)
    c.line(x, y - 2, x + width, y - 2)


def generate_nv_exhibit_cover(data, output_path):
    """
    Generate NV Exhibit Cover Page PDF (Washoe County only).

    Required data keys:
    - firstSpouseName: First Joint Petitioner name
    - secondSpouseName: Second Joint Petitioner name
    - exhibitNumber: Exhibit number (defaults to "1")
    - exhibitDescription: Description (defaults to "Decree of Divorce")
    """

    c = canvas.Canvas(output_path, pagesize=letter)

    spouse1_name = data.get('firstSpouseName', '').strip()
    spouse2_name = data.get('secondSpouseName', '').strip()
    exhibit_num = data.get('exhibitNumber', '1').strip()
    exhibit_desc = data.get('exhibitDescription', 'Decree of Divorce').strip()

    y = PAGE_HEIGHT - MARGIN_TOP

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
    y -= LINE_HEIGHT * 2.5

    # Caption block
    caption_mid = PAGE_WIDTH / 2
    box_top = y + LINE_HEIGHT * 0.5

    c.setFont("Times-Roman", 12)
    draw_underline(c, MARGIN_LEFT, y, 200)
    c.drawString(MARGIN_LEFT, y, spouse1_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Joint Petitioner,")

    right_x = caption_mid + 20
    c.drawString(right_x, y + LINE_HEIGHT, "Case No. ")
    draw_underline(c, right_x + c.stringWidth("Case No. ", "Times-Roman", 12),
                   y + LINE_HEIGHT, 120)
    c.drawString(right_x, y, "Dept. No. ")
    draw_underline(c, right_x + c.stringWidth("Dept. No. ", "Times-Roman", 12),
                   y, 120)

    y -= LINE_HEIGHT * 1.2
    c.drawString(MARGIN_LEFT, y, "and")
    y -= LINE_HEIGHT * 1.2

    draw_underline(c, MARGIN_LEFT, y, 200)
    c.drawString(MARGIN_LEFT, y, spouse2_name)
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Joint Petitioner.")

    box_bottom = y - LINE_HEIGHT * 0.5
    c.setLineWidth(0.5)
    c.line(caption_mid, box_top, caption_mid, box_bottom)

    y = box_bottom - LINE_HEIGHT * 0.5
    c.line(MARGIN_LEFT, y, PAGE_WIDTH - MARGIN_RIGHT, y)

    # Large centered exhibit label
    y -= LINE_HEIGHT * 6

    c.setFont("Times-Bold", 24)
    exhibit_label = f"EXHIBIT {exhibit_num}"
    c.drawString(
        (PAGE_WIDTH - c.stringWidth(exhibit_label, "Times-Bold", 24)) / 2,
        y, exhibit_label)
    y -= LINE_HEIGHT * 3

    c.setFont("Times-Roman", 16)
    c.drawString(
        (PAGE_WIDTH - c.stringWidth(exhibit_desc, "Times-Roman", 16)) / 2,
        y, exhibit_desc)

    # Footer
    c.setFont("Times-Roman", 9)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 30, "Exhibit Cover Page")
    c.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, MARGIN_BOTTOM - 30, "Page 1 of 1")

    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "firstSpouseName": "JOHN DOE",
        "secondSpouseName": "JANE DOE",
        "exhibitNumber": "1",
        "exhibitDescription": "Decree of Divorce",
    }
    output = generate_nv_exhibit_cover(test_data, "/tmp/test_nv_exhibit_cover.pdf")
    print(f"Generated: {output}")
