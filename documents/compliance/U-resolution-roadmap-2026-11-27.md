# Lộ trình giải quyết U1..U7 (điều kiện gỡ G3 HOLD)

Ngày: 2026-11-27 | G3: **HOLD** cho đến khi U1..U7 đóng + tính năng cần thiết xong.
Mọi mục cần **owner chốt số liệu/ngưỡng** — AI không tự quyết thay (CORE-009).

## U1 — Security assurance level (BSTD-007-R009)

- **RESOLVED 2026-11-27** — owner chốt **ASVS L2**; assessment:
  `documents/compliance/U1-ASVS-L2-assessment-2026-11-27.md`.
  Fix code F1: password register min 6 → 8 (BE + FE). F2/F3/G2 → checklist
  deploy RUNBOOK §5b. Gap G1 (quên/reset password) thuộc tính năng bỏ ngõ.

## U2 — Accessibility target (FSTD-002-R001)

- Việc cần: chọn WCAG level (A/AA/AAA), audit public pages (keyboard, contrast, alt, form labels), fix.
- Đề xuất: **WCAG 2.2 AA** cho public; admin nội bộ theo sau.
- UX public hiện tại đã có: label/input, alt ảnh, tương phản Ocean/dark — cần audit chính thức.

## U3 — Viewports / performance targets (FSTD-003-R001, FSTD-007-R001)

- Việc cần: chốt breakpoints + Core Web Vitals mục tiêu (LCP/INP/CLS), đo trên stack thật.
- Đề xuất: mobile 360px / tablet 768px / desktop 1280px (hiện CSS đã cover 768px + 900px admin);
  LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 ở trang home/destinations qua gateway.
- Cần owner chốt: có đo lab (Lighthouse CI) hay RUM production.

## U4 — Quality gate owners / blocking vs advisory (XSTD-002)

- **RESOLVED 2026-11-27** — xem `U4-U5-resolution-2026-11-27.md` §U4.
  Owner mặc định: project owner; blocking = pytest/phpunit/compose config
  (verified `docker compose config` exit 0); advisory = pip-audit/Trivy.
  Branch protection bật thủ công trên GitHub (backlog owner).

## U5 — Contract-change approval + compatibility window (XSTD-001-R007)

- **RESOLVED 2026-11-27** — xem `U4-U5-resolution-2026-11-27.md` §U5.
  Owner duyệt mọi đổi contract; window 1 minor; breaking chỉ ở major.

## U6 — Backup RPO/RTO, retention, on-call (BSTD-003-R008, BSTD-013)

- **RESOLVED 2026-11-27** — RPO 24h, retention 7 bản, on-call project owner;
  script `scripts/backup.sh` + RUNBOOK §5/§5b (kèm checklist deploy TLS/secrets).

## U7 — Evidence retention / audit cadence (CORE-001/006)

- Việc cần: giữ evidence bao lâu, audit định kỳ mấy tháng/lần.
- Đề xuất: giữ báo cáo compliance + artifact CI **12 tháng**; audit lại khi
  đổi boundary/stack hoặc **6 tháng/lần**; `audit_logs` DB giữ theo U6 retention.

## Thứ tự đề xuất

1. ~~U4 + U5~~ ✅ done 2026-11-27.
2. ~~U1 + U6~~ ✅ done 2026-11-27 (U1 = ASVS L2).
3. ~~U3 → U2 → U7~~ ✅ done 2026-11-27.
   U3: `U3-viewport-perf-2026-11-27.md`; U2: `U2-a11y-audit-2026-11-27.md`;
   U7: `U7-retention-2026-11-27.md`.

**Tất cả U1..U7 RESOLVED. G3 vẫn HOLD theo quyết định owner (tính năng bỏ ngõ).**

---
**Owner cho ý kiến từng U (chốt số hoặc sửa đề xuất), tôi sẽ triển khai theo thứ tự trên.**
