---
name: 📋 Provenance & Review Policy
about: Questions about AI assistance, code review, or repository polish
title: "[PROVENANCE] "
labels: ["documentation", "provenance"]
assignees: ["guidopardi"]
---

## Response to "Too Polished" Feedback

We've heard the feedback that the repo looks "too polished for a first release."
That's by design:

- We used **pre‑commit** (Black/Ruff/Docformatter) to make formatting uniform.
- We prioritized **security utilities** (safe I/O, atomic writes, size/time caps) so the preview is safe to test.
- We do use **AI assistance for boilerplate**, but **everything is human‑reviewed** and checked by CI. See [PROVENANCE.md](../../PROVENANCE.md).

This repo is **spec‑first and sim‑only**. We intentionally stub crypto/upload to avoid a false sense of security.
Partnerships, training lanes (Psyche), and compute subsidies live in **ShagaDAO/dgn** to keep boundaries clear.

## Key Documents

- **[PROVENANCE.md](../../PROVENANCE.md)** - AI assistance policy and human review process
- **[docs/adr/0001-preview-secure-posture.md](../../docs/adr/0001-preview-secure-posture.md)** - Why security came first
- **[CODEOWNERS](../../CODEOWNERS)** - Human review accountability
- **[SECURITY.md](../../SECURITY.md)** - External audit log

## Questions?

If you have specific concerns about:
- **AI assistance**: See commit trailers and PROVENANCE.md
- **Security architecture**: Check the ADR and SECURITY.md audit log  
- **Code review process**: All PRs require human sign-off per CODEOWNERS
- **Operational details**: Those live in ShagaDAO/dgn (GAP stays spec-focused) 