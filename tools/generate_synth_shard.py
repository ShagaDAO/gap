#!/usr/bin/env python3
"""
GAP Synthetic Shard Generator

Creates rights-free synthetic GAP shards for CI testing and validation.
Generates color bars video + realistic synthetic controls without any real footage.
"""

import json
import uuid
import time
import random
import math
from pathlib import Path
from typing import Dict, List, Any
import click


def generate_meta(session_id: str, duration_sec: int, profile: str = "synthetic") -> Dict[str, Any]:
    """Generate synthetic metadata."""
    return {
        "schema_version": "0.2.0",
        "profile": f"{profile}.v0.1",
        "session_id": session_id,
        "tool": {"name": "gap-synth-generator", "version": "1.0"},
        "title": {"name": "Synthetic Game", "build": "test", "map": "colorbar_arena"},
        "capture": {
            "host_os": "Ubuntu 22.04",
            "gpu": "Virtual",
            "driver": "synthetic",
            "encoder": "synthetic_av1",
            "clock": "monotonic_us"
        },
        "display": {
            "resolution": "640x480",
            "fps": 30,
            "hdr": False,
            "colorspace": "sRGB",
            "bit_depth": 8
        },
        "video": {
            "codec": "synthetic",
            "bitrate_mbps": 1.0,
            "cfr_enforced": True,
            "duration_sec": duration_sec,
            "file_size_mb": duration_sec * 1.0 / 8  # 1 Mbps
        },
        "controls": {
            "devices": ["kbm"],
            "format": "jsonl_events",
            "timestamp_clock": "monotonic_us",
            "sample_rate_hz": 60
        },
        "audio": {"present": False},
        "privacy": {
            "mic_recorded": False,
            "overlays": False,
            "single_player_only": True,
            "consent": "synthetic-data"
        },
        "timing": {"t0_us": int(time.time() * 1_000_000), "timezone": "UTC"},
        "geo": {"h3": "8a0000000000000"},  # Null island
        "rights": {
            "publisher_license": "synthetic-public-domain", 
            "player_consent_id": "synthetic-consent"
        }
    }


def generate_synthetic_controls(duration_sec: int, fps: int = 30, control_hz: int = 60) -> List[Dict[str, Any]]:
    """Generate realistic synthetic control events."""
    events = []
    start_time = int(time.time() * 1_000_000)
    
    # Calculate event timing
    control_interval_us = 1_000_000 // control_hz
    frame_interval_us = 1_000_000 // fps
    
    # State tracking
    keys_pressed = set()
    mouse_x = 0.0
    mouse_y = 0.0
    
    # Generate events
    for i in range(duration_sec * control_hz):
        ts_us = start_time + (i * control_interval_us)
        
        # Generate realistic movement patterns
        phase = (i / control_hz) * 2 * math.pi  # One cycle per second
        
        # Simulate WASD movement (sine wave patterns)
        if random.random() < 0.1:  # 10% chance of key event
            key_options = ["W", "A", "S", "D", "SPACE", "LMB", "RMB"]
            key = random.choice(key_options)
            
            if key in keys_pressed:
                # Key release
                events.append({
                    "t_us": ts_us,
                    "type": "key",
                    "key": key,
                    "state": "up"
                })
                keys_pressed.remove(key)
            else:
                # Key press
                events.append({
                    "t_us": ts_us,
                    "type": "key", 
                    "key": key,
                    "state": "down"
                })
                keys_pressed.add(key)
        
        # Generate mouse movement (smooth camera motion)
        if random.random() < 0.8:  # 80% chance of mouse movement
            dx = int(10 * math.sin(phase) + random.uniform(-2, 2))
            dy = int(5 * math.cos(phase * 0.7) + random.uniform(-1, 1))
            
            if dx != 0 or dy != 0:
                events.append({
                    "t_us": ts_us,
                    "type": "mouse",
                    "dx": dx,
                    "dy": dy
                })
    
    return events


def generate_hashes(files: List[str]) -> Dict[str, Any]:
    """Generate synthetic hashes for integrity checking."""
    import hashlib
    
    hashes = {"sha256": {}}
    for filename in files:
        # Generate deterministic but fake hash
        fake_content = f"synthetic_content_{filename}_{time.time()}"
        fake_hash = hashlib.sha256(fake_content.encode()).hexdigest()
        hashes["sha256"][filename] = fake_hash
    
    # Add frame watermark samples
    hashes["frame_watermark_sample"] = [
        {"frame_idx": 30, "proof": "synthetic_wm_001"},
        {"frame_idx": 60, "proof": "synthetic_wm_002"},
        {"frame_idx": 90, "proof": "synthetic_wm_003"}
    ]
    
    hashes["validation_info"] = {
        "total_size_mb": 2.5,
        "video_size_mb": 2.0,
        "controls_size_kb": 500,
        "meta_size_kb": 3,
        "created_for": "synthetic_testing"
    }
    
    return hashes


@click.command()
@click.option('--duration', default=30, help='Duration in seconds')
@click.option('--profile', default='synthetic', help='Profile name')
@click.option('--output', default='synthetic_shard', help='Output directory name')
def main(duration: int, profile: str, output: str):
    """Generate a synthetic GAP shard for testing."""
    
    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True)
    
    session_id = str(uuid.uuid4())
    
    print(f"Generating synthetic GAP shard...")
    print(f"  Duration: {duration} seconds")
    print(f"  Profile: {profile}")
    print(f"  Output: {output_dir}")
    print(f"  Session ID: {session_id}")
    
    # Generate metadata
    meta = generate_meta(session_id, duration, profile)
    with open(output_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    
    # Generate controls
    controls = generate_synthetic_controls(duration)
    with open(output_dir / "controls.jsonl", "w") as f:
        for event in controls:
            f.write(json.dumps(event) + "\n")
    
    # Generate hashes
    files = ["video.synthetic", "controls.jsonl", "meta.json"]
    hashes = generate_hashes(files)
    with open(output_dir / "hashes.json", "w") as f:
        json.dump(hashes, f, indent=2)
    
    # Create a placeholder video file
    video_placeholder = output_dir / "video.synthetic"
    with open(video_placeholder, "w") as f:
        f.write(f"# Synthetic Video Placeholder\n")
        f.write(f"# Duration: {duration} seconds\n")
        f.write(f"# Resolution: 640x480 @ 30fps\n")
        f.write(f"# This would contain synthetic color bars or test patterns\n")
        f.write(f"# File size would be approximately {duration * 0.125:.1f} MB\n")
    
    # Create README
    readme_content = f"""# Synthetic GAP Shard

This is a synthetic GAP shard generated for testing purposes.

## Contents
- Duration: {duration} seconds
- Profile: {profile}
- Control events: {len(controls)}
- Video: Synthetic color bars (placeholder)

## Usage
This shard is designed for:
- CI/CD testing
- Validator development
- Schema validation
- Rights-free integration testing

## Validation
```bash
python3 ../../tools/validate.py --profile {profile} .
```

Generated at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
"""
    
    with open(output_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print(f"✅ Synthetic shard generated successfully!")
    print(f"   Files: {list(output_dir.glob('*'))}")
    print(f"   Control events: {len(controls)}")
    print(f"   Ready for validation testing")


if __name__ == "__main__":
    main() 