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

It will NOT invent a VALUE. No income, percentage, amount, schedule or party
is ever guessed. Anything the payload does not supply prints as the blank the
official form prints, and is named in a completion marker on that paragraph.

It DOES now carry the child relief language for UD-10 and UD-11 — see the
CHILD RELIEF section at the bottom of this file. An earlier revision withheld
it for want of the real form text; that text is now in hand, and the operator
overruled the omission, correctly: a filing missing those paragraphs is
routinely kicked back.

So the three possible states of a child-bearing document are: correct (no
children), correct (children named, relief paragraphs present, every
unsupplied blank listed by name for counsel), or refused. Never false.
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
    """UD-10 — the findings paragraph identifying the children.

    The blanket completion marker that used to ride here is gone: UD-10 now
    generates the custody, support and health-insurance findings themselves
    (`ud10_child_findings`), and each of those carries its own marker naming
    the blanks it is actually missing. A generic marker on a paragraph that IS
    complete tells the attorney nothing and trains them to ignore it.
    """
    n = child_count(data)
    if n == 0:
        return "There are no children of the marriage."
    phrase, _ = _plural(n)
    detail = children_detail(data)
    if detail:
        return f"There {phrase} of the marriage, namely: {detail}."
    return (
        f"There {phrase} of the marriage. [ATTORNEY COMPLETION REQUIRED — the name and "
        "date of birth of each child must be stated.]"
    )


def judgment_clause(data):
    """UD-11 — the recital clause identifying the children.

    The decretal relief that follows it is `ud11_child_decrees`. As with
    findings_clause, the marker moved onto the specific paragraphs that are
    short a value.
    """
    n = child_count(data)
    if n == 0:
        return "that there are no children of the marriage; and it is further"
    phrase, _ = _plural(n)
    detail = children_detail(data)
    subject = f"there {phrase} of the marriage"
    if detail:
        subject += f", namely: {detail}"
    else:
        subject += (
            " [ATTORNEY COMPLETION REQUIRED — the name and date of birth of each child "
            "must be stated]"
        )
    return f"that {subject}; and it is further"


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


# ---------------------------------------------------------------------------
# CHILD RELIEF — UD-10 findings and UD-11 decretal paragraphs
# ---------------------------------------------------------------------------
#
# WHY THIS EXISTS NOW. The note at the top of this file said the remaining work
# was to align UD-10 and UD-11 to the real OCA language, and that it needed the
# form text rather than a paraphrase. That text is now in hand:
#
#   UD-10 (Findings of Fact and Conclusions of Law), rev. 3/1/26
#     https://webfiles.nycourts.gov/public/2026-04/ud-10.pdf
#     SEVENTH   — the children of the marriage
#     ELEVENTH  — residence, custody, visitation, DV/child-abuse allegations
#     THIRTEENTH— child support: existing order OR CSSA computation OR stipulation
#     FOURTEENTH— group health plans and the legally responsible relative
#
#   UD-11 (Judgment of Divorce), rev. 3/1/26
#     https://webfiles.nycourts.gov/public/2026-04/ud-11.pdf
#     custody · visitation · continuation of existing orders · child support
#     (existing order and primary) · DRL 240(1-b) maintenance-termination
#     adjustment · child care · health care and insurance · education and
#     extraordinary expenses · QMCSO
#
# The operator overruled the earlier decision to omit this language:
# "Courts routinely kick the filings if this isn't there." He is right, and a
# missing decretal paragraph is a rejection at the clerk's window.
#
# WHAT CHANGED, AND WHAT DID NOT. The paragraphs are now PRESENT and carry the
# official structure. Nothing is invented: every value comes from the payload,
# and every value the payload does not supply renders as the form's own blank
# and is named in a completion marker at the end of that paragraph. So a
# child-bearing UD-10/UD-11 is now one of:
#
#   * complete   — every blank filled from the payload, no marker at all
#   * complete-in-structure, flagged — the paragraph is there, the missing
#     blanks are listed by name for counsel
#
# It is never silently short a paragraph, and it never states a number nobody
# gave it. A childless matter renders EXACTLY as before: these paragraphs do
# not appear at all.
#
# ⚠ CSSA_COMBINED_INCOME_CAP is printed in the official UD-10 text and must
# track DGPT's src/config/legal/ny-guidelines-2026.ts `combinedIncomeCap`, and
# generate_stipulation.py's MAINTENANCE_CAP is the same class of copy. Three
# constants for two statutory figures across two repos; the caps adjust every
# other year. If you are here because a cap moved, grep all three.

