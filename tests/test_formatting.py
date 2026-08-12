"""
Court-formatting QA, pinned: margins, alignment, overflow, collisions.

WHY THIS FILE EXISTS
--------------------
A full mechanical audit on 2026-08-04 (render every form, measure every word
box with pdfplumber) found 103 raw findings across the 13 generators, which
triaged to six real defect classes — every one invisible to text-presence
tests and every one visible to a filing clerk:

  1. Six caption titles drawn past the right margin (worst: STIPULATION OF
     SETTLEMENT ended at x=572 — 32pt outside the 1" margin).
  2. Every page's first baseline sat ON the top margin line, so ascenders
     rose ~10pt INTO the margin: a measured 0.86" top margin on every page.
  3. UD-6's signature block escaped its page-break guard and printed 38pt
     into the bottom margin.
  4. A long-but-real party name (the fixture's 281pt hyphenated surname)
     overprinted the right caption column — pdfplumber read back the merged
     glyphs of the name struck through the word "Plaintiff.".
  5. Default underscore fill-lines on UD-4a and UD-9 ran past the margin.
  6. title_case() used str.capitalize(), printing "Sampleton-vandermeer" in
     the very signature block the party signs.

These tests re-run that audit. THE STANDARD: letter size, no ink outside the
1" margins except the form-id footer, no two rows of text closer than their
glyphs are tall, no orphaned signature page, and hyphenated names cased
correctly. If a layout change breaks any of that, this file goes red.
"""

import collections
import os
import re
import tempfile

import pdfplumber
import pytest

from states.new_york import (
    generate_complaint, generate_stipulation, generate_ud1, generate_ud4,
    generate_ud5, generate_ud6, generate_ud7, generate_ud9, generate_ud10,
    generate_ud11, generate_ud12, generate_ud14, generate_ud15,
)
from states.new_york.generate_ud1 import title_case

PAGE_W, PAGE_H = 612.0, 792.0
MARGIN = 72.0
RIGHT_EDGE = PAGE_W - MARGIN      # 540
BOTTOM_EDGE = PAGE_H - MARGIN     # 720
TOL = 2.0                         # extraction rounding slack

# Deliberately hostile fixture: hyphenated 281pt surname, long addresses.
BASE = {
    "county": "Westchester",
    "plaintiffName": "Alexandra M. Sampleton-Vandermeer",
    "defendantName": "Christopher J. Sampleton-Vandermeer",
    "plaintiffAddress": "1247 Longmeadow Boulevard, Apartment 14C, White Plains, NY 10601",
    "defendantAddress": "89 Shortwood Lane, Yonkers, NY 10701",
    "qualifyingParty": "plaintiff",
    "qualifyingAddress": "1247 Longmeadow Boulevard, Apartment 14C, White Plains, NY 10601",
    "filingCounty": "Westchester",
    "marriageDate": "2016-06-18",
    "marriageCity": "White Plains",
    "marriageState": "NY",
    "marriagePlace": "White Plains, New York",
    "ceremonyType": "civil",
    "religiousCeremony": False,
    "residencyParty": "plaintiff",
    "residencyBasis": "two_year",
    "residencyType": "A",
    "dateOfBreakdown": "2024-01-03",
    "indexNumber": "123456/2026",
    "filingDate": "2026-08-01",
    "summonsDate": "2026-08-01",
    "plaintiffIncome": "94000",
    "defendantIncome": "61000",
    "plaintiffPhone": "(914) 555-0101",
    "judgmentDate": "2026-09-15",
    "entryDate": "2026-09-16",
    "serviceDate": "2026-09-17",
}
KIDS = dict(
    BASE,
    children=[
        {"name": "Aria Sampleton-Vandermeer", "dateOfBirth": "March 4, 2019"},
        {"name": "Beau Sampleton-Vandermeer", "dateOfBirth": "July 9, 2021"},
    ],
    custody={"residesWith": "plaintiff", "custodian": "plaintiff",
             "visitationParty": "defendant", "visitationPerAgreement": True,
             "dvAllegations": False},
    childSupport={"basis": "stipulation", "agreementDate": "June 1, 2026",
                  "payor": "defendant", "payee": "plaintiff", "amount": "1850",
                  "frequency": "per month", "commencing": "September 1, 2026",
                  "presumptiveAmount": "1850", "conformsToGuideline": True,
                  "uncoveredHealthPct": "40", "childCarePct": "40",
                  "educationPct": "40"},
    childHealthInsurance={"coveringParty": "custodial", "byAgreement": True,
                          "responsibleRelative": "plaintiff",
                          "plaintiffPlan": {"planName": "Oxford Health Plans"},
                          "defendantPlan": {"planName": "Aetna Choice POS II"},
                          "nonCustodialProRataPremium": "180", "qmcso": True},
)
RELIGIOUS = dict(BASE, ceremonyType="religious", religiousCeremony=True)

