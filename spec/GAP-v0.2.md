# GAP v0.2 — Gameplay‑Action Pairs (publishable draft)

**Purpose.** A standard way to package time‑aligned **frames + controls** (+ optional labels) so partners can train **world‑models** and **neural codecs** with minimal glue code.

## 1) Packaging

```
/gap_shard/<session_id>/
  meta.json                 # session metadata (required)
  video.ivf | video.mkv     # AV1 or HEVC, constant‑frame‑rate (required)
  controls.parquet          # 60–240 Hz input state (required)
  netstats.parquet          # RTT/jitter/loss (optional, recommended)
  labels.jsonl              # chat/voice-derived hotspots (optional, opt‑in)
  hashes.json               # SHA‑256 per file, frame watermark proofs (required)
```

**Shard duration:** 30–120 minutes continuous gameplay (no menus/cutscenes).
**Timebase:** All timestamps are **monotonic microseconds** (`ts_us`, int64) from the same host clock used to capture video and inputs.

---

## 2) `meta.json` (required)

```json
{
  "schema_version": "0.2.0",
  "session_id": "c3e1a0c4-9d7a-4f1e-8c90-9e5d9e21a7ad",
  "title": {"name":"Star Atlas", "build":"1.24.3", "map":"SOG_Corvus"},
  "capture": {"host_os":"Windows 11", "gpu":"RTX 4090", "driver":"552.44",
              "encoder":"AV1_SVT", "clock":"monotonic_us"},
  "display": {"resolution":"1280x720","fps":60,"hdr":false},
  "timing":  {"t0_us": 1722900000000, "timezone":"UTC"},
  "privacy": {"voice_raw": false, "chat_raw": false, "labels_only": true, "consent":"on-file"},
  "geo": {"h3":"8a2a1072b59ffff"},
  "rights": {"publisher_license":"ref#...","player_consent_id":"ref#..."}
}
```

---

## 3) Video stream (required)

* **Codec:** AV1 (`.ivf`) or HEVC (`.mkv`), **CFR** at 60 fps (30/120 acceptable if specified).
* **Resolution:** 720p preferred (1080p accepted).
* **GOP/Key‑int:** 1–2 s (60–120 @ 60 fps).
* **Overlays:** no webcam/stream overlays; in‑game HUD ok.
* **Frame timestamps:** write **per‑frame `ts_us`** in container timebase.
* **Provenance:** embed a light **HMAC watermark** (LSB or QR corner). Document the secret rotation out‑of‑band.

**Size guidance @ 720p60:**
AV1 4–6 Mbps → **1.8–2.7 GB/hour**; HEVC 6–8 Mbps → **2.7–3.6 GB/hour**.
(Provide the actual bitrate in `meta.json` if you fix it.)

> ⚠️ **Why not "raw frames"?** Uncompressed 720p60 RGB is \~**570 GB/hour**. For Phase‑0/1, high‑quality AV1/HEVC is the pragmatic choice. If a partner insists on lossless for a *tiny* gold set, use PNG frames in a short shard.

---

## 4) Controls (`controls.parquet`, required)

**Rate:** **≥ 60 Hz** (recommended: **120 Hz**; mouse delta **240 Hz**).
**Alignment guarantee:** for ≥ 95% of pairs, `|ts_us(frame_n) − ts_us(nearest_input)| ≤ 8 ms` (report residuals in QAT).

**Column schema (flat, Parquet):**

| column            | type    | notes                                                              |
| ----------------- | ------- | ------------------------------------------------------------------ |
| `ts_us`           | int64   | monotonic μs (same clock as video)                                 |
| `player_id`       | uint32  | local anonymized id                                                |
| `device`          | string  | `kb` \| `mouse` \| `pad` \| `vr_hmd` \| `vr_hand_L` \| `vr_hand_R` |
| `keymask`         | uint16  | bitwise state (see mapping below)                                  |
| `mouse_dx`        | float32 | pixels since last sample (optional if using yaw/pitch)             |
| `mouse_dy`        | float32 | pixels since last sample                                           |
| `pad_lx` `pad_ly` | float32 | −1..1                                                              |
| `pad_rx` `pad_ry` | float32 | −1..1                                                              |
| `pad_lt` `pad_rt` | float32 | 0..1                                                               |
| `pad_buttons`     | uint16  | bitmask (A,B,X,Y,LB,RB,Start,Back,…)                               |
| `yaw_deg`         | float32 | camera yaw (if available)                                          |
| `pitch_deg`       | float32 | camera pitch (if available)                                        |
| `hmd_px,py,pz`    | float32 | VR pose (optional)                                                 |
| `hmd_rx,ry,rz`    | float32 | VR Euler or quaternion components                                  |

**Keyboard `keymask` (uint16) mapping (baseline):**

```
bit0: W   bit1: A   bit2: S   bit3: D
bit4: Space(jump)   bit5: Ctrl(crouch)
bit6: LMB(fire)     bit7: RMB(aim)
bit8: R(reload)     bit9: E(interact)
bit10: Shift(sprint)  bit11–15: reserved
```

> If a title needs more granularity, add columns under a `custom_*` prefix—GAP readers must ignore unknown fields.

**Controls size @ 60–120 Hz:** **\~3–15 MB/hour**, depending on columns present.

---

## 5) Network stats (`netstats.parquet`, optional)

| `ts_us` int64 | `rtt_ms` float32 | `jitter_ms` float32 | `loss_pct` float32 | `uplink_kbps` int32 | `downlink_kbps` int32 |

---

## 6) Engagement labels (`labels.jsonl`, optional, opt‑in)

Client‑side, PII‑free, aggregated signals:

```json
{"ts_us":1722901234567,"type":"chat_agg","val":{"excitement":0.83,"toxicity":0.02,"sentiment":0.61}}
{"ts_us":1722901240123,"type":"voice_agg","val":{"rms":0.74}}
```

---

## 7) Integrity (`hashes.json`, required)

```json
{
  "sha256": {
    "video.ivf": "…",
    "controls.parquet": "…",
    "netstats.parquet": "…",
    "labels.jsonl": "…"
  },
  "frame_watermark_sample": [
    {"frame_idx": 120, "proof":"…"},
    {"frame_idx": 240, "proof":"…"}
  ]
}
```

---

## 8) Quality Acceptance Tests (QAT)

* **Timestamp sanity:** strictly monotonic; drift < **1 ms/min**.
* **Sync:** cross‑corr peak |Δ| < **20 ms** (report histogram).
* **Drops:** CFR missing frames < **0.5%**; list indices if exceeded.
* **Controls coverage:** ≥ 95% of frames have a control sample within **±8 ms**.
* **Rights:** valid license & consent refs present in `meta.json`.

---

## 9) Size per hour (720p60)

* **Video (AV1/HEVC CFR):** **\~1.8–3.6 GB/h** (depends on bitrate: 4–8 Mbps).
* **Controls (60–120 Hz):** **\~3–15 MB/h**.
* **Netstats/labels:** **<10 MB/h** combined, when present.

---

## Version History

### v0.2.0 (Current)
- Standardized on AV1/HEVC CFR (dropped raw frames for Phase-0)
- Minimum 60Hz controls, recommended 120Hz/240Hz for mouse
- Formal alignment guarantee: ±8ms for 95% of pairs
- Fixed keymask mapping for consistent partner integration
- Added QAT requirements and size calculations

### v0.1.x (Legacy)
- Initial drafts with raw frame support
- Variable control rates
- No formal alignment guarantees 