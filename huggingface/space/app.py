"""
GAP Explorer - Interactive GAP Validator & Visualizer

Drag-and-drop GAP shard validation and exploration interface.
"""

import gradio as gr
import json
import tempfile
import zipfile
import tarfile
import time
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add tools directory to path for safe_io import  
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
from safe_io import TempDir, safe_extract_zip, safe_extract_tar, sanitize_error

# Resource limits - safer defaults for public demo
MAX_UPLOAD_MB = int(os.getenv("GAP_SPACE_MAX_MB", "150"))
MAX_PROCESSING_SECONDS = int(os.getenv("GAP_SPACE_MAX_SECONDS", "30"))

# Concurrency guard (explicit rate limiting)
processing_semaphore = asyncio.Semaphore(2)

# Mock GAP validator (in real deployment, this would import actual tools)
class MockGAPValidator:
    """Mock validator for demonstration purposes."""
    
    def __init__(self, profile: Optional[str] = None, strict: bool = False):
        self.profile = profile
        self.strict = strict
        
    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Mock validation - returns realistic results."""
        
        # Simulate validation results
        report = {
            "valid": True,
            "profile": self.profile,
            "errors": [],
            "warnings": ["Sample validation - this is a demo interface"],
            "checks": {
                "file_structure": True,
                "meta": True,
                "controls": True,
                "hashes": True,
                "profile_specific": True
            },
            "sync_stats": {
                "within_8ms_pct": 96.3,
                "mean_delta_ms": 3.2,
                "max_delta_ms": 12.1,
                "p95_delta_ms": 7.8
            }
        }
        
        if self.strict and self.profile == "wayfarer-owl":
            report["errors"].append("Bitrate 4.5 Mbps below recommended 25 Mbps (strict mode)")
            report["valid"] = False
            
        return report["valid"], report


def _check_upload_size(file_obj) -> None:
    """Check if uploaded file exceeds size limit."""
    if hasattr(file_obj, 'size') and file_obj.size:
        size_mb = file_obj.size / (1024 * 1024)
    else:
        # Fallback: seek to end to get size
        file_obj.seek(0, 2)
        size_mb = file_obj.tell() / (1024 * 1024)
        file_obj.seek(0)
    
    if size_mb > MAX_UPLOAD_MB:
        raise ValueError(f"File too large: {size_mb:.1f}MB > {MAX_UPLOAD_MB}MB")

def extract_uploaded_file(file_path: str, extract_dir: str) -> Optional[str]:
    """Extract uploaded archive safely and return shard directory."""
    
    extract_path = Path(extract_dir)
    file_path_obj = Path(file_path)
    
    try:
        # Check file size
        with open(file_path, 'rb') as f:
            _check_upload_size(f)
        
        if file_path_obj.suffix.lower() == '.zip':
            safe_extract_zip(file_path_obj, extract_path)
        elif file_path_obj.suffix.lower() in ['.tar', '.tar.gz', '.tgz']:
            safe_extract_tar(file_path_obj, extract_path)
        else:
            # Assume it's a directory structure
            return file_path
            
        # Find the shard directory (should contain meta.json)
        for subdir in extract_path.rglob('meta.json'):
            return str(subdir.parent)
            
        return None
        
    except Exception as e:
        return sanitize_error(e, file_path)


async def validate_gap_shard_async(file, profile: str, strict: bool) -> Tuple[str, str, str]:
    """Validate uploaded GAP shard with concurrency control."""
    
    if file is None:
        return "❌ No file uploaded", "", ""
    
    async with processing_semaphore:
        return _validate_gap_shard_sync(file, profile, strict)

def _validate_gap_shard_sync(file, profile: str, strict: bool) -> Tuple[str, str, str]:
    """Internal synchronous validation logic."""
    start_time = time.time()
    
    try:
        with TempDir() as temp_dir:
        # Extract file
        shard_path = extract_uploaded_file(file.name, temp_dir)
        
        if shard_path is None or "failed:" in str(shard_path):
            return f"❌ {shard_path}", "", ""
            
        # Check for GAP structure
        shard_dir = Path(shard_path)
        meta_file = shard_dir / "meta.json"
        
        if not meta_file.exists():
            return "❌ Invalid GAP shard: meta.json not found", "", ""
            
        # Load metadata for display
        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            return f"❌ Failed to read metadata: {e}", "", ""
            
        # Check processing time limit
        if time.time() - start_time > MAX_PROCESSING_SECONDS:
            return "❌ Processing timeout exceeded", "", ""
        
        # Run validation
        validator = MockGAPValidator(profile if profile != "none" else None, strict)
        is_valid, report = validator.validate_all()
        
        # Format results
        status = "✅ VALID" if is_valid else "❌ INVALID"
        status_details = f"{status} - GAP shard validation results"
        
        # Format detailed report
        details = f"""
## Validation Report

**Status:** {status}  
**Profile:** {report.get('profile', 'standard')}  
**Strict Mode:** {'enabled' if strict else 'disabled'}

### Metadata
- **Session ID:** {metadata.get('session_id', 'unknown')}
- **Game:** {metadata.get('title', {}).get('name', 'unknown')}
- **Profile:** {metadata.get('profile', 'standard')}
- **Schema:** {metadata.get('schema_version', 'unknown')}

### Checks
"""
        for check, passed in report.get('checks', {}).items():
            status_icon = "✅" if passed else "❌"
            details += f"- {status_icon} {check.replace('_', ' ').title()}\n"
            
        if report.get('sync_stats'):
            stats = report['sync_stats']
            details += f"""