CSSA_COMBINED_INCOME_CAP = 193_000  # DRL 240(1-b)(c)(2), eff. 3/1/2026

BLANK = "__________"

_FREQUENCIES = ("per week", "bi-weekly", "semi-monthly", "per month")


class _Fill:
    """Fills a form blank from the payload, or records that it is still blank.

    The official forms are blanks and checkboxes. When we have the fact we
    print it; when we do not we print the blank the form prints and remember
    the label, so the paragraph can end with an exact punch list instead of a
    generic "attorney review required" that says nothing about what is needed.
    """

    def __init__(self):
        self.missing = []

    def __call__(self, value, label, blank=BLANK):
        s = "" if value is None else str(value).strip()
        if s:
            return s
        if label not in self.missing:
            self.missing.append(label)
        return blank

    @property
    def complete(self):
        return not self.missing

    def marker(self):
        if self.complete:
            return ""
        return (
            " [ATTORNEY COMPLETION REQUIRED — "
            + "; ".join(self.missing)
            + ".]"
        )


def _section(data, key):
    v = data.get(key)
    return v if isinstance(v, dict) else {}


def _party_label(value, third_party_name="", default=""):
    """'plaintiff' -> 'Plaintiff'. A third party prints its name, per the form."""
    s = str(value or "").strip().lower()
    if s in ("plaintiff", "p"):
        return "Plaintiff"
    if s in ("defendant", "d"):
        return "Defendant"
    if s in ("third_party", "third party", "thirdparty"):
        name = str(third_party_name or "").strip()
        return name or ""
    return default


def _frequency(value, default=""):
    s = str(value or "").strip().lower().replace("_", "-").replace("biweekly", "bi-weekly")
    for f in _FREQUENCIES:
        if s == f or s == f.replace("per ", "") or s == f.replace("-", " "):
            return f
    return default


def _money(value):
    """'1234.5' -> '$1,234.50'. Anything already carrying a $ is left alone."""
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if s.startswith("$"):
        return s
    try:
        n = float(s.replace(",", ""))
    except (TypeError, ValueError):
        return s
    return f"${n:,.2f}"


def _pct(value):
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    return s if s.endswith("%") else f"{s}%"


def _child_table(data):
    """'Aaron Kim (d.o.b. March 4, 2019)' joined — UD-10 SEVENTH / UD-11 custody."""
    rows = child_rows(data)
    if not rows:
        return ""
    return "; ".join(
        f"{r['name']} (d.o.b. {r['dob']})" if r["dob"] else f"{r['name']} (d.o.b. {BLANK})"
        for r in rows
    )


# --- UD-10 findings -------------------------------------------------------


