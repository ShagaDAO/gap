#!/usr/bin/env python3
"""
GAP v0.2 Sample Data Loader Example

Demonstrates how to load and work with GAP format data using the provided sample files.
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path

# Add tools directory to path so we can import the loader
sys.path.append(str(Path(__file__).parent.parent / "tools"))
from loader import GAPLoader


def load_sample_data():
    """Load and demonstrate working with GAP sample data."""
    
    # Path to sample directory
    samples_dir = Path(__file__).parent.parent / "samples"
    
    print("GAP v0.2 Sample Data Loader")
    print("=" * 40)
    
    # Load sample metadata
    print("\n📄 Loading sample metadata...")
    with open(samples_dir / "meta.json", 'r') as f:
        meta = json.load(f)
    
    print(f"  Session ID: {meta['session_id']}")
    print(f"  Game: {meta['title']['name']} v{meta['title']['build']}")
    print(f"  Map: {meta['title']['map']}")
    print(f"  Resolution: {meta['display']['resolution']} @ {meta['display']['fps']}fps")
    print(f"  GPU: {meta['capture']['gpu']}")
    
    # Load sample controls (JSONL format for samples)
    print("\n🎮 Loading sample controls...")
    controls_data = []
    with open(samples_dir / "controls.jsonl", 'r') as f:
        for line in f:
            controls_data.append(json.loads(line.strip()))
    
    controls_df = pd.DataFrame(controls_data)
    print(f"  Controls records: {len(controls_df)}")
    print(f"  Time range: {controls_df['ts_us'].min()} to {controls_df['ts_us'].max()}")
    print(f"  Devices: {controls_df['device'].unique().tolist()}")
    
    # Decode some keymask examples
    print("\n🔍 Decoding keymasks...")
    
    # Import the keymask decoder
    loader = GAPLoader("dummy")  # Just to access the decode method
    
    for i, row in controls_df.iterrows():
        if 'keymask' in row and pd.notna(row['keymask']):
            keys = loader.decode_keymask(int(row['keymask']))
            print(f"  Record {i+1}: keymask {row['keymask']} = {keys}")
    
    # Load sample frame index
    print("\n🎬 Loading sample frame index...")
    frames_df = pd.read_csv(samples_dir / "frames.csv")
    print(f"  Frame records: {len(frames_df)}")
    print(f"  Codec: {frames_df['codec'].iloc[0]}")
    print(f"  Resolution: {frames_df['width'].iloc[0]}x{frames_df['height'].iloc[0]}")
    
    # Show temporal alignment
    print("\n⏱️  Temporal alignment analysis...")
    
    # Convert frame timestamps to microseconds for comparison
    frame_times_us = frames_df['ts_ms'] * 1000
    control_times_us = controls_df['ts_us']
    
    print(f"  Frame timestamps: {frame_times_us.min()} to {frame_times_us.max()} μs")
    print(f"  Control timestamps: {control_times_us.min()} to {control_times_us.max()} μs")
    
    # Calculate sync deltas for demonstration
    sync_deltas = []
    for frame_time in frame_times_us:
        # Find nearest control sample
        nearest_control_idx = (control_times_us - frame_time).abs().idxmin()
        nearest_control_time = control_times_us.iloc[nearest_control_idx]
        delta_ms = abs(frame_time - nearest_control_time) / 1000
        sync_deltas.append(delta_ms)
    
    sync_deltas = pd.Series(sync_deltas)
    print(f"  Mean sync delta: {sync_deltas.mean():.2f}ms")
    print(f"  Max sync delta: {sync_deltas.max():.2f}ms")
    print(f"  Samples within 8ms: {(sync_deltas <= 8.0).mean() * 100:.1f}%")
    
    # Show data structure summary
    print("\n📊 Data Structure Summary:")
    print("  Required files:")
    print("    ✅ meta.json - session metadata")
    print("    ✅ controls.parquet - input controls (sample as JSONL)")
    print("    ✅ video.ivf/mkv - AV1/HEVC video stream")
    print("    ✅ hashes.json - integrity verification")
    print("  Optional files:")
    print("    📄 netstats.parquet - network statistics")
    print("    📄 labels.jsonl - engagement labels")
    
    # Show size estimates
    print("\n💾 Size Estimates (720p60, per hour):")
    print("    Video (AV1): ~1.8-2.7 GB")
    print("    Video (HEVC): ~2.7-3.6 GB") 
    print("    Controls (60-120Hz): ~3-15 MB")
    print("    Metadata + hashes: <1 MB")
    
    print("\n✅ Sample data loaded successfully!")
    return meta, controls_df, frames_df


def demonstrate_keymask_decoding():
    """Demonstrate keymask decoding with various examples."""
    
    print("\n🔑 Keymask Decoding Examples")
    print("=" * 30)
    
    loader = GAPLoader("dummy")
    
    # Example keymasks
    examples = [
        (5, "W + A (forward + strafe left)"),
        (1029, "A + Shift (sprint strafe left)"),
        (1024, "Shift only (sprint)"),
        (64, "LMB (left mouse button)"),
        (192, "LMB + RMB (fire + aim)"),
        (0, "No keys pressed")
    ]
    
    print("Keymask mapping (uint16):")
    print("  bit0: W     bit1: A     bit2: S     bit3: D")
    print("  bit4: Space bit5: Ctrl  bit6: LMB   bit7: RMB")
    print("  bit8: R     bit9: E     bit10: Shift")
    print()
    
    for keymask, description in examples:
        keys = loader.decode_keymask(keymask)
        print(f"  {keymask:4d} (0b{keymask:011b}) = {keys} - {description}")


def show_qa_tests():
    """Show Quality Acceptance Test requirements."""
    
    print("\n🧪 Quality Acceptance Tests (QAT)")
    print("=" * 35)
    print("GAP v0.2 shards must pass these tests:")
    print()
    print("📊 Timestamp Requirements:")
    print("  ✓ Strictly monotonic timestamps")
    print("  ✓ Drift < 1ms/minute")
    print()
    print("🎯 Synchronization:")
    print("  ✓ Cross-correlation peak |Δ| < 20ms")
    print("  ✓ ≥95% of controls within ±8ms of nearest frame")
    print()
    print("🎬 Video Quality:")
    print("  ✓ CFR (Constant Frame Rate)")
    print("  ✓ Missing frames < 0.5%")
    print()
    print("📜 Legal Compliance:")
    print("  ✓ Valid license & consent references in meta.json")
    print()
    print("🔐 Integrity:")
    print("  ✓ SHA-256 hashes match for all files")
    print("  ✓ Frame watermark samples present")


if __name__ == "__main__":
    try:
        meta, controls, frames = load_sample_data()
        demonstrate_keymask_decoding()
        show_qa_tests()
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        sys.exit(1) 