CASES = [
    ("ud1-base", generate_ud1.generate_ud1, BASE),
    ("complaint-base", generate_complaint.generate_complaint, BASE),
    ("complaint-kids", generate_complaint.generate_complaint, KIDS),
    ("stipulation-base", generate_stipulation.generate_stipulation, BASE),
    ("stipulation-kids", generate_stipulation.generate_stipulation, KIDS),
    ("ud4-religious", generate_ud4.generate_ud4, RELIGIOUS),
    ("ud5-base", generate_ud5.generate_ud5, BASE),
    ("ud6-base", generate_ud6.generate_ud6, BASE),
    ("ud6-kids", generate_ud6.generate_ud6, KIDS),
    ("ud7-base", generate_ud7.generate_ud7, BASE),
    ("ud7-kids", generate_ud7.generate_ud7, KIDS),
    ("ud9-base", generate_ud9.generate_ud9, BASE),
    ("ud10-base", generate_ud10.generate_ud10, BASE),
    ("ud10-kids", generate_ud10.generate_ud10, KIDS),
    ("ud11-base", generate_ud11.generate_ud11, BASE),
    ("ud11-kids", generate_ud11.generate_ud11, KIDS),
    ("ud12-base", generate_ud12.generate_ud12, BASE),
    ("ud14-base", generate_ud14.generate_ud14, BASE),
    ("ud15-base", generate_ud15.generate_ud15, BASE),
]


def _is_footer(w):
    return w["top"] > BOTTOM_EDGE and re.match(r"^\(Form$|^UD-\d+a?\)$|^Page$|^of$|^\d+$", w["text"])


def _audit(pdf_path):
    findings = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            if abs(page.width - PAGE_W) > 0.5 or abs(page.height - PAGE_H) > 0.5:
                findings.append(f"p{i} PAGE-SIZE {page.width}x{page.height}")
            words = page.extract_words(use_text_flow=False)
            if not words:
                findings.append(f"p{i} BLANK PAGE")
                continue
            if min(w["x0"] for w in words) < MARGIN - TOL:
                findings.append(f"p{i} LEFT-MARGIN ink")
            over = [w for w in words if w["x1"] > RIGHT_EDGE + TOL]
            if over:
                findings.append(
                    f"p{i} RIGHT-OVERFLOW {[w['text'][:20] for w in over[:3]]}")
            if min(w["top"] for w in words) < MARGIN - TOL:
                findings.append(f"p{i} TOP-MARGIN ink")
            low = [w for w in words
                   if w["bottom"] > BOTTOM_EDGE + TOL and not _is_footer(w)]
            if low:
                findings.append(
                    f"p{i} BOTTOM-OVERRUN {[w['text'][:20] for w in low[:3]]}")
            # horizontal overlap on the same visual row = struck-through text
            rows = collections.defaultdict(list)
            for w in words:
                rows[round(w["top"])].append(w)
            for ws in rows.values():
                ws.sort(key=lambda w: w["x0"])
                for a, b in zip(ws, ws[1:]):
                    if b["x0"] < a["x1"] - 1.5:
                        findings.append(
                            f"p{i} OVERLAP '{a['text'][:15]}'/'{b['text'][:15]}'")
            # two rows closer than their glyphs are tall AND intersecting in x
            tops = sorted({round(w["top"], 1) for w in words})
            rowmap = {t: [w for w in words if round(w["top"], 1) == t]
                      for t in tops}
            for a, b in zip(tops, tops[1:]):
                if 0 < b - a < 11:
                    if any(wa["x0"] < wb["x1"] and wb["x0"] < wa["x1"]
                           for wa in rowmap[a] for wb in rowmap[b]):
                        findings.append(f"p{i} CRAMPED rows {b - a:.1f}pt apart")
        last = pdf.pages[-1].extract_words()
        if last and len(last) <= 4 and len(pdf.pages) > 1:
            findings.append("ORPHAN last page")
    return findings


