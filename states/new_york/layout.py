"""
Shared page-geometry helpers for the NY generators.

WHY THIS FILE EXISTS
--------------------
A full mechanical QA pass on 2026-08-04 (render every form, measure every
word's bounding box with pdfplumber) found two classes of defect repeated
across otherwise-independent generators:

1. CAPTION TITLES OVERFLOWING THE RIGHT MARGIN. The caption's right column
   runs from x=401 to the 540 margin line — 139pt. Six titles were wider than
   the column and were drawn on one line anyway:

       STIPULATION OF SETTLEMENT   → ended at x=572
       PART 130 CERTIFICATION      → 556
       AFFIRMATION OF DEFENDANT    → 563
       AFFIRMATION OF PLAINTIFF    → 558
       JUDGMENT OF DIVORCE         → 549
       REMOVAL OF BARRIERS         → 544

   The official OCA forms wrap these inside the column (UD-5's generator
   already did, by hand). caption_title() is that hand pattern, shared.

2. INK IN THE TOP MARGIN. Every generator opened each page with
   y = PAGE_HEIGHT - MARGIN_TOP, which puts the first BASELINE on the margin
   line — so ascenders and capitals rose ~10pt INTO the margin, and every
   page measured a 0.86" top margin instead of 1". A one-inch margin is
   measured to the top of the ink, not to the baseline. TOP_Y is the first
   baseline that keeps cap-tops at or below the margin line.

Import both from here; do not re-derive them per file. The one number that
is allowed to differ per form is the caption column left edge, and even that
is the same 401 (= PAGE_WIDTH/2 + 95) in every current caption.
"""

from reportlab.lib.pagesizes import letter

PAGE_WIDTH, PAGE_HEIGHT = letter          # 612 x 792
MARGIN = 72                                # 1 inch, all four sides
RIGHT_EDGE = PAGE_WIDTH - MARGIN           # 540 — no ink right of this
CAP_RISE = 10                              # Times 12: cap top sits ~10pt above baseline

# First baseline of a page: cap tops land ON the 1" margin line, not above it.
TOP_Y = PAGE_HEIGHT - MARGIN - CAP_RISE    # 710


def caption_title(c, text, y, col_left=PAGE_WIDTH / 2 + 95, col_right=RIGHT_EDGE,
                  font="Times-Bold", size=12, leading=14, underline=False):
    """Draw a caption title centered INSIDE the right caption column.

    Wraps on word boundaries to fit (col_right - col_left); each line is
    centered on the column's center. Returns the y of the line BELOW the last
    drawn line, so callers that flow further right-column content can chain.
    Never lets a line poke past the 540 margin: a single word wider than the
    column (none exists in the current form set) is drawn flush-left at
    col_left rather than centered off the edge.
    """
    width = col_right - col_left
    words = text.split()
    lines, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        if not cur or c.stringWidth(trial, font, size) <= width:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    c.setFont(font, size)
    center = (col_left + col_right) / 2
    for line in lines:
        lw = c.stringWidth(line, font, size)
        x = col_left if lw > width else center - lw / 2
        c.drawString(x, y, line)
        if underline:
            c.setLineWidth(0.5)
            c.line(x, y - 2, x + lw, y - 2)
        y -= leading
    return y


def fit_text(c, text, x, y, max_width, font="Times-Roman", size=12, min_size=8):
    """Draw text at `size`, shrinking just enough to fit max_width.

    WHY. The caption is two fixed columns: party names on the left, the index
    number and title in a column starting at x=306 or x=401. The name draws
    had no width limit, so a long-but-real name — the QA fixture uses
    "CHRISTOPHER J. SAMPLETON-VANDERMEER", 281pt in Times 12 caps — printed
    straight through the right column: pdfplumber read back the merged
    letters ("SAMPLETON-VANDERMEPElaRin.tiff") of a name overprinting the
    word "Plaintiff." on the live UD-1.

    A party's legal name is never truncated and never wrapped mid-caption
    (wrapping would shift every hand-positioned row below it). Shrink-to-fit
    is what commercial form fillers do: at 8pt even a 47-character name fits
    the narrow 224pt column. Returns the size actually used, with the
    canvas font left at (font, size) for the caller's next draw.
    """
    use = size
    while use > min_size and c.stringWidth(text, font, use) > max_width:
        use -= 0.5
    c.setFont(font, use)
    c.drawString(x, y, text)
    c.setFont(font, size)
    return use


