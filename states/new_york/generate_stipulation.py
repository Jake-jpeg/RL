#!/usr/bin/env python3
"""
DivorceGPT — Stipulation of Settlement (uncontested, no unemancipated children)
================================================================================

Phase 2 centerpiece. Drafted as the firm's standard uncontested architecture:
recitals → living separate → equitable distribution (the parties' AGREED terms
printed verbatim — this generator never invents a division) → debts →
maintenance (knowing waiver with the DRL § 236(B)(6) guideline recital, the
presumptive amount COMPUTED deterministically from the parties' stated
incomes) → insurance → name restoration → general provisions →
incorporation-not-merger → execution with notary acknowledgments.

EVERYTHING here is [ATTORNEY REVIEW REQUIRED] before use with a real client:
the output lands in DivorceGPT as ATTORNEY_REVIEW_REQUIRED and nothing is
released without counsel's approval.

Register in app.py STATE_CONFIGS ny→forms: 'stipulation': 'generate_stipulation'

Data keys (strings; deterministic mapping from saved answers — no AI output):
  plaintiffName, defendantName          required
  county                                required
  plaintiffAddress, defendantAddress    required
  marriageDate (ISO ok), marriagePlace  required
  indexNumber                           optional
  plaintiffIncome, defendantIncome      annual gross, digits (e.g. "65000");
                                        optional — recital falls back to
                                        attorney-fill blanks if absent
  maintenanceWaived                     "true" (default) | "false"
  assetsSummary                         deterministic text list of assets
  debtsSummary                          deterministic text list of debts
  divisionTerms                         the PARTIES' agreed division, verbatim
  nameRestoration                       former name to restore, or ""
  dateSigned                            optional
"""

from reportlab.lib.pagesizes import letter

from .children import stipulation_recital
from reportlab.pdfgen import canvas

from .layout import TOP_Y, caption_title, fit_text
from datetime import datetime
import re

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN_LEFT = 72
MARGIN_RIGHT = 72
MARGIN_TOP = 72
MARGIN_BOTTOM = 72
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
LEAD = 16          # agreement text spacing (tighter than a pleading)
TIGHT = 14
CAPTION_DIV_X = MARGIN_LEFT + 296
RIGHT_COL_X = CAPTION_DIV_X + 16

# DRL § 236(B)(6) — maintenance guideline, effective March 1, 2026.
MAINTENANCE_CAP = 241_000

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def title_case(s):
    """Name casing that survives real surnames.

    str.capitalize() lowercases everything after the first letter, so the
    QA fixture's hyphenated surname printed as "Sampleton-vandermeer" in the
    signature block and the stipulation preamble — a party's name, wrong, on
    a paper they sign. Capitalize each letter that FOLLOWS a separator too
    (hyphen, apostrophe: Sampleton-Vandermeer, O'Brien), and leave a letter
    already inside a word alone (McKay stays McKay because we only lowercase
    nothing — we uppercase after separators and at word starts).
    """
    out = []
    for word in s.split():
        chars = []
        boundary = True
        for ch in word:
            if ch.isalpha():
                chars.append(ch.upper() if boundary else ch.lower())
                boundary = False
            else:
                chars.append(ch)
                boundary = ch in "-'\u2019."
        out.append("".join(chars))
    return " ".join(out)


def fmt_date(value):
    value = (value or "").strip()
    if not value:
        return "____________________"
    try:
        d = datetime.strptime(value, "%Y-%m-%d")
        return f"{d.strftime('%B')} {d.day}, {d.year}"
    except ValueError:
        return value


def money(n):
    return f"${n:,.0f}"


def parse_income(v):
    digits = re.sub(r"[^0-9.]", "", str(v or ""))
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def guideline_maintenance(payor_income, payee_income):
    """DRL § 236(B)(6) no-child (higher) formula, payor income capped.
    Deterministic statutory arithmetic — not advice, not AI."""
    capped = min(payor_income, MAINTENANCE_CAP)
    a = 0.30 * capped - 0.20 * payee_income
    b = 0.40 * (capped + payee_income) - payee_income
    return max(0.0, min(a, b))


