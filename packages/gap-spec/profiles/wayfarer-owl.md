# Wayfarer Labs (OWL) Profile for GAP v0.2

**Wayfarer Labs (Open World Labs / "OWL") data profile for open Genie-3-class training**

This profile mirrors OWL's public defaults so shards ingest with zero surprises. It's a **strict subset** of GAP v0.2 that maintains full compatibility with existing OWL tooling.

## Capture Requirements

* **Video:** 1920×1080 @ **60 FPS**, **constant frame-rate**, SDR/sRGB.
  Container/codec: use what Owl Control/OBS emits; CFR is non-negotiable.
* **Bitrate:** OWL captures ≈ 25 Mbps; if you must compress, keep it visually lossless.
* **Controls:** raw keyboard/mouse (mouse-delta for FPS), timestamped with **monotonic µs**.
* **Audio:** not required; Owl Control records **video + raw inputs** (no audio). If audio is captured, store as a **sidecar**; ingestion will ignore it.
* **Segments:** split into 10–60 s chunks (I/O friendliness).

## Processing Targets (handled by OWL—contributors don't do this)

* Train preview: **512×512 @ ~2 Mbps** (~**900 MB/h**).
* Latent storage: **FP8 e4m3** for VAE latents; OWL reports no observed reconstruction loss; target **~400 MB/h**.

## File Layout (GAP v0.2 compliant)

```
/<session_id>/
  video_0001.mkv|ivf        # CFR, 1080p60
  controls_0001.jsonl       # event-based inputs (monotonic µs)
  meta_0001.json            # fields below
  hashes.json               # SHA-256 per file (and frame watermark proofs if used)
```

## Metadata Schema

**`meta_0001.json` (profile fields)**

```json
{
  "schema_version": "0.2.0",
  "profile": "wayfarer-owl.v0.1",
  "session_id": "c3e1a0c4-9d7a-4f1e-8c90-9e5d9e21a7ad",
  "tool": {"name": "owl-control", "version": "1.2.3"},
  "title": {"name": "Star Atlas", "build": "1.24.3", "map": "SOG_Corvus"},
  "capture": {
    "host_os": "Windows 11",
    "gpu": "RTX 4090",
    "driver": "552.44",
    "encoder": "as_emitted",
    "clock": "monotonic_us"
  },
  "display": {
    "resolution": "1920x1080",
    "fps": 60,
    "hdr": false,
    "colorspace": "sRGB",
    "bit_depth": 8
  },
  "video": {
    "codec": "as_emitted",
    "bitrate_mbps": 25,
    "cfr_enforced": true
  },
  "controls": {
    "devices": ["kbm"],
    "format": "jsonl_events",
    "timestamp_clock": "monotonic_us"
  },
  "audio": {"present": false},
  "privacy": {
    "mic_recorded": false,
    "overlays": false,
    "single_player_only": true,
    "consent": "on-file"
  },
  "timing": {"t0_us": 1722900000000, "timezone": "UTC"},
  "rights": {"publisher_license": "ref#...", "player_consent_id": "ref#..."}
}
```

## Controls Format (Event-based JSONL)

```jsonl
{"t_us": 238497124, "type": "key", "key": "W", "state": "down"}
{"t_us": 238497980, "type": "mouse", "dx": 14, "dy": -3}
{"t_us": 238498312, "type": "key", "key": "W", "state": "up"}
{"t_us": 238499105, "type": "key", "key": "SPACE", "state": "down"}
{"t_us": 238499205, "type": "key", "key": "SPACE", "state": "up"}
```

### Key Mappings
- Standard WASD movement keys
- Mouse delta (dx, dy) in pixels
- Common FPS keys: SPACE (jump), CTRL (crouch), SHIFT (sprint)
- Mouse buttons: LMB, RMB, MMB

## Quality Gates (Auto-check)

* **CFR integrity:** drop/dup < **0.5%**; no > **0.5s** black frames
* **No overlays:** no non-game overlays (window switches/popups) in segment
* **Input↔frame sync:** evidence of input around frames for FPS titles; publish jitter histogram
* **Timestamp sanity:** strictly monotonic; drift < **1 ms/min**
* **Controls coverage:** ≥ **95%** of frames have input within **±8ms**

## Compatibility with GAP v0.2

| OWL Profile Field | GAP v0.2 Equivalent |
|------------------|-------------------|
| `video.fps_src/fps_dst` | `display.fps` + CFR enforcement |
| event-based controls JSONL | `controls.parquet` (convertible) |
| optional audio sidecar | `labels/audio` sidecar (ignored by default) |
| 1080p@60 CFR capture | GAP "Video stream" requirements |
| quality gates | GAP QAT (drops, sync, drift) |

## Size Estimates

* **Video (1080p60 @ 25 Mbps):** ~11.25 GB/hour
* **Controls (120Hz events):** ~5-10 MB/hour  
* **Metadata + hashes:** <1 MB/hour

## Processing Notes

> **FP8 e4m3 isn't proprietary**; OWL's latent format is. The VAE encoder/decoder and training pipeline remain OWL's IP, but the numerical format is standard.

> **Storage compatibility**: References to `s3://` paths denote S3-compatible object stores (AWS S3, Cloudflare R2, MinIO, Backblaze B2, etc.). The OWL profile is storage-provider agnostic.

> Numbers like "1080p→512→~900 MB/h" and "latents ~400 MB/h" reference OWL's published specifications and should be verified against current OWL documentation.

## Validation

Use the GAP v0.2 validator with profile-specific checks:

```bash
python tools/validate.py --profile wayfarer-owl /path/to/shard/
```

This profile ensures **100% compatibility** with existing OWL tooling while enabling seamless integration into the broader GAP ecosystem. 