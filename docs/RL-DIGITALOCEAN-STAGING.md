# RL DigitalOcean Staging (dgpt-pdf-staging)

Isolated staging app — the live Goldfish RL app is NOT touched.

- Source: GitHub `Jake-jpeg/RL`, branch `divorcegpt-2-pdf-staging-auth`
- Deploy-on-push: OFF (manual deploys only)
- Build: repository `Dockerfile` (python:3.11-slim + libreoffice-writer +
  gunicorn :8080) — unchanged from main
- Domain: DigitalOcean-generated only; divorcegpt.com is not attached
- Instance: 1× apps-s-1vcpu-1gb (stateless; horizontal scaling is fine for
  RL itself, but the paired Dgpt staging app is single-instance)
- Health check: `GET /health` (open; secret-free)

Environment variables (encrypted where secret):

| Var | Type | Value |
|---|---|---|
| PDF_SERVICE_TOKEN | SECRET | same value as the Dgpt staging app |
| APP_STAGE | plain | `staging` |
| RATE_LIMIT_MAX / RATE_LIMIT_WINDOW_S | plain, optional | defaults 30 / 60 |
| MAX_REQUEST_BYTES | plain, optional | default 262144 |

Post-deploy verification: `GET /health` shows `auth_required: true` and
`app_stage: "staging"`; unauthenticated and wrong-token generation
requests return 401; a valid-token synthetic NJ request returns a `%PDF-`
document. The paired Dgpt staging acceptance run
(`scripts/staging-acceptance.mjs` in the Dgpt repo) exercises all of this
end-to-end. SYNTHETIC DATA ONLY — not approved for live client use.
