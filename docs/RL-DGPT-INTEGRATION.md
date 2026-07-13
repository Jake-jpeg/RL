# RL ↔ DivorceGPT Integration

DivorceGPT (branch `divorcegpt-2-online-staging`) calls this service
SERVER-TO-SERVER only, from `src/lib/pdf-service/client.ts`:

- endpoint: `POST {PDF_SERVICE_URL}/generate/{state}/{form}`
- auth: `Authorization: Bearer {PDF_SERVICE_TOKEN}` (encrypted env both
  sides; no NEXT_PUBLIC variant exists; the browser never calls RL)
- Dgpt-side allowlist: nj/verification, nj/complaint, ny/ud1
- payload: deterministic mapping from attorney-confirmed intake answers
  (see Dgpt `docs/PDF-DATA-MAPPINGS.md`); no AI output enters the payload
- response contract: `application/pdf` with `%PDF-` magic (content-sniffed
  by the caller), SHA-256 computed and stored, one bounded retry on 5xx
  only, 60s timeout
- lifecycle on the Dgpt side: rendered PDF becomes a new document version
  in ATTORNEY_REVIEW_REQUIRED; separate exact-version attorney approval +
  hash-matched release; RL never changes matter state and never releases

RL responsibilities end at deterministic rendering. RL makes no legal
judgments, calls no AI, and holds no client database; each request is
stateless and its temp files are cleaned even on failure.
