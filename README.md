# GAP: Gameplay–Action Pairs (Preview)

**Open standard + tools for time‑aligned frames + controls.**  
This repo contains the GAP spec, validator, and the `gap‑agent` packing/upload CLI.
It's the public, auditable **data path** that sits next to the closed Shaga Node Core.

> **Status: Preview**. APIs may change. Data uploads are **invite‑only** while we harden anti‑Sybil gates.

- 📄 **Spec & Schemas:** `packages/gap-spec/`
- 🧰 **CLI:** `packages/gap-agent/` (`gap pack|upload|verify|validate`)
- 🔎 **Validator:** `tools/validate.py` (+ drag‑and‑drop Space on Hugging Face)
- 🧪 **Sample:** 100 MB rights‑clean shard (download via `samples/.../download.sh`)

**What's open:** spec, validator, packing/upload client, sample & Space.  
**What's closed:** real‑time streaming, DRM, watermarking, Proof‑of‑Render.

## Quick Start

```bash
# Download and validate the reference sample
cd samples/star-atlas_100mb/
./download.sh
cd ../..
python3 tools/validate.py --profile wayfarer-owl samples/star-atlas_100mb/

# Install GAP agent for packaging
pip install ./packages/gap-agent

# Package your own GAP shard
gap pack video.mkv controls.jsonl --profile wayfarer-owl --encrypt

# Upload (allowlisted nodes only)
gap upload my_shard/ --endpoint s3://... --idle-policy smart
```

## Repository Structure

```
gap/
├── packages/               # Modular packages
│   ├── gap-spec/           # Core specifications and schemas
│   │   ├── GAP-v0.2.md     # Full GAP v0.2 specification
│   │   ├── schema.json     # JSON schema for meta.json
│   │   ├── manifest.schema.json # Schema for manifests
│   │   ├── receipt.schema.json  # Schema for ingest receipts
│   │   └── profiles/       # Partner-specific profiles
│   │       ├── wayfarer-owl.md # OWL baseline (1080p60)
│   │       └── wayfarer-owl-hqplus.md # OWL HQ+ (enhanced)
│   └── gap-agent/          # Open storage/upload module
│       ├── src/gap_agent/  # Public GAP packaging library
│       │   ├── packager.py # GAP shard creation + encryption
│       │   ├── uploader.py # S3-compatible with throttling
│       │   ├── verifier.py # Receipt validation + integrity
│       │   ├── dedupe.py   # pHash/SimHash duplicate detection
│       │   └── cli.py      # Command-line interface
│       ├── pyproject.toml  # Package configuration
│       └── README.md       # Gap-agent documentation
├── tools/                  # Utilities and validators
│   ├── validate.py         # GAP validator (supports hf://, s3://)
│   ├── uri_loader.py       # Universal URI loading
│   ├── ingest_check.py     # Local QAT + anti-sybil checks
│   ├── loader.py           # Python data loader
│   └── generate_synth_shard.py # Rights-free synthetic data
├── docs/                   # Documentation
│   ├── API.md              # Locked API contract for Node Core
│   ├── ANTI_SYBIL.md       # Anti-sybil defense strategy
│   └── data-card.md        # Dataset documentation
├── samples/                # Sample data and examples
│   ├── meta.json           # Basic GAP sample metadata
│   ├── controls.jsonl      # Basic controls (5 rows)
│   ├── frames.csv          # Basic frame index
│   └── star-atlas_100mb/   # 100MB OWL profile sample
├── huggingface/            # HF distribution
│   ├── dataset/            # Dataset card + script
│   └── space/              # Interactive validator Space
├── examples/               # Example usage
│   └── load_sample.py      # How to load GAP data
├── .github/workflows/      # CI/CD
│   ├── validate.yml        # Validation CI
│   └── publish-hf.yml      # HF publishing workflow
└── CHANGELOG.md            # Version history
```

## What is GAP?

GAP (Gameplay-Action Pairs) is a standardized format for packaging gameplay recordings that include:

