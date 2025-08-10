#!/usr/bin/env python3
"""
GAP v0.2 Validator

Validates GAP (Gameplay-Action Pairs) shards against the v0.2 specification.
Performs Quality Acceptance Tests (QAT) as defined in the spec.
Supports profile-specific validation (e.g., wayfarer-owl).
"""

import json
import hashlib
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import click
import os

from loader import GAPLoader
try:
    from uri_loader import URILoader, is_uri
except ImportError:
    URILoader = None
    is_uri = lambda x: False


class GAPValidator:
    """Validate GAP v0.2 format shards against specification requirements."""
    
    def __init__(self, shard_path: str, profile: Optional[str] = None, strict: bool = False):
        """Initialize validator with GAP shard path and optional profile."""
        self.shard_path = Path(shard_path)
        self.loader = GAPLoader(shard_path)
        self.profile = profile
        self.strict = strict
        self.errors = []
        self.warnings = []
        
        # Configurable limits - safer defaults, env-tunable for power users
        self.max_video_bytes = int(os.getenv("GAP_MAX_VIDEO_BYTES", 512 * 1024**2))  # 512MB default
        self.max_jsonl_lines = int(os.getenv("GAP_MAX_JSONL_LINES", 5_000_000))  # 5M lines
        self.max_jsonl_bytes = int(os.getenv("GAP_MAX_JSONL_MB", 100)) * 1024**2  # 100MB default
        
    def error(self, msg: str):
        """Record a validation error."""
        self.errors.append(msg)
        
    def warning(self, msg: str):
        """Record a validation warning."""
        self.warnings.append(msg)
        
    def _check_file_size(self, file_path: Path, max_bytes: int) -> None:
        """Check if file exceeds size limit."""
        if file_path.exists() and file_path.stat().st_size > max_bytes:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            max_mb = max_bytes / (1024 * 1024)
            raise ValueError(f"{file_path.name} too large: {size_mb:.1f}MB > {max_mb:.1f}MB")
    
    def validate_file_structure(self) -> bool:
        """Validate required files are present and within size limits."""
        required_files = ["meta.json", "hashes.json"]
        required_video = ["video.ivf", "video.mkv"]
        required_controls = ["controls.parquet"]
        
        # Profile-specific file requirements
        if self.profile and "wayfarer-owl" in self.profile:
            # OWL profile uses JSONL for controls, not Parquet
            required_controls = ["controls.jsonl"] 
        
        # Check required files
        for file in required_files:
            if not (self.shard_path / file).exists():
                self.error(f"Required file missing: {file}")
                
        # Check video file (one of the formats) and size
        video_files = [f for f in required_video if (self.shard_path / f).exists()]
        if not video_files:
            self.error(f"No video file found. Expected one of: {required_video}")
        elif len(video_files) > 1:
            self.warning(f"Multiple video files found: {video_files}")
        else:
            # Check video file size
            video_path = self.shard_path / video_files[0]
            try:
                self._check_file_size(video_path, self.max_video_bytes)
            except ValueError as e:
                self.error(str(e))
            
        # Check controls file
        controls_found = False
        for file in required_controls:
            if (self.shard_path / file).exists():
                controls_found = True
                break
        if not controls_found:
            # Allow both formats but prefer profile-specific
            alt_controls = ["controls.parquet", "controls.jsonl"]
            alt_found = [f for f in alt_controls if (self.shard_path / f).exists()]
            if not alt_found:
                self.error(f"No controls file found. Expected one of: {alt_controls}")
            elif self.profile:
                self.warning(f"Controls file format doesn't match profile {self.profile}")
                
        return len(self.errors) == 0
        
    def validate_meta(self) -> bool:
        """Validate meta.json structure and content."""
        try:
            meta = self.loader.load_meta()
        except Exception as e:
            self.error(f"Failed to load meta.json: {e}")
            return False
            
        # Check required fields
        required_fields = {
            "schema_version": str,
            "session_id": str,
            "title": dict,
            "capture": dict,
            "display": dict,
            "timing": dict,
            "privacy": dict,
            "rights": dict
        }
        
        for field, expected_type in required_fields.items():
            if field not in meta:
                self.error(f"meta.json missing required field: {field}")
            elif not isinstance(meta[field], expected_type):
                self.error(f"meta.json field {field} should be {expected_type.__name__}")
                
        # Validate schema version
        if meta.get("schema_version") != "0.2.0":
            self.error(f"Unsupported schema_version: {meta.get('schema_version')}")
            
        # Profile-specific validation
        if self.profile:
            self.validate_profile_meta(meta)
            
        return len(self.errors) == 0
        
    def validate_profile_meta(self, meta: Dict[str, Any]) -> None:
        """Validate profile-specific metadata requirements."""
        if "wayfarer-owl" in self.profile:
            # Validate OWL-specific fields
            display = meta.get("display", {})
            
            # OWL baseline: 1080p60
            if self.profile == "wayfarer-owl":
                if display.get("resolution") != "1920x1080":
                    self.warning(f"OWL baseline expects 1920x1080, got {display.get('resolution')}")
                if display.get("fps") != 60:
                    self.warning(f"OWL baseline expects 60fps, got {display.get('fps')}")
                    
            # Check for profile field
            if "profile" not in meta:
                self.warning("Profile field missing from meta.json")
            elif not meta["profile"].startswith("wayfarer-owl"):
                self.warning(f"Profile mismatch: expected wayfarer-owl.*, got {meta['profile']}")
                
            # OWL-specific privacy requirements
            privacy = meta.get("privacy", {})
            if privacy.get("mic_recorded") is True:
                self.error("OWL profile prohibits mic recording")
                
    def validate_controls(self) -> bool:
        """Validate controls data structure and QAT requirements."""
        # Handle both Parquet and JSONL formats
        controls_parquet = self.shard_path / "controls.parquet"
        controls_jsonl = self.shard_path / "controls.jsonl"
        
        controls = None
        
        if controls_parquet.exists():
            try:
                controls = self.loader.load_controls()
            except Exception as e:
                self.error(f"Failed to load controls.parquet: {e}")
                return False
        elif controls_jsonl.exists():
            try:
                # Check JSONL file size and line count
                self._check_file_size(controls_jsonl, self.max_jsonl_bytes)
                
                # Load JSONL format with line limit (for OWL profile)
                controls_data = []
                line_count = 0
                with open(controls_jsonl, 'r') as f:
                    for line in f:
                        line_count += 1
                        if line_count > self.max_jsonl_lines:
                            raise ValueError(f"controls.jsonl exceeds {self.max_jsonl_lines} lines")
                        if line.strip():  # Skip empty lines
                            controls_data.append(json.loads(line.strip()))
                controls = pd.DataFrame(controls_data)
                
                # Validate JSONL-specific fields
                if "t_us" not in controls.columns:
                    self.error("JSONL controls missing t_us timestamp field")
                    return False
                    
                # Rename for compatibility with existing validation
                if "t_us" in controls.columns:
                    controls = controls.rename(columns={"t_us": "ts_us"})
                    
            except Exception as e:
                self.error(f"Failed to load controls.jsonl: {e}")
                return False
        else:
            self.error("No controls file found")
            return False
            
        # Check required columns (adjusted for format)
        required_columns = ["ts_us"]
        if self.profile and "wayfarer-owl" in self.profile:
            required_columns.extend(["type"])  # JSONL event format
        else:
            required_columns.extend(["player_id", "device"])  # Parquet format
            
        for col in required_columns:
            if col not in controls.columns:
                self.error(f"Controls missing required column: {col}")
                
        # QAT: Timestamp sanity - strictly monotonic
        if not controls["ts_us"].is_monotonic_increasing:
            self.error("QAT FAIL: Timestamps not strictly monotonic")
            
        # QAT: Check timestamp drift
        if len(controls) > 1:
            time_diff = controls["ts_us"].iloc[-1] - controls["ts_us"].iloc[0]
            duration_minutes = time_diff / (1_000_000 * 60)
            
            # Check for unrealistic drift (simple heuristic)
            expected_samples = duration_minutes * 60 * 60  # Assume ~60Hz minimum
            actual_samples = len(controls)
            
            if abs(actual_samples - expected_samples) / expected_samples > 0.1:
                self.warning(f"Potential timestamp drift: expected ~{expected_samples:.0f} samples, got {actual_samples}")
                
        # Store controls for sync validation
        self.loader.controls = controls
        
        return len(self.errors) == 0
        
    def validate_profile_specific(self) -> bool:
        """Run profile-specific validation checks."""
        if not self.profile:
            return True
            
        if "wayfarer-owl" in self.profile:
            return self.validate_owl_profile()
            
        return True
        
    def validate_owl_profile(self) -> bool:
        """Validate OWL-specific requirements."""
        # Check for CFR enforcement
        try:
            meta = self.loader.load_meta()
            video_info = meta.get("video", {})
            if not video_info.get("cfr_enforced"):
                self.warning("OWL profile strongly recommends CFR enforcement")
                
            # Check bitrate expectations
            bitrate = video_info.get("bitrate_mbps")
            if bitrate and bitrate < 20:
                msg = f"OWL baseline expects ~25 Mbps, got {bitrate} Mbps (advisory)"
                if self.strict:
                    self.error(msg.replace(" (advisory)", ""))
                else:
                    self.warning(msg)
                
        except Exception as e:
            self.warning(f"Could not validate OWL video requirements: {e}")
            
        # Check controls format for OWL
        controls_jsonl = self.shard_path / "controls.jsonl"
        if controls_jsonl.exists():
            try:
                with open(controls_jsonl, 'r') as f:
                    first_line = json.loads(f.readline().strip())
                    
                # Validate event structure
                if "type" not in first_line:
                    self.error("OWL controls missing 'type' field")
                if "t_us" not in first_line:
                    self.error("OWL controls missing 't_us' timestamp")
                    
                # Check for expected event types
                valid_types = ["key", "mouse", "pad"]
                if first_line.get("type") not in valid_types:
                    self.warning(f"Unexpected event type: {first_line.get('type')}")
                    
            except Exception as e:
                self.warning(f"Could not validate OWL controls format: {e}")
                
        return len(self.errors) == 0
        
    def validate_hashes(self) -> bool:
        """Validate file integrity using hashes.json."""
        try:
            hashes = self.loader.load_hashes()
        except Exception as e:
            self.error(f"Failed to load hashes.json: {e}")
            return False
            
        if "sha256" not in hashes:
            self.error("hashes.json missing sha256 section")
            return False
            
        # Verify file hashes
        for filename, expected_hash in hashes["sha256"].items():
            file_path = self.shard_path / filename
            if not file_path.exists():
                self.warning(f"Hash entry for non-existent file: {filename}")
                continue
                
            # Calculate actual hash
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            actual_hash = sha256_hash.hexdigest()
            
            if actual_hash != expected_hash:
                self.error(f"Hash mismatch for {filename}: expected {expected_hash}, got {actual_hash}")
                
        return len(self.errors) == 0
        
    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all validation checks and return results."""
        self.errors = []
        self.warnings = []
        
        # Run validation steps
        file_structure_ok = self.validate_file_structure()
        meta_ok = self.validate_meta() if file_structure_ok else False
        controls_ok = self.validate_controls() if file_structure_ok else False
        hashes_ok = self.validate_hashes() if file_structure_ok else False
        profile_ok = self.validate_profile_specific()
        
        # Generate report
        is_valid = len(self.errors) == 0
        
        report = {
            "valid": is_valid,
            "profile": self.profile,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks": {
                "file_structure": file_structure_ok,
                "meta": meta_ok,
                "controls": controls_ok,
                "hashes": hashes_ok,
                "profile_specific": profile_ok
            }
        }
        
        # Add sync stats if available (skip for JSONL-only controls for now)
        try:
            if controls_ok and meta_ok and hasattr(self.loader, 'meta') and self.loader.meta:
                # Only run sync stats for Parquet format or if we can convert
                if (self.shard_path / "controls.parquet").exists():
                    report["sync_stats"] = self.loader.get_sync_stats()
        except:
            pass
            
        return is_valid, report


@click.command()
@click.argument('shard_path', type=click.Path(exists=True))
@click.option('--profile', type=str, help='Validate against specific profile (e.g., wayfarer-owl)')
@click.option('--strict', is_flag=True, help='Enforce strict validation (e.g., recommended bitrates)')
@click.option('--json', 'output_json', is_flag=True, help='Output results as JSON')
@click.option('--quiet', '-q', is_flag=True, help='Only show errors and warnings')
def main(shard_path: str, profile: Optional[str], strict: bool, output_json: bool, quiet: bool):
    """Validate a GAP v0.2 shard against specification requirements."""
    
    # Handle URI schemes (hf://, s3://, etc.)
    original_path = shard_path
    if URILoader and is_uri(shard_path):
        if not quiet:
            print(f"Loading from URI: {shard_path}")
        try:
            shard_path = URILoader.load_from_uri(shard_path)
            if not quiet:
                print(f"Downloaded to: {shard_path}")
        except Exception as e:
            print(f"❌ Failed to load from URI: {e}", err=True)
            raise click.Abort()
    
    validator = GAPValidator(shard_path, profile, strict)
    is_valid, report = validator.validate_all()
    
    if output_json:
        print(json.dumps(report, indent=2))
        return
        
    # Human-readable output
    if not quiet:
        print(f"Validating GAP shard: {shard_path}")
        if profile:
            print(f"Profile: {profile}")
        print("=" * 50)
        
    if is_valid:
        print("✅ VALID - GAP shard passes all validation checks")
    else:
        print("❌ INVALID - GAP shard has validation errors")
        
    if report["errors"]:
        print(f"\n🚨 Errors ({len(report['errors'])}):")
        for error in report["errors"]:
            print(f"  - {error}")
            
    if report["warnings"]:
        print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
        for warning in report["warnings"]:
            print(f"  - {warning}")
            
    if "sync_stats" in report and not quiet:
        stats = report["sync_stats"]
        print(f"\n📊 Sync Statistics:")
        print(f"  - {stats['within_8ms_pct']:.1f}% of controls within ±8ms")
        print(f"  - Mean delta: {stats['mean_delta_ms']:.2f}ms")
        print(f"  - Max delta: {stats['max_delta_ms']:.2f}ms")
        print(f"  - 95th percentile: {stats['p95_delta_ms']:.2f}ms")
        
    if not quiet:
        print(f"\nChecks completed:")
        for check, passed in report["checks"].items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")


if __name__ == "__main__":
    main() 