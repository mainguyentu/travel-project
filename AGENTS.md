# AGENTS.md — Travel Project

## Standards entry point (CORE-009)

- Upstream standard (read-only): `documents/web-development-engineering-standards/` v0.1.0.
- Project profile: `documents/STANDARDS-PROFILE.md` — scope, unresolved decisions U1..U7, verification approach.
- Compliance evidence: `documents/compliance/` (per-requirement assessments, CORE-008 outcomes).
- Contracts: `documents/contracts/` (versioned FE↔BE + service-to-service contracts, XSTD-001-R002).

## Operating rules for AI agents

1. Read this file + `documents/STANDARDS-PROFILE.md` before non-trivial tasks.
2. Map requirement IDs (BSTD/FSTD/XSTD/CORE) to planned changes + verification before editing.
3. Approved normative (`status: Approved`) only; `documents/...` upstream is read-only.
4. Smallest coherent change; preserve FastAPI/Laravel/Nginx stack (technology neutrality).
5. Run only authorized checks; report what ran / not run + results + limitations.
6. Record unresolved choices, missing evidence, conflicts; never invent policy, approval, or conformance.
7. MUST NOT weaken a MUST without a CORE-007 exception; SHOULD deviations need rationale.
8. Never expose secrets in docs/logs/summaries.

## Authorized verification commands

- File inspection (read/grep/glob).
- `docker compose config` (static compose validation, no secrets printed).
- Backend: `pytest -q` inside `backend/` (explicitly requested only).
- Frontend: `php artisan test` inside `frontend/` (explicitly requested only).

## Human accountability

AI output does not approve requirements, accept risk, grant exceptions, or replace
human review. Release/gate decisions and unresolved items U1..U7 need the project owner.
