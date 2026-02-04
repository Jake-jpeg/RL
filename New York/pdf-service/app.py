#!/usr/bin/env python3
"""
DivorceGPT PDF Microservice
============================

Flask API that generates court-compliant divorce forms using ReportLab.
Deployed separately from the Next.js frontend.

Endpoints:
- POST /generate/ud4  - DRL §253 Removal of Barriers (religious ceremonies)
- POST /generate/ud5  - Affirmation of Regularity
- POST /generate/ud6  - Affidavit of Plaintiff
- POST /generate/ud7  - Affidavit of Defendant
- POST /generate/ud9  - Note of Issue
- POST /generate/ud10 - Findings of Fact and Conclusions of Law
- POST /generate/ud11 - Judgment of Divorce
- POST /generate/ud12 - Part 130 Certification
- POST /generate/ud14 - Notice of Entry (Phase 3)
- POST /generate/ud15 - Affidavit of Service by Mail (Phase 3)
- POST /generate/phase2-package - All Phase 2 forms as ZIP
- POST /generate/phase3-package - All Phase 3 forms as ZIP
- GET  /health - Health check
"""

import os
import io
import tempfile
import zipfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Import generators
from generate_ud4 import generate_ud4
from generate_ud5 import generate_ud5
from generate_ud6 import generate_ud6
from generate_ud7 import generate_ud7
from generate_ud9 import generate_ud9
from generate_ud10 import generate_ud10
from generate_ud11 import generate_ud11
from generate_ud12 import generate_ud12
from generate_ud14 import generate_ud14
from generate_ud15 import generate_ud15

app = Flask(__name__)

# CORS - allow requests from your frontend
CORS(app, origins=[
    "http://localhost:3000",
    "https://squid-app-zsiqz.ondigitalocean.app",
    "https://goldfish-app-92wun.ondigitalocean.app",
    "https://divorcegpt.com",
    "https://www.divorcegpt.com",
], supports_credentials=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for DigitalOcean."""
    return jsonify({"status": "healthy", "service": "divorcegpt-pdf"})


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


@app.route('/generate/ud4', methods=['POST'])
def gen_ud4():
    """Generate UD-4 (DRL §253 Removal of Barriers)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud4, data, f"UD-4_Barriers_{plaintiff}.pdf")


@app.route('/generate/ud5', methods=['POST'])
def gen_ud5():
    """Generate UD-5 (Affirmation of Regularity)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud5, data, f"UD-5_Affirmation_{plaintiff}.pdf")


@app.route('/generate/ud6', methods=['POST'])
def gen_ud6():
    """Generate UD-6 (Affidavit of Plaintiff)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud6, data, f"UD-6_Plaintiff_Affidavit_{plaintiff}.pdf")


@app.route('/generate/ud7', methods=['POST'])
def gen_ud7():
    """Generate UD-7 (Affidavit of Defendant)."""
    data = request.get_json()
    defendant = data.get('defendantName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud7, data, f"UD-7_Defendant_Affidavit_{defendant}.pdf")


@app.route('/generate/ud9', methods=['POST'])
def gen_ud9():
    """Generate UD-9 (Note of Issue)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud9, data, f"UD-9_Note_of_Issue_{plaintiff}.pdf")


@app.route('/generate/ud10', methods=['POST'])
def gen_ud10():
    """Generate UD-10 (Findings of Fact and Conclusions of Law)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud10, data, f"UD-10_Findings_{plaintiff}.pdf")


@app.route('/generate/ud11', methods=['POST'])
def gen_ud11():
    """Generate UD-11 (Judgment of Divorce)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud11, data, f"UD-11_Judgment_{plaintiff}.pdf")


@app.route('/generate/ud12', methods=['POST'])
def gen_ud12():
    """Generate UD-12 (Part 130 Certification)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud12, data, f"UD-12_Certification_{plaintiff}.pdf")


@app.route('/generate/ud14', methods=['POST'])
def gen_ud14():
    """Generate UD-14 (Notice of Entry)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud14, data, f"UD-14_Notice_of_Entry_{plaintiff}.pdf")


@app.route('/generate/ud15', methods=['POST'])
def gen_ud15():
    """Generate UD-15 (Affidavit of Service by Mail)."""
    data = request.get_json()
    plaintiff = data.get('plaintiffName', 'Document').replace(' ', '_')
    return generate_pdf_response(generate_ud15, data, f"UD-15_Service_Affidavit_{plaintiff}.pdf")


@app.route('/generate/phase2-package', methods=['POST'])
def gen_phase2_package():
    """Generate all Phase 2 forms as a ZIP file."""
    data = request.get_json()
    
    try:
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            forms = [
                ('UD-5_Affirmation_of_Regularity.pdf', generate_ud5),
                ('UD-6_Affidavit_of_Plaintiff.pdf', generate_ud6),
                ('UD-7_Affidavit_of_Defendant.pdf', generate_ud7),
                ('UD-9_Note_of_Issue.pdf', generate_ud9),
                ('UD-10_Findings_of_Fact.pdf', generate_ud10),
                ('UD-11_Judgment_of_Divorce.pdf', generate_ud11),
                ('UD-12_Part_130_Certification.pdf', generate_ud12),
            ]
            
            # Add UD-4 if religious ceremony
            if data.get('religiousCeremony', False):
                forms.insert(0, ('UD-4_Barriers_to_Remarriage.pdf', generate_ud4))
            
            for filename, generator in forms:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name
                
                generator(data, tmp_path)
                
                with open(tmp_path, 'rb') as f:
                    zf.writestr(filename, f.read())
                
                os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        plaintiff = data.get('plaintiffName', 'DivorceGPT').replace(' ', '_')
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"Phase2_Filing_Package_{plaintiff}.zip"
        )
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Phase 2 package error: {e}")
        return jsonify({"error": "Failed to generate package"}), 500


@app.route('/generate/phase3-package', methods=['POST'])
def gen_phase3_package():
    """Generate all Phase 3 forms as a ZIP file."""
    data = request.get_json()
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            forms = [
                ('UD-14_Notice_of_Entry.pdf', generate_ud14),
                ('UD-15_Affidavit_of_Service.pdf', generate_ud15),
            ]
            
            for filename, generator in forms:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name
                
                generator(data, tmp_path)
                
                with open(tmp_path, 'rb') as f:
                    zf.writestr(filename, f.read())
                
                os.unlink(tmp_path)
        
        zip_buffer.seek(0)
        
        plaintiff = data.get('plaintiffName', 'DivorceGPT').replace(' ', '_')
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"Phase3_Final_Forms_{plaintiff}.zip"
        )
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Phase 3 package error: {e}")
        return jsonify({"error": "Failed to generate package"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
