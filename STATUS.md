# GAP Project Status

## Component Readiness

| Component                | Purpose                     | Status       | Notes |
|--------------------------|-----------------------------|--------------|-------|
| **Spec (v0.2.0)**       | Canonical data format       | ✅ **Stable**     | SemVer; breaking changes will bump minor |
| **Validator (Python)**  | CLI schemas + QA checks     | ✅ **Usable**     | `python3 tools/validate.py samples/` |
| **Sample dataset**       | Tiny, synthetic             | ✅ **Included**   | 100MB reference + basic samples |
| **gap-agent (uploader)** | Capture + encrypt + upload  | 🟠 **Sim only**  | No network/crypto; prints plan and exits |
| **Crypto module**        | Keygen + AES-GCM            | 🔴 **Stub**       | Placeholder functions intentionally fail |
| **Verifier**             | Integrity checks            | 🔴 **Stub**       | Planned for production release |
| **S3/HTTP upload**       | Transport                   | 🔴 **Stub**       | Planned for production release |
| **Security contact**     | Vulnerability intake        | ✅ **Added**      | See SECURITY.md |

## What Works Today

✅ **GAP v0.2 Specification** - Complete, production-ready data format  
✅ **JSON Schemas** - Formal validation for meta.json, manifests, receipts  
✅ **Validator CLI** - Quality acceptance tests, profile validation  
✅ **Sample Data** - 100MB Star Atlas reference + basic examples  
✅ **Documentation** - API contracts, anti-sybil strategy, data cards  

## What's Simulation-Only

🟠 **gap-agent CLI** - Prints encryption/upload plans but performs no actual network operations  
🟠 **Packaging** - Creates correct file structures but no real compression  
🟠 **Anti-sybil detection** - Algorithms implemented but not connected to production systems  

## What's Intentionally Stubbed

🔴 **Encryption (crypto.py)** - Functions raise `NotImplementedError` with links to STATUS.md  
🔴 **Upload (uploader.py)** - No S3 credentials, no network calls  
🔴 **Verification (verifier.py)** - Receipt validation stubbed  

## Preview Limitations

- **gap-agent requires `--sim-mode`** flag to acknowledge preview status
- **No production credentials** - uploads will fail safely with clear error messages  
- **Crypto operations fail fast** - no silent encryption failures or false security
- **Sample video file** downloaded via script, not included in repo

## Roadmap to Production

**Phase 1 (Q4 2024):** Real crypto implementation, S3 upload, verification  
**Phase 2 (Q1 2025):** Production deployment, allowlist onboarding  
**Phase 3 (Q2 2025):** Public data contributions, HF integration  

## For Auditors

This preview intentionally separates **specification readiness** from **implementation completeness**.

- ✅ **Evaluate the spec:** Complete, tested, ready for partner integration
- ✅ **Test the validator:** Production-quality validation of GAP data
- 🟠 **Try gap-agent:** Simulation only - shows structure, doesn't perform operations
- 🔴 **Don't expect crypto/upload:** Designed to fail safely with clear messages

**Questions?** See [CONTRIBUTING.md](CONTRIBUTING.md) for what types of contributions we're accepting in preview. 