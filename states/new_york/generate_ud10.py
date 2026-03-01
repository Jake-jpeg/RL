#!/usr/bin/env python3
"""
DivorceGPT UD-10 (Findings of Fact and Conclusions of Law) PDF Generator
=========================================================================

Court findings and conclusions for uncontested divorce.
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
DOUBLE_SPACE = 28  # Double spaced for body text

# Box layout positions
BOX1_LEFT_X = MARGIN_LEFT
BOX1_RIGHT_X = PAGE_WIDTH / 2


def draw_wrapped_text(c, text, x, y, max_width, font_name="Times-Roman", font_size=12, indent=0, line_height=None):
    """Draw text that wraps within max_width. Returns final Y position."""
    if line_height is None:
        line_height = DOUBLE_SPACE  # Default to double spacing
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
    
    first_line = True
    for line in lines:
        if first_line:
            c.drawString(x, y, line)
            first_line = False
        else:
            c.drawString(x + indent, y, line)
        y -= line_height
    
    return y


def draw_paragraph(c, label, text, x, y, label_font="Times-Bold", text_font="Times-Roman", font_size=12, line_height=None):
    """Draw a labeled paragraph with bold label and regular text."""
    if line_height is None:
        line_height = DOUBLE_SPACE  # Default to double spacing
    # Calculate label width
    c.setFont(label_font, font_size)
    label_width = c.stringWidth(label + " ", label_font, font_size)
    
    # Draw label
    c.drawString(x, y, label)
    
    # Draw text starting after label
    c.setFont(text_font, font_size)
    
    # Calculate remaining width on first line
    first_line_width = CONTENT_WIDTH - label_width
    
    words = text.split()
    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(' ', text_font, font_size)
    
    # First line has less space
    max_width = first_line_width
    first_line = True
    
    for word in words:
        word_width = c.stringWidth(word, text_font, font_size)
        test_width = current_width + word_width + (space_width if current_line else 0)
        
        if test_width <= max_width:
            current_line.append(word)
            current_width = test_width
        else:
            if current_line:
                lines.append((' '.join(current_line), first_line))
            current_line = [word]
            current_width = word_width
            if first_line:
                first_line = False
                max_width = CONTENT_WIDTH  # Full width for subsequent lines
    
    if current_line:
        lines.append((' '.join(current_line), first_line if not lines else False))
    
    # Draw lines
    for i, (line, is_first) in enumerate(lines):
        if is_first:
            c.drawString(x + label_width, y, line)
        else:
            c.drawString(x, y, line)
        y -= line_height
    
    return y


def check_page_break(c, y, needed_space):
    """Check if page break needed, return new y position."""
    if y < MARGIN_BOTTOM + needed_space:
        c.showPage()
        c.setFont("Times-Roman", 12)
        return PAGE_HEIGHT - MARGIN_TOP
    return y


def generate_ud10(data, output_path):
    """Generate UD-10 (Findings of Fact and Conclusions of Law) PDF."""
    
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Extract variables
    county_name = data.get('county', '').strip()
    county_upper = county_name.upper()
    
    plaintiff_name = data.get('plaintiffName', '').strip()
    defendant_name = data.get('defendantName', '').strip()
    index_number = data.get('indexNumber', '').strip()
    
    # Marriage info
    marriage_date = data.get('marriageDate', '').strip()
    marriage_city = data.get('marriageCity', '').strip()
    marriage_county = data.get('marriageCounty', '').strip()
    marriage_state = data.get('marriageState', '').strip()
    religious_ceremony = data.get('religiousCeremony', False)
    
    # Residency type
    residency_type = data.get('residencyType', 'A')
    
    # Filing date
    filing_date = data.get('filingDate', '').strip()
    
    # =========================================================================
    # PAGE 1
    # =========================================================================
    
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # Header - match UD-11 style
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "At the Matrimonial/IAS Part _____ of")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, "New York State Supreme Court at")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"the Courthouse, {county_name} County,")
    y -= LINE_HEIGHT
    
    # Date line with underscores - thin line
    on_text = "on "
    c.drawString(MARGIN_LEFT, y, on_text)
    on_width = c.stringWidth(on_text, "Times-Roman", 12)
    line_end_x = MARGIN_LEFT + 180  # Shorter line
    c.setLineWidth(0.3)  # Thinner line
    c.line(MARGIN_LEFT + on_width, y - 2, line_end_x, y - 2)
    c.drawString(line_end_x + 2, y, ".")
    y -= LINE_HEIGHT * 1.5
    
    # Present line
    c.drawString(MARGIN_LEFT, y, "Present:")
    y -= LINE_HEIGHT
    
    # Hon. line with underline - same length as "on" line above
    c.drawString(MARGIN_LEFT, y, "Hon. ")
    hon_width = c.stringWidth("Hon. ", "Times-Roman", 12)
    c.setLineWidth(0.3)  # Thinner line
    c.line(MARGIN_LEFT + hon_width, y - 2, line_end_x, y - 2)  # Same end point
    y -= LINE_HEIGHT
    # Justice/Referee indented under the line
    c.drawString(MARGIN_LEFT + 40, y, "Justice/Referee")
    y -= LINE_HEIGHT * 2
    
    # Court header - Bold
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= LINE_HEIGHT
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= LINE_HEIGHT * 1.5
    
    # Caption - two column layout
    # Left side: parties in box (no left border)
    # Right side: Index No., Calendar No., Document Title
    
    box_top = y
    box_left = MARGIN_LEFT
    box_right = MARGIN_LEFT + 230  # Left box width
    box_height = LINE_HEIGHT * 8  # Taller box for better spacing
    box_bottom = box_top - box_height
    
    # Draw box borders (no left side - only top, right, bottom)
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    c.line(box_left, box_top, box_right, box_top)        # top
    c.line(box_right, box_top, box_right, box_bottom)    # right
    c.line(box_left, box_bottom, box_right, box_bottom)  # bottom
    
    # Inside box - party names with proper spacing
    c.setFont("Times-Roman", 12)
    inner_y = box_top - LINE_HEIGHT * 1.5
    c.drawString(box_left + 10, inner_y, f"{plaintiff_name},")
    inner_y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(box_left + 30, inner_y, "Plaintiff,")
    
    inner_y -= LINE_HEIGHT * 1.5  # Space after Plaintiff
    
    c.setFont("Times-Roman", 12)
    c.drawString(box_left + 50, inner_y, "-against-")
    
    inner_y -= LINE_HEIGHT * 1.5  # Space after -against-
    
    c.drawString(box_left + 10, inner_y, f"{defendant_name},")
    inner_y -= LINE_HEIGHT
    c.setFont("Times-Italic", 12)
    c.drawString(box_left + 30, inner_y, "Defendant.")
    
    # Right side - Index No., Calendar No., and Document Title
    right_x = box_right + 20
    right_y = box_top - LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    if index_number:
        c.drawString(right_x, right_y, f"Index No.: {index_number}")
    else:
        c.drawString(right_x, right_y, "Index No.: _______________")
    right_y -= LINE_HEIGHT * 1.2
    
    c.drawString(right_x, right_y, "Calendar No.: ___________")
    right_y -= LINE_HEIGHT * 1.5
    
    # Document title on right side - centered in remaining space
    c.setFont("Times-Bold", 12)
    c.drawString(right_x, right_y, "FINDINGS OF FACT")
    right_y -= LINE_HEIGHT
    c.drawString(right_x + 40, right_y, "AND")
    right_y -= LINE_HEIGHT
    c.drawString(right_x, right_y, "CONCLUSIONS OF LAW")
    
    y -= LINE_HEIGHT
    
    c.setFont("Times-Italic", 12)
    c.drawString(MARGIN_LEFT + 100, y, "Plaintiff,")
    y -= LINE_HEIGHT * 1.5
    
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 80, y, "- against -")
    y -= LINE_HEIGHT * 1.5
    
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
    
    # Intro paragraph - flows naturally as two paragraphs
    c.setFont("Times-Roman", 12)
    
    intro_para1 = f"The issues of this action having been submitted to OR been heard before me as one of the Justices/Referees of this Court at Part _____ hereof, held in and for the County of {county_name} on ________________, and having considered the allegations and proofs of the respective parties, and due deliberation having been had thereon."
    y = draw_wrapped_text(c, intro_para1, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    intro_para2 = "NOW, after reading and considering the papers submitted hearing the testimony, I do hereby make the following findings of essential facts which I deem established by the evidence and reach the following conclusions of law."
    y = draw_wrapped_text(c, intro_para2, MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= LINE_HEIGHT
    
    # FINDINGS OF FACT - underlined and bold, CENTERED
    c.setFont("Times-Bold", 12)
    findings_title = "FINDINGS OF FACT"
    title_width = c.stringWidth(findings_title, "Times-Bold", 12)
    center_x = PAGE_WIDTH / 2
    c.drawString(center_x - title_width / 2, y, findings_title)
    c.line(center_x - title_width / 2, y - 2, center_x + title_width / 2, y - 2)
    y -= LINE_HEIGHT * 1.5
    
    # FIRST - Age
    y = draw_paragraph(c, "FIRST:", "Plaintiff and Defendant were both eighteen (18) years of age or over when this action was commenced.", MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 4)
    
    # SECOND - Residency
    residency_texts = {
        'A': "The Plaintiff has resided in New York State for a continuous period of at least one (1) year immediately preceding the commencement of this divorce action and the parties were married in New York State.",
        'B': "The Plaintiff has resided in New York State for a continuous period of at least one (1) year immediately preceding the commencement of this divorce action and the parties have resided as married persons in New York State.",
        'C': "The Plaintiff has resided in New York State for a continuous period of at least one (1) year immediately preceding the commencement of this divorce action and the cause of action occurred in New York State.",
        'D': "The cause of action occurred in New York State and both parties were residents of New York State at the time of commencement of this action.",
        'E': "The parties were married in New York State and both parties were residents of New York State at the time of commencement of this action.",
        'F': "The Plaintiff has resided in New York State for a continuous period of at least two (2) years immediately preceding the commencement of this divorce action."
    }
    residency_text = residency_texts.get(residency_type, residency_texts['F'])
    y = draw_paragraph(c, "SECOND:", residency_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 4)
    
    # THIRD - Marriage
    marriage_date_display = marriage_date if marriage_date else "________________"
    marriage_city_display = marriage_city if marriage_city else "________________"
    marriage_county_display = marriage_county if marriage_county else "________________"
    marriage_state_display = marriage_state if marriage_state else "________________"
    ceremony_check = "[ ] civil / [X] religious" if religious_ceremony else "[X] civil / [ ] religious"
    
    third_text = f"Plaintiff and Defendant were married on {marriage_date_display} in {marriage_city_display}, County of {marriage_county_display}, State of {marriage_state_display}, in a {ceremony_check} ceremony."
    y = draw_paragraph(c, "THIRD:", third_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 5)
    
    # FOURTH - No prior decree
    fourth_text = "No decree, judgment, or order of divorce, annulment, or dissolution of marriage has been granted to either party against the other in any Court of competent jurisdiction of this state or any other state, territory, or country, and there is no other action pending for divorce by either party against the other in any Court."
    y = draw_paragraph(c, "FOURTH:", fourth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 5)
    
    # FIFTH - Service
    filing_date_display = filing_date if filing_date else "________________"
    fifth_text = f"This action was commenced by filing the Summons With Notice with the County Clerk on {filing_date_display}. Defendant was served personally with the above stated pleadings and the Notice of Automatic Orders. Defendant appeared and waived his/her right to answer, and neither admitted nor denied the allegations in plaintiff's complaint, and consented to entry of judgment."
    y = draw_paragraph(c, "FIFTH:", fifth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 4)
    
    # SIXTH - Jurisdiction
    sixth_text = "The Supreme Court of the State of New York has jurisdiction over the subject matter of this action and the parties hereto, and venue is proper in this Court."
    y = draw_paragraph(c, "SIXTH:", sixth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 3)
    
    # SEVENTH - Automatic Orders
    seventh_text = "The Notice of Automatic Orders was duly served upon Defendant and no violations thereof are alleged."
    y = draw_paragraph(c, "SEVENTH:", seventh_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 4)
    
    # EIGHTH - Military
    eighth_text = "Neither Plaintiff nor Defendant is in the military service of the United States of America, the State of New York, or any other state, and no protections under the Servicemembers Civil Relief Act apply."
    y = draw_paragraph(c, "EIGHTH:", eighth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 3)
    
    # NINTH - No children
    ninth_text = "There are no children of the marriage."
    y = draw_paragraph(c, "NINTH:", ninth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 4)
    
    # TENTH - Grounds
    tenth_text = "The grounds for divorce that are alleged in the Verified Complaint were proved as follows: The relationship between Plaintiff and Defendant has broken down irretrievably for a period of at least six (6) months as stated in the Plaintiff's Affidavit. (DRL §170 subd. 7)"
    y = draw_paragraph(c, "TENTH:", tenth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 3)
    
    # ELEVENTH - Barriers to remarriage
    if religious_ceremony:
        eleventh_text = "A sworn statement pursuant to DRL §253 that Plaintiff has taken all steps within his or her power to remove all barriers to Defendant's remarriage following the divorce was served upon Defendant."
    else:
        eleventh_text = "A sworn statement as to the removal of barriers to remarriage is not required because the parties were married in a civil ceremony."
    y = draw_paragraph(c, "ELEVENTH:", eleventh_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 3)
    
    # TWELFTH - No maintenance
    twelfth_text = "No maintenance was awarded because neither party seeks maintenance."
    y = draw_paragraph(c, "TWELFTH:", twelfth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 3)
    
    # THIRTEENTH - Equitable distribution
    thirteenth_text = "Equitable Distribution is not an issue."
    y = draw_paragraph(c, "THIRTEENTH:", thirteenth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 4)
    
    # FOURTEENTH - All issues resolved
    fourteenth_text = "All issues of equitable distribution of marital property, maintenance, and child support have been resolved or are not in issue, and no other ancillary relief is sought by either party."
    y = draw_paragraph(c, "FOURTEENTH:", fourteenth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 3)
    
    # FIFTEENTH - DRL 255 compliance
    fifteenth_text = "Compliance with DRL §255(1) and (2) has been satisfied. Each party has been provided notice as required by DRL §255(1)."
    y = draw_paragraph(c, "FIFTEENTH:", fifteenth_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 1.5
    
    # Force new page for CONCLUSIONS OF LAW
    c.showPage()
    c.setFont("Times-Roman", 12)
    y = PAGE_HEIGHT - MARGIN_TOP
    
    # CONCLUSIONS OF LAW - underlined and bold, CENTERED
    c.setFont("Times-Bold", 12)
    conclusions_title = "CONCLUSIONS OF LAW"
    title_width = c.stringWidth(conclusions_title, "Times-Bold", 12)
    center_x = PAGE_WIDTH / 2
    c.drawString(center_x - title_width / 2, y, conclusions_title)
    c.line(center_x - title_width / 2, y - 2, center_x + title_width / 2, y - 2)
    y -= LINE_HEIGHT * 1.5
    
    # Conclusions
    y = draw_paragraph(c, "FIRST:", "Residency as required by DRL §230 has been satisfied.", MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = draw_paragraph(c, "SECOND:", "The requirements of DRL §255 have been satisfied.", MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = draw_paragraph(c, "THIRD:", "The requirements of DRL §236(B)(2)(b) have been satisfied.", MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = draw_paragraph(c, "FOURTH:", "The requirements of DRL §236(B)(6) have been satisfied.", MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 5)
    
    fifth_conc_text = "All economic issues of equitable distribution of marital property, the payment or waiver of spousal support, the payment of child support, the payment of counsel and experts' fees and expenses as well as the custody and visitation with the minor children of the marriage have been resolved by the parties or determined by the court and incorporated into the judgment of divorce."
    y = draw_paragraph(c, "FIFTH:", fifth_conc_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 0.5
    
    y = check_page_break(c, y, LINE_HEIGHT * 3)
    
    sixth_conc_text = "Plaintiff is entitled to a judgment of divorce on the ground of DRL §170 subd. (7) and granting the incidental relief awarded."
    y = draw_paragraph(c, "SIXTH:", sixth_conc_text, MARGIN_LEFT, y)
    y -= LINE_HEIGHT * 2
    
    y = check_page_break(c, y, LINE_HEIGHT * 6)
    
    # Signature section - cleaner layout
    c.setFont("Times-Roman", 12)
    y -= LINE_HEIGHT
    
    # Date line
    c.drawString(MARGIN_LEFT, y, "Dated: _______________________")
    y -= LINE_HEIGHT * 2.5
    
    # Signature line - right-aligned, proper spacing
    sig_line_start = PAGE_WIDTH / 2 + 20
    sig_line_end = PAGE_WIDTH - MARGIN_RIGHT
    c.setLineWidth(0.5)
    c.line(sig_line_start, y, sig_line_end, y)
    y -= LINE_HEIGHT * 1.2
    
    # Title centered under signature line
    title_text = "Justice of the Supreme Court / Referee"
    title_width = c.stringWidth(title_text, "Times-Roman", 12)
    title_center = sig_line_start + (sig_line_end - sig_line_start) / 2
    c.drawString(title_center - title_width / 2, y, title_text)
    
    # Form identifier and revision date at bottom
    c.setFont("Times-Roman", 10)
    c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 10, "(Form UD-10)")
    
    c.save()
    return output_path


if __name__ == "__main__":
    # Test with civil ceremony
    test_data = {
        "plaintiffName": "JANE DOE",
        "defendantName": "JOHN DOE",
        "county": "Orange",
        "indexNumber": "12345/2027",
        "marriageDate": "June 15, 2015",
        "marriageCity": "Monroe",
        "marriageCounty": "Orange",
        "marriageState": "New York",
        "religiousCeremony": False,
        "residencyType": "F",
        "filingDate": "January 10, 2027",
    }
    
    output = generate_ud10(test_data, "/home/claude/test_ud10_civil.pdf")
    print(f"Generated CIVIL: {output}")
    
    # Test with religious ceremony
    test_data["religiousCeremony"] = True
    output = generate_ud10(test_data, "/home/claude/test_ud10_religious.pdf")
    print(f"Generated RELIGIOUS: {output}")
