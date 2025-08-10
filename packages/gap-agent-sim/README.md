# GAP Agent (Simulation Preview)

> **SIMULATION‑ONLY PREVIEW**  
> This package prints what it *would* capture/encrypt/upload, then exits.  
> Network, crypto, and verification are intentionally unimplemented in this preview.

**Open-source client prototype for GAP data packaging, encryption, and upload**

## What's Public (This Module)

✅ **GAP shard packaging** - Manifest creation, hashing, validation  
✅ **Device encryption** - Envelope X25519 → AES-GCM  
✅ **Ring buffer management** - Local disk buffering  
✅ **Upload scheduling** - Idle-only, token-bucket throttling  
✅ **Receipt verification** - Ingest confirmation and validation  

## What Stays Closed (Shaga Node Core)

🔒 Real-time streaming  
🔒 Watermark embedding  
🔒 PoR challenge cadence  
🔒 DRM plumbing  
🔒 Gameplay session management  

## Installation

```bash
pip install gap-agent
```

## CLI Usage

```bash
# Package raw video + controls into encrypted GAP shard
gap pack video.mkv controls.jsonl --output my_shard/ --encrypt

# Upload shard to S3-compatible storage (idle-only)
gap upload my_shard/ --endpoint s3://my-bucket --throttle 10MB/s

# Verify upload integrity and receipt
gap verify my_shard/ --receipt receipt.json

# Validate existing shard
gap validate my_shard/ --profile wayfarer-owl --strict
```

## Library Usage

```python
from gap_agent import ShardPackager, Uploader, Verifier

# Package GAP shard
packager = ShardPackager(encryption=True)
manifest = packager.pack(
    video_path="video.mkv",
    controls_path="controls.jsonl", 
    output_dir="my_shard/"
)

# Upload with throttling
uploader = Uploader(endpoint="s3://my-bucket")
receipt = uploader.upload(manifest, idle_only=True, max_rate="10MB/s")

# Verify integrity
verifier = Verifier()
verified = verifier.verify_receipt(receipt)
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Shaga Node    │───▶│   GAP Agent     │───▶│  S3-Compatible  │
│     (closed)    │    │    (public)     │    │    Storage      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Partner Audits  │
                       │ & Integration   │
                       └─────────────────┘
```

## Security Model

- **Envelope encryption**: X25519 key exchange → AES-256-GCM
- **Local buffering**: Ring buffer with configurable retention
- **Upload scheduling**: Respects system idle state and bandwidth limits
- **Receipt verification**: Cryptographic proof of successful ingest

## Integration

Gap Agent is designed to be called by closed systems while remaining fully auditable:

```bash
# Shaga Node Core shells out to gap-agent
gap pack $VIDEO $CONTROLS --output $SHARD_DIR --encrypt --profile wayfarer-owl
gap upload $SHARD_DIR --endpoint $STORAGE_URL --idle-only
```

## Documentation

- [**Packaging Guide**](docs/packaging.md) - Creating GAP shards
- [**Encryption Spec**](docs/encryption.md) - Security implementation  
- [**Storage Tiers**](docs/storage-tiers.md) - S3/R2/B2 compatibility
- [**API Reference**](docs/api.md) - Library interface

## Contributing

This module follows strict open-source principles:
- No proprietary dependencies
- Full encryption/packaging transparency  
- Partner-auditable data paths
- MIT licensed

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

---

*"Shaga Node is closed, but the way we package, encrypt, and move GAP is open and verifiable."* 