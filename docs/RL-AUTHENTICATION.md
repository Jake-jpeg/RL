# RL Service Authentication

Every `/generate/*` path — state routes, phase packages, and the legacy
`/generate/ud*` routes — requires:

    Authorization: Bearer <PDF_SERVICE_TOKEN>

Properties (all regression-tested in `tests/test_auth.py`):

- Constant-time comparison (`hmac.compare_digest`); no timing oracle.
- Missing, malformed (non-Bearer), and incorrect tokens all receive the
  SAME information-free 401 `{"error":"Unauthorized"}` — no hint whether
  a token was close, malformed, or absent.
- The token is never logged, never echoed in any error, and never appears
  in `/health`.
- Unset `PDF_SERVICE_TOKEN` ⇒ the service FAILS CLOSED: every generation
  request answers 503; it never runs open.
- CORS is a browser courtesy only and is NOT authentication; the intended
  caller is the DivorceGPT backend server-to-server. Browsers never hold
  the token.
- `/health` stays open (uptime checks) and reveals only service name,
  state list, `auth_required`, and `app_stage` — no credentials, no client
  data, no filesystem paths.

Supporting hardening: 256KB request cap (413), malformed/non-object JSON
⇒ 400 (never 500), explicit state/form allowlists before any dynamic
import (generator modules resolve ONLY from the hardcoded STATE_CONFIGS
map, never from raw request values), filenames sanitized to
[A-Za-z0-9_-], per-source fixed-window rate limit (defaults 30/60s),
guaranteed temp-file cleanup including generator-crash paths.

Token rotation: set the same new value in both apps' encrypted env vars
(RL and the DivorceGPT backend) and redeploy; there is no cached state.
