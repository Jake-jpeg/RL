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
