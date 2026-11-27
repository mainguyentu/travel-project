# Task plan — WDES restructuring (travel-project, WDES 0.1.0)

Profile: `documents/STANDARDS-PROFILE.md`. Unresolved U1..U7 stay unresolved.
Rule: smallest coherent change; upstream `web-development-engineering-standards/` read-only.

## Done

- [x] T1 — Project standards profile (`documents/STANDARDS-PROFILE.md`)
- [x] T2 — Agent entry point (`AGENTS.md`, CORE-009 §4)

## Next (in order, one at a time)

- [ ] T3 — Boundary + contract inventory (`documents/contracts/BOUNDARIES.md`)
  maps XSTD-001-R001/R002: producer/consumer/owner per material boundary,
  contract version + evidence location. Inspection only.
- [ ] T4 — Compliance skeleton (`documents/compliance/README.md` + per-track index)
  maps CORE-008 §1/§4, XSTD-002-R002: outcomes default **Not assessed**.
- [ ] T5 — Backend contract doc v0.1.0 (`documents/contracts/BE-API-0.1.0.md`)
  maps BSTD-004-R001/R002/R004/R007/R009 + XSTD-001-R006: operations, auth,
  errors, pagination, compatibility. Derived from code + `backend/docs/API_REFERENCE.md`.
- [ ] T6 — Frontend inventory (`documents/contracts/FE-0.1.0.md`)
  maps FSTD-004-R001/R003, FSTD-005-R001, XSTD-001-R005: routes, ApiClient,
  state ownership, identity flow. No behavior change.
- [x] T7 — Backend code gaps, smallest fixes first (BSTD-008-R001/R003: error redaction;
  BSTD-004-R005: pagination bounds — verified already bounded `le=100` on all
  list endpoints; validation-error `input`/`ctx` redaction applied in
  `backend/app/app_factory.py` + evidence `documents/compliance/BSTD-008-R001-R003-2026-11-27.md`).
- [x] T8 — Frontend code gaps (FSTD-006-R001: `toSafeUrl()` allow-list `http(s)://`+`/`
  for image/map URLs in `resources/js/destination-modal.js` + evidence
  `documents/compliance/FSTD-006-R001-2026-11-27.md`; forms already carry
  labels/field errors/server-side FormRequests — per-form verification pending).
- [x] T9 — Gate mapping (`documents/compliance/GATES.md`, XSTD-002-R001/R002:
  stages, evidence, owners = unresolved U4 until assigned).

Each step reports: changed files, requirement coverage, verification
(run / not run + results + limitations), unresolved items.
