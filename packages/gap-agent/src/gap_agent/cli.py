#!/usr/bin/env python3
"""
GAP Agent CLI - Command line interface for GAP shard operations
"""

import click
import json
from pathlib import Path
from typing import Optional

from .packager import ShardPackager
from .uploader import Uploader
from .verifier import Verifier


@click.group()
@click.version_option()
def gap():
    """GAP Agent - Open GAP shard packaging, encryption, and upload tool."""
    pass


@gap.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.argument('controls_path', type=click.Path(exists=True))
@click.option('--output', '-o', required=True, help='Output directory for GAP shard')
@click.option('--encrypt', is_flag=True, help='Enable encryption (X25519 + AES-GCM)')
@click.option('--profile', default='standard', help='GAP profile (wayfarer-owl, standard)')
@click.option('--compress', is_flag=True, help='Compress video if needed')
@click.option('--meta', type=click.Path(exists=True), help='Custom metadata JSON file')
def pack(video_path: str, controls_path: str, output: str, encrypt: bool, 
         profile: str, compress: bool, meta: Optional[str]):
    """Package video + controls into a GAP shard."""
    
    click.echo(f"📦 Packaging GAP shard...")
    click.echo(f"   Video: {video_path}")
    click.echo(f"   Controls: {controls_path}")
    click.echo(f"   Output: {output}")
    click.echo(f"   Profile: {profile}")
    click.echo(f"   Encryption: {'enabled' if encrypt else 'disabled'}")
    
    try:
        packager = ShardPackager(
            encryption=encrypt,
            profile=profile,
            compression=compress
        )
        
        # Load custom metadata if provided
        custom_meta = None
        if meta:
            with open(meta, 'r') as f:
                custom_meta = json.load(f)
        
        manifest = packager.pack(
            video_path=video_path,
            controls_path=controls_path,
            output_dir=output,
            custom_meta=custom_meta
        )
        
        click.echo(f"✅ GAP shard packaged successfully!")
        click.echo(f"   Manifest: {manifest['manifest_path']}")
        click.echo(f"   Session ID: {manifest['session_id']}")
        click.echo(f"   Size: {manifest['total_size_mb']:.1f} MB")
        
        if encrypt:
            click.echo(f"   Encryption: {manifest['encryption_info']['algorithm']}")
            click.echo(f"   Key fingerprint: {manifest['encryption_info']['key_fingerprint']}")
            
    except Exception as e:
        click.echo(f"❌ Packaging failed: {e}", err=True)
        raise click.Abort()


@gap.command()
@click.argument('shard_path', type=click.Path(exists=True))
@click.option('--endpoint', required=True, help='S3-compatible endpoint (s3://bucket/path)')
@click.option('--throttle', default='10MB/s', help='Upload rate limit')
@click.option('--idle-only', is_flag=True, help='Only upload when system is idle')
@click.option('--chunks', default=8, help='Number of parallel chunks')
@click.option('--retry', default=3, help='Retry attempts on failure')
def upload(shard_path: str, endpoint: str, throttle: str, idle_only: bool, 
           chunks: int, retry: int):
    """Upload GAP shard to S3-compatible storage."""
    
    click.echo(f"⬆️  Uploading GAP shard...")
    click.echo(f"   Shard: {shard_path}")
    click.echo(f"   Endpoint: {endpoint}")
    click.echo(f"   Throttle: {throttle}")
    click.echo(f"   Idle only: {idle_only}")
    
    try:
        uploader = Uploader(
            endpoint=endpoint,
            max_rate=throttle,
            parallel_chunks=chunks,
            retry_attempts=retry
        )
        
        receipt = uploader.upload(
            shard_path=shard_path,
            idle_only=idle_only
        )
        
        click.echo(f"✅ Upload completed successfully!")
        click.echo(f"   Receipt ID: {receipt['receipt_id']}")
        click.echo(f"   Upload time: {receipt['upload_duration_sec']:.1f}s")
        click.echo(f"   Verification: {receipt['verification_status']}")
        
        # Save receipt
        receipt_path = Path(shard_path) / "upload_receipt.json"
        with open(receipt_path, 'w') as f:
            json.dump(receipt, f, indent=2)
        click.echo(f"   Receipt saved: {receipt_path}")
        
    except Exception as e:
        click.echo(f"❌ Upload failed: {e}", err=True)
        raise click.Abort()


