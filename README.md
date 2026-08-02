# DivorceGPT PDF Service - Multi-State

PDF generation microservice for DivorceGPT. Supports multiple states with state-specific divorce form generators.

## Structure

```
divorcegpt-pdf/
├── app.py                    # Flask API with state routing
├── Dockerfile                # Container configuration
├── requirements.txt          # Python dependencies
├── states/
│   ├── new_york/            # New York form generators
│   │   ├── generate_ud1.py  # Summons with Notice (Phase 1)
│   │   ├── generate_ud4.py  # Barriers to Remarriage (religious only)
│   │   ├── generate_ud5.py  # Affirmation of Regularity
│   │   ├── generate_ud6.py  # Plaintiff's Affirmation
│   │   ├── generate_ud7.py  # Defendant's Affirmation
│   │   ├── generate_ud9.py  # Note of Issue
│   │   ├── generate_ud10.py # Findings of Fact
│   │   ├── generate_ud11.py # Judgment of Divorce
│   │   ├── generate_ud12.py # Part 130 Certification
│   │   ├── generate_ud14.py # Notice of Entry (Phase 3)
│   │   └── generate_ud15.py # Affidavit of Service (Phase 3)
└── README.md
```

## API Endpoints

### Health Check
```
GET /health
```

### State-Specific Forms
```
POST /generate/{state}/{form}
POST /generate/{state}/phase2-package
POST /generate/{state}/phase3-package
```

**Examples:**
```bash
# New York UD-1
POST /generate/ny/ud1

# New York UD-6
POST /generate/ny/ud6

# New York Phase 2 Package
POST /generate/ny/phase2-package
```

### Legacy Routes (Backward Compatible)
For existing frontend compatibility, these routes still work:
```
POST /generate/ud1        # Routes to NY
POST /generate/ud6        # Routes to NY
POST /generate/phase2-package  # Routes to NY
```

## State Module Routing

Each state config has a `module` key that maps the short state code to the actual
directory name under `states/`:

```python
STATE_CONFIGS = {
    'ny': {
        'name': 'New York',
        'module': 'new_york',   # maps to states/new_york/
        'forms': { ... },
    },
}
```

This prevents the `states.ny.generate_ud6` import error — the actual import
path is `states.new_york.generate_ud6`.

## Supported States

- **ny** (New York) - Full uncontested divorce packet

## Adding a New State

1. Create state directory:
   ```bash
   mkdir states/your_state
   touch states/your_state/__init__.py
   ```

2. Add form generators:
   ```python
   # states/your_state/generate_complaint.py
   def generate_complaint(data, output_path):
       # Your PDF generation logic
       pass
   ```

3. Update `app.py` STATE_CONFIGS:
   ```python
   STATE_CONFIGS = {
       'ny': { ... },
       'your_state': {
           'name': 'Your State',
           'module': 'your_state',
           'forms': {
               'complaint': 'generate_complaint',
               'decree': 'generate_decree',
           },
       },
   }
   ```

4. Deploy - same app handles all states!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py

# Test endpoint
curl http://localhost:8080/health
```

## Deployment (Digital Ocean)

**App:** Goldfish
**Source Directory:** (blank or `/`)
**Dockerfile:** Auto-detected at root
**Port:** 8080

Single app deployment handles all states.

## Technology Stack

- **Flask** - REST API framework
- **ReportLab** - PDF generation (all forms, all states)
- **Flask-CORS** - Cross-origin requests
- **Docker** - Containerization

## Cost Efficiency

**One app, all states:** $5/month total
- Handles NY, NV, CA, etc. from single deployment
- Scales horizontally as needed
- State-specific logic isolated in folders

---

**Maintained by:** JGS Legal Services
**License:** Proprietary
