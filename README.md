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
│   │   ├── generate_ud4.py
│   │   ├── generate_ud5.py
│   │   ├── generate_ud6.py
│   │   ├── generate_ud7.py
│   │   ├── generate_ud9.py
│   │   ├── generate_ud10.py
│   │   ├── generate_ud11.py
│   │   ├── generate_ud12.py
│   │   ├── generate_ud14.py
│   │   └── generate_ud15.py
│   └── nevada/              # Coming soon
│       └── ...
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
# New York UD-6
POST /generate/ny/ud6

# New York Phase 2 Package
POST /generate/ny/phase2-package

# Nevada (future)
POST /generate/nv/complaint
```

### Legacy Routes (Backward Compatible)
For existing frontend compatibility, these routes still work:
```
POST /generate/ud6        # Routes to NY
POST /generate/phase2-package  # Routes to NY
```

## Supported States

- **ny** (New York) - Full uncontested divorce packet
- **nv** (Nevada) - Coming soon
- **ca** (California) - Planned

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
- **ReportLab** - PDF generation
- **Flask-CORS** - Cross-origin requests
- **Docker** - Containerization

## Frontend Integration

```typescript
// Old way (still works)
const response = await fetch(`${PDF_SERVICE_URL}/generate/ud6`, {...})

// New way (state-specific)
const response = await fetch(`${PDF_SERVICE_URL}/generate/ny/ud6`, {...})
```

## Cost Efficiency

**One app, all states:** $5/month total
- Handles NY, NV, CA, etc. from single deployment
- Scales horizontally as needed
- State-specific logic isolated in folders

---

**Maintained by:** JGS Legal Services
**License:** Proprietary
