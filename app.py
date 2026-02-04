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

# State configuration
STATE_CONFIGS = {
    'ny': {
        'name': 'New York',
        'forms': {
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
        'phase2': ['ud5', 'ud6', 'ud7', 'ud9', 'ud10', 'ud11', 'ud12'],
        'phase3': ['ud14', 'ud15'],
    },
    # Future: Nevada, California, etc.
    # 'nv': {
    #     'name': 'Nevada',
    #     'forms': {
    #         'complaint': 'generate_complaint',
    #         'decree': 'generate_decree',
    #     },
    # },
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
    
    state_module = state.replace('-', '_')  # ny-forms -> ny_forms
    
    if form_name not in STATE_CONFIGS[state]['forms']:
        raise ValueError(f"Unknown form '{form_name}' for state '{state}'")
    
    generator_module_name = STATE_CONFIGS[state]['forms'][form_name]
    
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


@app.route('/generate/<state>/phase2-package', methods=['POST'])
def generate_phase2_package(state):
    """Generate all Phase 2 forms for a state as a ZIP file."""
    if state not in STATE_CONFIGS:
        return jsonify({"error": f"Unsupported state: {state}"}), 400
    
    if 'phase2' not in STATE_CONFIGS[state]:
        return jsonify({"error": f"Phase 2 not available for state: {state}"}), 400
    
    data = request.get_json()
    
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
                
                filename = f"{form_name.upper()}.pdf"
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
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for form_name in STATE_CONFIGS[state]['phase3']:
                generator = get_generator(state, form_name)
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name
                
                generator(data, tmp_path)
                
                filename = f"{form_name.upper()}.pdf"
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