def custody_findings(data):
    """UD-10 ELEVENTH — residence, custody, visitation, DV allegations."""
    cu = _section(data, "custody")
    f = _Fill()

    if cu.get("childrenOutsideNY"):
        body = (
            "No award of custody is made, the minor child(ren) of the marriage "
            "not residing in New York State."
        )
    else:
        resides = f(
            _party_label(cu.get("residesWith"), cu.get("residesWithName")),
            "the party the child(ren) reside with",
        )
        custodian = f(
            _party_label(cu.get("custodian"), cu.get("custodianName")),
            "the party entitled to custody",
        )
        body = (
            f"The minor child(ren) of the marriage now reside with {resides}. "
            f"{custodian} is entitled to custody."
        )
        other = str(cu.get("arrangement") or "").strip()
        if other:
            body += f" Other custody arrangement: {other}."

        if cu.get("visitationNotApplicable"):
            body += " Visitation is not applicable."
        else:
            visitor = f(
                _party_label(cu.get("visitationParty"), cu.get("visitationPartyName")),
                "the party entitled to visitation",
            )
            body += f" {visitor} is entitled to visitation away from the custodial residence"
            if cu.get("visitationPerAgreement"):
                body += " in accordance with the parties' settlement agreement."
            else:
                sched = f(cu.get("visitationSchedule"), "the visitation schedule",
                          blank="_" * 40)
                body += f" according to the following schedule: {sched}."

    # The DV / child-abuse finding is not optional on the form and its absence
    # is a known reason for rejection.
    if cu.get("dvAllegations") is None:
        f("", "whether allegations of domestic violence and/or child abuse were made")
        body += (
            " Allegations of domestic violence and/or child abuse "
            f"{BLANK} made in this case."
        )
    elif cu.get("dvAllegations"):
        body += " Allegations of domestic violence and/or child abuse were made in this case."
        if cu.get("dvSupported") is None:
            f("", "the Court's finding on the domestic-violence allegations")
            body += (
                f" The Court has found that they {BLANK} supported by a preponderance "
                "of the evidence."
            )
        elif cu.get("dvSupported"):
            body += (
                " The Court has found that they were supported by a preponderance of "
                "the evidence, and has set forth on the record or in writing how such "
                "findings, facts and circumstances were factored into the custody or "
                "visitation direction."
            )
        else:
            body += (
                " The Court has found that they were not supported by a preponderance "
                "of the evidence."
            )
    else:
        body += (
            " Allegations of domestic violence and/or child abuse were not made in "
            "this case."
        )

    return body + f.marker()


def _support_existing_order(cs, f):
    court = f(cs.get("orderCourt"), "the court that issued the existing support order")
    county = f(cs.get("orderCounty"), "the county of the existing support order")
    number = f(cs.get("orderIndex"), "the index/docket number of the existing support order")
    date = f(cs.get("orderDate"), "the date of the existing support order")
    payor = f(_party_label(cs.get("payor")), "the party directed to pay support")
    amount = f(_money(cs.get("orderAmount")), "the amount of the existing support order")
    freq = f(_frequency(cs.get("orderFrequency")), "the payment frequency of the existing order")
    return (
        f"By order of {court} Court, {county} County, Index/Docket No. {number}, "
        f"dated {date}, {payor} was directed to pay the sum of {amount} {freq} for "
        "child support. Said Order shall continue."
    )


def _support_cssa(cs, f):
    p_income = f(_money(cs.get("plaintiffAdjustedIncome")), "Plaintiff's adjusted gross income")
    d_income = f(_money(cs.get("defendantAdjustedIncome")), "Defendant's adjusted gross income")
    combined = f(_money(cs.get("combinedIncome")), "the combined parental annual income")
    p_role = f(cs.get("plaintiffRole"), "whether Plaintiff is the custodial or non-custodial parent")
    d_role = f(cs.get("defendantRole"), "whether Defendant is the custodial or non-custodial parent")
    pct = f(_pct(cs.get("percentage")), "the applicable child support percentage")
    cap = f"${CSSA_COMBINED_INCOME_CAP:,}"
    basic = f(_money(cs.get("basicObligationUpToCap")),
              f"the combined basic child support obligation on income up to {cap}")
    over = f(_money(cs.get("basicObligationOverCap")),
             f"the combined obligation on income over {cap}")
    p_rata = f(_pct(cs.get("plaintiffProRata")), "Plaintiff's pro rata share of combined income")
    d_rata = f(_pct(cs.get("defendantProRata")), "Defendant's pro rata share of combined income")
    ncp_up = f(_money(cs.get("ncpShareUpToCap")),
               f"the non-custodial parent's pro rata share of the obligation up to {cap}")
    ncp_over = f(_money(cs.get("ncpShareOverCap")),
                 f"the non-custodial parent's pro rata share of the obligation over {cap}")
    health_pct = f(_pct(cs.get("uncoveredHealthPct")),
                   "the non-custodial parent's pro rata share of uncovered health care expenses")
    care = f(_money(cs.get("childCareAmount")) or _pct(cs.get("childCarePct")),
             "the non-custodial parent's share of reasonable child care expenses")
    edu = f(_money(cs.get("educationAmount")) or _pct(cs.get("educationPct")),
            "the non-custodial parent's share of educational or extraordinary expenses")
    return (
        f"The adjusted gross income of the Plaintiff, who is the {p_role} parent, is "
        f"{p_income} per year, and the adjusted gross income of the Defendant, who is "
        f"the {d_role} parent, is {d_income} per year, and the combined parental annual "
        f"income is {combined}. The gross incomes of the parties have been adjusted to "
        "deduct maintenance paid to, and to add maintenance received by, a party spouse. "
        f"The applicable child support percentage is {pct}. The combined basic child "
        f"support obligation attributable to both parents is {basic} per year on combined "
        f"income up to {cap} as adjusted for low income if applicable, and {over} per year "
        f"on income over {cap}. The Plaintiff's pro rata share of the combined parental "
        f"income is {p_rata} and the Defendant's pro rata share of the combined parental "
        f"income is {d_rata}. The non-custodial parent's pro rata share of the child "
        f"support obligation on combined income up to {cap} is {ncp_up} per year. The "
        "non-custodial parent's pro rata share of the child support obligation on combined "
        f"income over {cap} is {ncp_over} per year. The non-custodial parent's pro rata "
        f"share of future health care expenses not covered by insurance is {health_pct}. "
        f"The non-custodial parent's share of reasonable child care expenses is {care}. "
        f"The non-custodial parent's share of educational or extraordinary expenses for "
        f"the children, if any, is {edu}."
    )