class Doc:
    """Tiny flow-layout helper: wrapped paragraphs with auto page breaks."""

    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=letter)
        self.y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)
        self.page = 1

    def need(self, height):
        if self.y - height < MARGIN_BOTTOM + LEAD:
            self.c.showPage()
            self.page += 1
            self.y = TOP_Y  # first baseline: cap tops ON the margin line (layout.py)

    def wrap(self, text, width, font="Times-Roman", size=12):
        words, lines, line = text.split(), [], ""
        for w in words:
            t = (line + " " + w) if line else w
            if self.c.stringWidth(t, font, size) <= width:
                line = t
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    def para(self, text, indent=0, font="Times-Roman", size=12, lead=LEAD, gap=6):
        lines = self.wrap(text, CONTENT_WIDTH - indent, font, size)
        self.need(len(lines) * lead + gap)
        self.c.setFont(font, size)
        for i, ln in enumerate(lines):
            x = MARGIN_LEFT + (indent if i == 0 else 0)
            # hanging style: first line indented, rest flush
            self.c.drawString(x if i == 0 else MARGIN_LEFT, self.y, ln)
            self.y -= lead
        self.y -= gap

    def heading(self, label, title):
        self.need(LEAD * 3)
        text = f"ARTICLE {label} — {title}"
        self.c.setFont("Times-Bold", 12)
        w = self.c.stringWidth(text, "Times-Bold", 12)
        x = (PAGE_WIDTH - w) / 2
        self.c.drawString(x, self.y, text)
        self.c.line(x, self.y - 2, x + w, self.y - 2)
        self.y -= LEAD * 1.6

    def spacer(self, n=1):
        self.need(LEAD * n)
        self.y -= LEAD * n


def draw_caption(d, county_upper, plaintiff_upper, defendant_upper, index_number):
    c = d.c
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN_LEFT, d.y, "SUPREME COURT OF THE STATE OF NEW YORK")
    d.y -= TIGHT
    c.drawString(MARGIN_LEFT, d.y, f"COUNTY OF {county_upper}")
    d.y -= TIGHT
    c.setFont("Times-Roman", 12)
    dash_w = c.stringWidth("-", "Times-Roman", 12)
    n = max(10, int((CAPTION_DIV_X - MARGIN_LEFT) / dash_w))
    c.drawString(MARGIN_LEFT, d.y, "-" * n + "X")
    d.y -= TIGHT + 4
    rows = d.y
    fit_text(c, plaintiff_upper + ",", MARGIN_LEFT + 8, d.y, CAPTION_DIV_X - MARGIN_LEFT - 20)  # never into the right column
    d.y -= TIGHT + 2
    c.drawString(MARGIN_LEFT + 176, d.y, "Plaintiff,")
    d.y -= TIGHT + 6
    c.drawString(MARGIN_LEFT + 56, d.y, "-against-")
    d.y -= TIGHT + 6
    fit_text(c, defendant_upper + ",", MARGIN_LEFT + 8, d.y, CAPTION_DIV_X - MARGIN_LEFT - 20)  # never into the right column
    d.y -= TIGHT + 2
    c.drawString(MARGIN_LEFT + 176, d.y, "Defendant.")
    d.y -= TIGHT + 4
    c.drawString(MARGIN_LEFT, d.y, "-" * n + "X")
    c.drawString(RIGHT_COL_X, rows, f"Index No.: {index_number or '______________'}")
    # Title wrapped INSIDE the caption column, each line underlined; the
    # one-line draw ran to x=572, 32pt past the right margin (QA 2026-08-04).
    caption_title(c, "STIPULATION OF SETTLEMENT", rows - TIGHT - 6,
                  RIGHT_COL_X, underline=True)
    d.y -= TIGHT * 1.6


