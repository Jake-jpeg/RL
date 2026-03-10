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

States supported: ny (New York), nv (Nevada - coming soon)
"""

import os
import io
import tempfile
import zipfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from importlib import import_module

app = Flask(__name__)

# CORS - allow requests from your frontend
CORS(app, origins=[
    "http://localhost:3000",
    "https://squid-app-zsiqz.ondigitalocean.app",
    "https://goldfish-app-92wun.ondigitalocean.app",
    "https://divorcegpt.com",
    "https://www.divorcegpt.com",
], supports_credentials=True)

import re

# =====================================================================
# ADDRESS PARSING UTILITY
# =====================================================================
# DivorceGPT AI collects a single combined address like:
#   "2030 Hudson Street, Fort Lee, NJ 07024"
# ReportLab generators expect split fields:
#   plaintiffAddress = "2030 Hudson Street"
#   plaintiffCityStateZip = "Fort Lee, NJ 07024"
#   plaintiffFullCityState = "Fort Lee, New Jersey"
# This utility parses the combined address into the split format.

STATE_ABBREVS = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia',
}

def parse_address(full_address):
    """
    Parse a combined address into street, city/state/zip, and full city/state.
    Input:  "2030 Hudson Street, Fort Lee, NJ 07024"
    Output: ("2030 Hudson Street", "Fort Lee, NJ 07024", "Fort Lee, New Jersey")
    """
    if not full_address:
        return ('', '', '')
    
    # Try to match: street, city, STATE ZIP
    match = re.match(
        r'^(.+?),\s*(.+?),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$',
        full_address.strip()
    )
    if match:
        street = match.group(1).strip()
        city = match.group(2).strip()
        state_abbr = match.group(3).strip()
        zipcode = match.group(4).strip()
        state_full = STATE_ABBREVS.get(state_abbr, state_abbr)
        city_state_zip = f"{city}, {state_abbr} {zipcode}"
        full_city_state = f"{city}, {state_full}"
        return (street, city_state_zip, full_city_state)
    
    # Fallback: try splitting by last comma
    parts = full_address.rsplit(',', 1)
    if len(parts) == 2:
        street_and_city = parts[0].strip()
        state_zip = parts[1].strip()
        # Try to split street from city
        street_parts = street_and_city.rsplit(',', 1)
        if len(street_parts) == 2:
            return (street_parts[0].strip(), f"{street_parts[1].strip()}, {state_zip}", street_parts[1].strip())
    
    # Last resort: return as-is for street, empty for others
    return (full_address, '', '')


def preprocess_nj_data(data):
    """
    Preprocess data from DivorceGPT AI into the format NJ ReportLab generators expect.
    Parses combined addresses, derives ceremony location, etc.
    """
    processed = dict(data)  # copy
    
    # Parse plaintiff address
    p_addr = data.get('plaintiffAddress', '')
    if p_addr and not data.get('plaintiffCityStateZip'):
        street, city_state_zip, full_city_state = parse_address(p_addr)
        processed['plaintiffAddress'] = street
        processed['plaintiffCityStateZip'] = city_state_zip
        processed['plaintiffFullCityState'] = full_city_state
    
    # Parse defendant address
    d_addr = data.get('defendantAddress', '')
    if d_addr and not data.get('defendantCityStateZip'):
        street, city_state_zip, full_city_state = parse_address(d_addr)
        processed['defendantAddress'] = street
        processed['defendantCityStateZip'] = city_state_zip
        processed['defendantFullCityState'] = full_city_state
    
    # Derive ceremony location from marriageCity + marriageState
    if not data.get('ceremonyLocation'):
        city = data.get('marriageCity', '').strip()
        state = data.get('marriageState', '').strip()
        if city and state:
            # Construct "the Borough of Fort Lee, State of New Jersey"
            processed['ceremonyLocation'] = f"the Borough of {city}, State of {state}"
    
    return processed


# Display-friendly filenames for ZIP packages
NV_FORM_DISPLAY_NAMES = {
    'coversheet': 'FAMILY_COURT_COVER_SHEET',
    'joint-petition': 'JOINT_PETITION_FOR_DIVORCE',
    'decree': 'DECREE_OF_DIVORCE',
    'affidavit': 'AFFIDAVIT_OF_RESIDENT_WITNESS',
}

NJ_FORM_DISPLAY_NAMES = {
    'complaint': 'COMPLAINT',
    'verification': 'VERIFICATION',
    'cdr-plaintiff': 'CDR-PLAINTIFF',
    'cdr-defendant': 'CDR-DEFENDANT',
    'insurance': 'INSURANCE',
    'summons': 'SUMMONS',
    'acknowledgment': 'ACKNOWLEDGMENT_OF_SERVICE',
    'jod-cert-plaintiff': 'CN12620-PLAINTIFF',
    'jod-cert-defendant': 'CN12620-DEFENDANT',
    'jod': 'FINAL_JUDGMENT_OF_DIVORCE',
}

def get_zip_filename(state, form_name):
    """Get display-friendly filename for a form in a ZIP package."""
    if state == 'nv' and form_name in NV_FORM_DISPLAY_NAMES:
        return f"{NV_FORM_DISPLAY_NAMES[form_name]}.pdf"
    if state == 'nj' and form_name in NJ_FORM_DISPLAY_NAMES:
        return f"{NJ_FORM_DISPLAY_NAMES[form_name]}.pdf"
    return f"{form_name.upper()}.pdf"


# State configuration
STATE_CONFIGS = {
    'ny': {
        'name': 'New York',
        'module': 'new_york',
        'forms': {
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
    'nv': {
        'name': 'Nevada',
        'module': 'nevada',
        'forms': {
            'joint-petition': 'generate_nv_joint_petition',
            'decree': 'generate_nv_decree',
            'affidavit': 'generate_nv_affidavit',
            'coversheet': 'generate_nv_coversheet',
        },
        'phase1': ['coversheet', 'joint-petition', 'decree', 'affidavit'],
    },
    'nj': {
        'name': 'New Jersey',
        'module': 'new_jersey',
        'forms': {
            'verification': 'generate_nj_verification',
            'complaint': 'generate_nj_complaint',
            'cdr-plaintiff': 'generate_nj_cdr_plaintiff',
            'cdr-defendant': 'generate_nj_cdr_defendant',
            'insurance': 'generate_nj_insurance',
            'jod-cert-plaintiff': 'generate_nj_jod_cert_plaintiff',
            'jod-cert-defendant': 'generate_nj_jod_cert_defendant',
            'acknowledgment': 'generate_nj_acknowledgment',
            'jod': 'generate_nj_jod',
            'summons': 'generate_nj_summons',
        },
        'phase1': ['complaint', 'verification', 'cdr-plaintiff', 'cdr-defendant', 'insurance', 'summons'],
        'phase2': ['complaint', 'verification', 'cdr-plaintiff', 'cdr-defendant', 'insurance', 'summons', 'acknowledgment', 'jod-cert-plaintiff', 'jod-cert-defendant', 'jod'],
    },
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for DigitalOcean."""
    return jsonify({
        "status": "healthy",
        "service": "divorcegpt-pdf-multistate",
        "states": list(STATE_CONFIGS.keys())
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


def generate_pdf_response(generator_func, data, filename):
    """Helper to generate PDF and return as response."""
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Generate PDF
        generator_func(data, tmp_path)
        
        # Read and return
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Cleanup
        os.unlink(tmp_path)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"PDF generation error: {e}")
        return jsonify({"error": "Failed to generate PDF"}), 500


@app.route('/generate/<state>/<form_name>', methods=['POST'])
def generate_form(state, form_name):
    """Generate a specific form for a state."""
    data = request.get_json()
    
    # Preprocess NJ addresses and derived fields
    if state == "nj":
        data = preprocess_nj_data(data)
    
    try:
        generator = get_generator(state, form_name)
        
        # Get plaintiff or defendant name for filename
        plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
        defendant = data.get('defendantName', 'Document').replace(' ', '_')
        name = plaintiff if plaintiff != 'Document' else defendant
        
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
    
    data = request.get_json()
    
    # Preprocess NJ addresses and derived fields
    if state == "nj":
        data = preprocess_nj_data(data)
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            form_list = STATE_CONFIGS[state]['phase1'].copy()
            
            for form_name in form_list:
                generator = get_generator(state, form_name)
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name
                
                generator(data, tmp_path)
                
                filename = get_zip_filename(state, form_name)
                with open(tmp_path, 'rb') as f:
                    zf.writestr(filename, f.read())
                
                os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        plaintiff = data.get('plaintiffName', 'DivorceGPT').replace(' ', '_')
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{state.upper()}_Phase1_Package_{plaintiff}.zip"
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
    
    data = request.get_json()
    
    # Preprocess NJ addresses and derived fields
    if state == "nj":
        data = preprocess_nj_data(data)
    
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
                
                generator(data, tmp_path)
                
                filename = get_zip_filename(state, form_name)
                with open(tmp_path, 'rb') as f:
                    zf.writestr(filename, f.read())
                
                os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        plaintiff = data.get('plaintiffName', 'DivorceGPT').replace(' ', '_')
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
    
    data = request.get_json()
    
    # Preprocess NJ addresses and derived fields
    if state == "nj":
        data = preprocess_nj_data(data)
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for form_name in STATE_CONFIGS[state]['phase3']:
                generator = get_generator(state, form_name)
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name
                
                generator(data, tmp_path)
                
                filename = get_zip_filename(state, form_name)
                with open(tmp_path, 'rb') as f:
                    zf.writestr(filename, f.read())
                
                os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        plaintiff = data.get('plaintiffName', 'DivorceGPT').replace(' ', '_')
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