- **Video streams** (AV1/HEVC, 720p60+ CFR)
- **Input controls** (keyboard, mouse, gamepad at ≥60Hz)
- **Network stats** (optional RTT/jitter/loss)
- **Engagement labels** (optional PII-free chat/voice aggregates)

## Partner Profiles

GAP v0.2 supports partner-specific profiles that ensure compatibility while extending the core specification:

### Wayfarer Labs (OWL) Profiles

- **[wayfarer-owl](profiles/wayfarer-owl.md)** - Baseline OWL compatibility (1080p60, JSONL controls)
- **[wayfarer-owl-hqplus](profiles/wayfarer-owl-hqplus.md)** - Enhanced capture (4K, 120fps, depth, audio)

These profiles mirror OWL's public defaults for seamless integration with existing tooling.

## Key Features

- **Time-aligned**: All data uses monotonic microsecond timestamps
- **Compact**: ~2-4 GB/hour for 720p60 video + controls
- **Verifiable**: SHA-256 hashes and frame watermarking
- **Privacy-first**: Optional labels are aggregated and PII-free
- **Profile-aware**: Partner-specific compatibility layers

## Phase-0 Ready

This v0.2 specification is production-ready for Phase-0 partner pilots with:
- ✅ Formal schema and validation
- ✅ Sample data and acceptance tests  
- ✅ Realistic size calculations
- ✅ Python tooling for easy integration
- ✅ Partner profiles (Wayfarer-OWL)
- ✅ 100MB reference shard for testing

## 100MB Reference Sample

The [`samples/star-atlas_100mb/`](samples/star-atlas_100mb/) directory contains a complete reference implementation:

- **3-minute Star Atlas gameplay** @ 1080p60 AV1 (~101MB)
- **Wayfarer-OWL profile format** with JSONL controls
- **Ready-to-ingest structure** for partner evaluation
- **Complete metadata schema** and validation

## Validation Examples

```bash
# Validate core GAP v0.2 compliance
python tools/validate.py samples/

# Validate with OWL profile requirements  
python tools/validate.py --profile wayfarer-owl samples/star-atlas_100mb/

# JSON output for automated testing
python tools/validate.py --json --profile wayfarer-owl samples/star-atlas_100mb/
```

## Size Estimates by Profile

### Standard GAP v0.2 (720p60)
- Video (AV1): ~1.8-2.7 GB/hour
- Video (HEVC): ~2.7-3.6 GB/hour
- Controls: ~3-15 MB/hour

### Wayfarer-OWL Baseline (1080p60)
- Video (AV1 @ 25 Mbps): ~11.25 GB/hour
- Controls (120Hz events): ~5-10 MB/hour
- Processing target: ~900 MB/hour (512×512)

### Wayfarer-OWL HQ+ (4K60+)
- Video (4K @ 50 Mbps): ~22.5 GB/hour
- Enhanced features: ~2-6 GB/hour additional
- Research-grade fidelity with backward compatibility

## Versioning

| Version | Status | Support | Notes |
|---------|--------|---------|-------|
| **v0.2.x** | Current | Active | Production ready, partner profiles |
| v0.1.x | Deprecated | Legacy | Raw frames, variable rates (migrate to v0.2) |

Migration from v0.1.x: Use AV1/HEVC CFR, standardize control rates to ≥60Hz.

## Known Limitations (Preview Status)

- **APIs may change** between preview versions
- **Bitrate checks** are advisory unless `--strict` flag is used
- **Upload requires allowlist** credentials (invite-only)
- **Validator outputs** may change format in future versions
- **Anti-sybil detection** is in early testing phase

## Contributing

**Spec/Code contributions:** Standard GitHub issues + PRs welcome
**Data contributions:** [Apply for allowlist access](CONTRIBUTORS.md#allowlist-application)

For specification changes:
1. Review existing profiles for compatibility patterns
2. Ensure backward compatibility with core GAP spec
3. Include validation rules and sample data
4. Test with provided validator tools

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for detailed guidelines.

## License

See individual files for licensing terms. 