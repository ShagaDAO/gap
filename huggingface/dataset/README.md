---
title: "GAP Samples - Gameplay Action Pairs"
language:
- en
license: "custom"
size_categories:
- 100M<n<1B
task_categories:
- video-classification
- multimodal
- time-series-forecasting
tags:
- gameplay
- gaming
- multimodal
- video
- controls
- time-series
- wayfarer-owl
pretty_name: "GAP v0.2 Reference Samples"
---

# GAP v0.2 Reference Samples

**Gameplay-Action Pairs (GAP) reference dataset for ML-native discovery and integration testing.**

## Dataset Overview

This dataset contains reference implementations of the GAP v0.2 specification, designed for:
- Partner integration testing
- Academic research on gameplay data
- Tooling development and validation
- ML model development with aligned video+controls

**Format:** GAP v0.2 (Wayfarer-OWL Profile)  
**Size:** 101.25 MB total (~3 minutes gameplay)  
**License:** Research use only, redistribution restricted  

## Quick Start

```python
from datasets import load_dataset

# Load GAP samples
dataset = load_dataset("Shaga/GAP-samples")

# Access sample shard
sample = dataset["train"][0]
print(f"Session: {sample['session_id']}")
print(f"Video: {sample['video_path']}")
print(f"Controls: {sample['controls_events']}")
```

## Data Structure

| Component | Size | Type | Description |
|-----------|------|------|-------------|
| Video | 101.0 MB | AV1/IVF | 1080p60 CFR gameplay footage |
| Controls | ~245 KB | JSONL | 120Hz keyboard/mouse events |
| Metadata | ~3.5 KB | JSON | Session and quality information |

**Features:**
- `session_id`: Unique session identifier
- `video_path`: Path to AV1-encoded video file
- `controls_events`: List of timestamped input events
- `metadata`: Complete GAP v0.2 metadata
- `profile`: Wayfarer-OWL profile specification

## Technical Specifications

**Video Stream:**
- Codec: AV1 in IVF container
- Resolution: 1920×1080 progressive
- Frame rate: 60 fps constant
- Duration: 180 seconds
- Bitrate: 4.5 Mbps

**Controls Stream:**
- Format: Event-based JSONL
- Sample rate: 120 Hz
- Devices: Keyboard + mouse
- Precision: Microsecond timestamps
- Events: Key press/release, mouse delta

## Privacy & Consent

**Data Collection:**
- ✅ Video: Game screen capture only, no webcam
- ✅ Audio: None captured (OWL profile excludes mic audio)
- ✅ Controls: Keyboard/mouse inputs only, no PII
- ✅ Location: Coarse geohash only (H3 level 8)

**Consent & Rights:**
- Player consent: On file (reference: ref#reference-impl-001)
- Publisher license: Research use permitted
- Distribution: Restricted to research and development use

## Quality Assurance

All samples pass GAP v0.2 Quality Acceptance Tests:
- ✅ Monotonic timestamps (drift < 1ms/minute)
- ✅ CFR video stream (>99.5% integrity)
- ✅ Event-frame temporal alignment (±8ms for 95% of pairs)
- ✅ File integrity (SHA-256 verified)
- ✅ Metadata schema compliance

## Usage Examples

### Validate GAP Shard
```python
from datasets import load_dataset
from gap_tools.validate import GAPValidator

# Load dataset
dataset = load_dataset("Shaga/GAP-samples", split="train")
sample = dataset[0]

# Validate with GAP tools (secure API usage)
validator = GAPValidator(sample['shard_path'], profile="wayfarer-owl")
is_valid, report = validator.validate_all()

print(f"Validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
```

> **Security Note:** Examples using `subprocess.run()` with shell commands are for 
> illustration only. In production code, use library APIs directly and validate 
> all inputs to prevent command injection attacks.
```

### Load Control Events
```python
import json

# Access control events
sample = dataset[0]
for event in sample['controls_events'][:5]:
    print(f"t={event['t_us']}: {event['type']} {event.get('key', event.get('dx', ''))}")
```

### Access Larger Shards
```python
# For larger datasets, use external URLs
external_shard_url = "s3://gap-samples/star-atlas-full-session.tar.gz"

# The dataset script can handle streaming from external storage
# (This keeps HF lightweight while supporting big data)
```

## Integration with GAP Tools

This dataset is designed to work seamlessly with GAP tooling:

```bash
# Install GAP tools
pip install gap-agent gap-tools

# Validate sample
gap validate path/to/shard --profile wayfarer-owl

# Load with gap-agent
from gap_agent import ShardPackager
packager = ShardPackager()
# ... use with your data
```

## Related Resources

- **[GAP Specification](https://github.com/ShagaDAO/gap)**: Complete GAP v0.2 documentation
- **[GAP Explorer Space](https://huggingface.co/spaces/Shaga/gap-explorer)**: Interactive validator and visualizer
- **[Research Paper](https://arxiv.org)**: Technical details on GAP alignment methodology

## Citation

```bibtex
@dataset{gap_samples_2024,
  title={GAP v0.2 Reference Samples: Gameplay-Action Pairs for ML Research},
  author={GAP Contributors},
  year={2024},
  url={https://huggingface.co/datasets/Shaga/GAP-samples},
  license={Research Use Only}
}
```

## Support

- **Technical Issues**: [GitHub Issues](https://github.com/ShagaDAO/gap/issues)
- **Data Licensing**: Contact dataset maintainers
- **Game Content Rights**: Contact Star Atlas team for commercial use

---

*This dataset follows responsible AI practices with clear consent, privacy protection, and usage restrictions.* 