# tools/safe_io.py
from __future__ import annotations
from pathlib import Path
import os, zipfile, tarfile, tempfile, shutil

MAX_FILES = 10_000
MAX_TOTAL_BYTES = 2 * 1024**3  # 2 GiB
MAX_EXPANSION = 20.0  # zip-bomb guard (uncompressed/compressed)

def _resolve_under(root: Path, child: Path) -> Path:
    """Resolve child path under root, preventing traversal attacks."""
    root = root.resolve()
    dest = (root / child).resolve()
    if not str(dest).startswith(str(root) + os.sep):
        raise ValueError(f"unsafe path outside root: {child}")
    return dest

def safe_extract_zip(zip_path: Path, dest_dir: Path) -> None:
    """Safely extract ZIP archive with size and traversal protection."""
    dest_dir = dest_dir.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path) as zf:
        files = [i for i in zf.infolist() if not i.is_dir()]
        if len(files) > MAX_FILES:
            raise ValueError("archive has too many files")
        
        total_uc = sum(i.file_size for i in files)
        total_c = sum(i.compress_size or 1 for i in files)
        
        if total_uc > MAX_TOTAL_BYTES:
            raise ValueError("archive too large")
        if (total_uc / max(total_c, 1.0)) > MAX_EXPANSION:
            raise ValueError("suspicious expansion ratio")
        
        for i in files:
            # reject absolute paths and parent traversal
            if i.filename.startswith("/") or ".." in Path(i.filename).parts:
                raise ValueError(f"unsafe member: {i.filename}")
            
            target = _resolve_under(dest_dir, Path(i.filename))
            target.parent.mkdir(parents=True, exist_ok=True)
            
            with zf.open(i, "r") as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)

def safe_extract_tar(tar_path: Path, dest_dir: Path) -> None:
    """Safely extract TAR archive with size and traversal protection."""
    dest_dir = dest_dir.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    with tarfile.open(tar_path) as tf:
        members = [m for m in tf.getmembers() if m.isreg()]
        if len(members) > MAX_FILES:
            raise ValueError("archive has too many files")
        
        total_uc = sum(m.size for m in members)
        if total_uc > MAX_TOTAL_BYTES:
            raise ValueError("archive too large")
        
        for m in members:
            if m.name.startswith("/") or ".." in Path(m.name).parts:
                raise ValueError(f"unsafe member: {m.name}")
            
            target = _resolve_under(dest_dir, Path(m.name))
            target.parent.mkdir(parents=True, exist_ok=True)
            
            with tf.extractfile(m) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)

class TempDir:
    """Auto-clean temp dir with restricted permissions."""
    def __init__(self, prefix="gap-"):
        self._td = tempfile.TemporaryDirectory(prefix=prefix)
        os.chmod(self._td.name, 0o700)
    
    def __enter__(self) -> Path:
        return Path(self._td.name)
    
    def __exit__(self, *exc):
        self._td.cleanup()

def safe_resolve_path(base_dir: Path, relative_path: str) -> Path:
    """Safely resolve a relative path under base_dir."""
    return _resolve_under(base_dir, Path(relative_path))

def sanitize_error(error: Exception, filepath: str) -> str:
    """Sanitize error message to prevent path disclosure."""
    filename = Path(filepath).name
    return f"Failed processing file '{filename}': {error.__class__.__name__}" 