@pytest.mark.parametrize("name,fn,data", CASES, ids=[c[0] for c in CASES])
def test_form_is_court_ready(name, fn, data):
    d = tempfile.mkdtemp()
    path = os.path.join(d, f"{name}.pdf")
    fn(dict(data), path)
    findings = _audit(path)
    assert findings == [], f"{name}: " + "; ".join(findings)


def test_title_case_survives_real_surnames():
    """capitalize() printed 'Sampleton-vandermeer' in a signature block."""
    assert title_case("ALEXANDRA M. SAMPLETON-VANDERMEER") == \
        "Alexandra M. Sampleton-Vandermeer"
    assert title_case("PATRICK O'BRIEN") == "Patrick O'Brien"
    assert title_case("jae-won kim") == "Jae-Won Kim"
    assert title_case("JANE A. KIM") == "Jane A. Kim"


def test_fit_text_never_lets_a_name_cross_the_column():
    """The 281pt fixture name must render smaller, never overprint."""
    from reportlab.pdfgen import canvas as rl_canvas
    from states.new_york.layout import fit_text
    c = rl_canvas.Canvas(os.path.join(tempfile.mkdtemp(), "t.pdf"))
    used = fit_text(c, "CHRISTOPHER J. SAMPLETON-VANDERMEER", 72, 700, 224)
    assert used < 12
    assert c.stringWidth("CHRISTOPHER J. SAMPLETON-VANDERMEER",
                         "Times-Roman", used) <= 224
    # and a normal name is untouched
    assert fit_text(c, "JANE A. KIM", 72, 680, 224) == 12


def test_caption_geometry_matches_the_filed_exemplar():
    """The operator compared a generated caption against his own filed
    papers (2026-08-04) and rejected the generated one on two grounds. Both
    are pinned here against UD-6's first page.

    1. The dashed rules must terminate — X included — at the right edge of
       "SUPREME COURT OF THE STATE OF NEW YORK" ("the X is where the K in
       New York is"). The old rules stopped ~70pt short and floated.
    2. Breathing room: "-against-" carries a blank line of air above and
       below, instead of the six-consecutive-row block the generators drew.
    """
    d = tempfile.mkdtemp()
    path = os.path.join(d, "cap.pdf")
    generate_ud6.generate_ud6(dict(BASE), path)
    with pdfplumber.open(path) as pdf:
        words = pdf.pages[0].extract_words()

    header_end = max(w["x1"] for w in words if w["text"] == "YORK")
    rules = [w for w in words if w["text"].startswith("---") and w["text"].endswith("X")]
    assert len(rules) == 2, "caption must have a top and a bottom rule"
    for r in rules:
        assert abs(r["x1"] - header_end) < 6, (
            f"rule ends at x={r['x1']:.0f}, header at x={header_end:.0f} — "
            "the X belongs under the K in NEW YORK")

    def row(text):
        return min(w["top"] for w in words if w["text"] == text)

    against = row("-against-")
    # Rev 2 (operator, 2026-08-05): "hit return once on each side" — a full
    # blank line of air each side, so >= 38pt from the labels, not 24.
    assert against - row("Plaintiff,") >= 38, "no air above -against-"
    assert row("Defendant.") - against >= 38, "no air below -against-"


def test_affirmation_formula_is_verbatim_cplr_2106():
    """The statutory form (as amended eff. 2025) says "under the penalties of
    perjury under the laws of New York" — no comma. Ours carried one. CPLR
    2106 allows "substantially" the form, but courts have bounced creative
    variants; verbatim is free, so be verbatim."""
    d = tempfile.mkdtemp()
    path = os.path.join(d, "ud6.pdf")
    generate_ud6.generate_ud6(dict(BASE), path)
    with pdfplumber.open(path) as pdf:
        text = re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in pdf.pages))
    assert "under the penalties of perjury under the laws of New York" in text
    assert "perjury, under the laws" not in text
    assert "except as to matters alleged on information and belief" in text


