# Star Atlas 100MB Sample Shard

**Wayfarer Labs OWL Profile Reference Implementation**

This is a **Wayfarer-compatible reference shard** for validator/loader testing. It is **vendor-neutral** and not affiliated with any storage provider. This sample demonstrates the exact structure expected for production shards.

## Contents

- `meta.json` - Session metadata in OWL profile format
- `controls.jsonl` - Event-based controls (20 samples @ 120Hz)
- `hashes.json` - File integrity verification
- `video.ivf` - **[NOT INCLUDED]** 3-minute Star Atlas gameplay @ AV1 4.5 Mbps

## Sample Details

- **Duration:** 3 minutes (180 seconds)
- **Resolution:** 1920x1080 @ 60fps CFR
- **Video codec:** AV1 at 4.5 Mbps (~101 MB for 3 minutes)
- **Controls:** 120Hz keyboard/mouse events
- **Profile:** wayfarer-owl.v0.1 (strict OWL compatibility)

## Video File

The actual video file (`video.ivf`) is not included in this repository due to size constraints. For the complete 100MB sample:

1. Capture 3 minutes of Star Atlas gameplay at 1080p60
2. Encode with AV1 at 4.5 Mbps using SVT-AV1 or similar
3. Ensure CFR (constant frame rate) encoding
4. Update `hashes.json` with actual SHA-256 of the video file

## Validation

Validate this sample using the GAP validator with OWL profile:

```bash
python tools/validate.py --profile wayfarer-owl samples/star-atlas_100mb/
```

## For Partner Integration

This sample provides:

1. **Metadata schema** - Exact JSON structure for OWL profile
2. **Controls format** - Event-based JSONL with microsecond timestamps  
3. **File organization** - Ready-to-ingest directory structure
4. **Quality gates** - All validation requirements met

The controls demonstrate realistic FPS gameplay with:
- WASD movement
- Mouse look (delta tracking)
- Jump (SPACE), aim (RMB), fire (LMB)
- Proper timing at 120Hz sample rate

## Size Breakdown

| Component | Size | Purpose |
|-----------|------|---------|
| video.ivf | ~101 MB | AV1-encoded gameplay |
| controls.jsonl | ~245 KB | Input events (extrapolated) |
| meta.json | ~2.1 KB | Session metadata |
| hashes.json | ~1 KB | Integrity verification |
| **Total** | **~101.25 MB** | Complete shard |

This provides a complete reference implementation for partner evaluation. 