def _support_stipulation(cs, f):
    date = f(cs.get("agreementDate"), "the date of the parties' stipulation or agreement")
    payor = f(_party_label(cs.get("payor")), "the party who agrees to pay child support")
    amount = f(_money(cs.get("amount")), "the agreed child support amount")
    freq = f(_frequency(cs.get("frequency")), "the agreed payment frequency")
    payee = f(_party_label(cs.get("payee"), cs.get("payeeName")),
              "the party to whom child support is paid")
    route = "through the Support Collection Unit" if cs.get("throughSCU") else "directly"
    cap = f"${CSSA_COMBINED_INCOME_CAP:,}"
    cssa_over = "waive" if cs.get("waiveOverCap") else "apply"
    presumptive = f(_money(cs.get("presumptiveAmount")),
                    "the presumptive amount of child support attributable to the "
                    "non-custodial parent")
    uncovered = f(_pct(cs.get("uncoveredHealthPct")),
                  "the agreed share of uncovered health care expenses")
    care = f(_money(cs.get("childCareAmount")) or _pct(cs.get("childCarePct")),
             "the agreed share of reasonable child care expenses")
    edu = f(_money(cs.get("educationAmount")) or _pct(cs.get("educationPct")),
            "the agreed share of educational and extraordinary expenses")

    body = (
        f"The parties entered into a stipulation/agreement on {date}, wherein {payor} "
        f"agrees to pay {amount} {freq} child support {route} to {payee}. The parties "
        f"agree to {cssa_over} the Child Support Standards Act to combined income over "
        f"{cap}. The parties have agreed that health care expenses not covered by "
        f"insurance shall be paid in the amount of {uncovered} of the uncovered expenses; "
        f"that reasonable child care expenses shall be paid in the amount of {care}; and "
        f"that educational and extraordinary expenses shall be paid in the amount of {edu}. "
        "Said agreement recites, in compliance with DRL §240(1-b)(h): the parties have "
        "been advised of the Child Support Standards Act; the basic child support "
        "obligation presumptively results in the correct amount of child support; and the "
        "unrepresented party, if any, has received a copy of the Child Support Standards "
        "Chart promulgated by the Commissioner of Social Services pursuant to Social "
        "Services Law §111-i. The presumptive amount of child support attributable to the "
        f"non-custodial parent is {presumptive}."
    )

    if cs.get("conformsToGuideline") is False:
        reasons = f(cs.get("deviationReasons"),
                    "the parties' stated reasons for deviating from the basic child "
                    "support obligation", blank="_" * 40)
        court_reasons = f(cs.get("courtDeviationReasons"),
                          "the Court's reasons for finding the deviation just and "
                          "appropriate", blank="_" * 40)
        body += (
            " The amount of child support agreed to deviates from the non-custodial "
            f"parent's basic child support obligation for the following reasons: {reasons}. "
            "The court finds said amount to be just and appropriate for the following "
            f"reasons: {court_reasons}."
        )
    elif cs.get("conformsToGuideline"):
        body += (
            " The amount of child support agreed to conforms with the non-custodial "
            "parent's basic child support obligation."
        )
    else:
        f("", "whether the agreed amount conforms with or deviates from the basic child "
              "support obligation")
        body += (
            f" The amount of child support agreed to {BLANK} with the non-custodial "
            "parent's basic child support obligation."
        )
    return body


