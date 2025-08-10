# Wayfarer Labs (OWL) HQ+ Profile for GAP v0.2

**Optional sidecars and enhanced capture options** that remain backward-compatible with the baseline Wayfarer-OWL profile.

This profile extends the base `wayfarer-owl.md` specification with higher quality capture options and additional data streams while maintaining full compatibility.

## Enhanced Capture Options

### Video Enhancements
* **Higher resolution:** 1440p/4K@60, flag `video.fps_src`/`bit_depth` in meta; downstream will downsample to 1080p→512
* **Higher framerate:** 120 FPS capture; deterministically decimate to 60 during preprocess
* **10-bit SDR:** allowed; tonemap to 8-bit for baseline processing
* **HDR capture:** optional; include tone mapping metadata

### Additional Data Streams
* **Depth maps:** `/features/depth/*.png` or `.npy` files
* **Optical flow:** `/features/flow/*.png` or `.npy` files  
* **Game audio:** `/audio/*.wav` files (separate from mic audio)
* **Gamepad support:** Extended control events in the same JSONL stream

## File Layout (Extended)

```
/<session_id>/
  # Core files (same as baseline)
  video_0001.mkv|ivf        # CFR, potentially higher res/fps
  controls_0001.jsonl       # includes gamepad events
  meta_0001.json            # extended metadata
  hashes.json               # includes all sidecars
  
  # Optional sidecars
  features/
    depth_0001/
      frame_000001.png      # per-frame depth maps
      frame_000002.png
      ...
    flow_0001/
      frame_000001.png      # optical flow vectors
      frame_000002.png
      ...
  audio/
    game_0001.wav           # game audio (no mic)
    ambience_0001.wav       # environmental audio
```

## Extended Metadata

Additional fields in `meta_0001.json`:

```json
{
  "schema_version": "0.2.0",
  "profile": "wayfarer-owl-hqplus.v0.1",
  
  // ... baseline fields ...
  
  "display": {
    "resolution": "2560x1440",  // or "3840x2160"
    "fps": 120,                 // capture rate
    "fps_target": 60,           // processing target
    "hdr": true,                // HDR capture
    "colorspace": "Rec2020",
    "bit_depth": 10
  },
  
  "features": {
    "depth": {
      "present": true,
      "format": "png",          // or "npy"
      "bit_depth": 16,
      "units": "meters",
      "range": [0.1, 1000.0]
    },
    "optical_flow": {
      "present": true,
      "format": "png",
      "encoding": "rgb_flow"    // or "uv_displacement"
    }
  },
  
  "audio": {
    "game_audio": true,
    "sample_rate": 48000,
    "channels": 2,
    "format": "wav",
    "mic_recorded": false       // still no mic audio
  },
  
  "controls": {
    "devices": ["kbm", "gamepad"],
    "gamepad_type": "xbox_wireless",
    "format": "jsonl_events",
    "timestamp_clock": "monotonic_us"
  }
}
```

## Extended Controls Format

Includes gamepad events in the same JSONL stream:

```jsonl
{"t_us": 238497124, "type": "key", "key": "W", "state": "down"}
{"t_us": 238497980, "type": "mouse", "dx": 14, "dy": -3}
{"t_us": 238498100, "type": "pad", "axis": "LX", "value": 0.41}
{"t_us": 238498105, "type": "pad", "axis": "LY", "value": -0.23}
{"t_us": 238498312, "type": "key", "key": "W", "state": "up"}
{"t_us": 238499000, "type": "pad", "button": "A", "state": "down"}
{"t_us": 238499100, "type": "pad", "button": "A", "state": "up"}
```

### Gamepad Mappings
- **Axes:** LX, LY, RX, RY, LT, RT (values -1.0 to 1.0)
- **Buttons:** A, B, X, Y, LB, RB, Start, Back, LS, RS, DPad_Up, DPad_Down, DPad_Left, DPad_Right

## Processing Guidelines

### Downsampling Strategy
1. **4K→1080p:** Use high-quality bicubic downsampling
2. **120fps→60fps:** Deterministic frame selection (every 2nd frame)
3. **10-bit→8-bit:** Apply appropriate tone mapping
4. **HDR→SDR:** Use standard tone mapping curves

### Feature Processing
- **Depth maps:** Normalize to 0-1 range, store as 16-bit PNG
- **Optical flow:** Encode as RGB or UV displacement vectors
- **Audio:** Keep game audio separate from any voice/chat data

## Quality Gates (Enhanced)

All baseline quality gates plus:

* **Resolution consistency:** All frames match declared resolution
* **Framerate stability:** 120fps capture maintains <1% jitter
* **Feature alignment:** Depth/flow maps align temporally with video frames
* **Audio sync:** Game audio synchronized within ±2ms of video
* **Gamepad validation:** Analog values within expected ranges

## Backward Compatibility

- **Baseline processors** can ignore all sidecar directories
- **Core video/controls** follow standard wayfarer-owl profile
- **Metadata extensions** are clearly marked and optional
- **File naming** maintains consistency with baseline

## Size Estimates

* **Video (1440p120 @ 35 Mbps):** ~15.75 GB/hour
* **Video (4K60 @ 50 Mbps):** ~22.5 GB/hour
* **Depth maps (16-bit PNG):** ~2-4 GB/hour
* **Optical flow:** ~1-2 GB/hour
* **Game audio (48kHz stereo):** ~0.35 GB/hour
* **Controls (extended):** ~10-15 MB/hour

## Validation

Extended validation checks for HQ+ features:

```bash
python tools/validate.py --profile wayfarer-owl-hqplus /path/to/shard/
```

Additional checks:
- Feature directory structure
- Temporal alignment of sidecars
- Audio/video synchronization
- Gamepad value ranges
- HDR metadata presence

## Use Cases

This profile is ideal for:
- **Research datasets** requiring high fidelity
- **Codec development** and compression studies  
- **Multi-modal training** (vision + audio + depth)
- **Advanced control studies** (gamepad + keyboard/mouse)
- **Future-proofing** data collection efforts

The enhanced profile ensures maximum data utility while maintaining seamless compatibility with existing OWL processing pipelines. 