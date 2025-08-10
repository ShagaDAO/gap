# Launch Materials - GAP v0.4.0-preview

**Draft materials for safe public preview launch**

## 🚀 GitHub Issue: Allowlist Onboarding

**Title:** Data Contribution Allowlist - Apply Here

**Body:**
```markdown
# 🎮 GAP Data Contribution Allowlist

**Status:** Invite-only during preview phase while we harden anti-sybil defenses.

## Quick Apply

📝 **[Apply Here: Allowlist Registration Form](https://forms.gle/YOUR_FORM_ID)**

## Why Allowlist?

During the preview phase, we're limiting data uploads to:
- Prevent fake/duplicate content during early development
- Ensure data quality for initial validation runs  
- Test anti-sybil detection with known-good contributors
- Build a trusted contributor community

## What You'll Get

✅ **Node credentials** (scoped, time-limited)  
✅ **Technical onboarding** session with our team  
✅ **Early access** to new tools and profiles  
✅ **Contributor recognition** in our Hall of Fame  
✅ **Research credit** if your data is used in papers  

## Requirements

**Hardware Minimums:**
- GPU: GTX 1060 / RX 580 or better
- CPU: 4+ cores for real-time encode  
- RAM: 16GB+ for buffering
- Storage: 100GB+ free space
- Network: 10 Mbps+ sustained upload

**Data Quality Standards:**
- ✅ Original gameplay footage (no re-encoded streams)
- ✅ Single-player sessions (privacy compliance)
- ✅ Clean captures (no overlays, notifications)
- ✅ Stable framerate (CFR enforced)
- ✅ Synchronized controls (±8ms alignment)

## Timeline

**Phase 0 (Now):** Strict allowlist with manual onboarding  
**Phase 1 (4-6 weeks):** Vouching system for trusted contributors  
**Phase 2 (8-12 weeks):** Automated gating with statistical verification  

## Questions?

Comment below or check our [Contributors Guide](CONTRIBUTORS.md) for details.
```

---

## 📢 Dev Announcement Post

**Title:** Introducing GAP (Preview): Open Standard for Gameplay Data

**Body:**
```markdown
# Introducing GAP (Preview): Open Standard for Gameplay Data

Today we're releasing **GAP v0.4.0-preview** - an open standard and toolkit for packaging time-aligned gameplay video + controls data.

## What's GAP?

GAP (Gameplay-Action Pairs) provides a **vendor-neutral specification** for ML-ready gameplay data:

- 📄 **Formal specification** with JSON schemas
- 🧰 **CLI tools** for packaging and upload (`gap-agent`) 
- 🔎 **Validators** with URI support (local, s3://, hf://)
- 🧪 **100MB sample** for testing and integration
- 🎮 **Interactive validator** on Hugging Face

## Architecture: Open Data Path

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Shaga Node  │───▶│ gap-agent   │───▶│ S3-compat   │
│ (closed)    │    │ (open)      │    │ Storage     │
└─────────────┘    └─────────────┘    └─────────────┘
```

**What's open:** Spec, packaging, validation, anti-sybil detection  
**What's closed:** Real-time capture, DRM, watermarking, PoR

## Quick Start

```bash
# Try the validator
cd samples/star-atlas_100mb/
./download.sh
python3 tools/validate.py --profile wayfarer-owl .

# Install the CLI
pip install ./packages/gap-agent

# Package your own data
gap pack video.mkv controls.jsonl --profile wayfarer-owl --encrypt
```

## Preview Status

⚠️ **This is a preview release:**
- APIs may change between versions
- Data uploads are invite-only (allowlist)
- Anti-sybil detection is in testing phase

## Key Features

**🛡️ Anti-Sybil Defense:**
- Perceptual hashing for duplicate video detection
- SimHash for control pattern similarity
- Risk scoring with configurable thresholds
- Local pre-checks before upload

**🔒 Security & Privacy:**
- Envelope encryption (X25519 + AES-GCM)
- Formal JSON schemas for validation
- Responsible disclosure policy
- Rights-clean sample data

**🤝 Partner-Friendly:**
- Locked API contracts for integration stability
- Transparent verification (same checks locally as server-side)
- Multiple storage backends (S3, R2, B2, MinIO)
- Profile system for partner-specific requirements

## Data Contributions

Currently **invite-only** while we test anti-sybil defenses.

🎯 **[Apply for allowlist access](GITHUB_ISSUE_LINK)**

**Requirements:**
- Original gameplay footage (no re-encoded streams)
- GPU: GTX 1060+ for real-time encoding
- Clean captures with synchronized controls

