#!/usr/bin/env python3
"""
DivorceGPT UD-7 (Affirmation of Defendant) PDF Generator
=======================================================

Defendant's affidavit consenting to uncontested divorce.
Simplified for DivorceGPT scope: no children, no assets, no maintenance.
"""

from reportlab.lib.pagesizes import letter

from .children import affidavit_clause
from reportlab.pdfgen import canvas

from .layout import TOP_Y, caption_title, fit_text, draw_caption

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points
MARGIN_LEFT = 72   # 1 inch
MARGIN_RIGHT = 72
MARGIN_TOP = 72
MARGIN_BOTTOM = 72

# Content area
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 468 points

# Line height
LINE_HEIGHT = 14

# Box layout positions
BOX1_LEFT_X = MARGIN_LEFT
BOX1_RIGHT_X = PAGE_WIDTH / 2

BOX2_LEFT_X = PAGE_WIDTH / 2
BOX2_RIGHT_X = PAGE_WIDTH - MARGIN_RIGHT


def draw_wrapped_text(c, text, x, y, max_width, font_name="Times-Roman", font_size=12):
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
        y -= LINE_HEIGHT
    
    return y


def generate_ud7(data, output_path):
    """Generate UD-7 (Affirmation of Defendant) PDF."""
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract variables
    county_name = data.get('county', '').strip()
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    defendant_name = data.get('defendantName', '').strip()
    plaintiff_name_upper = plaintiff_name.upper()
    defendant_name_upper = defendant_name.upper()
    index_number = data.get('indexNumber', '').strip()
    
    defendant_address = data.get('defendantAddress', '').strip()
    
    # Summons date (date on the UD-1 Summons with Notice)
    summons_date = data.get('summonsDate', '').strip()
    
    # Religious ceremony - affects barriers to remarriage section
    religious_ceremony = data.get('religiousCeremony', False)
    
    # For affirmation
    state_signed = data.get('stateSigned', 'NEW YORK').strip().upper()
    county_signed = data.get('countySigned', county_name).strip().upper()
    
    # =========================================================================
    # PAGE 1
    # =========================================================================
    
    y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
    
    # The standard litigation caption (layout.draw_caption) — geometry
    # matched to the operator's own filed papers: the X of each dashed
    # rule lands at the header's right edge, and -against- gets a blank
    # line of air on both sides.
    y = draw_caption(c, county_upper, plaintiff_name_upper, defendant_name_upper,
                     "AFFIRMATION OF DEFENDANT", y, index_no=index_number)
    
    # State/County line
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"STATE OF {state_signed}, COUNTY OF {county_signed}, ss:")
    y -= LINE_HEIGHT * 1.5
    
    # Opening - Defendant's name and address
    defendant_address_display = defendant_address if defendant_address else "_____________________________________________"
    
    para_open = f"{defendant_name}, affirms the following under the penalties of perjury:"
    y = draw_wrapped_text(c, para_open, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    para1 = f"I am the Defendant in the within action for divorce, and I am over the age of 18. I reside at {defendant_address_display}."
    y = draw_wrapped_text(c, para1, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # 1. Service acknowledgment - references the Summons with Notice date
    summons_date_display = summons_date if summons_date else "_______________"
    para2 = f"1. I admit service of the Summons with Notice dated {summons_date_display}, wherein the grounds for divorce alleged are: DRL §170 subd. (7) - The relationship between Plaintiff and Defendant has broken down irretrievably for a period of at least six months."
    y = draw_wrapped_text(c, para2, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    para2b = "I also admit service of the Notice of Automatic Orders and the Notice of Guideline Maintenance."
    y = draw_wrapped_text(c, para2b, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # 2. Consent to uncontested calendar
    para3 = "2. I appear in this action; however, I do not intend to respond to the summons or answer the complaint, and I waive the twenty (20) or thirty (30) day period provided by law to respond to the summons or answer the complaint. I waive the forty (40) day waiting period to place this matter on the calendar, and I hereby consent to this action being placed on the uncontested divorce calendar immediately."
    y = draw_wrapped_text(c, para3, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check page break
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 8:
        c.showPage()
        y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
        c.setFont("Times-Roman", 12)
    
    # 3. Military status
    c.drawString(MARGIN_LEFT, y, "3. [X] I am not a member of the military service of this state, any other state, or this nation.")
    y -= LINE_HEIGHT * 1.5
    
    # 4. Waiver of further papers
    para4 = "4. [X] I waive service of all further papers in this action except for a copy of the final Judgment of Divorce."
    y = draw_wrapped_text(c, para4, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # 5. No equitable distribution / maintenance
    para5a = "5a. I am not seeking equitable distribution other than what was already agreed to in a written stipulation. I understand that I may be prevented from further asserting my right to equitable distribution."
    y = draw_wrapped_text(c, para5a, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    para5b = "5b. [X] I am not seeking maintenance as payee."
    y = draw_wrapped_text(c, para5b, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check page break
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 8:
        c.showPage()
        y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
        c.setFont("Times-Roman", 12)
    
    # 6. Barriers to remarriage
    if religious_ceremony:
        para6a = "6a. I will take or have taken all steps solely within my power to remove any barriers to the Plaintiff's remarriage."
        y = draw_wrapped_text(c, para6a, MARGIN_LEFT, y, CONTENT_WIDTH)
        y -= LINE_HEIGHT
        para6b = "6b. [ ] I waive the requirements of DRL §253 subdivisions (2), (3), and (4)."
        y = draw_wrapped_text(c, para6b, MARGIN_LEFT, y, CONTENT_WIDTH)
    else:
        para6 = "6. The Barriers to Remarriage provisions (DRL §253) do not apply as the marriage was not performed in a religious ceremony."
        y = draw_wrapped_text(c, para6, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # 7. Children of the marriage — READ FROM THE PAYLOAD. UD-7 is SWORN.
    para7 = affidavit_clause(data, "7.")
    y = draw_wrapped_text(c, para7, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # 8. Health care notice
    para8 = "8. I have been provided a copy of Notice Relating to Health Care of the Parties. I fully understand that upon the entrance of this divorce judgment, I may no longer be allowed to receive health coverage under my former spouse's health insurance plan."
    y = draw_wrapped_text(c, para8, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check page break before signature
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 16:  # same 13-line math as UD-6
        c.showPage()
        y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
        c.setFont("Times-Roman", 12)
    
    # 9. Guideline maintenance notice
    para9 = "9. I acknowledge receipt of the Notice of Guideline Maintenance."
    y = draw_wrapped_text(c, para9, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 2
    
    # Affirmation under penalty of perjury
    affirm_text = "I, ________________________ (print or type name), affirm this ___ day of ______, ____, under the penalties of perjury, under the laws of New York, which may include a fine or imprisonment, that the foregoing is true, except as to matters alleged on information and belief and as to those matters I believe it to be true, and I understand that this document may be filed in an action or proceeding in a court of law."
    y = draw_wrapped_text(c, affirm_text, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 3
    
    # Signature line - right side
    sig_x = PAGE_WIDTH / 2 + 20
    c.setLineWidth(0.25)
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(sig_x, y, "Defendant's Signature")
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(sig_x, y, defendant_name)
    
    # Footer - Form ID in bottom margin
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, 36, "(Form UD-7)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # Test with CIVIL ceremony
    test_data_civil = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Orange",
        "indexNumber": "12345/2027",
        "defendantAddress": "123 Main Street, Newburgh, NY 12550",
        "summonsDate": "January 15, 2027",
        "religiousCeremony": False,
        "stateSigned": "New York",
        "countySigned": "Orange",
    }
    
    output = generate_ud7(test_data_civil, "/home/claude/test_ud7_civil.pdf")
    print(f"Generated CIVIL: {output}")
    
    # Test with RELIGIOUS ceremony
    test_data_religious = test_data_civil.copy()
    test_data_religious["religiousCeremony"] = True
    output = generate_ud7(test_data_religious, "/home/claude/test_ud7_religious.pdf")
    print(f"Generated RELIGIOUS: {output}")