def child_support_findings(data):
    """UD-10 THIRTEENTH — the basis of the child support award."""
    cs = _section(data, "childSupport")
    f = _Fill()

    table = _child_table(data) or f("", "the name and date of birth of each child "
                                       "entitled to receive support")
    head = f"The unemancipated children of the marriage entitled to receive support are: {table}."

    basis = str(cs.get("basis") or "").strip().lower()
    if basis in ("existing_order", "existing", "order"):
        body = _support_existing_order(cs, f)
    elif basis in ("cssa", "computation", "court"):
        body = _support_cssa(cs, f)
    elif basis in ("stipulation", "agreement"):
        body = _support_stipulation(cs, f)
    else:
        f("", "the basis of the child support award — an existing order, a CSSA "
              "computation, or the parties' stipulation")
        body = (
            "The award of child support is based upon " + BLANK + ": an existing order "
            "of another court, a computation under the Child Support Standards Act, or "
            "the parties' stipulation."
        )

    return f"{head} {body}{f.marker()}"


def child_health_findings(data):
    """UD-10 FOURTEENTH — group health plans and the responsible relative."""
    hi = _section(data, "childHealthInsurance")
    f = _Fill()

    if hi.get("noPlansAvailable"):
        plans = "There are no health plans available to the parties through their employment."
    else:
        p = _section(hi, "plaintiffPlan")
        d = _section(hi, "defendantPlan")
        p_name = f(p.get("planName"), "Plaintiff's group health plan")
        d_name = f(d.get("planName"), "Defendant's group health plan")
        plans = (
            "The parties are covered by the following group health plans through their "
            f"employment: Plaintiff — {p_name}; Defendant — {d_name}."
        )

    who = f(_party_label(hi.get("responsibleRelative")),
            "the party who shall be the legally responsible relative for the child(ren)'s "
            "health insurance")
    source = ("The parties have agreed or stipulated"
              if hi.get("byAgreement") else "The court has determined")
    enrol = (
        f"{source} that {who} shall be the legally responsible relative and that the "
        "unemancipated child(ren) shall be enrolled in his or her group health plan as "
        "specified above until the age of 21 years or until the child(ren) is or are "
        "sooner emancipated."
    )
    return f"{plans} {enrol}{f.marker()}"


def ud10_child_findings(data):
    """The child findings UD-10 adds, in order. Empty when there are no children.

    Returned as (label, text) so the generator keeps ownership of its own
    paragraph numbering — this form is a narrative Findings of Fact modeled on
    filed samples, not the OCA checkbox layout, and its ordinals are its own.
    """
    if not has_children(data):
        return []
    return [
        ("SIXTEENTH:", custody_findings(data)),
        ("SEVENTEENTH:", child_support_findings(data)),
        ("EIGHTEENTH:", child_health_findings(data)),
    ]


# --- UD-11 decretal paragraphs -------------------------------------------


