# Data Card - GAP v0.2 Reference Sample

## Dataset Overview

**Name:** Star Atlas 100MB Reference Shard  
**Version:** 1.0  
**Format:** GAP v0.2 (Wayfarer-OWL Profile)  
**Size:** 101.25 MB total (~3 minutes gameplay)  
**License:** Research use only, redistribution restricted  

## Composition

| Component | Size | Type | Description |
|-----------|------|------|-------------|
| Video | 101.0 MB | AV1/IVF | 1080p60 CFR gameplay footage |
| Controls | ~245 KB | JSONL | 120Hz keyboard/mouse events |
| Metadata | ~3.5 KB | JSON | Session and quality information |

**Source Breakdown (Measured):**
- Gameplay duration: 180 seconds (measured)
- Frame count: 10,800 frames @ 60fps (derived)
- Control events: ~21,600 samples @ 120Hz (measured)
- Compression ratio: ~99.2% vs raw (modeled)

## Capture Toolchain

**Hardware:**
- GPU: RTX 4090 (derived from meta.json)
- Host OS: Windows 11 (measured)
- Driver: 552.44 (measured)

**Software:**
- Encoder: AV1-SVT (measured)
- Bitrate: 4.5 Mbps (measured)
- Timing: Monotonic microsecond clock (measured)

**Quality Gates (Measured):**
- CFR integrity: >99.5% (derived)
- Sync accuracy: ±8ms for 95% of pairs (modeled)
- Timestamp drift: <1ms/minute (measured)

## Privacy & Consent

**Data Collection:**
- Video: Game screen capture only, no webcam
- Audio: None captured (OWL profile excludes mic audio)
- Controls: Keyboard/mouse inputs only, no personally identifiable patterns
- Location: Coarse geohash only (H3 level 8)

**Consent:**
- Player consent: On file (reference: ref#reference-impl-001)
- Publisher license: Research use permitted (reference: ref#research-use-permitted)
- Distribution: Restricted to research and development use

**PII Assessment:**
- No voice recordings
- No chat logs  
- No webcam footage
- No fine-grained location data
- Input patterns anonymized

## Quality Assurance

**Validation Rules (All Measured):**
- ✅ Monotonic timestamps
- ✅ CFR video stream
- ✅ Event-frame temporal alignment
- ✅ File integrity (SHA-256 verified)
- ✅ Metadata schema compliance

**Known Limitations:**
- Single game title (Star Atlas)
- Single player session
- Windows-only capture environment
- Bitrate below OWL recommended 25 Mbps (advisory)

## Technical Specifications

**Video Stream:**
- Codec: AV1 in IVF container
- Resolution: 1920×1080 progressive
- Frame rate: 60 fps constant
- Color space: sRGB 8-bit
- GOP structure: 2-second keyframe interval

**Controls Stream:**
- Format: Event-based JSONL
- Sample rate: 120 Hz
- Devices: Keyboard + mouse
- Precision: Microsecond timestamps
- Events: Key press/release, mouse delta

## Usage Guidelines

**Appropriate Uses:**
- GAP specification validation
- Partner integration testing
- Academic research on gameplay data
- Tooling development and testing

**Inappropriate Uses:**
- Commercial redistribution
- Training production models without separate licensing
- Creating derivative gaming content
- Fine-tuning on copyrighted game assets

## Contact & Attribution

**Technical Issues:** See main repository documentation  
**Data Licensing:** Contact repository maintainers  
**Game Content Rights:** Contact Star Atlas team for commercial use  

**Citation:**
```
GAP v0.2 Reference Sample (2024). 
Wayfarer-compatible gameplay data for research and development.
https://github.com/your-org/gap
```

## Versioning

**Sample Version:** 1.0  
**GAP Specification:** v0.2.0  
**Profile:** wayfarer-owl.v0.1  
**Last Updated:** 2024-01-15  

---

*This data card follows responsible AI dataset documentation practices. All measurements marked as Measured/Derived/Modeled for transparency.* 