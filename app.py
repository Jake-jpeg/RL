#!/usr/bin/env python3
"""
DivorceGPT PDF Microservice - Multi-State
==========================================

Flask API that generates court-compliant divorce forms using ReportLab.
Supports multiple states with state-specific form generators.

Endpoints:
- POST /generate/{state}/form  - Generate state-specific forms
- POST /generate/{state}/package - Generate form packages
- GET  /health - Health check

States supported: ny (New York)
"""

import os
import io
import hmac
import time
import shutil
import tempfile
import zipfile
from collections import defaultdict, deque
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from importlib import import_module

from docx_pdf import ConversionError, docx_to_pdf, libreoffice_available

app = Flask(__name__)

# Bound request bodies (form payloads are small structured JSON).
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_REQUEST_BYTES", str(256 * 1024)))

# CORS - allow requests from your frontend.
# NOTE: CORS is a browser courtesy, NOT authentication. Every /generate
# route additionally requires the server-to-server bearer token below;
# the intended caller is the DivorceGPT backend, never a browser.
CORS(app, origins=[
    "http://localhost:3000",
    "https://squid-app-zsiqz.ondigitalocean.app",
    "https://goldfish-app-92wun.ondigitalocean.app",
    "https://divorcegpt.com",
    "https://www.divorcegpt.com",
], supports_credentials=True)

import re

# =====================================================================
# SERVER-TO-SERVER AUTHENTICATION (PDF_SERVICE_TOKEN)
# =====================================================================
# Every generation/package endpoint requires:
#   Authorization: Bearer <PDF_SERVICE_TOKEN>
# - constant-time comparison (hmac.compare_digest);
# - missing/invalid token => 401 with an identical, information-free body
#   (never reveals whether a token was close, malformed, or absent);
# - the token is never logged and never echoed in errors;
# - /health stays open but confidential-detail-free.
# If PDF_SERVICE_TOKEN is unset the service refuses generation entirely
# (fail closed) rather than running open.

_RATE_BUCKETS = defaultdict(deque)  # ip -> recent request timestamps
RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "30"))
RATE_LIMIT_WINDOW_S = int(os.environ.get("RATE_LIMIT_WINDOW_S", "60"))


def _client_ip():
    fwd = request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0].strip() if fwd else request.remote_addr) or "unknown"


def _unauthorized():
    resp = jsonify({"error": "Unauthorized"})
    resp.status_code = 401
    resp.headers["WWW-Authenticate"] = "Bearer"
    return resp


@app.before_request
def _guard_generate_routes():
    """Auth + rate limit for every /generate path (incl. legacy routes)."""
    if not request.path.startswith("/generate"):
        return None
    if request.method == "OPTIONS":  # CORS preflight carries no credentials
        return None

    expected = os.environ.get("PDF_SERVICE_TOKEN", "")
    if not expected:
        # Fail closed: an unconfigured service must not generate documents.
        return jsonify({"error": "Service not configured"}), 503

    header = request.headers.get("Authorization", "")
    supplied = header[7:] if header.startswith("Bearer ") else ""
    if not supplied or not hmac.compare_digest(
        supplied.encode("utf-8"), expected.encode("utf-8")
    ):
        return _unauthorized()

    # Simple fixed-window rate limit per source (single-instance staging).
    now = time.monotonic()
    bucket = _RATE_BUCKETS[_client_ip()]
    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_S:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_MAX:
        return jsonify({"error": "Too many requests"}), 429
    bucket.append(now)
    return None


def sanitize_name_component(value, fallback="Document"):
    """Filenames derive only from [A-Za-z0-9_-]; everything else is dropped."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value or "")).strip("_")
    return cleaned[:60] or fallback


def get_request_data():
    """Parse the JSON body; malformed or non-object JSON => 400, never 500."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="Request body must be a JSON object")
    return data


@app.errorhandler(400)
def _bad_request(e):
    return jsonify({"error": getattr(e, "description", "Bad request")}), 400


@app.errorhandler(413)
def _too_large(e):
    return jsonify({"error": "Request body too large"}), 413

def get_zip_filename(state, form_name):
    """Get display-friendly filename for a form in a ZIP package."""
    return f"{form_name.upper()}.pdf"


