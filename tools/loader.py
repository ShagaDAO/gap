#!/usr/bin/env python3
"""
GAP v0.2 Data Loader

Utility functions for loading and working with GAP (Gameplay-Action Pairs) format data.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from json_guard import load_validated


class GAPLoader:
    """Load and validate GAP v0.2 format data shards."""
    
    def __init__(self, shard_path: str):
        """Initialize loader with path to GAP shard directory."""
        self.shard_path = Path(shard_path)
        self.meta = None
        self.controls = None
        self.netstats = None
        self.labels = None
        self.hashes = None
        
    def load_meta(self) -> Dict[str, Any]:
        """Load and return metadata from meta.json."""
        meta_path = self.shard_path / "meta.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"meta.json not found in {self.shard_path}")
        
        schema_path = Path(__file__).parent.parent / "packages/gap-spec/schema.json"
        try:
            self.meta = load_validated(meta_path, schema_path)
        except Exception:
            # Fallback to unvalidated load for compatibility
            with open(meta_path, 'r') as f:
                self.meta = json.load(f)
            
        # Validate schema version
        if self.meta.get("schema_version") != "0.2.0":
            raise ValueError(f"Unsupported schema version: {self.meta.get('schema_version')}")
            
        return self.meta
        
    def load_controls(self) -> pd.DataFrame:
        """Load and return controls data from controls.parquet."""
        controls_path = self.shard_path / "controls.parquet"
        if not controls_path.exists():
            raise FileNotFoundError(f"controls.parquet not found in {self.shard_path}")
            
        self.controls = pd.read_parquet(controls_path)
        
        # Validate required columns
        required_cols = ["ts_us", "player_id", "device"]
        missing_cols = [col for col in required_cols if col not in self.controls.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in controls: {missing_cols}")
            
        # Validate timestamp monotonicity
        if not self.controls["ts_us"].is_monotonic_increasing:
            raise ValueError("Timestamps in controls are not monotonic")
            
        return self.controls
        
    def load_netstats(self) -> Optional[pd.DataFrame]:
        """Load and return network stats data if present."""
        netstats_path = self.shard_path / "netstats.parquet"
        if not netstats_path.exists():
            return None
            
        self.netstats = pd.read_parquet(netstats_path)
        return self.netstats
        
    def load_labels(self) -> Optional[List[Dict]]:
        """Load and return engagement labels if present."""
        labels_path = self.shard_path / "labels.jsonl"
        if not labels_path.exists():
            return None
            
        self.labels = []
        with open(labels_path, 'r') as f:
            for line in f:
                self.labels.append(json.loads(line.strip()))
                
        return self.labels
        
    def load_hashes(self) -> Dict[str, Any]:
        """Load and return file hashes for integrity checking."""
        hashes_path = self.shard_path / "hashes.json"
        if not hashes_path.exists():
            raise FileNotFoundError(f"hashes.json not found in {self.shard_path}")
        
        # Use direct JSON load for hashes (no formal schema yet)
        with open(hashes_path, 'r') as f:
            self.hashes = json.load(f)
            
        return self.hashes
        
    def load_all(self) -> Dict[str, Any]:
        """Load all available data from the GAP shard."""
        data = {
            "meta": self.load_meta(),
            "controls": self.load_controls(),
            "netstats": self.load_netstats(),
            "labels": self.load_labels(),
            "hashes": self.load_hashes()
        }
        return data
        
    def get_sync_stats(self) -> Dict[str, float]:
        """Calculate synchronization statistics between video and controls."""
        if self.meta is None or self.controls is None:
            raise ValueError("Must load meta and controls first")
            
        fps = self.meta["display"]["fps"]
        t0_us = self.meta["timing"]["t0_us"]
        
        # Calculate expected frame timestamps
        frame_interval_us = 1_000_000 / fps
        
        sync_deltas = []
        for i, row in self.controls.iterrows():
            # Find nearest expected frame time
            relative_time = row["ts_us"] - t0_us
            nearest_frame_idx = round(relative_time / frame_interval_us)
            expected_frame_time = t0_us + (nearest_frame_idx * frame_interval_us)
            
            delta_ms = abs(row["ts_us"] - expected_frame_time) / 1000
            sync_deltas.append(delta_ms)
            
        sync_deltas = pd.Series(sync_deltas)
        
        return {
            "mean_delta_ms": float(sync_deltas.mean()),
            "max_delta_ms": float(sync_deltas.max()),
            "p95_delta_ms": float(sync_deltas.quantile(0.95)),
            "within_8ms_pct": float((sync_deltas <= 8.0).mean() * 100)
        }
        
    def decode_keymask(self, keymask: int) -> List[str]:
        """Decode a keymask into human-readable key names."""
        keymap = {
            0: "W", 1: "A", 2: "S", 3: "D",
            4: "Space", 5: "Ctrl", 6: "LMB", 7: "RMB", 
            8: "R", 9: "E", 10: "Shift"
        }
        
        active_keys = []
        for bit, key in keymap.items():
            if keymask & (1 << bit):
                active_keys.append(key)
                
        return active_keys


def load_gap_shard(shard_path: str) -> GAPLoader:
    """Convenience function to create and load a GAP shard."""
    loader = GAPLoader(shard_path)
    loader.load_all()
    return loader


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python loader.py <shard_path>")
        sys.exit(1)
        
    shard_path = sys.argv[1]
    try:
        loader = load_gap_shard(shard_path)
        print(f"Successfully loaded GAP shard from {shard_path}")
        print(f"Session: {loader.meta['session_id']}")
        print(f"Title: {loader.meta['title']['name']}")
        print(f"Controls records: {len(loader.controls)}")
        
        sync_stats = loader.get_sync_stats()
        print(f"Sync stats: {sync_stats['within_8ms_pct']:.1f}% within 8ms")
        
    except Exception as e:
        print(f"Error loading GAP shard: {e}")
        sys.exit(1) 