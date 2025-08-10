"""
GAP Shard Packager

Handles GAP shard creation, manifest generation, and hashing.
"""

import json
import uuid
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
import shutil

from .crypto import EncryptionManager


class ShardPackager:
    """Packages raw video + controls into GAP shards with encryption."""
    
    def __init__(self, encryption: bool = False, profile: str = "standard", 
                 compression: bool = False):
        """Initialize packager with configuration."""
        self.encryption = encryption
        self.profile = profile
        self.compression = compression
        self.encryption_manager = EncryptionManager() if encryption else None
        
    def pack(self, video_path: str, controls_path: str, output_dir: str,
             custom_meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Package video + controls into a GAP shard."""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        session_id = str(uuid.uuid4())
        
        # Generate metadata
        meta = self._generate_metadata(session_id, video_path, controls_path, custom_meta)
        
        # Copy/process files
        video_dest, controls_dest = self._process_files(
            video_path, controls_path, output_path
        )
        
        # Generate hashes
        hashes = self._generate_hashes([video_dest, controls_dest, output_path / "meta.json"])
        
        # Save metadata and hashes
        with open(output_path / "meta.json", 'w') as f:
            json.dump(meta, f, indent=2)
            
        with open(output_path / "hashes.json", 'w') as f:
            json.dump(hashes, f, indent=2)
            
        # Handle encryption if enabled
        encryption_info = None
        if self.encryption and self.encryption_manager:
            encryption_info = self._encrypt_shard(output_path)
            
        # Calculate total size
        total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
        
        return {
            "manifest_path": str(output_path / "meta.json"),
            "session_id": session_id,
            "total_size_mb": total_size / (1024 * 1024),
            "files": [str(f.relative_to(output_path)) for f in output_path.rglob('*') if f.is_file()],
            "encryption_info": encryption_info,
            "profile": self.profile
        }
        
    def _generate_metadata(self, session_id: str, video_path: str, 
                          controls_path: str, custom_meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate GAP metadata."""
        
        video_path_obj = Path(video_path)
        controls_path_obj = Path(controls_path)
        
        meta = {
            "schema_version": "0.2.0",
            "profile": f"{self.profile}.v0.1",
            "session_id": session_id,
            "tool": {"name": "gap-agent", "version": "0.1.0"},
            "title": {"name": "Unknown", "build": "unknown", "map": "unknown"},
            "capture": {
                "host_os": "Unknown",
                "gpu": "Unknown", 
                "driver": "unknown",
                "encoder": "gap-agent",
                "clock": "monotonic_us"
            },
            "display": {
                "resolution": "1920x1080",  # Default, should be detected
                "fps": 60,
                "hdr": False,
                "colorspace": "sRGB",
                "bit_depth": 8
            },
            "video": {
                "codec": video_path_obj.suffix[1:].upper(),
                "bitrate_mbps": 0.0,  # Should be calculated
                "cfr_enforced": True,
                "duration_sec": 0,  # Should be detected
                "file_size_mb": video_path_obj.stat().st_size / (1024 * 1024)
            },
            "controls": {
                "devices": ["kbm"],
                "format": "jsonl_events" if controls_path_obj.suffix == ".jsonl" else "parquet",
                "timestamp_clock": "monotonic_us",
                "sample_rate_hz": 60  # Should be calculated
            },
            "audio": {"present": False},
            "privacy": {
                "mic_recorded": False,
                "overlays": False,
                "single_player_only": True,
                "consent": "gap-agent-packaged"
            },
            "timing": {"t0_us": int(time.time() * 1_000_000), "timezone": "UTC"},
            "rights": {
                "publisher_license": "user-provided",
                "player_consent_id": "gap-agent-session"
            }
        }
        
        # Merge custom metadata if provided
        if custom_meta:
            meta.update(custom_meta)
            
        return meta
        
    def _process_files(self, video_path: str, controls_path: str, 
                      output_path: Path) -> tuple[Path, Path]:
        """Copy and optionally process input files."""
        
        video_src = Path(video_path)
        controls_src = Path(controls_path)
        
        # Determine output filenames
        if video_src.suffix.lower() in ['.mkv', '.mp4']:
            video_dest = output_path / "video.mkv"
        elif video_src.suffix.lower() in ['.ivf']:
            video_dest = output_path / "video.ivf"
        else:
            video_dest = output_path / f"video{video_src.suffix}"
            
        if controls_src.suffix.lower() == '.jsonl':
            controls_dest = output_path / "controls.jsonl"
        elif controls_src.suffix.lower() == '.parquet':
            controls_dest = output_path / "controls.parquet"
        else:
            controls_dest = output_path / f"controls{controls_src.suffix}"
            
        # Copy files (TODO: add compression/processing)
        shutil.copy2(video_src, video_dest)
        shutil.copy2(controls_src, controls_dest)
        
        return video_dest, controls_dest
        
    def _generate_hashes(self, files: List[Path]) -> Dict[str, Any]:
        """Generate SHA-256 hashes for shard files."""
        
        hashes = {"sha256": {}}
        
        for file_path in files:
            if file_path.exists():
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                hashes["sha256"][file_path.name] = sha256_hash.hexdigest()
                
        # Add frame watermark samples (placeholder)
        hashes["frame_watermark_sample"] = [
            {"frame_idx": 60, "proof": "gap_agent_wm_001"},
            {"frame_idx": 120, "proof": "gap_agent_wm_002"},
            {"frame_idx": 180, "proof": "gap_agent_wm_003"}
        ]
        
        return hashes
        
    def _encrypt_shard(self, shard_path: Path) -> Dict[str, Any]:
        """Encrypt shard files using envelope encryption."""
        
        if not self.encryption_manager:
            raise ValueError("Encryption manager not initialized")
            
        # Encrypt each file in place
        encrypted_files = []
        for file_path in shard_path.rglob('*'):
            if file_path.is_file() and file_path.name != "encryption.json":
                encrypted_path = self.encryption_manager.encrypt_file(file_path)
                encrypted_files.append(str(encrypted_path.relative_to(shard_path)))
                
        # Save encryption metadata
        encryption_info = {
            "algorithm": "X25519-AES256-GCM",
            "key_fingerprint": self.encryption_manager.get_key_fingerprint(),
            "encrypted_files": encrypted_files,
            "envelope_key": self.encryption_manager.get_envelope_key()
        }
        
        with open(shard_path / "encryption.json", 'w') as f:
            json.dump(encryption_info, f, indent=2)
            
        return encryption_info 