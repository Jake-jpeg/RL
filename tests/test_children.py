"""
No generated document may ever deny a child who exists.

THE DEFECT THIS PINS
--------------------
Five generators asserted the ABSENCE of children as a hardcoded string with no
read of the payload:

    generate_ud6.py    "4. There are no children of the marriage under 21."
    generate_ud6.py    "...and there are no children of the marriage."
    generate_ud7.py    "7. There are no children of the marriage under 21."
    generate_ud10.py   "There are no children of the marriage."
    generate_ud11.py   "that there are no children of the marriage"
    generate_stipulation.py  "There are no unemancipated children..."

Only the Verified Complaint read the data. One matter could therefore produce
a complaint naming a child, plus affidavits SWORN BY BOTH PARTIES, findings of
fact, and a Judgment of Divorce all reciting that the child does not exist.

These tests render the real PDFs and read the text back out, because that is
the only level at which the bug was visible — every unit in isolation looked
fine.
"""

import os
import re
import subprocess
import tempfile

import pytest

from states.new_york import (
    generate_complaint,
    generate_stipulation,
    generate_ud6,
    generate_ud7,
    generate_ud10,
    generate_ud11,
)
from states.new_york.children import (
    child_count,
    children_detail,
    has_children,
)

BASE = {
    "county": "New York",
    "plaintiffName": "Jake Kim",
    "defendantName": "Joo Kim",
    "marriageDate": "2023-01-02",
    "marriagePlace": "New York, New York",
    "ceremonyType": "civil",
    "residencyParty": "plaintiff",
    "residencyBasis": "two_year",
    "dateOfBreakdown": "2024-01-03",
    "plaintiffAddress": "60 W 13th St, New York, NY 10011",
    "defendantAddress": "60 W 13th St, New York, NY 10011",
    "indexNumber": "12345/2026",
    "plaintiffIncome": "90000",
    "defendantIncome": "60000",
}

# The two payload shapes in the wild: what DGPT's buildNyComplaintPayload
# actually sends (a count plus a pre-formatted string), and a structured list.
DGPT_SHAPE = dict(BASE, unemancipatedChildren="1",
                  childrenDetail="Aaron Kim, born March 4, 2019")
LIST_SHAPE = dict(BASE, children=[{"name": "Aaron Kim", "dateOfBirth": "March 4, 2019"}])

CHILD_BEARING = [
    ("ud6", generate_ud6.generate_ud6),
    ("ud7", generate_ud7.generate_ud7),
    ("ud10", generate_ud10.generate_ud10),
    ("ud11", generate_ud11.generate_ud11),
    ("stipulation", generate_stipulation.generate_stipulation),
    ("complaint", generate_complaint.generate_complaint),
]

DENIAL = re.compile(r"no (unemancipated )?child(ren)? of (the|this) marriage", re.I)


def render_text(fn, data, name):
    """Render to PDF and extract the text — the level the bug lived at."""
    d = tempfile.mkdtemp()
    path = os.path.join(d, f"{name}.pdf")
    fn(data, path)
    txt = os.path.join(d, "t.txt")
    r = subprocess.run(["pdftotext", "-layout", path, txt], capture_output=True)
    if r.returncode != 0:
        pytest.skip("pdftotext unavailable")
    with open(txt, errors="ignore") as f:
        return re.sub(r"\s+", " ", f.read())


@pytest.mark.parametrize("name,fn", CHILD_BEARING)
@pytest.mark.parametrize("shape", ["dgpt", "list"], ids=["dgpt-payload", "list-payload"])
def test_no_document_denies_an_existing_child(name, fn, shape):
    data = DGPT_SHAPE if shape == "dgpt" else LIST_SHAPE
    text = render_text(fn, data, name)
    assert not DENIAL.search(text), (
        f"{name} DENIES a child that exists — this is the sworn-falsehood bug"
    )
    assert "Aaron Kim" in text, f"{name} does not name the child"


@pytest.mark.parametrize("name,fn", CHILD_BEARING)
def test_childless_documents_still_say_so(name, fn):
    """The no-children path is the common case and must not regress."""
    text = render_text(fn, BASE, name)
    assert DENIAL.search(text), f"{name} lost its no-children recital"
    assert "Aaron Kim" not in text


@pytest.mark.parametrize("name,fn", CHILD_BEARING)
@pytest.mark.parametrize("shape", ["dgpt", "list"], ids=["dgpt-payload", "list-payload"])
def test_child_documents_are_flagged_for_counsel(name, fn, shape):
    """Custody and support relief is NOT generated — it must be marked."""
    data = DGPT_SHAPE if shape == "dgpt" else LIST_SHAPE
    text = render_text(fn, data, name)
    assert "ATTORNEY" in text.upper(), (
        f"{name} carries child facts with no attorney-completion marker"
    )


def test_a_count_without_names_is_still_honest():
    """A half-finished intake states the count and flags the missing names —
    it never falls back to denying the children."""
    data = dict(BASE, unemancipatedChildren="2")
    assert child_count(data) == 2
    assert has_children(data)
    assert children_detail(data) == ""
    text = render_text(generate_ud6.generate_ud6, data, "ud6")
    assert not DENIAL.search(text)
    assert "ATTORNEY" in text.upper()


