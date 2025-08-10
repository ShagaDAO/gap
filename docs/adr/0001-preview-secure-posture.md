# ADR 0001 – Preview‑Secure Posture & Sim‑Only Agent

- **Date**: 2025-02-05
- **Status**: Accepted
- **Deciders**: @guidopardi
- **Technical Story**: GAP needs public audit-friendly spec and validator without misleading users about crypto/upload capabilities

## Context

We need a public, audit‑friendly spec and validator for GAP. Shipping incomplete crypto/upload code risks misleading users about security guarantees. The preview must be safe for public testing while clearly communicating limitations.

## Decision

- Keep repo **spec‑first** with a **simulation‑only** agent.
- Stub crypto/upload/verify to hard‑fail with clear errors pointing to STATUS.md.
- Add safe I/O, atomic writes, archive limits early to protect reviewers and the HF Space.
- Prioritize security utilities first to make the preview genuinely safe for public use.

## Rationale

1. **Clear boundaries**: Separate specification (ready) from implementation (preview)
2. **Safety first**: Real security measures for what we do implement
3. **No false promises**: Hard failures better than silent failures for crypto
4. **Audit-friendly**: External reviewers can focus on spec and validation logic

## Consequences

### Positive
- Security looks "mature" for a preview; this is intentional and tool‑driven
- Clear separation of concerns between GAP spec and operational deployment
- Safe for public testing and community contributions
- Honest about limitations while demonstrating architectural patterns

### Negative
- May appear "over-engineered" for a preview to some observers
- Requires clear communication about what is/isn't production-ready
- Operational and partnership docs must live outside this repo (see ShagaDAO/dgn)

## Compliance

This decision aligns with:
- **Security-first development**: Implement safety measures before features
- **Transparency**: Clear documentation of what works vs. what's stubbed
- **Community safety**: Protect public demo users and contributors 