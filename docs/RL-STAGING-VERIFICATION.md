# RL Staging Branch — Verification Record

Branch `divorcegpt-2-pdf-staging-auth`. SYNTHETIC DATA ONLY.
Not deployed; not merged; awaiting the operator's manual push.

## Where each validation ran (honest scoping)

Claude's cloud sandbox blocks all container registries (docker.io, ecr,
ghcr) and debian mirrors, so the LITERAL `docker build` of the unmodified
Dockerfile (FROM python:3.11-slim + libreoffice apt install) cannot run
there, and the Cowork device VM has no network at all. Everything else ran
faithfully in the sandbox's own Docker daemon (v29.4.3) on the exact
branch commit, using a Python 3.11.15 base image synthesized from the
sandbox rootfs (registries unreachable):

| Validation | Where | Result |
|---|---|---|
| Full pytest suite in an ISOLATED python 3.11 container, declared requirements only (`requirements.txt` + `requirements-dev.txt`) | sandbox Docker | 13/13 before repair · 14/14 after |
| Live containerized service (gunicorn, 2 workers, timeout 120, port 18080, `PDF_SERVICE_TOKEN=synthetic-local-test-token`) | sandbox Docker | all checks below |
| `GET /health` without token | container | 200; states + auth_required only — no credentials, client data, or filesystem paths |
| Generation without token / wrong token / non-Bearer scheme | container | 401 / 401 / 401, identical information-free body |
| NJ verification with valid token (synthetic payload) | container | 200, 3,889 bytes, starts `%PDF-` |
| NY UD-1 with valid token (synthetic payload) | container | 200, 3,320 bytes, starts `%PDF-` |
| Unsupported state `zz` / unsupported form | container | 400 / 400 |
| Malformed JSON / oversized body (300KB > 256KB cap) | container | 400 / 413 |
| Bearer token occurrences in container logs | container | 0 |
| Synthetic payload names/addresses in container logs | container | 0 |
| Orphaned `/tmp/*.pdf` after all requests | container | 0 |
| Container stopped and removed after testing | container | yes |
| `docker build -t divorcegpt-rl-staging:test .` (unmodified Dockerfile) | **OPERATOR machine (Docker Desktop)** | pending — see command below |

The Dockerfile itself is UNCHANGED from `main` (the branch diff touches
only `app.py`, `requirements-dev.txt`, `tests/test_auth.py`, `docs/`), and
the same Dockerfile builds the currently-running production RL service —
build risk is limited to the operator confirmation:

```bat
cd %USERPROFILE%\Desktop\RL
docker build -t divorcegpt-rl-staging:test .
docker run --rm -p 18080:8080 -e PDF_SERVICE_TOKEN=synthetic-local-test-token divorcegpt-rl-staging:test
```

## Repair log

**R1 — temp-file leak on generator failure.**
`generate_pdf_response` and the three package loops created a
`NamedTemporaryFile` and unlinked it only on the success path; a generator
exception after file creation orphaned the temp file (the 500 path).
Fixed with try/finally around generate+read in all four sites so cleanup
is guaranteed. Regression test:
`test_generator_failure_returns_500_and_cleans_temp_files` (forces a
crashing generator; asserts 500, generic error body, and zero new
temp files). Full suite re-run in the isolated container after the
repair: 14/14.

No other requirement failed; no other code was changed. No court-form
substance was modified.
