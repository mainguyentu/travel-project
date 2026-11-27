---
id: TRAVEL-PROFILE-001
title: Travel Project Standards Profile (WDES 0.1.0)
status: Approved
version: 0.1.0
owner: Project owner
approved_by: Project owner (user approval recorded 2026-11-26)
created: 2026-11-27
updated: 2026-11-27
applies_to: [travel-project backend, frontend, gateway, delivery pipeline]
normative: false
compatible_releases: ['0.1.0']
---

# Travel Project Standards Profile

Adopts `documents/web-development-engineering-standards` version **0.1.0**
(All tracks Approved 2026-11-26: Governance CORE, Backend BSTD-001..013,
Frontend FSTD-001..008, Cross-cutting XSTD-001/002).

## 1. Scope

- In scope: `backend/` (FastAPI monolith + 5 service profiles + worker),
  `frontend/` (Laravel Blade SSR + ApiClient), `gateway/` + `nginx.conf`,
  `docker-compose*.yml`, `.github/workflows`, `design-docs/`.
- Out of scope (Not applicable, CORE-005): `figma-design/` (static mockups),
  `graphify-out/` (generated index), `documents/web-development-engineering-standards`
  (upstream standard, read-only — MUST NOT edit to claim conformance).
- Technology neutrality (CORE-002 P9): project keeps FastAPI / Laravel /
  Nginx / Postgres / Redis / Kafka / Elasticsearch. WDES does not force a stack change.

## 2. Unresolved decisions (MUST NOT invent — CORE-009)

| # | Decision left open by WDES | Travel project status |
|---|----------------------------|-----------------------|
| U1 | Security assurance level / profile (BSTD-007-R009) | **Resolved 2026-11-27** — ASVS L2 (owner decision; assessment in `U1-ASVS-L2-assessment-2026-11-27.md`) |
| U2 | Accessibility conformance target (FSTD-002-R001) | **Resolved 2026-11-27** — WCAG 2.2 AA; audit `U2-a11y-audit-2026-11-27.md` |
| U3 | Supported viewports / performance targets (FSTD-003-R001, FSTD-007-R001) | **Resolved 2026-11-27** — 360/768/1280 + LCP/INP/CLS; `U3-viewport-perf-2026-11-27.md` |
| U4 | Quality gate owners, blocking vs advisory, thresholds (XSTD-002) | **Resolved 2026-11-27** — see `documents/compliance/U4-U5-resolution-2026-11-27.md` §U4 |
| U5 | Contract-change approval authority, compatibility window (XSTD-001-R007) | **Resolved 2026-11-27** — see `documents/compliance/U4-U5-resolution-2026-11-27.md` §U5 |
| U6 | Backup RPO/RTO, retention durations, on-call/incident owner (BSTD-003-R008, BSTD-013) | **Resolved 2026-11-27** — RPO 24h, retention 7 bản, on-call owner; script `scripts/backup.sh` + RUNBOOK §5/§5b |
| U7 | Evidence retention / audit cadence (CORE-001/006) | **Resolved 2026-11-27** — giữ 12 tháng, audit 6 tháng/lần; `U7-retention-2026-11-27.md` |

## 3. Applicability

- All Approved MUST requirements are **Applicable** unless a task record
  justifies Not applicable (CORE-005) or an Exception (CORE-007).
- SHOULD deviations need a recorded rationale; MAY needs no record.
- Current overall assessment per CORE-008: **Not assessed** for every
  requirement until evidence is linked in `documents/compliance/`.

## 4. Verification approach

- Authorized checks only: file inspection, `docker compose config`,
  `pytest -q` (backend), `php artisan test` (frontend) — run explicitly per task,
  report results + limitations. No secret is embedded in evidence (CORE-008).
- Human review required for: architecture decisions, accessibility interaction,
  release decisions (CORE-002 P7).

## 5. Reassessment triggers

Material change of boundary, data/users, exposure, architecture, delivery path,
ops ownership, or external obligation (CORE-005) → update this profile.

## Change history

- 0.1.0 (2026-11-27): Initial profile; all targets/gates recorded as unresolved.