@gap.command()
@click.argument('shard_path', type=click.Path(exists=True))
@click.option('--receipt', type=click.Path(exists=True), help='Upload receipt JSON file')
@click.option('--remote', is_flag=True, help='Verify against remote storage')
@click.option('--deep', is_flag=True, help='Deep verification (re-download and hash)')
def verify(shard_path: str, receipt: Optional[str], remote: bool, deep: bool):
    """Verify GAP shard integrity and upload receipt."""
    
    click.echo(f"🔍 Verifying GAP shard...")
    click.echo(f"   Shard: {shard_path}")
    click.echo(f"   Receipt: {receipt or 'auto-detect'}")
    click.echo(f"   Remote check: {remote}")
    click.echo(f"   Deep verification: {deep}")
    
    try:
        verifier = Verifier()
        
        # Load receipt
        receipt_data = None
        if receipt:
            with open(receipt, 'r') as f:
                receipt_data = json.load(f)
        else:
            # Auto-detect receipt
            receipt_path = Path(shard_path) / "upload_receipt.json"
            if receipt_path.exists():
                with open(receipt_path, 'r') as f:
                    receipt_data = json.load(f)
        
        result = verifier.verify(
            shard_path=shard_path,
            receipt=receipt_data,
            check_remote=remote,
            deep_verify=deep
        )
        
        if result['valid']:
            click.echo(f"✅ Verification passed!")
        else:
            click.echo(f"❌ Verification failed!")
            
        click.echo(f"   Local integrity: {'✅' if result['local_integrity'] else '❌'}")
        click.echo(f"   Hash verification: {'✅' if result['hash_verification'] else '❌'}")
        
        if remote and 'remote_verification' in result:
            click.echo(f"   Remote verification: {'✅' if result['remote_verification'] else '❌'}")
            
        if not result['valid']:
            for error in result.get('errors', []):
                click.echo(f"   Error: {error}")
                
    except Exception as e:
        click.echo(f"❌ Verification failed: {e}", err=True)
        raise click.Abort()


@gap.command()
@click.argument('shard_path', type=click.Path(exists=True))
@click.option('--profile', help='Validate against specific profile')
@click.option('--strict', is_flag=True, help='Strict validation mode')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
def validate(shard_path: str, profile: Optional[str], strict: bool, output_json: bool):
    """Validate GAP shard against specification."""
    
    # Import the existing validator
    import sys
    from pathlib import Path
    
    # Add tools directory to path
    tools_dir = Path(__file__).parent.parent.parent.parent / "tools"
    sys.path.insert(0, str(tools_dir))
    
    try:
        from validate import GAPValidator
        
        validator = GAPValidator(shard_path, profile, strict)
        is_valid, report = validator.validate_all()
        
        if output_json:
            click.echo(json.dumps(report, indent=2))
        else:
            if is_valid:
                click.echo("✅ GAP shard is valid")
            else:
                click.echo("❌ GAP shard validation failed")
                
            if report.get('errors'):
                click.echo("Errors:")
                for error in report['errors']:
                    click.echo(f"  - {error}")
                    
            if report.get('warnings'):
                click.echo("Warnings:")
                for warning in report['warnings']:
                    click.echo(f"  - {warning}")
                    
    except ImportError:
        click.echo("❌ GAP validator not found. Install gap-tools package.", err=True)
        raise click.Abort()


if __name__ == '__main__':
    gap() 