def ud11_child_decrees(data):
    """The ORDERED AND ADJUDGED paragraphs UD-11 adds when there are children.

    Each string is the body that follows "ORDERED AND ADJUDGED,". The caller
    appends its own "and it is further" chaining. Empty when childless, so a
    no-children judgment is byte-identical to the one this repo already
    produced.
    """
    if not has_children(data):
        return []

    cu = _section(data, "custody")
    cs = _section(data, "childSupport")
    hi = _section(data, "childHealthInsurance")
    out = []

    # Custody
    f = _Fill()
    table = _child_table(data) or f("", "the name and date of birth of each child")
    if cu.get("childrenOutsideNY"):
        out.append(
            "that no award of custody is made, the minor child(ren) of the marriage, "
            f"i.e.: {table}, not residing in New York State" + f.marker()
        )
    else:
        custodian = f(_party_label(cu.get("custodian"), cu.get("custodianName")),
                      "the party who shall have custody")
        out.append(
            f"that {custodian} shall have custody of the minor child(ren) of the "
            f"marriage, i.e.: {table}" + f.marker()
        )

    # Visitation
    f = _Fill()
    if cu.get("visitationNotApplicable"):
        out.append("that visitation is not applicable")
    else:
        visitor = f(_party_label(cu.get("visitationParty"), cu.get("visitationPartyName")),
                    "the party who shall have visitation")
        if cu.get("visitationPerAgreement"):
            tail = "in accordance with the parties' settlement agreement"
        else:
            tail = ("according to the following schedule: "
                    + f(cu.get("visitationSchedule"), "the visitation schedule",
                        blank="_" * 40))
        out.append(
            f"that {visitor} shall have visitation with the minor child(ren) of the "
            f"marriage {tail}" + f.marker()
        )

    # Continuation of existing custody / visitation orders
    ex = _section(cu, "existingOrder")
    if ex:
        f = _Fill()
        county = f(ex.get("county"), "the county of the existing custody/visitation order")
        court = f(ex.get("court"), "the court of the existing custody/visitation order")
        num = f(ex.get("number"), "the index/docket number of the existing order")
        subject = f(ex.get("subject"), "whether the existing order is as to custody or "
                                       "visitation")
        out.append(
            f"that the existing {county} County, {court} Court order under "
            f"No. {num} as to {subject} shall continue" + f.marker()
        )
    else:
        out.append(
            "that there are no court orders with regard to custody or visitation to be "
            "continued"
        )

    # Child support
    f = _Fill()
    basis = str(cs.get("basis") or "").strip().lower()
    if basis in ("existing_order", "existing", "order"):
        payor = f(_party_label(cs.get("payor")), "the party who shall pay child support")
        payee = f(_party_label(cs.get("payee"), cs.get("payeeName")),
                  "the party to whom child support shall be paid")
        amount = f(_money(cs.get("orderAmount")), "the amount of the existing support order")
        freq = f(_frequency(cs.get("orderFrequency")), "the frequency of the existing order")
        county = f(cs.get("orderCounty"), "the county of the existing support order")
        court = f(cs.get("orderCourt"), "the court of the existing support order")
        num = f(cs.get("orderIndex"), "the index/docket number of the existing support order")
        out.append(
            f"that {payor} shall pay to {payee}, as and for the support of the parties' "
            f"unemancipated children of the marriage, the sum of {amount} {freq}, pursuant "
            f"to an existing order issued by the {county} County, {court} Court, under "
            f"No. {num}, the terms of which are hereby continued" + f.marker()
        )
    else:
        payor = f(_party_label(cs.get("payor")), "the party who shall pay child support")
        payee = f(_party_label(cs.get("payee"), cs.get("payeeName")),
                  "the party to whom child support shall be paid")
        amount = f(_money(cs.get("amount")), "the child support amount")
        freq = f(_frequency(cs.get("frequency")), "the payment frequency")
        commencing = f(cs.get("commencing"), "the commencement date of child support")
        table = _child_table(data) or f("", "the name and date of birth of each child")
        route = (
            "through the NYS Child Support Processing Center, PO Box 15363, Albany, NY "
            "12212-5363" if cs.get("throughSCU") else f"directly to {payee}"
        )
        source = ("the parties' Settlement Agreement"
                  if str(cs.get("basis") or "").lower() in ("stipulation", "agreement")
                  else "the Court's decision")
        out.append(
            f"that {payor} shall pay to {payee}, as and for the support of the parties' "
            f"unemancipated child(ren) of the marriage, namely: {table}, the sum of "
            f"{amount} {freq}, commencing on {commencing}, and to be paid {route}, "
            f"together with such dollar amounts or percentages for child care, education "
            f"and health care as set forth below in accordance with {source}" + f.marker()
        )

    # DRL 240(1-b) adjustment on termination of maintenance — unconditional on
    # the form, and it is boilerplate: no blank to fill.
    out.append(
        "that, if maintenance is to be paid pursuant to this Judgment of Divorce, then, "
        "subject to the terms of DRL §240(1-b), upon termination of the maintenance award, "
        "the amount of child support payable shall be adjusted, without prejudice to "
        "either party's right to seek a modification pursuant to DRL §236(B)(9)(2)"
    )

    # Child care
    f = _Fill()
    if cs.get("childCareNotApplicable"):
        out.append("that reasonable child care expenses are not applicable")
    else:
        payor = f(_party_label(cs.get("payor")), "the party who shall pay child care expenses")
        payee = f(_party_label(cs.get("payee"), cs.get("payeeName")),
                  "the party to whom child care expenses shall be paid")
        care = f(_money(cs.get("childCareAmount")) or _pct(cs.get("childCarePct")),
                 "the child care amount or percentage")
        basis_txt = ("written agreement of the parties"
                     if cs.get("childCareByAgreement", True) else "the court's decision")
        out.append(
            f"that {payor} shall pay to {payee}, as and for reasonable child care expenses "
            f"pursuant to {basis_txt}, {care}" + f.marker()
        )

    # Health care expenses and insurance premiums
    f = _Fill()
    uncovered = f(_pct(cs.get("uncoveredHealthPct")),
                  "the non-custodial parent's pro rata share of uncovered health care "
                  "expenses")
    covering = str(hi.get("coveringParty") or "").strip().lower()
    if covering in ("custodial", "custodial parent"):
        premium = f(_money(hi.get("nonCustodialProRataPremium")),
                    "the non-custodial parent's pro rata share of the children's health "
                    "insurance premiums")
        premium_txt = (
            "the custodial parent provides the health insurance for the children, and the "
            f"non-custodial parent's pro rata share of health insurance premiums for the "
            f"children is {premium}"
        )
    elif covering in ("non-custodial", "noncustodial", "non custodial", "non-custodial parent"):
        premium = f(_money(hi.get("custodialProRataPremium")),
                    "the custodial parent's pro rata share of the children's health "
                    "insurance premiums")
        premium_txt = (
            "the non-custodial parent provides the health insurance for the children, and "
            f"the custodial parent's pro rata share of health insurance premiums for the "
            f"children, {premium}, will be deducted from the child support obligation"
        )
    else:
        f("", "which parent provides health insurance for the children")
        premium_txt = (
            f"{BLANK} provides the health insurance for the children, and the other "
            f"parent's pro rata share of the premiums is {BLANK}"
        )
    payor = f(_party_label(cs.get("payor")), "the party who shall pay health care expenses")
    payee = f(_party_label(cs.get("payee"), cs.get("payeeName")),
              "the party to whom health care expenses shall be paid")
    health = (
        f"that {payor} shall pay to {payee}, as and for the non-custodial parent's pro "
        f"rata share of future health care expenses not covered by insurance, {uncovered} "
        f"of such expenses; and that {premium_txt}"
    )
    if hi.get("stateSponsored"):
        who = f(_party_label(hi.get("stateSponsoredApplicant")),
                "the party who shall apply for state-sponsored health insurance")
        health += (
            f"; and that {who} shall apply to the state sponsored health insurance plan "
            "for coverage for the unemancipated children of the marriage"
        )
    out.append(health + f.marker())

    # Education and extraordinary expenses
    f = _Fill()
    if cs.get("educationNotApplicable"):
        out.append("that education or extraordinary expenses of the children are not applicable")
    else:
        payor = f(_party_label(cs.get("payor")), "the party who shall pay education expenses")
        payee = f(_party_label(cs.get("payee"), cs.get("payeeName")),
                  "the party to whom education expenses shall be paid")
        edu = f(_money(cs.get("educationAmount")) or _pct(cs.get("educationPct")),
                "the education or extraordinary expense amount or percentage")
        basis_txt = ("written agreement of the parties"
                     if cs.get("educationByAgreement", True) else "the court's decision")
        out.append(
            f"that {payor} shall pay to {payee}, for education or extraordinary expenses "
            f"of the children, {edu}, pursuant to {basis_txt}" + f.marker()
        )

    # QMCSO
    if hi.get("qmcso"):
        out.append(
            "that a separate Qualified Medical Child Support Order shall be issued "
            "simultaneously herewith"
        )
    else:
        out.append(
            "that a separate Qualified Medical Child Support Order is not applicable"
        )

    return out
