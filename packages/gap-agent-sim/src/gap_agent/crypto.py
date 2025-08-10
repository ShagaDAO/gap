"""
GAP Encryption Manager

Handles X25519 + AES-GCM envelope encryption for GAP shards.
"""

from pathlib import Path
from typing import Dict, Any


class EncryptionManager:
    """Manages envelope encryption for GAP shards."""
    
    def __init__(self):
        """Initialize encryption manager with key generation."""
        # Intentionally unimplemented in preview - see STATUS.md
        pass
        
    def encrypt_file(self, file_path: Path) -> Path:
        """Encrypt file in place using envelope encryption."""
        raise NotImplementedError(
            "Preview build: crypto is stubbed by design. "
            "See STATUS.md for roadmap to production implementation."
        )
        
    def get_key_fingerprint(self) -> str:
        """Get fingerprint of public key for verification."""
        raise NotImplementedError(
            "Preview build: crypto is stubbed by design. "
            "See STATUS.md for roadmap to production implementation."
        )
        
    def get_envelope_key(self) -> str:
        """Get envelope key for recipient decryption."""
        raise NotImplementedError(
            "Preview build: crypto is stubbed by design. "
            "See STATUS.md for roadmap to production implementation."
        ) 