# --- The standard litigation caption ---------------------------------------
#
# Rebuilt 2026-08-04 against the operator's own filed exemplar (an Answer &
# Counterclaims out of New York County). Two things his filing does that the
# generated captions did not:
#
#   * BREATHING ROOM. Every element gets its own line with air around it —
#     name / label tight, then a full blank line either side of "-against-".
#     The generated captions packed the whole box into six consecutive rows.
#
#   * THE X LANDS UNDER THE "K" IN NEW YORK. The dashed rules are exactly as
#     wide as the court-name line, so the X terminates at the header's right
#     edge. The generated rules were 62 ten-point dashes — they stopped ~70pt
#     short of the header and the X floated mid-page.
#
# One function, all forms. UD-1 keeps its official boxed summons layout.

LEAD = 14
_HEADER = "SUPREME COURT OF THE STATE OF NEW YORK"


def _dash_rule(c, y):
    """Dashed rule ending in X at the header's right edge."""
    c.setFont("Times-Roman", 12)
    header_w = c.stringWidth(_HEADER, "Times-Bold", 12)
    dash_w = c.stringWidth("-", "Times-Roman", 12)
    x_w = c.stringWidth("X", "Times-Roman", 12)
    n = max(10, int((header_w - x_w) / dash_w))
    c.drawString(MARGIN, y, "-" * n + "X")


def draw_caption(c, county, plaintiff, defendant, title, y, index_no="",
                 calendar=False, defendant_label="Defendant.", subtitle=""):
    """The full caption block. Returns the y BELOW the bottom rule, with the
    canvas font left at Times-Roman 12.

    Left column geometry (the caption box is exactly as wide as the header):
    party names flush left, their italic labels centered under them, and
    "-against-" centered with a blank line above and below. Right column
    starts 24pt right of the rules' X: Index No. (and Calendar No. when
    `calendar`) aligned with the plaintiff rows, then the document title —
    bold, underlined, wrapped — aligned with "-against-", then any subtitle
    (the complaint's "ACTION FOR A DIVORCE").
    """
    header_w = c.stringWidth(_HEADER, "Times-Bold", 12)
    box_right = MARGIN + header_w
    box_center = MARGIN + header_w / 2
    right_col = box_right + 24
    name_max = box_right - MARGIN - 4

    def centered(text, yy, font="Times-Italic"):
        c.setFont(font, 12)
        c.drawString(box_center - c.stringWidth(text, font, 12) / 2, yy, text)

    # Header
    c.setFont("Times-Bold", 12)
    c.drawString(MARGIN, y, _HEADER)
    y -= LEAD
    c.drawString(MARGIN, y, f"COUNTY OF {county}")
    y -= LEAD
    _dash_rule(c, y)
    y -= LEAD + 2

    # Half a line of air under the top rule before the first name.
    y -= LEAD // 2

    # Plaintiff
    c.setFont("Times-Roman", 12)
    fit_text(c, plaintiff + ",", MARGIN, y, name_max)
    plaintiff_row = y
    y -= LEAD + 2
    centered("Plaintiff,", y)
    label_row = y

    # air / -against- / air — a FULL blank line each side, plus the row gaps.
    # (Operator, 2026-08-05, on the first cut: "still looks a little too
    # tight... hit return once on each side." So: one more return each side.)
    y -= LEAD * 3
    centered("-against-", y, font="Times-Roman")
    against_row = y
    y -= LEAD * 3

    # Defendant
    c.setFont("Times-Roman", 12)
    fit_text(c, defendant + ",", MARGIN, y, name_max)
    y -= LEAD + 2
    centered(defendant_label, y)
    y -= LEAD + LEAD // 2 + 2
    _dash_rule(c, y)
    bottom_rule = y

    # Right column
    c.setFont("Times-Roman", 12)
    c.drawString(right_col, plaintiff_row, f"Index No.: {index_no or '_______________'}")
    if calendar:
        c.drawString(right_col, label_row, "Calendar No.: __________")
    title_bottom = caption_title(c, title, against_row, right_col,
                                 underline=True)
    if subtitle:
        c.setFont("Times-Roman", 12)
        c.drawString(right_col, title_bottom - 2, subtitle)

    c.setFont("Times-Roman", 12)
    return bottom_rule - LEAD * 1.5
