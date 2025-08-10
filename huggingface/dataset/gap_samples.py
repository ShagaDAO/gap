"""
GAP Samples Dataset Script

Loads GAP v0.2 reference samples for Hugging Face datasets.
Supports both local files and external S3 URLs for larger shards.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

import datasets


_DESCRIPTION = """
GAP v0.2 Reference Samples - Gameplay Action Pairs for ML research.
Contains time-aligned video + controls data in GAP format with Wayfarer-OWL profile.
"""

_HOMEPAGE = "https://github.com/ShagaDAO/gap"

_LICENSE = "Research use only, redistribution restricted"

_URLS = {
    "default": {
        "star_atlas_100mb": "https://github.com/ShagaDAO/gap/releases/download/v0.2.2/star-atlas-100mb.tar.gz",
        "synthetic_shard": "https://github.com/ShagaDAO/gap/releases/download/v0.2.2/synthetic-shard.tar.gz"
    }
}


class GapSamplesDataset(datasets.GeneratorBasedBuilder):
    """GAP Samples dataset builder."""

    VERSION = datasets.Version("0.2.0")

    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="default",
            version=VERSION,
            description="GAP v0.2 reference samples with Wayfarer-OWL profile"
        ),
    ]

    DEFAULT_CONFIG_NAME = "default"

    def _info(self):
        """Dataset metadata and features."""
        
        features = datasets.Features({
            "session_id": datasets.Value("string"),
            "profile": datasets.Value("string"),
            "video_path": datasets.Value("string"),
            "controls_events": datasets.Sequence({
                "t_us": datasets.Value("int64"),
                "type": datasets.Value("string"),
                "key": datasets.Value("string"),
                "state": datasets.Value("string"),
                "dx": datasets.Value("float32"),
                "dy": datasets.Value("float32"),
            }),
            "metadata": {
                "schema_version": datasets.Value("string"),
                "title": {
                    "name": datasets.Value("string"),
                    "build": datasets.Value("string"),
                    "map": datasets.Value("string")
                },
                "display": {
                    "resolution": datasets.Value("string"),
                    "fps": datasets.Value("int32"),
                    "hdr": datasets.Value("bool")
                },
                "video": {
                    "codec": datasets.Value("string"),
                    "bitrate_mbps": datasets.Value("float32"),
                    "duration_sec": datasets.Value("int32"),
                    "file_size_mb": datasets.Value("float32")
                },
                "timing": {
                    "t0_us": datasets.Value("int64"),
                    "timezone": datasets.Value("string")
                }
            },
            "shard_path": datasets.Value("string"),
            "quality_stats": {
                "frame_count": datasets.Value("int32"),
                "control_events": datasets.Value("int32"),
                "sync_within_8ms_pct": datasets.Value("float32"),
                "timestamp_drift_ms": datasets.Value("float32")
            }
        })

        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage=_HOMEPAGE,
            license=_LICENSE,
        )

    def _split_generators(self, dl_manager):
        """Download and extract data files."""
        
        urls = _URLS[self.config.name]
        downloaded_files = dl_manager.download_and_extract(urls)
        
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "filepaths": downloaded_files,
                    "split": "train"
                }
            )
        ]

    def _generate_examples(self, filepaths: Dict[str, str], split: str):
        """Generate examples from GAP shards."""
        
        for shard_name, shard_path in filepaths.items():
            shard_dir = Path(shard_path)
            
            # Load metadata
            meta_path = shard_dir / "meta.json"
            if not meta_path.exists():
                continue
                
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
                
            # Load controls
            controls_path = shard_dir / "controls.jsonl"
            controls_events = []
            
            if controls_path.exists():
                with open(controls_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            event = json.loads(line.strip())
                            # Normalize event structure
                            normalized_event = {
                                "t_us": event.get("t_us", 0),
                                "type": event.get("type", ""),
                                "key": event.get("key", ""),
                                "state": event.get("state", ""),
                                "dx": float(event.get("dx", 0.0)),
                                "dy": float(event.get("dy", 0.0))
                            }
                            controls_events.append(normalized_event)
            
            # Find video file
            video_files = list(shard_dir.glob("video.*"))
            video_path = str(video_files[0]) if video_files else ""
            
            # Calculate quality stats
            quality_stats = self._calculate_quality_stats(metadata, controls_events)
            
            # Generate example
            example = {
                "session_id": metadata.get("session_id", ""),
                "profile": metadata.get("profile", ""),
                "video_path": video_path,
                "controls_events": controls_events,
                "metadata": {
                    "schema_version": metadata.get("schema_version", ""),
                    "title": metadata.get("title", {}),
                    "display": metadata.get("display", {}),
                    "video": metadata.get("video", {}),
                    "timing": metadata.get("timing", {})
                },
                "shard_path": str(shard_dir),
                "quality_stats": quality_stats
            }
            
            yield f"{shard_name}_{metadata.get('session_id', 'unknown')}", example

    def _calculate_quality_stats(self, metadata: Dict[str, Any], 
                                controls_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality statistics for the shard."""
        
        # Basic stats
        fps = metadata.get("display", {}).get("fps", 60)
        duration_sec = metadata.get("video", {}).get("duration_sec", 180)
        frame_count = fps * duration_sec
        
        # Control event analysis
        control_count = len(controls_events)
        
        # Estimate sync quality (simplified)
        if control_count > 0 and frame_count > 0:
            expected_rate = control_count / duration_sec
            sync_quality = min(100.0, (expected_rate / 120.0) * 100)  # Assume 120Hz target
        else:
            sync_quality = 0.0
            
        # Timestamp drift analysis (simplified)
        timestamp_drift = 0.0
        if len(controls_events) > 1:
            time_diffs = []
            for i in range(1, min(len(controls_events), 100)):
                diff = controls_events[i]["t_us"] - controls_events[i-1]["t_us"]
                time_diffs.append(diff)
            
            if time_diffs:
                expected_interval = 1_000_000 / 120  # 120Hz in microseconds
                avg_interval = sum(time_diffs) / len(time_diffs)
                timestamp_drift = abs(avg_interval - expected_interval) / 1000  # Convert to ms
        
        return {
            "frame_count": int(frame_count),
            "control_events": control_count,
            "sync_within_8ms_pct": sync_quality,
            "timestamp_drift_ms": timestamp_drift
        } 