def test_ud6_residence_paragraph_is_the_official_structure():
    """Official UD-6 (rev 3/1/26): FOUR options — two-year first, one-year
    with (a)/(b) sub-conditions, then the two cause prongs. The old list had
    six letters including an option that is not a DRL 230 prong at all, and
    ignored the residencyBasis DGPT actually sends."""
    d = tempfile.mkdtemp()
    path = os.path.join(d, "ud6.pdf")
    generate_ud6.generate_ud6(dict(BASE, residencyBasis="two_year"), path)
    with pdfplumber.open(path) as pdf:
        text = re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in pdf.pages))
    assert "[X] 1. The Plaintiff has resided in New York State for a continuous period of at least two years" in text
    assert "The parties were married in New York State." in text
    assert "The parties have resided as married persons in New York State." in text
    # the invented prong must never come back
    assert "married in New York State and both parties were residents" not in text
    # basis mapping: one_year_married checks 2 and (a), not 1
    generate_ud6.generate_ud6(dict(BASE, residencyBasis="one_year_married"), path)
    with pdfplumber.open(path) as pdf:
        text = re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in pdf.pages))
    assert "[X] 2. The Plaintiff resided in New York State on the date of commencement" in text
    assert "[X] a. The parties were married in New York State." in text
    assert "[X] 1." not in text


# --- New Jersey — same ruler, second state (QA'd 2026-08-05) ---------------
# The 11 NJ generators went through the identical audit and carried the same
# birth defects (baseline on the margin line, unguarded overflow — the JOD
# printed body text 25pt from the paper's edge THROUGH its page number, on a
# hard-coded two-page layout). Fixed; pinned here so both states hold the bar.

from states.new_jersey import (
    generate_nj_acknowledgment, generate_nj_cdr_defendant,
    generate_nj_cdr_plaintiff, generate_nj_complaint, generate_nj_insurance,
    generate_nj_jod, generate_nj_jod_cert_defendant,
    generate_nj_jod_cert_plaintiff, generate_nj_summons,
    generate_nj_verification,
)

NJ_BASE = {
    "filingCounty": "Bergen",
    "docketNumber": "FM-02-12345-26",
    "plaintiffName": "Alexandra M. Sampleton-Vandermeer",
    "defendantName": "Christopher J. Sampleton-Vandermeer",
    "plaintiffAddress": "1247 Longmeadow Boulevard, Apartment 14C",
    "plaintiffCityStateZip": "Hackensack, NJ 07601",
    "plaintiffPhone": "(201) 555-0101",
    "defendantAddress": "89 Shortwood Lane",
    "defendantCityStateZip": "Teaneck, NJ 07666",
    "defendantFullCityState": "Teaneck, New Jersey",
    "marriageDate": "2016-06-18",
    "ceremonyType": "civil",
    "ceremonyLocation": "Hackensack, New Jersey",
    "separationDate": "2024-01-03",
    "filingDate": "2026-08-01",
    "judgmentDate": "2026-09-15",
    "hearingDate": "2026-09-15",
}

NJ_CASES = [
    ("nj-complaint", generate_nj_complaint.generate_nj_complaint),
    ("nj-summons", generate_nj_summons.generate_nj_summons),
    ("nj-verification", generate_nj_verification.generate_nj_verification),
    ("nj-acknowledgment", generate_nj_acknowledgment.generate_nj_acknowledgment),
    ("nj-cdr-plaintiff", generate_nj_cdr_plaintiff.generate_nj_cdr_plaintiff),
    ("nj-cdr-defendant", generate_nj_cdr_defendant.generate_nj_cdr_defendant),
    ("nj-insurance", generate_nj_insurance.generate_nj_insurance),
    ("nj-jod", generate_nj_jod.generate_nj_jod),
    ("nj-jod-cert-p", generate_nj_jod_cert_plaintiff.generate_nj_jod_cert_plaintiff),
    ("nj-jod-cert-d", generate_nj_jod_cert_defendant.generate_nj_jod_cert_defendant),
]


@pytest.mark.parametrize("name,fn", NJ_CASES, ids=[c[0] for c in NJ_CASES])
def test_nj_form_is_court_ready(name, fn):
    d = tempfile.mkdtemp()
    path = os.path.join(d, f"{name}.pdf")
    fn(dict(NJ_BASE), path)
    findings = _audit(path)
    assert findings == [], f"{name}: " + "; ".join(findings)
