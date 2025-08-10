"""
GAP Agent - Open Storage & Upload Module

Public, auditable GAP shard packaging, encryption, and upload library.
"""

__version__ = "0.1.0"
__author__ = "GAP Contributors"
__license__ = "MIT"

from .packager import ShardPackager
from .uploader import Uploader  
from .verifier import Verifier
from .crypto import EncryptionManager
from .buffer import RingBuffer

__all__ = [
    "ShardPackager",
    "Uploader", 
    "Verifier",
    "EncryptionManager",
    "RingBuffer"
] 