## Resources

- 📖 **[GitHub Repository](https://github.com/ShagaDAO/gap)**
- 🎮 **[Interactive Validator](https://huggingface.co/spaces/Shaga/gap-explorer)**
- 📊 **[Sample Dataset](https://huggingface.co/datasets/Shaga/GAP-samples)**
- 📋 **[Contributors Guide](https://github.com/ShagaDAO/gap/blob/main/CONTRIBUTORS.md)**

## What's Next

**v0.5.x roadmap:**
- Additional game profiles beyond Wayfarer-OWL
- Enhanced encryption options
- Performance optimizations
- Improved HF integration

---

*GAP is developed as part of the broader decentralized gaming initiative. This preview focuses purely on the data specification and tools - no performance promises or token economics.*
```

---

## 🏷️ GitHub Release Notes

**Title:** GAP v0.4.0-preview - Public Preview Release

**Body:**
```markdown
# GAP v0.4.0-preview - Public Preview Release 🚀

**First public preview of GAP (Gameplay-Action Pairs) standard and tools.**

## ⚠️ Preview Status

This is a **preview release** for community feedback:
- APIs may change between versions
- Data uploads require allowlist credentials
- Anti-sybil detection is in testing phase
- Focus on specification and tools (not performance claims)

## 🎯 What's Included

### Open Standard & Tools
- **GAP v0.2 specification** with formal JSON schemas
- **gap-agent CLI** for packaging, upload, verification
- **Multi-format validator** supporting hf://, s3://, local paths
- **Anti-sybil detection** with pHash + SimHash algorithms
- **100MB reference sample** with rights-clean data

### Documentation
- **[API Contract](docs/API.md)** - Locked interfaces for integrations
- **[Anti-Sybil Strategy](docs/ANTI_SYBIL.md)** - Comprehensive defense plan
- **[Contributors Guide](CONTRIBUTORS.md)** - Allowlist onboarding process
- **[Security Policy](SECURITY.md)** - Responsible disclosure guidelines

### Hugging Face Integration
- **Dataset:** `Shaga/GAP-samples` with ML-native access
- **Space:** Interactive drag-and-drop validator
- **Streaming:** External URL support for larger datasets

## 🛡️ Security & Quality

**Anti-Sybil Defenses:**
- Perceptual hashing (DCT-based) for video duplicate detection
- SimHash for control pattern similarity analysis
- Risk scoring system (0-100 points) with action thresholds
- Local pre-checks to avoid bandwidth waste

**Data Quality:**
- Quality Acceptance Tests (QAT) with ±8ms alignment guarantee
- Formal validation against JSON schemas
- Transparent verification (same checks locally and server-side)
- Rights-clean sample data with clear licensing

## 🎮 Getting Started

```bash
# Download and validate sample
cd samples/star-atlas_100mb/
./download.sh
python3 tools/validate.py --profile wayfarer-owl .

# Install and try the CLI
pip install ./packages/gap-agent
gap pack video.mkv controls.jsonl --profile wayfarer-owl --encrypt

# Run local ingest checks
python3 tools/ingest_check.py my_shard/ --profile wayfarer-owl --verbose
```

## 📝 Data Contributions

Currently **invite-only** during preview phase.

**[Apply for allowlist access](GITHUB_ISSUE_LINK)**

**Requirements:**
- Original gameplay footage (no re-encoded content)
- Hardware: GTX 1060+ GPU, 16GB+ RAM, 10+ Mbps upload
- Quality: CFR video, synchronized controls, no overlays

## 🔗 Resources

- **Repository:** https://github.com/ShagaDAO/gap
- **Validator Space:** https://huggingface.co/spaces/Shaga/gap-explorer  
- **Sample Dataset:** https://huggingface.co/datasets/Shaga/GAP-samples
- **Contributors Guide:** [CONTRIBUTORS.md](CONTRIBUTORS.md)

## ⚖️ License & Legal

- **Code & Specs:** MIT License
- **Sample Data:** Research use only (see LICENSE-data.md)
- **Security:** Responsible disclosure via security@shaga.ai

---

**Ready to preview GAP and provide feedback? We'd love to hear from the community!**
```

---

## 🎯 Next Steps for Launch

1. **Create actual Google Form** for allowlist applications
2. **Set up security@shaga.ai** email for responsible disclosure
3. **Create HF organizations** and upload initial datasets/spaces
4. **Post GitHub issue** for allowlist onboarding
5. **Announce on relevant channels** (dev Twitter, Discord, etc.)

---

*These materials maintain strict scope discipline: GAP spec + tools only, no performance/token claims.* 