def test_reader_normalizes_both_contracts_and_junk():
    assert child_count(BASE) == 0
    assert child_count(DGPT_SHAPE) == 1
    assert child_count(LIST_SHAPE) == 1
    assert children_detail(DGPT_SHAPE) == children_detail(LIST_SHAPE)
    # Junk must read as zero, never crash a filing.
    assert child_count(dict(BASE, unemancipatedChildren="")) == 0
    assert child_count(dict(BASE, unemancipatedChildren="two")) == 0
    assert child_count(dict(BASE, unemancipatedChildren=-3)) == 0
    assert child_count(dict(BASE, children="not a list")) == 0
    # A row with no name cannot be pled — the form prints a name.
    assert child_count(dict(BASE, children=[{"dateOfBirth": "2019-03-04"}])) == 0


def test_no_generator_hardcodes_a_child_denial_any_more():
    """Source tripwire: the literal strings that caused this must not return."""
    import pathlib

    ny = pathlib.Path(__file__).resolve().parent.parent / "states" / "new_york"
    offenders = []
    for py in sorted(ny.glob("generate_*.py")):
        src = py.read_text()
        for line in src.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if DENIAL.search(line) and "children.py" not in line:
                offenders.append(f"{py.name}: {line.strip()[:90]}")
    assert not offenders, (
        "a child denial is hardcoded again outside children.py:\n" + "\n".join(offenders)
    )


# ---------------------------------------------------------------------------
# CHILD RELIEF — UD-10 findings and UD-11 decretal paragraphs
# ---------------------------------------------------------------------------
#
# The operator overruled the earlier decision to omit this language:
# "Courts routinely kick the filings if this isn't there." These tests pin the
# three properties that make generating it safe:
#
#   1. the paragraphs are PRESENT on a child matter (the reason for the change)
#   2. the childless document is UNCHANGED (the floor)
#   3. nothing is INVENTED — an unsupplied value prints a blank and is named
#
# Source: UD-10 and UD-11, rev. 3/1/26.
#   https://webfiles.nycourts.gov/public/2026-04/ud-10.pdf
#   https://webfiles.nycourts.gov/public/2026-04/ud-11.pdf

from states.new_york.children import (
    CSSA_COMBINED_INCOME_CAP,
    ud10_child_findings,
    ud11_child_decrees,
)

RELIEF = [("ud10", generate_ud10.generate_ud10), ("ud11", generate_ud11.generate_ud11)]

FULL_RELIEF = dict(
    LIST_SHAPE,
    custody={
        "residesWith": "plaintiff",
        "custodian": "plaintiff",
        "visitationParty": "defendant",
        "visitationPerAgreement": True,
        "dvAllegations": False,
    },
    childSupport={
        "basis": "stipulation",
        "agreementDate": "June 1, 2026",
        "payor": "defendant",
        "payee": "plaintiff",
        "amount": "1150",
        "frequency": "per month",
        "commencing": "September 1, 2026",
        "presumptiveAmount": "1150",
        "conformsToGuideline": True,
        "uncoveredHealthPct": "40",
        "childCarePct": "40",
        "educationPct": "40",
    },
    childHealthInsurance={
        "coveringParty": "custodial",
        "byAgreement": True,
        "responsibleRelative": "plaintiff",
        "plaintiffPlan": {"planName": "Oxford Health Plans"},
        "defendantPlan": {"planName": "Aetna Choice POS II"},
        "nonCustodialProRataPremium": "180",
        "qmcso": True,
    },
)


@pytest.mark.parametrize("name,fn", RELIEF)
@pytest.mark.parametrize("shape", ["dgpt", "list"], ids=["dgpt-payload", "list-payload"])
def test_child_relief_paragraphs_are_present(name, fn, shape):
    """The filing gets kicked without them. They must exist on every child matter."""
    text = render_text(fn, DGPT_SHAPE if shape == "dgpt" else LIST_SHAPE, name)
    for required in ("custody", "visitation", "child support"):
        assert required in text.lower(), f"{name} has no {required} paragraph"
    assert "health" in text.lower(), f"{name} says nothing about the children's health cover"


def test_ud11_carries_the_decretal_paragraphs_a_judge_signs():
    text = render_text(generate_ud11.generate_ud11, LIST_SHAPE, "ud11")
    # Each of these is its own ORDERED AND ADJUDGED on the official form.
    for phrase in (
        "shall have custody of the minor child",
        "shall have visitation with the minor child",
        "as and for the support of the parties' unemancipated child",
        "DRL §240(1-b)",
        "reasonable child care expenses",
        "health care expenses not covered by insurance",
        "education or extraordinary expenses",
        "Qualified Medical Child Support Order",
    ):
        assert phrase in text, f"UD-11 is missing the decretal paragraph: {phrase}"


