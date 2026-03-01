#!/usr/bin/env python3
"""
DivorceGPT UD-6 (Affirmation of Plaintiff) PDF Generator
=======================================================

Main substantive affidavit for uncontested divorce.
Simplified for DivorceGPT scope: no children, no assets, no maintenance.
Grounds: DRL §170(7) - irretrievable breakdown for 6+ months.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


def generate_ud6(data, output_path):
    """Generate UD-6 (Affirmation of Plaintiff) PDF."""
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract variables
    county_name = data.get('county', '').strip()
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    defendant_name = data.get('defendantName', '').strip()
    index_number = data.get('indexNumber', '').strip()
    
    plaintiff_address = data.get('plaintiffAddress', '').strip()
    defendant_address = data.get('defendantAddress', '').strip()
    
    # SSN - in memory only, displayed with dashes
    plaintiff_ssn = data.get('plaintiffSSN', 'XXX-XX-XXXX').strip()
    defendant_ssn = data.get('defendantSSN', 'XXX-XX-XXXX').strip()
    
    # Marriage info
    marriage_date = data.get('marriageDate', '').strip()
    marriage_place = data.get('marriagePlace', '').strip()  # City/Town, County, State
    religious_ceremony = data.get('religiousCeremony', False)
    
    # Residency - which applies
    residency_type = data.get('residencyType', 'A')  # A, B, C, D, E, or F
    
    # For affirmation
    state_signed = data.get('stateSigned', 'NEW YORK').strip().upper()
    county_signed = data.get('countySigned', county_name).strip().upper()
    
    # =========================================================================
    # PAGE 1
    # =========================================================================
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Header
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT
    
    # Dashed line with X (top of caption)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT
    
    # Plaintiff name
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"{plaintiff_name},")
    
    # Index No. (right side)
    index_display = index_number if index_number else "_______________"
    c.drawString(PAGE_WIDTH/2 + 95, y, f"Index No.: {index_display}")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    
    # Document title (right side, centered)
    c.setFont("Times-Bold", 12)
    right_center = PAGE_WIDTH/2 + 95 + (PAGE_WIDTH - MARGIN_RIGHT - (PAGE_WIDTH/2 + 95)) / 2
    title_text = "AFFIRMATION OF PLAINTIFF"
    c.drawString(right_center - c.stringWidth(title_text, "Times-Bold", 12)/2, y, title_text)
    y -= LINE_HEIGHT * 1.5
    
    # Defendant name
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"{defendant_name},")
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Defendant.")
    y -= LINE_HEIGHT
    
    # Dashed line with X (bottom of caption)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, y, "-" * 62 + "X")
    y -= LINE_HEIGHT * 1.5
    
    # State/County line
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"STATE OF {state_signed}, COUNTY OF {county_signed}, ss:")
    y -= LINE_HEIGHT * 1.5
    
    # Opening
    c.drawString(MARGIN_LEFT, y, f"{plaintiff_name}, being duly sworn, deposes and says:")
    y -= LINE_HEIGHT * 1.5
    
    # 1. Identity and addresses
    para1 = f"1. I am the Plaintiff in this action. I reside at {plaintiff_address if plaintiff_address else '_______________________________'}."
    y = draw_wrapped_text(c, para1, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 0.5
    
    para1b = f"Defendant resides at {defendant_address if defendant_address else '_______________________________'}."
    y = draw_wrapped_text(c, para1b, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 0.5
    
    # SSN line - LEFT BLANK, user must fill in manually
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "Plaintiff's Social Security Number: _____ - _____ - _________")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "Defendant's Social Security Number: _____ - _____ - _________")
    y -= LINE_HEIGHT
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "(YOU MUST MANUALLY WRITE IN THE FULL SOCIAL SECURITY NUMBERS ABOVE)")
    c.setFont("Times-Roman", 12)
    y -= LINE_HEIGHT * 1.5
    
    # 2. Residency requirement
    c.drawString(MARGIN_LEFT, y, "2. The residency requirement is satisfied as follows:")
    y -= LINE_HEIGHT
    
    # Residency checkboxes - simplified for our use case
    residency_options = {
        'A': "The parties were married in New York State and Plaintiff has resided in New York State for a continuous period of at least one year immediately preceding the commencement of this action.",
        'B': "The parties have resided as married persons in New York State and Plaintiff has resided in New York State for a continuous period of at least one year immediately preceding the commencement of this action.",
        'C': "The cause of action occurred in New York State and Plaintiff has resided in New York State for a continuous period of at least one year immediately preceding the commencement of this action.",
        'D': "The cause of action occurred in New York State and both parties were residents of New York State at the time of commencement of this action.",
        'E': "The parties were married in New York State and both parties were residents of New York State at the time of commencement of this action.",
        'F': "Either party has resided in New York State for a continuous period of at least two years immediately preceding the commencement of this action."
    }
    
    for opt, text in residency_options.items():
        box = "[X]" if residency_type == opt else "[ ]"
        c.setFont("Times-Roman", 12)
        c.drawString(MARGIN_LEFT + 20, y, f"{box} {opt}.")
        y -= LINE_HEIGHT
        y = draw_wrapped_text(c, text, MARGIN_LEFT + 50, y, CONTENT_WIDTH - 50, "Times-Roman", 12)
        y -= LINE_HEIGHT * 0.3
        
        # Check if we need to go to next page (1 inch bottom margin = 72 points)
        if y < MARGIN_BOTTOM + LINE_HEIGHT * 4:
            c.showPage()
            y = PAGE_HEIGHT - MARGIN_TOP
            c.setFont("Times-Roman", 12)
    
    y -= LINE_HEIGHT * 0.5
    
    # Check if remaining content fits, if not go to page 2
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 8:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
        c.setFont("Times-Roman", 12)
    
    # 3. Marriage info
    marriage_place_display = marriage_place if marriage_place else "_________________, _____________ County, ______________"
    marriage_date_display = marriage_date if marriage_date else "________________"
    
    para3 = f"3. Plaintiff and Defendant were married on {marriage_date_display} in {marriage_place_display}."
    y = draw_wrapped_text(c, para3, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    # Religious/civil ceremony
    if religious_ceremony:
        c.drawString(MARGIN_LEFT, y, "The marriage was performed in a religious ceremony.")
    else:
        c.drawString(MARGIN_LEFT, y, "The marriage was NOT performed in a religious ceremony.")
    y -= LINE_HEIGHT * 1.5
    
    # 4. No children
    para4 = "4. There are no children of the marriage under the age of 21."
    y = draw_wrapped_text(c, para4, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check if we need page break before continuing
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 6:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
        c.setFont("Times-Roman", 12)
    
    # 5. Grounds for divorce
    para5 = "5. The grounds for divorce are: DRL §170 subd. (7) - The relationship between Plaintiff and Defendant has broken down irretrievably for a period of at least six months."
    y = draw_wrapped_text(c, para5, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check page break
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 4:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
        c.setFont("Times-Roman", 12)
    
    # 6. Ancillary relief - NONE for our product
    para6a = "6a. I am not seeking equitable distribution other than what was already agreed to in a written stipulation. I understand that I may be prevented from further asserting my right to equitable distribution."
    y = draw_wrapped_text(c, para6a, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    para6b = "6b. I am not seeking maintenance as payee."
    y = draw_wrapped_text(c, para6b, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    para6c = "6c. Since the grounds alleged are DRL §170(7), all economic issues of equitable distribution of marital property, the payment or waiver of spousal support have been resolved by the parties and there are no children of the marriage."
    y = draw_wrapped_text(c, para6c, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check page break
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 4:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
        c.setFont("Times-Roman", 12)
    
    # 7. Barriers to remarriage (if religious)
    if religious_ceremony:
        para7 = "7. I have taken or will take all steps solely within my power to remove any barriers to the Defendant's remarriage."
    else:
        para7 = "7. The Barriers to Remarriage provisions (DRL §253) do not apply as the marriage was not performed in a religious ceremony."
    y = draw_wrapped_text(c, para7, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # 8. Military status
    para8 = "8. Defendant is not in the active military service of this state, any other state of this nation, or of the United States."
    y = draw_wrapped_text(c, para8, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check page break
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 4:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
        c.setFont("Times-Roman", 12)
    
    # 9. No other actions
    para9 = "9. No other action or proceeding for divorce, annulment, or dissolution of marriage has been commenced by or against either party in this or any other court."
    y = draw_wrapped_text(c, para9, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # 10. Health care notice
    para10 = "10. I have been provided a copy of Notice Relating to Health Care of the Parties. I fully understand that upon the entrance of this divorce judgment, I may no longer be allowed to receive health coverage under my former spouse's health insurance plan."
    y = draw_wrapped_text(c, para10, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT * 1.5
    
    # Check page break before final section
    if y < MARGIN_BOTTOM + LINE_HEIGHT * 10:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
        c.setFont("Times-Roman", 12)
    
    # 11. Guideline maintenance notice
    para11 = "11. I acknowledge receipt of the Notice of Guideline Maintenance."
    y = draw_wrapped_text(c, para11, MARGIN_LEFT, y, CONTENT_WIDTH)
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
    c.drawString(sig_x, y, "Plaintiff's Signature")
    y -= LINE_HEIGHT
    c.setFont("Times-Roman", 12)
    c.drawString(sig_x, y, plaintiff_name)
    
    # Footer - Form ID in bottom margin (below content area)
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, 36, "(Form UD-6)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # Test with RELIGIOUS ceremony
    test_data = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Orange",
        "indexNumber": "12345/2027",
        "plaintiffAddress": "74 Fitzgerald Court, Monroe, NY 10950",
        "defendantAddress": "123 Main Street, Newburgh, NY 12550",
        "marriageDate": "June 15, 2015",
        "marriagePlace": "Monroe, Orange County, New York",
        "religiousCeremony": True,  # RELIGIOUS
        "residencyType": "A",
        "stateSigned": "New York",
        "countySigned": "Orange",
    }
    
    output = generate_ud6(test_data, "/home/claude/test_ud6_religious.pdf")
    print(f"Generated RELIGIOUS: {output}")
    
    # Test with CIVIL ceremony
    test_data["religiousCeremony"] = False
    output = generate_ud6(test_data, "/home/claude/test_ud6_civil.pdf")
    print(f"Generated CIVIL: {output}")
