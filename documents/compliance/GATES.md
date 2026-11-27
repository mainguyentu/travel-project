# Quality gate mapping (XSTD-002-R001/R002, CORE-008)

Version: 0.1.0 | Date: 2026-11-27.
Gate owners, blocking-vs-advisory, thresholds: **Unresolved (U4)** —
no gate passes until the project owner assigns them.

## Stages

| Gate | Entry | Required evidence | Owner | Outcome |
|------|-------|-------------------|-------|---------|
| G1 change review | PR opened | requirement IDs mapped, diff inspection | Unassigned (U4) | approve / request changes |
| G2 automated checks | G1 pass | `scripts/ci.ps1` + backend `pytest -q` + frontend `php artisan test`, contract evidence B1..B10 | Unassigned (U4) | pass / fail |
| G3 release decision | G2 pass | TPL-001 checklist copy, rollback plan (`backend/docs/DEPLOYMENT_RUNBOOK.md`), artifact identity | Project owner | ship / hold |

## Requirement → gate trace (sample; full trace pending)

- BSTD-004-R001/R002/R004/R009, XSTD-001-R002/R006 → G1+G2 (`BE-API-0.1.0.md`, contract tests).
- BSTD-008-R001/R003 → G2 (`BSTD-008-R001-R003-2026-11-27.md` + pytest).
- BSTD-003-R002/R004 → G1+G2 (Alembic review + migration tests).
- FSTD-004/005/006 → G1+G2 (`FE-0.1.0.md`, `FSTD-006-R001-2026-11-27.md`).
- XSTD-001-R003/R008, XSTD-002-R007 → G2+G3 (integration + failure/retry checks — open).
- Security/privacy (BSTD-007, XSTD-002-R008) → G3 owner review — open (U1).

## Blocking rule (XSTD-002-R004)

A gate MUST NOT pass when a required blocking criterion failed or is unassessed;
exceptions only per CORE-007 and visible in the decision record.