def test_ud10_carries_the_findings_that_support_them():
    text = render_text(generate_ud10.generate_ud10, LIST_SHAPE, "ud10")
    assert "is entitled to custody" in text
    assert "visitation away from the custodial residence" in text
    assert "domestic violence and/or child abuse" in text, (
        "the DV/child-abuse finding is not optional on UD-10 and its absence is a "
        "known reason for rejection"
    )
    assert "entitled to receive support are" in text
    assert "legally responsible relative" in text


@pytest.mark.parametrize("name,fn", RELIEF)
def test_childless_documents_are_unchanged(name, fn):
    """THE FLOOR. No child relief may appear on a matter with no children."""
    text = render_text(fn, BASE, name)
    # Phrases introduced ONLY by the new child paragraphs. UD-10's existing
    # CONCLUSIONS OF LAW FIFTH already contains the words "custody and
    # visitation" in every document, child or not, so the probes have to be
    # tighter than that.
    for phrase in (
        "shall have custody",
        "is entitled to custody",
        "visitation away from the custodial residence",
        "shall have visitation",
        "reasonable child care expenses",
        "Qualified Medical Child Support Order",
        "entitled to receive support are",
        "legally responsible relative",
        "SIXTEENTH",
        "SEVENTEENTH",
        "EIGHTEENTH",
    ):
        assert phrase not in text, f"childless {name} grew a child paragraph: {phrase}"
    assert ud10_child_findings(BASE) == []
    assert ud11_child_decrees(BASE) == []


@pytest.mark.parametrize("name,fn", RELIEF)
def test_a_complete_payload_leaves_no_marker(name, fn):
    """When counsel has supplied everything, the document must come out CLEAN.

    A completion marker on a paragraph that is finished is noise, and noise is
    how a real marker gets skipped.
    """
    text = render_text(fn, FULL_RELIEF, name)
    assert "ATTORNEY COMPLETION" not in text.upper(), (
        f"{name} flags a paragraph that is fully supplied"
    )
    assert "Defendant shall pay to Plaintiff" in text or "Defendant agrees to pay" in text
    assert "$1,150.00" in text
    assert "Aaron Kim" in text


@pytest.mark.parametrize("name,fn", RELIEF)
def test_a_missing_value_is_named_not_guessed(name, fn):
    """The whole safety property: no invented values, and an exact punch list."""
    text = render_text(fn, LIST_SHAPE, name)
    assert "ATTORNEY COMPLETION REQUIRED" in text
    # The marker names the blank, rather than saying "review required".
    assert "the party who shall have custody" in text or "the party entitled to custody" in text
    # Nothing that was never supplied may appear as a number.
    assert "$1,150.00" not in text
    assert "per month" not in text


def test_no_amount_is_ever_invented():
    """Not one figure in the child support paragraph may come from anywhere but
    the payload."""
    findings = dict(ud10_child_findings(LIST_SHAPE))["SEVENTEENTH:"]
    money = re.findall(r"\$[\d,]+(?:\.\d\d)?", findings)
    # The only dollar figure allowed with no payload data is the statutory cap,
    # and here there is no CSSA branch at all, so there must be none.
    assert money == [], f"UD-10 invented a figure: {money}"


def test_the_cssa_cap_is_the_statutory_one_and_is_printed():
    """$193,000 is on the face of UD-10 (rev. 3/1/26). It must match DGPT's
    ny-guidelines-2026.ts combinedIncomeCap."""
    assert CSSA_COMBINED_INCOME_CAP == 193_000
    data = dict(LIST_SHAPE, childSupport={"basis": "cssa"})
    findings = dict(ud10_child_findings(data))["SEVENTEENTH:"]
    assert "$193,000" in findings
    assert "Child Support Standards Act" in findings or "child support percentage" in findings


def test_existing_order_branch_continues_the_order():
    data = dict(LIST_SHAPE, childSupport={
        "basis": "existing_order", "orderCourt": "Family", "orderCounty": "Kings",
        "orderIndex": "F-01234-26", "orderDate": "March 2, 2026", "payor": "defendant",
        "payee": "plaintiff", "orderAmount": "900", "orderFrequency": "per month",
    })
    findings = dict(ud10_child_findings(data))["SEVENTEENTH:"]
    assert "Said Order shall continue." in findings
    assert "F-01234-26" in findings
    assert "$900.00" in findings
    assert "ATTORNEY COMPLETION" not in findings


def test_children_outside_new_york_get_the_no_award_alternative():
    data = dict(LIST_SHAPE, custody={"childrenOutsideNY": True, "dvAllegations": False})
    findings = dict(ud10_child_findings(data))["SIXTEENTH:"]
    assert "not residing in New York State" in findings
    decrees = ud11_child_decrees(data)
    assert any("no award of custody" in d for d in decrees)


@pytest.mark.parametrize("name,fn", RELIEF)
def test_rendering_is_deterministic(name, fn):
    """Same payload, same document. This is what makes a regression visible."""
    assert render_text(fn, FULL_RELIEF, name) == render_text(fn, FULL_RELIEF, name)
