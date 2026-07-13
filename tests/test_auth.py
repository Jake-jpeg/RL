"""
Server-to-server authentication + input-hardening tests (staging-auth branch).
SYNTHETIC DATA ONLY. Run: PDF_SERVICE_TOKEN not required (set per-test).
"""
import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TOKEN = "synthetic-test-service-token-never-real"

SYNTH_NJ = {
    "plaintiffName": "Avery Stagingperson",
    "defendantName": "Blake Stagingperson",
    "plaintiffAddress": "12 Synthetic Way, Fort Lee, NJ 07024",
    "plaintiffPhone": "(201) 555-0100",
    "filingCounty": "Bergen",
    "docketNumber": "",
}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("PDF_SERVICE_TOKEN", TOKEN)
    import app as app_module
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture()
def unconfigured_client(monkeypatch):
    monkeypatch.delenv("PDF_SERVICE_TOKEN", raising=False)
    import app as app_module
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def auth(token=TOKEN):
    return {"Authorization": f"Bearer {token}"}


def test_health_open_and_secret_free(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] == "healthy"
    assert "states" in body
    assert body["auth_required"] is True
    assert TOKEN not in json.dumps(body)


def test_missing_token_rejected_401(client):
    r = client.post("/generate/nj/verification", json=SYNTH_NJ)
    assert r.status_code == 401
    assert r.get_json() == {"error": "Unauthorized"}


def test_invalid_token_rejected_401_same_body(client):
    r = client.post(
        "/generate/nj/verification", json=SYNTH_NJ, headers=auth("wrong-token")
    )
    assert r.status_code == 401
    # Identical, information-free body — no closeness/malformation hints.
    assert r.get_json() == {"error": "Unauthorized"}
    r2 = client.post(
        "/generate/nj/verification",
        json=SYNTH_NJ,
        headers={"Authorization": "NotBearer xyz"},
    )
    assert r2.status_code == 401
    assert r2.get_json() == {"error": "Unauthorized"}


def test_token_never_echoed_in_error(client):
    r = client.post("/generate/nj/verification", json=SYNTH_NJ, headers=auth("bad"))
    assert TOKEN not in r.get_data(as_text=True)


def test_legacy_routes_are_guarded_too(client):
    r = client.post("/generate/ud1", json={})
    assert r.status_code == 401


def test_valid_token_generates_pdf(client):
    r = client.post("/generate/nj/verification", json=SYNTH_NJ, headers=auth())
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"
    assert r.data[:5] == b"%PDF-"


def test_unsupported_state_400(client):
    r = client.post("/generate/zz/verification", json=SYNTH_NJ, headers=auth())
    assert r.status_code == 400


def test_unsupported_form_400(client):
    r = client.post("/generate/nj/not-a-form", json=SYNTH_NJ, headers=auth())
    assert r.status_code == 400


def test_malformed_json_400(client):
    r = client.post(
        "/generate/nj/verification",
        data="{not json",
        content_type="application/json",
        headers=auth(),
    )
    assert r.status_code == 400
    r2 = client.post(
        "/generate/nj/verification",
        data=json.dumps(["not", "an", "object"]),
        content_type="application/json",
        headers=auth(),
    )
    assert r2.status_code == 400


def test_oversized_request_413(client):
    big = dict(SYNTH_NJ)
    big["padding"] = "x" * (300 * 1024)
    r = client.post("/generate/nj/verification", json=big, headers=auth())
    assert r.status_code == 413


def test_filename_is_sanitized(client):
    payload = dict(SYNTH_NJ)
    payload["plaintiffName"] = '../../etc <script>"passwd"'
    r = client.post("/generate/nj/verification", json=payload, headers=auth())
    assert r.status_code == 200
    disposition = r.headers.get("Content-Disposition", "")
    assert ".." not in disposition
    assert "<" not in disposition and ">" not in disposition
    assert "/" not in disposition.split("filename=")[-1]


def test_unconfigured_service_fails_closed_503(unconfigured_client):
    r = unconfigured_client.post(
        "/generate/nj/verification", json=SYNTH_NJ, headers=auth()
    )
    assert r.status_code == 503


def test_ny_ud1_generates_with_token(client):
    r = client.post(
        "/generate/ny/ud1",
        json={
            "plaintiffName": "Quinn Stagingperson",
            "defendantName": "Reese Stagingperson",
            "plaintiffAddress": "9 Synthetic Ave, White Plains, NY 10601",
            "qualifyingAddress": "9 Synthetic Ave, White Plains, NY 10601",
            "filingCounty": "Westchester",
            "qualifyingParty": "plaintiff",
        },
        headers=auth(),
    )
    assert r.status_code == 200
    assert r.data[:5] == b"%PDF-"


def test_generator_failure_returns_500_and_cleans_temp_files(client, monkeypatch, tmp_path):
    """Repair regression: a crashing generator must not orphan temp files."""
    import glob
    import tempfile as tf
    import app as app_module

    def exploding_generator(data, path):
        # Simulate a generator crash AFTER the temp file exists.
        raise RuntimeError("synthetic generator failure")

    monkeypatch.setattr(app_module, "get_generator", lambda s, f: exploding_generator)
    before = set(glob.glob(os.path.join(tf.gettempdir(), "*.pdf")))
    r = client.post("/generate/nj/verification", json=SYNTH_NJ, headers=auth())
    after = set(glob.glob(os.path.join(tf.gettempdir(), "*.pdf")))
    assert r.status_code == 500
    assert r.get_json() == {"error": "Failed to generate PDF"}
    assert after == before  # no orphaned temp file
