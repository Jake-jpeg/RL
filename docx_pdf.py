"""
docx -> PDF conversion via headless LibreOffice.

WHY THIS EXISTS
---------------
The Dockerfile has installed `libreoffice-writer` since the image was first
built, and until now NOTHING in the codebase called it. Several hundred
megabytes of LibreOffice were shipping in every deploy and doing nothing.

WHY IT MATTERS MORE THAN "SAVING THE MEGABYTES"
----------------------------------------------
The Complaint and the Stipulation are DRAFTED documents, and the plan is for
AI to write some of their paragraphs. ReportLab draws text at coordinates —
`draw_allegation(c, y, ...)`, a `y` cursor threaded manually down the page.
That is fine while every clause is a known fixed string, which is why it works
today. It stops being fine the moment a clause is three lines for one couple
and fourteen for another: text overflows into the signature block or runs off
the bottom of the page, and the fix is hand-writing a layout engine.

Word already does reflow and pagination, and Word is what the attorney edits
before filing anyway. So the drafted documents become docx-first, and THIS is
how they become the PDF the court gets.

The fixed-layout OCA packet forms (UD-1, UD-4..UD-12, UD-14, UD-15) keep their
ReportLab generators. Coordinate drawing genuinely suits a form whose layout
is prescribed and whose text never varies.

OPERATIONAL NOTES
-----------------
* Conversion is 2-5 seconds warm and slower on the first call in a fresh
  container, because LibreOffice builds a user profile before it will convert
  anything. `_warm_profile()` does that once at import so the first real client
  request does not pay for it.
* Every call gets its OWN profile directory. Two concurrent conversions
  sharing one profile is the classic way to get a silent hang, and gunicorn
  runs 2 workers.
* soffice is given a hard timeout. It is a desktop application in a server
  process; if it wedges, the request must die rather than hold a worker.
* Nothing here touches the network and no document ever leaves the container.
"""

import os
import shutil
import subprocess
import tempfile
import uuid

# Where the binary lives in the Debian slim image the Dockerfile builds.
SOFFICE = os.environ.get("SOFFICE_BIN", "soffice")

# A single document, not a batch. Generous enough for a long stipulation on a
# shared vCPU, short enough to fail well inside any sane gateway.
CONVERT_TIMEOUT_S = int(os.environ.get("DOCX_PDF_TIMEOUT_S", "90"))


class ConversionError(RuntimeError):
    """LibreOffice could not produce a PDF. Never carries document content."""


def libreoffice_available() -> bool:
    """True when the binary is on PATH — reported by /health, never assumed."""
    return shutil.which(SOFFICE) is not None


def _run(args, timeout):
    try:
        return subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        raise ConversionError(
            "PDF conversion is unavailable: LibreOffice is not installed in this image"
        )
    except subprocess.TimeoutExpired:
        raise ConversionError("PDF conversion timed out")


def docx_to_pdf(docx_path: str, out_dir: str = None) -> str:
    """Convert a .docx on disk to a .pdf beside it. Returns the PDF path.

    Raises ConversionError on any failure. The message NEVER includes
    LibreOffice's stdout/stderr: it can echo document text, and these documents
    carry client names and addresses.
    """
    if not os.path.exists(docx_path):
        raise ConversionError("PDF conversion failed: source document is missing")

    out_dir = out_dir or os.path.dirname(docx_path) or tempfile.gettempdir()

    # A private profile per conversion. Concurrent conversions sharing one
    # profile hang instead of failing, which is far worse.
    profile = os.path.join(tempfile.gettempdir(), f"lo-{uuid.uuid4().hex}")
    try:
        proc = _run(
            [
                SOFFICE,
                "--headless",
                "--norestore",
                "--invisible",
                "--nolockcheck",
                f"-env:UserInstallation=file://{profile}",
                "--convert-to",
                "pdf:writer_pdf_Export",
                "--outdir",
                out_dir,
                docx_path,
            ],
            CONVERT_TIMEOUT_S,
        )

        produced = os.path.join(
            out_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
        )
        # soffice frequently exits 0 having produced nothing, so the FILE is
        # the success condition, not the return code.
        if not os.path.exists(produced) or os.path.getsize(produced) == 0:
            raise ConversionError(
                f"PDF conversion produced no output (soffice exit {proc.returncode})"
            )
        return produced
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def _warm_profile() -> None:
    """Pay LibreOffice's first-run profile cost at import, not on a client."""
    if not libreoffice_available():
        return
    profile = os.path.join(tempfile.gettempdir(), "lo-warm")
    try:
        _run(
            [
                SOFFICE,
                "--headless",
                "--norestore",
                "--invisible",
                "--nolockcheck",
                f"-env:UserInstallation=file://{profile}",
                "--terminate_after_init",
            ],
            30,
        )
    except ConversionError:
        pass  # warming is best-effort; a real conversion will report properly
