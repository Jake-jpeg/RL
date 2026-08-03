"""
Children of the marriage — ONE source of truth for every NY generator.

WHY THIS FILE EXISTS
--------------------
Until now, five generators asserted the ABSENCE of children as a hardcoded
string, with no read of the payload at all:

    generate_ud6.py:237   "4. There are no children of the marriage under 21."
    generate_ud6.py:267   "...and there are no children of the marriage."
    generate_ud7.py:222   "7. There are no children of the marriage under 21."
    generate_ud10.py:356  "There are no children of the marriage."
    generate_ud11.py:298  "that there are no children of the marriage"
    generate_stipulation.py:221  "There are no unemancipated children..."

Only generate_complaint.py read the data. So a single matter could produce a
Verified Complaint naming a child, and then affidavits SWORN BY BOTH PARTIES,
findings of fact, and a Judgment of Divorce all reciting that the child does
not exist. UD-6 and UD-7 are sworn. UD-11 is what the judge signs.

That is the defect this closes. Every one of those call sites now asks THIS
module, and this module reads the payload.

WHAT THIS MODULE WILL AND WILL NOT DO
-------------------------------------
It will state the TRUE facts it has: how many unemancipated children there
are, and each one's name and date of birth. That is what UD-6 paragraph 4
prints ("There is (are) ___ child(ren) of the marriage under the age of 21",
with Name and Date of Birth), and it is exactly what the intake collects.

It will NOT invent decretal or custodial language. Custody, parenting time,
and child support relief in UD-10 and UD-11 have prescribed form text that is
not reproduced here, and inventing a substitute for a clause a judge signs
would be worse than the bug it replaced. Where that language is required, the
generators emit an unmissable ATTORNEY COMPLETION REQUIRED marker instead.

So the three possible states of a child-bearing document are: correct (no
children), correct (children, named, with an explicit completion marker), or
refused. Never false.

NOTE FOR THE OPERATOR: OCA publishes a SEPARATE uncontested packet for cases
with children under 21. Aligning UD-10/UD-11 to that packet's exact language
is the remaining work here, and it needs the real form text, not a
paraphrase.
"""

ATTORNEY_COMPLETION = (
    "[ATTORNEY COMPLETION REQUIRED — child-related relief (custody, parenting "
    "time, and child support under DRL 240(1-b)) must be completed by counsel "
    "on the OCA packet for cases with children under 21.]"
)


def child_rows(data):
    """Normalized child records from the payload.

    Accepts the DGPT shape (a list of {name, dateOfBirth}) and tolerates a
    plain count with no detail, which is what a partially-completed intake
    produces. A row with no name is not a child for pleading purposes — the
    form prints a name, so an unnamed row would print a blank line.
    """
    rows = data.get("children") or data.get("childrenRecords") or []
    out = []
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict):
                name = str(r.get("name") or "").strip()
                dob = str(r.get("dateOfBirth") or r.get("dob") or "").strip()
                if name:
                    out.append({"name": name, "dob": dob})
    return out


def child_count(data):
    """How many unemancipated children the payload asserts.

    The explicit count wins when there is no detail, so a document can still
    say "there is 1 child" honestly while the names are being collected.
    """
    rows = child_rows(data)
    if rows:
        return len(rows)
    raw = data.get("unemancipatedChildren", data.get("childCount", 0))
    try:
        return max(0, int(str(raw).strip() or 0))
    except (TypeError, ValueError):
        return 0


def has_children(data):
    return child_count(data) > 0


def children_detail(data):
    """"Aaron Doe, born March 4, 2019; Mia Doe, born July 9, 2021" — or "" .

    Falls back to `childrenDetail`, which is the pre-formatted string DGPT's
    buildNyComplaintPayload already sends. Two payload contracts for the same
    fact is how the generators drifted apart in the first place; this accepts
    both and normalizes to one.
    """
    parts = []
    for r in child_rows(data):
        parts.append(f"{r['name']}, born {r['dob']}" if r["dob"] else r["name"])
    if parts:
        return "; ".join(parts)
    return str(data.get("childrenDetail") or "").strip()