# State configuration
STATE_CONFIGS = {
    'ny': {
        'name': 'New York',
        'module': 'new_york',
        'forms': {
            'complaint': 'generate_complaint',
            'stipulation': 'generate_stipulation',
            'ud1': 'generate_ud1',
            'ud4': 'generate_ud4',
            'ud5': 'generate_ud5',
            'ud6': 'generate_ud6',
            'ud7': 'generate_ud7',
            'ud9': 'generate_ud9',
            'ud10': 'generate_ud10',
            'ud11': 'generate_ud11',
            'ud12': 'generate_ud12',
            'ud14': 'generate_ud14',
            'ud15': 'generate_ud15',
        },
        'phase1': ['ud1'],
        'phase2': ['ud5', 'ud6', 'ud7', 'ud9', 'ud10', 'ud11', 'ud12'],
        'phase3': ['ud14', 'ud15'],
    },
    # New Jersey — the 11 generators existed since the 08-02 merge and were
    # QA'd to the same bar as NY (RL cde44ca), but were never REGISTERED:
    # this dict is the routing table, and /generate/nj/* raised
    # "Unsupported state: nj" while every generator sat importable one
    # directory away. Found by the operator assistant, 2026-08-12.
    'nj': {
        'name': 'New Jersey',
        'module': 'new_jersey',
        'forms': {
            'complaint': 'generate_nj_complaint',
            'summons': 'generate_nj_summons',
            'verification': 'generate_nj_verification',
            'acknowledgment': 'generate_nj_acknowledgment',
            'cdr_plaintiff': 'generate_nj_cdr_plaintiff',
            'cdr_defendant': 'generate_nj_cdr_defendant',
            'insurance': 'generate_nj_insurance',
            'jod': 'generate_nj_jod',
            'jod_cert_plaintiff': 'generate_nj_jod_cert_plaintiff',
            'jod_cert_defendant': 'generate_nj_jod_cert_defendant',
        },
        'phase1': ['complaint', 'summons', 'verification'],
        'phase2': ['acknowledgment', 'cdr_plaintiff', 'cdr_defendant', 'insurance'],
        'phase3': ['jod', 'jod_cert_plaintiff', 'jod_cert_defendant'],
    },
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for DigitalOcean."""
    return jsonify({
        "status": "healthy",
        "service": "divorcegpt-pdf-multistate",
        "states": list(STATE_CONFIGS.keys()),
        # Reported, never assumed: the Dockerfile installs libreoffice-writer,
        # but a buildpack build would not, and the failure would otherwise only
        # surface as a 500 on somebody's filing day.
        "docx_to_pdf": libreoffice_available(),
        "auth_required": bool(os.environ.get("PDF_SERVICE_TOKEN")),
        "app_stage": os.environ.get("APP_STAGE", ""),
    })


def get_generator(state, form_name):
    """Dynamically import and return the generator function for a state/form."""
    if state not in STATE_CONFIGS:
        raise ValueError(f"Unsupported state: {state}")
    
    config = STATE_CONFIGS[state]
    
    if form_name not in config['forms']:
        raise ValueError(f"Unknown form '{form_name}' for state '{state}'")
    
    # Use explicit module name from config, fallback to state key
    state_module = config.get('module', state)
    generator_module_name = config['forms'][form_name]
    
    try:
        # Import: states.new_york.generate_ud6
        module = import_module(f'states.{state_module}.{generator_module_name}')
        generator_func = getattr(module, generator_module_name)
        return generator_func
    except (ImportError, AttributeError) as e:
        app.logger.error(f"Failed to load generator {state}/{form_name}: {e}")
        raise ValueError(f"Form generator not available: {form_name}")


def generate_file_response(generator_func, data, filename, suffix='.pdf', mimetype='application/pdf'):
    """Generate with a temp file and return as a download response."""
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = tmp.name

        try:
            generator_func(data, tmp_path)
            with open(tmp_path, 'rb') as f:
                file_bytes = f.read()
        finally:
            # Cleanup even when a generator raises (no orphaned temp files).
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        return send_file(
            io.BytesIO(file_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Document generation error: {e}")
        return jsonify({"error": "Failed to generate document"}), 500


def generate_pdf_response(generator_func, data, filename):
    """Helper to generate PDF and return as response."""
    return generate_file_response(generator_func, data, filename)


def generate_converted_pdf_response(generator_func, data, filename):
    """Build a .docx, convert it with LibreOffice, return the PDF.

    One temp directory for both artifacts so the .docx is never left behind:
    it carries the client's name and address, and this container is shared.
    """
    tmp_dir = tempfile.mkdtemp(prefix="dgpt-")
    try:
        docx_path = os.path.join(tmp_dir, "document.docx")
        generator_func(data, docx_path)
        pdf_path = docx_to_pdf(docx_path, out_dir=tmp_dir)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except ConversionError as e:
        # ConversionError is written to be safe to surface: it never carries
        # LibreOffice output, which can echo document text.
        app.logger.error(f"docx->pdf conversion failed: {e}")
        return jsonify({"error": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Document generation error: {e}")
        return jsonify({"error": "Failed to generate document"}), 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# Forms with an editable Word (.docx) build — operator directive 2026-07-27:
# the attorney downloads forms in WORD from the matter rail. Phase-1 forms
# first; the map grows form by form as each docx build is proven. The PDF
# path exists for every form regardless.
DOCX_FORMS = {
    'ny': {
        'complaint': 'generate_complaint_docx',
        'ud1': 'generate_ud1_docx',
    },
}
DOCX_MIME = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


@app.route('/generate/<state>/<form_name>', methods=['POST'])
def generate_form(state, form_name):
    """Generate a specific form for a state."""
    if state not in STATE_CONFIGS:
        return jsonify({"error": f"Unsupported state: {state}"}), 400
    if form_name not in STATE_CONFIGS[state]['forms']:
        return jsonify({"error": f"Unknown form '{form_name}' for state '{state}'"}), 400
    data = get_request_data()

    fmt = (request.args.get('format') or 'pdf').strip().lower()
    if fmt not in ('pdf', 'docx', 'pdf-from-docx'):
        return jsonify({"error": f"Unsupported format '{fmt}'"}), 400
    if fmt in ('docx', 'pdf-from-docx') and form_name not in DOCX_FORMS.get(state, {}):
        return jsonify({"error": f"No Word build for '{state}/{form_name}' yet — request PDF"}), 400
    if fmt == 'pdf-from-docx' and not libreoffice_available():
        return jsonify({"error": "PDF-from-Word conversion is unavailable on this deployment"}), 503

    try:
        # Get plaintiff or defendant name for filename (sanitized)
        plaintiff = sanitize_name_component(data.get('plaintiffName', ''), 'Document')
        defendant = sanitize_name_component(data.get('defendantName', ''), 'Document')
        name = plaintiff if plaintiff != 'Document' else defendant

        if fmt == 'docx':
            state_module = STATE_CONFIGS[state].get('module', state)
            module = import_module(f'states.{state_module}.docx_forms')
            generator = getattr(module, DOCX_FORMS[state][form_name])
            filename = f"{state.upper()}_{form_name.upper()}_{name}.docx"
            return generate_file_response(generator, data, filename, suffix='.docx', mimetype=DOCX_MIME)

        # format=pdf-from-docx: build the Word document and convert it, so the
        # PDF the court receives is the SAME artifact the attorney edited. The
        # drafted documents (complaint, stipulation) are moving to docx-first
        # because AI-written clauses are variable-length and ReportLab draws at
        # fixed coordinates; see docx_pdf.py.
        if fmt == 'pdf-from-docx':
            state_module = STATE_CONFIGS[state].get('module', state)
            module = import_module(f'states.{state_module}.docx_forms')
            generator = getattr(module, DOCX_FORMS[state][form_name])
            filename = f"{state.upper()}_{form_name.upper()}_{name}.pdf"
            return generate_converted_pdf_response(generator, data, filename)

        generator = get_generator(state, form_name)
        filename = f"{state.upper()}_{form_name.upper()}_{name}.pdf"
        return generate_pdf_response(generator, data, filename)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Form generation error ({state}/{form_name}): {e}")
        return jsonify({"error": "Failed to generate form"}), 500


@app.route('/generate/<state>/phase1-package', methods=['POST'])
def generate_phase1_package(state):
    """Generate all Phase 1 forms for a state as a ZIP file."""
    if state not in STATE_CONFIGS:
        return jsonify({"error": f"Unsupported state: {state}"}), 400
    
    if 'phase1' not in STATE_CONFIGS[state]:
        return jsonify({"error": f"Phase 1 not available for state: {state}"}), 400
    
    data = get_request_data()
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            form_list = STATE_CONFIGS[state]['phase1'].copy()
            
            for form_name in form_list:
                generator = get_generator(state, form_name)
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name

                try:
                    generator(data, tmp_path)

                    filename = get_zip_filename(state, form_name)
                    with open(tmp_path, 'rb') as f:
                        zf.writestr(filename, f.read())
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        filer = sanitize_name_component(data.get('plaintiffName', ''), 'DivorceGPT')
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{state.upper()}_Phase1_Package_{filer}.zip"
        )
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Phase 1 package error ({state}): {e}")
        return jsonify({"error": "Failed to generate package"}), 500


@app.route('/generate/<state>/phase2-package', methods=['POST'])
def generate_phase2_package(state):
    """Generate all Phase 2 forms for a state as a ZIP file."""
    if state not in STATE_CONFIGS:
        return jsonify({"error": f"Unsupported state: {state}"}), 400
    
    if 'phase2' not in STATE_CONFIGS[state]:
        return jsonify({"error": f"Phase 2 not available for state: {state}"}), 400
    
    data = get_request_data()
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            form_list = STATE_CONFIGS[state]['phase2'].copy()
            
            # Add UD-4 if religious ceremony (NY only)
            if state == 'ny' and data.get('religiousCeremony', False):
                form_list.insert(0, 'ud4')
            
            for form_name in form_list:
                generator = get_generator(state, form_name)
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name

                try:
                    generator(data, tmp_path)

                    filename = get_zip_filename(state, form_name)
                    with open(tmp_path, 'rb') as f:
                        zf.writestr(filename, f.read())
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        plaintiff = sanitize_name_component(data.get('plaintiffName', ''), 'DivorceGPT')
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{state.upper()}_Phase2_Package_{plaintiff}.zip"
        )
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Phase 2 package error ({state}): {e}")
        return jsonify({"error": "Failed to generate package"}), 500


@app.route('/generate/<state>/phase3-package', methods=['POST'])
def generate_phase3_package(state):
    """Generate all Phase 3 forms for a state as a ZIP file."""
    if state not in STATE_CONFIGS:
        return jsonify({"error": f"Unsupported state: {state}"}), 400
    
    if 'phase3' not in STATE_CONFIGS[state]:
        return jsonify({"error": f"Phase 3 not available for state: {state}"}), 400
    
    data = get_request_data()
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for form_name in STATE_CONFIGS[state]['phase3']:
                generator = get_generator(state, form_name)
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name

                try:
                    generator(data, tmp_path)

                    filename = get_zip_filename(state, form_name)
                    with open(tmp_path, 'rb') as f:
                        zf.writestr(filename, f.read())
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        plaintiff = sanitize_name_component(data.get('plaintiffName', ''), 'DivorceGPT')
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{state.upper()}_Phase3_Package_{plaintiff}.zip"
        )
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Phase 3 package error ({state}): {e}")
        return jsonify({"error": "Failed to generate package"}), 500


# Legacy routes for backward compatibility (redirect to ny)
@app.route('/generate/ud1', methods=['POST'])
def legacy_ud1():
    return generate_form('ny', 'ud1')

@app.route('/generate/ud4', methods=['POST'])
def legacy_ud4():
    return generate_form('ny', 'ud4')

@app.route('/generate/ud5', methods=['POST'])
def legacy_ud5():
    return generate_form('ny', 'ud5')

@app.route('/generate/ud6', methods=['POST'])
def legacy_ud6():
    return generate_form('ny', 'ud6')

@app.route('/generate/ud7', methods=['POST'])
def legacy_ud7():
    return generate_form('ny', 'ud7')

@app.route('/generate/ud9', methods=['POST'])
def legacy_ud9():
    return generate_form('ny', 'ud9')

@app.route('/generate/ud10', methods=['POST'])
def legacy_ud10():
    return generate_form('ny', 'ud10')

@app.route('/generate/ud11', methods=['POST'])
def legacy_ud11():
    return generate_form('ny', 'ud11')

@app.route('/generate/ud12', methods=['POST'])
def legacy_ud12():
    return generate_form('ny', 'ud12')

@app.route('/generate/ud14', methods=['POST'])
def legacy_ud14():
    return generate_form('ny', 'ud14')

@app.route('/generate/ud15', methods=['POST'])
def legacy_ud15():
    return generate_form('ny', 'ud15')

@app.route('/generate/phase2-package', methods=['POST'])
def legacy_phase2():
    return generate_phase2_package('ny')

@app.route('/generate/phase3-package', methods=['POST'])
def legacy_phase3():
    return generate_phase3_package('ny')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
