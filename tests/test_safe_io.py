import pytest
from hypothesis import given, strategies as st
from pathlib import Path
import sys
import os

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from safe_io import _resolve_under

@given(st.lists(st.text(min_size=0, max_size=10), min_size=1, max_size=5))
def test_resolve_under_never_escapes(parts):
    """Property test: path resolution should never escape base directory."""
    base = Path("/tmp/base")
    candidate = Path(*parts)
    # inject traversal markers
    candidate = Path("..") / candidate / ".."
    with pytest.raises(ValueError, match="unsafe path outside root"):
        _resolve_under(base, candidate)

def test_resolve_under_basic_cases():
    """Basic test cases for path resolution."""
    base = Path("/tmp/base")
    
    # Valid case should work
    result = _resolve_under(base, Path("subdir/file.txt"))
    assert str(result).startswith(str(base))
    
    # Direct traversal should fail
    with pytest.raises(ValueError):
        _resolve_under(base, Path("../../../etc/passwd"))
    
    # Hidden traversal should fail
    with pytest.raises(ValueError):
        _resolve_under(base, Path("good/../../bad/file"))

@given(st.integers(min_value=1, max_value=20))
def test_many_traversals_fail(depth):
    """Property test: any number of ../ should not escape."""
    base = Path("/tmp/base")
    traversal = Path("/".join([".."] * depth))
    with pytest.raises(ValueError):
        _resolve_under(base, traversal) 