def _plural(n):
    return ("is one child", "child") if n == 1 else (f"are {n} children", "children")


def affidavit_clause(data, number):
    """UD-6 para 4 / UD-7 para 7 — the sworn recital of children under 21.

    `number` is the paragraph label the calling form uses ("4." / "7."), so
    each form keeps its own numbering.
    """
    n = child_count(data)
    if n == 0:
        return f"{number} There are no children of the marriage under the age of 21."
    phrase, _ = _plural(n)
    detail = children_detail(data)
    body = f"{number} There {phrase} of the marriage under the age of 21"
    if detail:
        body += f", namely: {detail}."
    else:
        body += ". [ATTORNEY COMPLETION REQUIRED — the name and date of birth of each child must be stated.]"
    # The marker rides on EVERY child-bearing affidavit, named or not. A sworn
    # affidavit in a with-children case carries obligations this generator does
    # not produce (custody and support consent), and the person signing it must
    # see that before they sign.
    return body + " " + ATTORNEY_COMPLETION


def ud6_economic_clause(data):
    """UD-6 para 6c — the DRL 170(7) economic-resolution recital.

    With children, the clause cannot simply assert that everything is
    resolved: child support is not the parties' to waive.
    """
    base = (
        "6c. Since the grounds alleged are DRL §170(7), all economic issues of "
        "equitable distribution of marital property, the payment or waiver of "
        "spousal support have been resolved by the parties"
    )
    if not has_children(data):
        return base + " and there are no children of the marriage."
    return (
        base
        + ", and the custody and support of the child(ren) of the marriage "
        + "have been resolved as set forth in the parties' agreement. "
        + ATTORNEY_COMPLETION
    )


def findings_clause(data):
    """UD-10 — the findings paragraph about children."""
    n = child_count(data)
    if n == 0:
        return "There are no children of the marriage."
    phrase, _ = _plural(n)
    detail = children_detail(data)
    if detail:
        return f"There {phrase} of the marriage, namely: {detail}. {ATTORNEY_COMPLETION}"
    return f"There {phrase} of the marriage. {ATTORNEY_COMPLETION}"


def judgment_clause(data):
    """UD-11 — the decretal clause about children.

    With children this deliberately does NOT invent custody or support
    decretal language. It states the fact and marks the clause for counsel,
    because this is the paragraph a judge signs.
    """
    n = child_count(data)
    if n == 0:
        return "that there are no children of the marriage; and it is further"
    phrase, _ = _plural(n)
    detail = children_detail(data)
    subject = f"there {phrase} of the marriage"
    if detail:
        subject += f", namely: {detail}"
    return f"that {subject}; {ATTORNEY_COMPLETION} and it is further"


def complaint_clause(data):
    """Verified Complaint, paragraph FIFTH.

    Lives here rather than in generate_complaint.py: the complaint keeping its
    own private copy of this logic is precisely how it ended up naming a child
    while UD-6, UD-7, UD-10 and UD-11 swore there were none.
    """
    n = child_count(data)
    if n == 0:
        return "There are no unemancipated children of this marriage."
    word = "is one unemancipated child" if n == 1 else f"are {n} unemancipated children"
    detail = children_detail(data)
    if detail:
        return f"There {word} of this marriage, namely: {detail}. {ATTORNEY_COMPLETION}"
    return f"There {word} of this marriage. {ATTORNEY_COMPLETION}"


def stipulation_recital(data):
    """Stipulation of Settlement — the recital about children."""
    n = child_count(data)
    if n == 0:
        return "There are no unemancipated children of the marriage, and none are expected."
    phrase, _ = _plural(n)
    detail = children_detail(data)
    recital = f"There {phrase} of the marriage"
    if detail:
        recital += f", namely: {detail}"
    return f"{recital}. {ATTORNEY_COMPLETION}"
