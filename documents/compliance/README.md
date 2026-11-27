# Compliance evidence index (CORE-008)

Version: 0.1.0 | Date: 2026-11-27.
Default outcome for every applicable MUST: **Not assessed** until evidence is linked.

## Outcome legend (CORE-008 §1)

`Conforms` | `Does not conform` | `Exception approved` (≠ conformance, CORE-007)
| `Not assessed` | `Not applicable` (justified, CORE-005).

## Track status

| Track | Requirements | Assessed | Evidence location |
|-------|--------------|----------|-------------------|
| Backend BSTD-001..013 (90 reqs) | 76 MUST/MUST NOT + 14 SHOULD | 0 | this folder (pending T7) |
| Frontend FSTD-001..008 (46 reqs) | ~42 MUST/MUST NOT + 4 SHOULD | 0 | this folder (pending T8) |
| Cross-cutting XSTD-001 (9) + XSTD-002 (10) | 19 MUST | 2 partial* | `contracts/BOUNDARIES.md` |
| Governance CORE-001..009 | process | profile+AGENTS.md done | `STANDARDS-PROFILE.md`, `AGENTS.md` |

\*Partial: XSTD-001-R001/R002 have a boundary inventory (B1..B10) but owners
unresolved (U4) and versioned contracts T5/T6 not yet written — still Not assessed.

## Evidence minimum per claim (CORE-008 §3)

Requirement ID + doc/version; system/component + scope; date + assessor/role +
method + result; artifact location + access/retention; conditions, tool/version,
limitations, linked defects. No secrets in evidence.

## Next

T5 backend contract → enables producer-side assessment (BSTD-004).
T6 frontend inventory → enables consumer-side assessment (FSTD-004/005, XSTD-001-R003/R005).
T9 gate mapping → XSTD-002-R001/R002 (owners pending U4).
