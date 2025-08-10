# Security Policy

## Reporting Security Vulnerabilities

**We take security seriously.** If you discover a security vulnerability in GAP, please report it responsibly.

### Scope

This security policy covers:
- **GAP specification vulnerabilities** (bypass validation, forge manifests)
- **gap-agent tool vulnerabilities** (RCE, privilege escalation, data exfiltration)
- **Anti-sybil bypass techniques** (duplicate detection evasion)
- **Cryptographic issues** (encryption weaknesses, key derivation)

### What to Report

**High Priority:**
- Remote code execution in gap-agent tools
- Authentication bypass in upload verification
- Anti-sybil detection bypass methods
- Cryptographic weaknesses in envelope encryption
- Schema validation bypasses leading to malformed data

**Medium Priority:**
- Denial of service in validators
- Information disclosure from metadata
- Cache poisoning in duplicate detection

### How to Report

If you believe you've found a vulnerability, please use **GitHub Security Advisories** for this repository. We'll coordinate disclosure there.

**Please do not open public issues for security reports.**

**To report via GitHub Security Advisories:**
1. Go to the Security tab of this repository
2. Click "Report a vulnerability"
3. Fill out the advisory form with:
   - Detailed description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Suggested mitigation (if any)

### Response Timeline

- **24 hours:** Initial acknowledgment
- **7 days:** Preliminary assessment and triage
- **30 days:** Detailed investigation and fix development
- **90 days:** Coordinated disclosure (after fix deployment)

### Disclosure Policy

We follow **coordinated disclosure**:

1. **Private reporting period** (90 days maximum)
2. **Fix development and testing**
3. **Coordinated public disclosure** with credit to reporter
4. **CVE assignment** for significant vulnerabilities

### Security Considerations

**Known Limitations (Preview Status):**
- Crypto/upload/verifier are intentionally stubbed (sim-only)
- Public demo enforces hard file/time caps
- No cookies/session state → CSRF out of scope; requests must be explicit uploads
- Validator outputs may change between versions
- Upload credentials are allowlist-only (security through obscurity)
- Anti-sybil detection is in early testing phase

**Out of Scope:**
- DoS attacks on public HF Space or samples
- Social engineering attacks
- Vulnerabilities in third-party dependencies (report upstream)
- Issues in closed Shaga Node Core (separate security contact)

### Security Features

**Implemented:**
- ✅ Input validation with JSON schemas
- ✅ File integrity verification (SHA-256)
- ✅ Envelope encryption (X25519 + AES-GCM)
- ✅ Anti-sybil duplicate detection
- ✅ Secure receipt verification

**In Development:**
- ⏳ Challenge-response watermarking
- ⏳ Proof of Retrieval mechanisms
- ⏳ Hardware attestation for node registration

### Bug Bounty

Currently **no formal bug bounty program**. Security researchers will receive:
- Public acknowledgment in release notes
- CVE credit where applicable
- Consideration for future bug bounty programs

## External Audits & Reviews

| Date       | Commit  | Focus                       | Outcome                |
|------------|---------|----------------------------|------------------------|
| 2025-02-05 | HEAD    | Safe I/O, size caps, atomic writes | ✅ Provenance documented |
| 2025-02-05 | HEAD    | Schema‑first JSON validation | ✅ Passed              |
| 2025-02-05 | HEAD    | HF Space rate/time limits   | ✅ Passed              |

See [docs/adr/0001-preview-secure-posture.md](docs/adr/0001-preview-secure-posture.md) for our architectural security decisions.

## Dependency Security Notes

**CVE False Positives:**
- **CVE-2024-42992** (pandas): **REJECTED by NVD** - [withdrawn by CNA as "not a security issue"](https://nvd.nist.gov/vuln/detail/CVE-2024-42992)
- **CVE-2021-3918**: Affects **npm `json-schema`** package (JavaScript), **NOT** Python `jsonschema` library used here

Our locked dependencies (`requirements-preview.lock`) use current stable versions with no known security vulnerabilities.

---

**Thank you for helping keep GAP secure!** 