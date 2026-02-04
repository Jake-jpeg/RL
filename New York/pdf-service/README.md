# DivorceGPT PDF Microservice

Python Flask API that generates court-compliant NY divorce forms using ReportLab.

## Deployment on DigitalOcean

1. Create a new App in DigitalOcean App Platform
2. Connect this repository (or upload as a folder)
3. DigitalOcean will auto-detect the Dockerfile
4. Set HTTP port to 8080
5. Deploy

## Environment Variables

None required - all data comes from API requests.

## Endpoints

### Individual Forms

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate/ud4` | POST | DRL §253 Removal of Barriers |
| `/generate/ud5` | POST | Affirmation of Regularity |
| `/generate/ud6` | POST | Affidavit of Plaintiff |
| `/generate/ud7` | POST | Affidavit of Defendant |
| `/generate/ud9` | POST | Note of Issue |
| `/generate/ud10` | POST | Findings of Fact |
| `/generate/ud11` | POST | Judgment of Divorce |
| `/generate/ud12` | POST | Part 130 Certification |
| `/generate/ud14` | POST | Notice of Entry |
| `/generate/ud15` | POST | Affidavit of Service |

### Packages

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate/phase2-package` | POST | All Phase 2 forms as ZIP |
| `/generate/phase3-package` | POST | All Phase 3 forms as ZIP |

### Health Check

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |

## Request Format

All POST endpoints expect JSON with form data:

```json
{
  "plaintiffName": "Jane Doe",
  "defendantName": "John Doe",
  "county": "New York",
  "indexNumber": "12345/2026",
  "plaintiffAddress": "123 Main St, New York, NY 10001",
  "defendantAddress": "456 Oak Ave, Brooklyn, NY 11201",
  "marriageDate": "June 15, 2020",
  "marriageCity": "Brooklyn",
  "marriageState": "New York",
  "religiousCeremony": false
}
```

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Service runs at http://localhost:8080

## CORS

Configured to allow requests from:
- localhost:3000 (local dev)
- *.ondigitalocean.app (staging)
- divorcegpt.com (production)
