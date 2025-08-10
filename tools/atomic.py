from pathlib import Path
import os, tempfile

def atomic_write_bytes(dest: Path, data: bytes):
    """Write bytes atomically to prevent partial/corrupt outputs."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=dest.parent) as tmp:
      tmp.write(data)
      tmp.flush()
      os.fsync(tmp.fileno())
      tmp_path = Path(tmp.name)
    os.replace(tmp_path, dest)

def atomic_write_text(dest: Path, text: str, encoding: str = 'utf-8'):
    """Write text atomically to prevent partial/corrupt outputs."""
    atomic_write_bytes(dest, text.encode(encoding)) 