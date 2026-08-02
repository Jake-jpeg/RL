#!/usr/bin/env python3
"""
DivorceGPT — NY Verified Complaint (Action for Divorce) PDF Generator
=====================================================================

Companion to generate_ud1.py (Summons). Same ReportLab pipeline and style.
Layout modeled on real filed uncontested Summons+Complaint pleadings:
  - two-column caption: dash rule ending in "X", right column carries
    Index No. / document title / ACTION FOR A DIVORCE
  - hanging-indent numbered allegations (FIRST: ... NINTH:) at pleading
    line spacing
  - WHEREFORE demand list lettered A., B., C. ...
  - attorney signature block on the right half
  - VERIFICATION page with the traditional STATE/COUNTY ss.: block
  - Part 130 certification

SCOPE: Phase 1, uncontested, NO unemancipated children. If children are
present the DivorceGPT intake stops and routes to an attorney BEFORE this
generator is ever called. The generator still renders a flagged paragraph
if a count is passed, but the product gate is upstream.

Register in app.py STATE_CONFIGS under ny -> forms:
    'complaint': 'generate_complaint'

Required data keys (deterministic mapping from attorney-confirmed answers;
NO AI output in the payload — same contract as generate_ud1):
    plaintiffName, defendantName          full legal names
    county                                NY county of venue
    plaintiffAddress, defendantAddress    full address w/ ZIP
    residentParty                         'plaintiff' | 'defendant' | 'both'
    marriageDate                          ISO 'YYYY-MM-DD' or free text
    marriagePlace                         e.g. 'Middletown, New York' or 'South Korea'
    ceremonyType                          'civil' | 'religious'
Optional:
    unemancipatedChildren                 int, default 0
    attorneyName / attorneyFirm / attorneyAddress / attorneyPhone
    dateSigned                            free text; default blank line
    reliefBundle                          list[str]; default STANDARD_RELIEF
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import re

PAGE_WIDTH, PAGE_HEIGHT = letter          # 612 x 792
MARGIN_LEFT = 72
MARGIN_RIGHT = 72
MARGIN_TOP = 72
MARGIN_BOTTOM = 72
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT   # 468

# 22 NYCRR 202.5(a)(1): papers must be "at least double space between each
# line, except for quotations and the names and addresses of attorneys."
# Body text is 12pt Times, so double spacing is 24pt of leading. The old
# value of 20 was 1.67x — pleading-ish, and non-conforming.
BODY_LEADING = 24            # DOUBLE-SPACED allegations (12pt x 2)
# The rule's own exceptions: captions carry the names and addresses of
# attorneys, and the signature/notice blocks are not body lines. These stay
# single-spaced, which is what the exception is for and what every filed
# pleading looks like.
TIGHT_LEADING = 14           # captions, signature blocks, notices
PARA_GAP = 8                 # extra gap between allegations

# Caption geometry: the dash rule runs from the left margin to the divider
# and ends in "X"; the right column starts just past it.
CAPTION_DIV_X = MARGIN_LEFT + 296        # ≈ mid-page, like the filed samples
RIGHT_COL_X = CAPTION_DIV_X + 16

# Current maintenance income cap — effective March 1, 2026 (verified 2026).
# Not printed on the complaint (it belongs to the Notice of Guideline
# Maintenance attached to the summons) — kept here for the phase-1 package.
MAINTENANCE_INCOME_CAP = "$241,000"

# Firm defaults (attorney-editable in review; never client-entered).
DEFAULT_ATTORNEY_NAME = "Jake S. Kim, Esq."
DEFAULT_ATTORNEY_FIRM = "Jake Kim Law Firm, LLC"
DEFAULT_ATTORNEY_ADDRESS = "2460 Lemoine Avenue, Suite 400H\nFort Lee, New Jersey 07024"
DEFAULT_ATTORNEY_PHONE = "(201) 800-4564"

# Jake-confirmed standard WHEREFORE bundle (attorney-editable).
STANDARD_RELIEF = [
    "Granting a judgment of absolute divorce in favor of the Plaintiff and against the "
    "Defendant, dissolving the marriage between the parties;",
    "Granting the Plaintiff equitable distribution of all marital property pursuant to "
    "Domestic Relations Law § 236(B), and/or a distributive award;",
    "Declaring the separate property of each party;",
    "Awarding maintenance in accordance with the parties' agreement, or as the Court "
    "deems just and proper;",
    "Awarding the Plaintiff exclusive use and occupancy of the marital residence;",
    "Awarding the Plaintiff counsel fees, expert fees, and the costs and disbursements of "
    "this action pursuant to Domestic Relations Law § 237; and",
    "Granting the Plaintiff such other and further relief as this Court deems just and proper.",
]

CHILD_RELIEF = [
    "Awarding custody and a parenting schedule for the unemancipated children of "
    "the marriage in accordance with the parties' agreement and the best interests "
    "of the children;",
    "Awarding child support in accordance with the Child Support Standards Act, "
    "Domestic Relations Law § 240(1-b), including the parties' pro rata shares of "
    "health-care and child-care expenses;",
]


def relief_bundle(children=0):
    """The WHEREFORE clause. A complaint that recites children of the marriage
    must also demand child relief -- the attorney edits it, but it is never
    silently absent."""
    relief = list(STANDARD_RELIEF)
    if children and int(children) > 0:
        # After "Declaring the separate property of each party" (index 2).
        relief[3:3] = CHILD_RELIEF
    return relief


ORDINALS = ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH",
            "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"]


# ────────────────────────── helpers ──────────────────────────

def title_case(s):
    return " ".join(w.capitalize() for w in s.split())


def strip_county_suffix(county):
    return re.sub(r"\s+County$", "", (county or "").strip(), flags=re.IGNORECASE).strip()


def fmt_marriage_date(value):
    """Accept ISO or free text; render 'Month D, YYYY' when ISO."""
    value = (value or "").strip()
    if not value:
        return "____________________"
    try:
        d = datetime.strptime(value, "%Y-%m-%d")
        return f"{d.strftime('%B')} {d.day}, {d.year}"
    except ValueError:
        return value


def wrap_lines(c, text, max_width, font="Times-Roman", size=12):
    """Pure word-wrap → list of lines (no drawing)."""
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word) if line else word
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_dash_rule(c, y):
    c.setFont("Times-Roman", 12)
    dash_w = c.stringWidth("-", "Times-Roman", 12)
    n = max(10, int((CAPTION_DIV_X - MARGIN_LEFT) / dash_w))
    c.drawString(MARGIN_LEFT, y, "-" * n + "X")


def draw_caption(c, y, county_upper, plaintiff_upper, defendant_upper, doc_title):
    """Two-column NY pleading caption. Returns the y below the bottom rule."""
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, y, "SUPREME COURT OF THE STATE OF NEW YORK")
    y -= TIGHT_LEADING
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    y -= TIGHT_LEADING
    draw_dash_rule(c, y)
    y -= TIGHT_LEADING + 4

    row_y = []   # capture each caption row's y for the right column
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT + 8, y, plaintiff_upper + ",")
    row_y.append(y)
    y -= TIGHT_LEADING + 2
    c.drawString(MARGIN_LEFT + 176, y, "Plaintiff,")
    row_y.append(y)
    y -= TIGHT_LEADING + 6
    c.drawString(MARGIN_LEFT + 56, y, "-against-")
    row_y.append(y)
    y -= TIGHT_LEADING + 6
    c.drawString(MARGIN_LEFT + 8, y, defendant_upper + ",")
    row_y.append(y)
    y -= TIGHT_LEADING + 2
    c.drawString(MARGIN_LEFT + 176, y, "Defendant.")
    row_y.append(y)
    y -= TIGHT_LEADING + 4
    draw_dash_rule(c, y)

    # Right column, aligned to caption rows: Index No. / title / action label.
    c.setFont("Times-Roman", 12)
    c.drawString(RIGHT_COL_X, row_y[0], "Index No.: ______________")
    c.setFont("Times-Bold", 12)
    tw = c.stringWidth(doc_title, "Times-Bold", 12)
    c.drawString(RIGHT_COL_X, row_y[1] - 4, doc_title)
    c.line(RIGHT_COL_X, row_y[1] - 6, RIGHT_COL_X + tw, row_y[1] - 6)
    c.setFont("Times-Roman", 12)
    c.drawString(RIGHT_COL_X, row_y[3], "ACTION FOR A DIVORCE")

    return y - TIGHT_LEADING * 1.6


def draw_allegation(c, y, label, text):
    """Hanging-indent allegation: bold 'FIRST:' inline, first line indented,
    continuation lines flush left. Returns (canvas_maybe_new_page, y)."""
    indent = MARGIN_LEFT + 50
    label_disp = label + ":"
    c.setFont("Times-Bold", 12)
    label_w = c.stringWidth(label_disp + "  ", "Times-Bold", 12)

    first_width = CONTENT_WIDTH - 50 - label_w
    all_lines = []
    words = text.split()
    # First line fills the space after the label; remaining lines are full width.
    line, taken = "", []
    for i, word in enumerate(words):
        test = (line + " " + word) if line else word
        if c.stringWidth(test, "Times-Roman", 12) <= first_width:
            line = test
            taken.append(word)
        else:
            break
    rest = " ".join(words[len(taken):])
    all_lines.append(line)
    if rest:
        all_lines.extend(wrap_lines(c, rest, CONTENT_WIDTH))

    needed = len(all_lines) * BODY_LEADING + PARA_GAP
    if y - needed < MARGIN_BOTTOM + BODY_LEADING:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP

    c.setFont("Times-Bold", 12)
    c.drawString(indent, y, label_disp)
    c.setFont("Times-Roman", 12)
    c.drawString(indent + label_w, y, all_lines[0])
    y -= BODY_LEADING
    for ln in all_lines[1:]:
        c.drawString(MARGIN_LEFT, y, ln)
        y -= BODY_LEADING
    return y - PARA_GAP


def draw_paragraph(c, y, text, leading=BODY_LEADING, x=MARGIN_LEFT,
                   width=CONTENT_WIDTH, font="Times-Roman", size=12):
    lines = wrap_lines(c, text, width, font, size)
    if y - len(lines) * leading < MARGIN_BOTTOM:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
    c.setFont(font, size)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


# ────────────────────────── substance ──────────────────────────

def residency_clause(resident_party, basis="two_year"):
    """The FIRST allegation — pleads the DRL § 230 prong actually satisfied.

    basis: 'two_year'         → § 230(5)  (default)
           'one_year_married' → § 230(1)  married in NY + 1yr residence
           'one_year_spouses' → § 230(2)  lived in NY as spouses + 1yr
           'one_year_cause'   → § 230(3)  cause occurred in NY + 1yr
                                 (arrives attorney-flagged from the intake)
    """
    party = "The Plaintiff" if resident_party == "plaintiff" else (
        "The Defendant" if resident_party == "defendant" else "Both parties")
    verb = "has" if resident_party in ("plaintiff", "defendant") else "have"
    one_year_tail = (
        f"{party.lower().replace('the p', 'the P').replace('the d', 'the D')} "
        f"{verb} resided in the State of New York for a continuous period of at "
        f"least one year immediately preceding the commencement of this action."
    )
    if basis == "one_year_married":
        return ("The parties were married in the State of New York, and "
                + one_year_tail)
    if basis == "one_year_spouses":
        return ("The parties have resided in the State of New York as spouses, and "
                + one_year_tail)
    if basis == "one_year_cause":
        return ("The cause of action occurred in the State of New York, and "
                + one_year_tail)
    return (
        f"{party} {verb} resided in the State of New York for a continuous period of at "
        f"least two years immediately preceding the commencement of this action."
    )


def marriage_clause(marriage_date, marriage_place, ceremony_type):
    date_str = fmt_marriage_date(marriage_date)
    place = (marriage_place or "____________________").strip()
    if ceremony_type == "religious":
        return (
            f"The parties were married to each other on {date_str}, in {place}. The "
            f"marriage was performed by a clergyman, minister, or a leader of the Society "
            f"for Ethical Culture."
        )
    return (
        f"The parties were married to each other on {date_str}, in a civil ceremony in "
        f"{place}. The marriage was not performed by a clergyman, minister, or a leader "
        f"of the Society for Ethical Culture."
    )


def drl253_clause(ceremony_type):
    if ceremony_type == "religious":
        return (
            "The marriage having been solemnized by a religious ceremony, the Plaintiff "
            "has taken, or will take prior to the entry of final judgment, all steps "
            "solely within the Plaintiff's power to remove any barrier to the Defendant's "
            "remarriage, pursuant to Domestic Relations Law § 253."
        )
    return (
        "The parties married in a civil ceremony and, therefore, the provisions of "
        "Domestic Relations Law § 253 are not applicable."
    )


def children_clause(count, detail=""):
    """DRL para FIFTH. The pleading recites each child's name and date of
    birth -- that is exactly what the intake collects and the only child
    information that belongs on the complaint."""
    if not count or int(count) == 0:
        return "There are no unemancipated children of this marriage."
    n = int(count)
    word = "is one unemancipated child" if n == 1 else f"are {n} unemancipated children"
    detail = (detail or "").strip()
    if detail:
        return (
            f"There {word} of this marriage, namely: {detail}. [ATTORNEY REVIEW "
            f"REQUIRED -- child-related relief must be completed by counsel.]"
        )
    return (
        f"There {word} of this marriage. [ATTORNEY REVIEW REQUIRED -- name and "
        f"date of birth of each child must be supplied, and child-related relief "
        f"completed, by counsel.]"
    )


# ────────────────────────── generator ──────────────────────────

def generate_complaint(data, output_path):
    county = strip_county_suffix(data.get("county") or data.get("filingCounty"))
    if not county:
        raise ValueError("County is required")
    plaintiff = (data.get("plaintiffName") or "").strip()
    defendant = (data.get("defendantName") or "").strip()
    if not plaintiff or not defendant:
        raise ValueError("Plaintiff and Defendant names are required")

    plaintiff_addr = (data.get("plaintiffAddress") or "").strip()
    defendant_addr = (data.get("defendantAddress") or "").strip()
    if not plaintiff_addr or not defendant_addr:
        raise ValueError("Both party addresses are required")

    resident_party = (data.get("residentParty") or "plaintiff").strip().lower()
    ceremony_type = (data.get("ceremonyType") or "civil").strip().lower()
    children = data.get("unemancipatedChildren", 0)

    attorney_name = data.get("attorneyName", DEFAULT_ATTORNEY_NAME)
    attorney_firm = data.get("attorneyFirm", DEFAULT_ATTORNEY_FIRM)
    attorney_addr = data.get("attorneyAddress", DEFAULT_ATTORNEY_ADDRESS)
    attorney_phone = data.get("attorneyPhone", DEFAULT_ATTORNEY_PHONE)
    date_signed = (data.get("dateSigned") or "").strip() or "____________________"
    relief = data.get("reliefBundle") or relief_bundle(children)

    county_upper = county.upper()
    c = canvas.Canvas(output_path, pagesize=letter)

    # ── PAGE 1: caption + allegations ──
    y = PAGE_HEIGHT - MARGIN_TOP
    y = draw_caption(c, y, county_upper, plaintiff.upper(), defendant.upper(),
                     "VERIFIED COMPLAINT")

    y = draw_paragraph(
        c, y,
        f"Plaintiff, by {attorney_name}, complaining of the Defendant, as and for a "
        f"Verified Complaint, alleges:",
    )
    y -= PARA_GAP

    residency_basis = (data.get("residencyBasis") or "two_year").strip().lower()
    allegations = [
        residency_clause(resident_party, residency_basis),
        "Both parties are over the age of eighteen (18) years as of the date set forth herein.",
        marriage_clause(data.get("marriageDate"), data.get("marriagePlace"), ceremony_type),
        drl253_clause(ceremony_type),
        children_clause(children, data.get("childrenDetail", "")),
        f"The Plaintiff resides at {plaintiff_addr}. The Defendant resides at "
        f"{defendant_addr}.",
        "This marriage has never been altered or dissolved by any judgment of divorce, "
        "annulment, or dissolution of marriage issued by any court of competent "
        "jurisdiction.",
        "No other action or proceeding between the parties for divorce, annulment, "
        "separation, or dissolution of the marriage is pending in this or any other "
        "court of competent jurisdiction.",
        "The grounds for divorce, pursuant to Subdivision (7) of Section 170 of the "
        "Domestic Relations Law, are as follows: the relationship between the parties "
        "has broken down irretrievably for a period of at least six months.",
    ]
    for i, text in enumerate(allegations):
        y = draw_allegation(c, y, ORDINALS[i], text)

    # ── WHEREFORE ──
    if y < MARGIN_BOTTOM + BODY_LEADING * 5:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
    y -= PARA_GAP
    y = draw_paragraph(
        c, y,
        "WHEREFORE, the Plaintiff demands judgment against the Defendant as follows:")
    y -= PARA_GAP * 0.5
    for i, item in enumerate(relief):
        label = chr(ord("A") + i) + "."
        lines = wrap_lines(c, item, CONTENT_WIDTH - 60)
        if y - (len(lines) * TIGHT_LEADING + 6) < MARGIN_BOTTOM:
            c.showPage()
            y = PAGE_HEIGHT - MARGIN_TOP
        c.setFont("Times-Roman", 12)
        c.drawString(MARGIN_LEFT + 24, y, label)
        for ln in lines:
            c.drawString(MARGIN_LEFT + 60, y, ln)
            y -= TIGHT_LEADING
        y -= 6

    # ── Dated + attorney signature block (right half) ──
    if y < MARGIN_BOTTOM + TIGHT_LEADING * 9:
        c.showPage()
        y = PAGE_HEIGHT - MARGIN_TOP
    y -= TIGHT_LEADING * 2
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, f"Dated: {date_signed}")
    sig_x = CAPTION_DIV_X - 20
    y -= TIGHT_LEADING * 2.5
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= TIGHT_LEADING
    for line in ([attorney_name, "Attorney for Plaintiff", attorney_firm]
                 + attorney_addr.split("\n") + [attorney_phone]):
        c.drawString(sig_x, y, line)
        y -= TIGHT_LEADING

    # ── VERIFICATION page ──
    c.showPage()
    y = PAGE_HEIGHT - MARGIN_TOP
    c.setFont("Times-Bold", 12)
    vt = "VERIFICATION"
    vw = c.stringWidth(vt, "Times-Bold", 12)
    c.drawString((PAGE_WIDTH - vw) / 2, y, vt)
    c.line((PAGE_WIDTH - vw) / 2, y - 2, (PAGE_WIDTH + vw) / 2, y - 2)
    y -= TIGHT_LEADING * 2.5

    paren_x = MARGIN_LEFT + 190
    c.setFont("Times-Roman", 12)
    c.drawString(MARGIN_LEFT, y, "STATE OF NEW YORK")
    c.drawString(paren_x, y, ")")
    y -= TIGHT_LEADING
    c.drawString(paren_x, y, ") ss.:")
    y -= TIGHT_LEADING
    c.drawString(MARGIN_LEFT, y, f"COUNTY OF {county_upper}")
    c.drawString(paren_x, y, ")")
    y -= TIGHT_LEADING * 2

    y = draw_paragraph(
        c, y,
        f"{title_case(plaintiff)}, being duly sworn, deposes and says: I am the "
        f"Plaintiff in the within action for a divorce. I have read the foregoing "
        f"Verified Complaint and know the contents thereof. The contents are true to my "
        f"own knowledge, except as to matters therein stated to be alleged upon "
        f"information and belief, and as to those matters I believe them to be true.")

    y -= BODY_LEADING * 2
    sig_x = CAPTION_DIV_X - 20
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    c.setFont("Times-Roman", 12)
    c.drawString(sig_x, y - TIGHT_LEADING, title_case(plaintiff))
    y -= TIGHT_LEADING * 4

    c.drawString(MARGIN_LEFT, y, "Sworn to before me on")
    y -= TIGHT_LEADING
    c.drawString(MARGIN_LEFT, y, "____________________, 20___")
    y -= TIGHT_LEADING * 3
    c.line(MARGIN_LEFT, y, MARGIN_LEFT + 200, y)
    c.drawString(MARGIN_LEFT, y - TIGHT_LEADING, "Notary Public")

    # ── Part 130 certification (bottom of verification page) ──
    y -= TIGHT_LEADING * 4
    c.line(MARGIN_LEFT, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    y -= TIGHT_LEADING * 1.5
    y = draw_paragraph(
        c, y,
        "Pursuant to 22 NYCRR § 130-1.1-a, the undersigned, an attorney admitted to "
        "practice in the courts of New York State, certifies that, upon information and "
        "belief and reasonable inquiry, the contentions contained in the annexed "
        "document are not frivolous.",
        leading=TIGHT_LEADING + 2)
    y -= TIGHT_LEADING * 2
    c.line(sig_x, y, PAGE_WIDTH - MARGIN_RIGHT, y)
    c.drawString(sig_x, y - TIGHT_LEADING, attorney_name)

    c.save()
    return output_path


if __name__ == "__main__":
    # Smoke test: the clean no-kids civil case (the Phase-1 ideal).
    sample = {
        "plaintiffName": "JAMIE PLAINTIFF",
        "defendantName": "ALEX DEFENDANT",
        "county": "Orange",
        "plaintiffAddress": "15 Bristol Drive, Middletown, NY 10941",
        "defendantAddress": "24 Manhattan Avenue, Middletown, NY 10940",
        "residentParty": "plaintiff",
        "marriageDate": "2012-06-11",
        "marriagePlace": "Middletown, New York",
        "ceremonyType": "civil",
        "unemancipatedChildren": 0,
    }
    out = generate_complaint(sample, "/tmp/test_complaint.pdf")
    print("Generated:", out)

    sample2 = dict(sample, ceremonyType="religious", marriagePlace="South Korea",
                   residentParty="both")
    generate_complaint(sample2, "/tmp/test_complaint_religious.pdf")
    print("Generated religious variant")

    # § 230(1) variant: married in NY + one year of residence.
    sample3 = dict(sample, residencyBasis="one_year_married")
    generate_complaint(sample3, "/tmp/test_complaint_1yr.pdf")
    print("Generated one-year-married variant")
