# GAP v0.2 — Gameplay-Action Pairs

**A standard way to package time-aligned frames + controls (+ optional labels) so partners can train world-models and neural codecs with minimal glue code.**

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Validate a standard GAP shard
python tools/validate.py /path/to/gap_shard/session_id/

# Validate with a specific profile (e.g., Wayfarer-OWL)
python tools/validate.py --profile wayfarer-owl /path/to/shard/

# Load sample data
python examples/load_sample.py
```

## Repository Structure

```
gap/
├── spec/                    # Core specification
│   ├── GAP-v0.2.md         # Full GAP v0.2 specification
│   └── schema.json         # JSON schema for validation
├── profiles/                # Partner-specific profiles
│   ├── wayfarer-owl.md     # OWL baseline profile (1080p60)
│   └── wayfarer-owl-hqplus.md # OWL HQ+ profile (enhanced)
├── samples/                 # Sample data and examples
│   ├── meta.json           # Basic GAP sample metadata
│   ├── controls.jsonl      # Basic controls (5 rows)
│   ├── frames.csv          # Basic frame index
│   └── star-atlas_100mb/   # 100MB OWL profile sample
├── tools/                  # Utilities and validators
│   ├── validate.py         # GAP shard validator
│   └── loader.py           # Python data loader
├── examples/               # Example usage
│   └── load_sample.py      # How to load GAP data
├── CHANGELOG.md            # Version history
└── requirements.txt        # Python dependencies
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

## Contributing

GAP v0.2 is designed for immediate production use. For profile additions or specification changes, please:

1. Review existing profiles for compatibility patterns
2. Ensure backward compatibility with core GAP v0.2
3. Include validation rules and sample data
4. Test with the provided validator tools

## License

See individual files for licensing terms. 