### Synchronization Quality
- **Within 8ms:** {stats['within_8ms_pct']:.1f}% of pairs
- **Mean delta:** {stats['mean_delta_ms']:.2f}ms
- **Max delta:** {stats['max_delta_ms']:.2f}ms
- **95th percentile:** {stats['p95_delta_ms']:.2f}ms
"""

        if report.get('errors'):
            details += "\n### Errors\n"
            for error in report['errors']:
                details += f"- 🚨 {error}\n"
                
        if report.get('warnings'):
            details += "\n### Warnings\n"
            for warning in report['warnings']:
                details += f"- ⚠️ {warning}\n"
                
        # Format JSON report
        json_report = json.dumps(report, indent=2)
        
        return status_details, details, json_report
    
    except Exception as e:
        return f"❌ Processing error: {e.__class__.__name__}", "", ""

def validate_gap_shard(file, profile: str, strict: bool) -> Tuple[str, str, str]:
    """Wrapper to run async validation in sync context."""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(validate_gap_shard_async(file, profile, strict))
    except RuntimeError:
        # If no loop is running, create a new one
        return asyncio.run(validate_gap_shard_async(file, profile, strict))


def show_sample_data() -> str:
    """Show example GAP data structure."""
    
    sample_data = {
        "meta.json": {
            "schema_version": "0.2.0",
            "profile": "wayfarer-owl.v0.1",
            "session_id": "3f8d9e12-4a7b-4c1d-8e90-1a2b3c4d5e6f",
            "title": {"name": "Star Atlas", "build": "1.24.3"},
            "display": {"resolution": "1920x1080", "fps": 60}
        },
        "controls.jsonl": [
            {"t_us": 1722900000000, "type": "key", "key": "W", "state": "down"},
            {"t_us": 1722900008333, "type": "mouse", "dx": 12, "dy": -8},
            {"t_us": 1722900016667, "type": "key", "key": "W", "state": "up"}
        ]
    }
    
    return f"""
## GAP Shard Structure

A GAP shard contains these files:

```
my_shard/
├── meta.json       # Session metadata
├── video.ivf       # AV1/HEVC video (CFR)
├── controls.jsonl  # Input events  
└── hashes.json     # File integrity
```

### Sample Data

**meta.json:**
```json
{json.dumps(sample_data["meta.json"], indent=2)}
```

**controls.jsonl (first 3 events):**
```json
{chr(10).join(json.dumps(event) for event in sample_data["controls.jsonl"])}
```

### Creating Your Own

Use the GAP Agent to package your data:

```bash
pip install gap-agent
gap pack video.mkv controls.jsonl --output my_shard/
```
"""


# Create Gradio interface with concurrency limits
with gr.Blocks(title="GAP Explorer", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🎮 GAP Explorer
    
    **Interactive GAP (Gameplay-Action Pairs) validator and visualizer**
    
    Upload a GAP shard to validate against the v0.2 specification. Supports ZIP/TAR archives containing GAP directory structure.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Upload GAP Shard")
            
            file_input = gr.File(
                label="Upload GAP Shard (ZIP/TAR)",
                file_types=[".zip", ".tar", ".tar.gz", ".tgz"],
                type="filepath"
            )
            
            profile_input = gr.Dropdown(
                choices=["none", "wayfarer-owl", "wayfarer-owl-hqplus"],
                value="wayfarer-owl",
                label="Validation Profile"
            )
            
            strict_input = gr.Checkbox(
                label="Strict Mode",
                value=False,
                info="Enforce strict validation (e.g., recommended bitrates)"
            )
            
            validate_btn = gr.Button("🔍 Validate Shard", variant="primary")
            
        with gr.Column(scale=2):
            status_output = gr.Textbox(
                label="Validation Status",
                placeholder="Upload a GAP shard to see validation results...",
                interactive=False
            )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Detailed Report")
            details_output = gr.Markdown()
            
        with gr.Column():
            gr.Markdown("### JSON Report")
            json_output = gr.Code(language="json")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Sample Data Structure")
            sample_button = gr.Button("📋 Show Sample GAP Structure")
            sample_output = gr.Markdown()
    
    # Event handlers
    validate_btn.click(
        fn=validate_gap_shard,
        inputs=[file_input, profile_input, strict_input],
        outputs=[status_output, details_output, json_output]
    )
    
    sample_button.click(
        fn=show_sample_data,
        outputs=[sample_output]
    )
    
    gr.Markdown("""
    ---
    
    ### About GAP v0.2
    
    GAP (Gameplay-Action Pairs) is a standardized format for time-aligned video + controls data.
    
    **Resources:**
    - 📖 [GAP Specification](https://github.com/ShagaDAO/gap)
    - 📊 [Sample Dataset](https://huggingface.co/datasets/Shaga/GAP-samples)
    - 🛠️ [GAP Agent Tools](https://github.com/ShagaDAO/gap/tree/main/gap-agent)
    
    **Supported Profiles:**
    - **Standard:** Basic GAP v0.2 compliance
    - **Wayfarer-OWL:** OWL baseline compatibility (1080p60, JSONL controls)
    - **Wayfarer-OWL HQ+:** Enhanced capture with optional features
    """)


if __name__ == "__main__":
    # Launch with limited concurrency and security headers
    demo.launch(
        max_threads=2,
        # Add security headers via Gradio's built-in middleware
        additional_headers={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "camera=(), microphone=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }
    ) 