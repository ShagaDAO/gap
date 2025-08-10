"""
URI Loader for GAP Validator

Supports loading GAP shards from various URI schemes:
- hf://dataset/shard_name (Hugging Face datasets)
- s3://bucket/path (S3-compatible storage)
- file://path (local files)
"""

import tempfile
import urllib.parse
from pathlib import Path
from typing import Optional

from .safe_io import TempDir, safe_extract_zip, safe_extract_tar, sanitize_error


class URILoader:
    """Loads GAP shards from various URI schemes."""
    
    @staticmethod
    def load_from_uri(uri: str) -> Optional[str]:
        """Download and extract GAP shard from URI, return local path."""
        
        parsed = urllib.parse.urlparse(uri)
        scheme = parsed.scheme.lower()
        
        if scheme == "hf":
            return URILoader._load_from_huggingface(parsed)
        elif scheme == "s3":
            return URILoader._load_from_s3(parsed)
        elif scheme == "file":
            return parsed.path
        else:
            raise ValueError(f"Unsupported URI scheme: {scheme}")
    
    @staticmethod
    def _load_from_huggingface(parsed_uri) -> Optional[str]:
        """Load GAP shard from Hugging Face dataset."""
        
        try:
            from datasets import load_dataset
            
            # Parse hf://dataset_name/shard_name
            dataset_name = parsed_uri.netloc
            shard_name = parsed_uri.path.lstrip('/')
            
            # Load dataset
            dataset = load_dataset(dataset_name, split="train")
            
            # Find matching shard
            for example in dataset:
                if shard_name in example.get('session_id', '') or shard_name in example.get('shard_path', ''):
                    return example['shard_path']
                    
            raise ValueError(f"Shard {shard_name} not found in dataset {dataset_name}")
            
        except ImportError:
            raise ValueError("Hugging Face datasets library not installed")
        except Exception as e:
            raise ValueError(f"Failed to load from HF: {e}")
    
    @staticmethod 
    def _load_from_s3(parsed_uri) -> Optional[str]:
        """Load GAP shard from S3-compatible storage."""
        
        try:
            import boto3
            from botocore.config import Config
            
            # Extract bucket and key
            bucket = parsed_uri.netloc
            key = parsed_uri.path.lstrip('/')
            
            # Create S3 client (assumes credentials are configured)
            s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
            
            # Download to temporary directory with safe cleanup
            with TempDir() as temp_dir:
                local_path = temp_dir / Path(key).name
                
                s3_client.download_file(bucket, key, str(local_path))
                
                # If it's an archive, extract it safely
                if local_path.suffix.lower() in ['.tar', '.tar.gz', '.tgz', '.zip']:
                    extract_dir = temp_dir / local_path.stem
                    
                    if local_path.suffix.lower() == '.zip':
                        safe_extract_zip(local_path, extract_dir)
                    elif local_path.suffix.lower() in ['.tar', '.tar.gz', '.tgz']:
                        safe_extract_tar(local_path, extract_dir)
                    else:
                        raise ValueError("unsupported archive type")
                            
                    # Find GAP shard directory
                    for subdir in extract_dir.rglob('meta.json'):
                        return str(subdir.parent)
                        
                    return str(extract_dir)
                else:
                    return str(local_path.parent)
                
        except ImportError:
            raise ValueError("boto3 library not installed")
        except Exception as e:
            raise ValueError(sanitize_error(e, key))


def is_uri(path: str) -> bool:
    """Check if path is a URI (contains scheme)."""
    try:
        parsed = urllib.parse.urlparse(path)
        return bool(parsed.scheme)
    except:
        return False 