def generate_stipulation(data, output_path):
    plaintiff = (data.get("plaintiffName") or "").strip()
    defendant = (data.get("defendantName") or "").strip()
    county = re.sub(r"\s+County$", "", (data.get("county") or "").strip(), flags=re.I)
    p_addr = (data.get("plaintiffAddress") or "").strip()
    d_addr = (data.get("defendantAddress") or "").strip()
    if not plaintiff or not defendant:
        raise ValueError("Plaintiff and Defendant names are required")
    if not county:
        raise ValueError("County is required")
    if not p_addr or not d_addr:
        raise ValueError("Both party addresses are required")

    marriage_date = fmt_date(data.get("marriageDate"))
    marriage_place = (data.get("marriagePlace") or "____________________").strip()
    index_number = (data.get("indexNumber") or "").strip()
    assets = (data.get("assetsSummary") or "").strip()
    debts = (data.get("debtsSummary") or "").strip()
    division = (data.get("divisionTerms") or "").strip()
    name_restore = (data.get("nameRestoration") or "").strip()
    waived = (str(data.get("maintenanceWaived", "true")).strip().lower() != "false")
    date_signed = (data.get("dateSigned") or "").strip() or "____________________"

    p_inc = parse_income(data.get("plaintiffIncome"))
    d_inc = parse_income(data.get("defendantIncome"))

    d = Doc(output_path)
    draw_caption(d, county.upper(), plaintiff.upper(), defendant.upper(), index_number)

    P, D = title_case(plaintiff), title_case(defendant)

    d.para(
        f"THIS STIPULATION OF SETTLEMENT is made and entered into by and between "
        f"{P}, residing at {p_addr} (the “Plaintiff”), and {D}, residing at "
        f"{d_addr} (the “Defendant”, and together with the Plaintiff, the "
        f"“parties”).")

    # ── I. RECITALS ──
    d.heading(ROMAN[0], "RECITALS")
    recitals = [
        f"The parties were married on {marriage_date}, in {marriage_place}.",
        stipulation_recital(data),
        "The relationship between the parties has broken down irretrievably for a "
        "period of at least six months (Domestic Relations Law § 170(7)), and an "
        "action for divorce is pending or about to be commenced in the Supreme "
        f"Court, {title_case(county)} County.",
        "Each party has made, and each party acknowledges receiving, a fair and "
        "reasonable disclosure of the other's income, assets, and liabilities, and "
        "each enters this Stipulation voluntarily, free of coercion or duress, "
        "believing its terms to be fair and reasonable.",
        "Each party has had the opportunity to consult independent counsel of their "
        "own choosing regarding this Stipulation and its legal consequences.",
    ]
    for i, r in enumerate(recitals, 1):
        d.para(f"{i}. {r}", indent=24)

    # ── II. LIVING SEPARATE AND APART ──
    d.heading(ROMAN[1], "LIVING SEPARATE AND APART")
    d.para(
        "From the date of this Stipulation, each party may live separate and apart "
        "from the other, free from interference, molestation, or restraint by the "
        "other, as fully as if unmarried.")

    # ── III. EQUITABLE DISTRIBUTION ──
    d.heading(ROMAN[2], "EQUITABLE DISTRIBUTION OF PROPERTY")
    d.para(
        "The parties have agreed between themselves upon a complete division of "
        "their marital property, and each acknowledges that the division set forth "
        "below is fair and equitable within the meaning of Domestic Relations Law "
        "§ 236(B)(5).")
    if assets:
        d.para("The parties' significant property consists of the following:", indent=24)
        for line in [ln.strip() for ln in assets.splitlines() if ln.strip()]:
            d.para(f"•  {line}", indent=40, gap=2)
        d.spacer(0.5) if False else None
    if division:
        d.para("The parties have agreed to divide their property as follows:", indent=24)
        for line in [ln.strip() for ln in division.splitlines() if ln.strip()]:
            d.para(f"•  {line}", indent=40, gap=2)
    else:
        d.para(
            "[ATTORNEY REVIEW REQUIRED — the parties' agreed division of property "
            "must be set forth here before execution.]", indent=24)
    d.para(
        "Except as expressly provided above, each party shall retain, free of any "
        "claim by the other, all property currently in that party's name or "
        "possession, including bank accounts, personal effects, and vehicles titled "
        "to that party. Each party waives any claim to the other's separate "
        "property under Domestic Relations Law § 236(B)(1)(d).")

    # ── IV. DEBTS AND LIABILITIES ──
    d.heading(ROMAN[3], "DEBTS AND LIABILITIES")
    if debts:
        d.para("The parties' significant debts consist of the following:", indent=24)
        for line in [ln.strip() for ln in debts.splitlines() if ln.strip()]:
            d.para(f"•  {line}", indent=40, gap=2)
    d.para(
        "Except as expressly provided in this Stipulation or as the parties have "
        "listed above with a contrary agreement, each party shall be solely "
        "responsible for the debts in that party's own name, and each shall "
        "indemnify and hold the other harmless from any claim arising from those "
        "debts. Neither party shall hereafter incur any debt in the name of, or "
        "chargeable to, the other.")

    # ── V. MAINTENANCE ──
    d.heading(ROMAN[4], "SPOUSAL MAINTENANCE")
    if p_inc is not None and d_inc is not None:
        payor_name, payor_inc, payee_name, payee_inc = (
            (P, p_inc, D, d_inc) if p_inc >= d_inc else (D, d_inc, P, p_inc)
        )
        g_annual = guideline_maintenance(payor_inc, payee_inc)
        d.para(
            f"For purposes of the Maintenance Guidelines Law (Domestic Relations Law "
            f"§ 236(B)(6)), the parties state that the annual gross income of {P} is "
            f"approximately {money(p_inc)} and the annual gross income of {D} is "
            f"approximately {money(d_inc)}. Applying the statutory formula (payor "
            f"income capped at {money(MAINTENANCE_CAP)}), the presumptive guideline "
            f"amount of maintenance would be approximately {money(g_annual)} per year "
            f"({money(g_annual / 12)} per month), payable by {payor_name} to "
            f"{payee_name}.")
    else:
        d.para(
            "For purposes of the Maintenance Guidelines Law (Domestic Relations Law "
            "§ 236(B)(6)), the parties state that the annual gross income of the "
            "Plaintiff is approximately $____________ and the annual gross income of "
            "the Defendant is approximately $____________, and that the presumptive "
            "guideline amount of maintenance would be approximately $____________ "
            "per year. [ATTORNEY REVIEW REQUIRED — complete before execution.]")
    if waived:
        d.para(
            "Each party has been advised of, and acknowledges, the guideline amount "
            "of maintenance set forth above. Knowing that amount, and intending to "
            "deviate from it, EACH PARTY KNOWINGLY, VOLUNTARILY, AND IRREVOCABLY "
            "WAIVES, now and forever, any claim to spousal maintenance or support "
            "from the other, past, present, and future. The parties agree this "
            "deviation is fair and reasonable because each is self-supporting and "
            "the parties have divided their property as set forth above.")
    else:
        d.para(
            "[ATTORNEY REVIEW REQUIRED — the parties have not waived maintenance; "
            "counsel must set forth the agreed maintenance terms (amount, duration, "
            "termination events) here before execution.]")

    # ── VI. HEALTH INSURANCE ──
    d.heading(ROMAN[5], "HEALTH INSURANCE")
    d.para(
        "Each party acknowledges, pursuant to Domestic Relations Law § 255, that "
        "upon entry of the judgment of divorce a party may no longer be eligible "
        "for coverage under the other party's health insurance plan, and that each "
        "party may be responsible for obtaining their own coverage, including any "
        "right of continuation coverage under COBRA at that party's own expense.")

    # ── VII. NAME ──
    art = 6
    if name_restore:
        d.heading(ROMAN[art], "RESTORATION OF FORMER NAME")
        d.para(
            f"The parties agree that the judgment of divorce may provide that the "
            f"party formerly known by that name may resume the use of the former "
            f"name {title_case(name_restore)}, and neither party shall object.")
        art += 1

    # ── GENERAL PROVISIONS ──
    d.heading(ROMAN[art], "GENERAL PROVISIONS")
    for i, g in enumerate(
        [
            "Entire agreement. This Stipulation contains the parties' entire "
            "agreement; it supersedes all prior discussions and may be modified "
            "only by a writing signed and acknowledged by both parties.",
            "Incorporation without merger. This Stipulation shall be submitted to "
            "the Court for incorporation into the judgment of divorce; it shall "
            "survive and not merge into the judgment, and shall be enforceable "
            "independently as a contract.",
            "Severability. If any provision is held invalid, the remaining "
            "provisions remain in full force.",
            "Governing law. This Stipulation is governed by the laws of the State "
            "of New York.",
            "Implementation. Each party shall sign any documents reasonably "
            "necessary to carry out this Stipulation, including title transfers "
            "and account designations.",
            "No other actions. Each party represents that no other matrimonial "
            "action is pending between them in any other court.",
        ],
        1,
    ):
        d.para(f"{i}. {g}", indent=24)

    # ── EXECUTION ──
    d.need(LEAD * 14)
    d.spacer(1)
    d.para(
        f"IN WITNESS WHEREOF, the parties have executed this Stipulation of "
        f"Settlement on the date(s) set forth below. Dated: {date_signed}")
    d.spacer(1)
    for who in (P, D):
        d.need(LEAD * 3)
        d.c.line(MARGIN_LEFT, d.y, MARGIN_LEFT + 220, d.y)
        d.c.setFont("Times-Roman", 12)
        d.c.drawString(MARGIN_LEFT, d.y - TIGHT, who)
        d.y -= LEAD * 3

    # Notary acknowledgments — one per party, NY statutory short form.
    for who in (P, D):
        d.need(LEAD * 8)
        d.para(f"STATE OF NEW YORK, COUNTY OF {county.upper()}, ss.:", gap=2)
        d.para(
            f"On the ____ day of ____________, 20___, before me personally appeared "
            f"{who}, personally known to me or proved to me on the basis of "
            f"satisfactory evidence to be the individual whose name is subscribed "
            f"to the within instrument, and acknowledged to me that they executed "
            f"the same.", gap=2)
        d.need(LEAD * 2)
        d.c.line(MARGIN_LEFT, d.y, MARGIN_LEFT + 200, d.y)
        d.c.drawString(MARGIN_LEFT, d.y - TIGHT, "Notary Public")
        d.y -= LEAD * 2.5

    d.c.save()
    return output_path


if __name__ == "__main__":
    sample = {
        "plaintiffName": "JAMIE PLAINTIFF",
        "defendantName": "ALEX DEFENDANT",
        "county": "Orange",
        "plaintiffAddress": "15 Bristol Drive, Middletown, NY 10941",
        "defendantAddress": "24 Manhattan Avenue, Middletown, NY 10940",
        "marriageDate": "2012-06-11",
        "marriagePlace": "Middletown, New York",
        "indexNumber": "EF001234-2026",
        "plaintiffIncome": "68000",
        "defendantIncome": "52000",
        "maintenanceWaived": "true",
        "assetsSummary": "2019 Honda CR-V, titled to Plaintiff\nJoint checking account, Chase (approx. $4,200)\nDefendant's 401(k), approx. $18,000",
        "debtsSummary": "Visa credit card in Plaintiff's name (approx. $2,100)",
        "divisionTerms": "Plaintiff keeps the 2019 Honda CR-V and its loan.\nThe Chase joint checking account will be divided equally and closed.\nDefendant keeps the 401(k) in Defendant's sole name; Plaintiff waives any claim to it.",
        "nameRestoration": "JAMIE ORIGINAL",
    }
    print("Generated:", generate_stipulation(sample, "/tmp/test_stip.pdf"))
