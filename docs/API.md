# GAP Agent API Contract

**Public API surface for Shaga Node Core integration**

This document defines the exact interface that Shaga Node Core will call. These signatures are locked and tested to ensure backward compatibility across gap-agent versions.

## Core API Functions

### `pack()` - Package GAP Shard

```python
def pack(
    video_path: str,
    controls_path: str,
    *,
    profile: str,
    session_id: str,
    segment_index: int,
    output_dir: Optional[str] = None,
    encrypt: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -> PackResult
```

**Parameters:**
- `video_path`: Path to AV1/HEVC video file (CFR enforced)
- `controls_path`: Path to JSONL controls file
- `profile`: GAP profile name ("wayfarer-owl", "standard")
- `session_id`: Unique session identifier (UUID)
- `segment_index`: Sequential segment number within session
- `output_dir`: Target directory (default: temp directory)
- `encrypt`: Enable envelope encryption (X25519 + AES-GCM)
- `metadata`: Additional metadata to merge

**Returns:**
```python
@dataclass
class PackResult:
    shard_dir: str
    session_id: str
    segment_index: int
    total_size_mb: float
    manifest_hash: str
    encryption_info: Optional[EncryptionInfo]
    qat_results: QATResults
    dedup_score: DedupScore
```

### `upload()` - Upload to Storage

```python
def upload(
    shard_dir: str,
    *,
    endpoint: str,
    idle_policy: IdlePolicy = IdlePolicy.SMART,
    max_rate: str = "10MB/s",
    daily_cap: Optional[str] = None,
    prefix: Optional[str] = None,
    credentials: Optional[Credentials] = None
) -> UploadReceipt
```

**Parameters:**
- `shard_dir`: GAP shard directory to upload
- `endpoint`: S3-compatible endpoint URL
- `idle_policy`: When to upload (`SMART`, `MANUAL`, `ALWAYS`)
- `max_rate`: Bandwidth throttling ("10MB/s", "unlimited")
- `daily_cap`: Daily upload limit ("1GB", "500MB")
- `prefix`: Node-specific prefix for object keys
- `credentials`: Upload credentials (default: env/config)

**Returns:**
```python
@dataclass
class UploadReceipt:
    receipt_id: str
    object_uri: str
    upload_duration_sec: float
    verification_status: str
    server_receipt: Optional[ServerReceipt]
    checkpoints: List[UploadCheckpoint]
```

### `verify()` - Verify Upload & Receipt

```python
def verify(
    receipt_path: str,
    *,
    remote: bool = True,
    deep: bool = False,
    check_signature: bool = True
) -> VerificationResult
```

**Parameters:**
- `receipt_path`: Path to upload receipt JSON
- `remote`: Verify against remote storage
- `deep`: Re-download and hash-check (expensive)
- `check_signature`: Verify server signature on receipt

**Returns:**
```python
@dataclass
class VerificationResult:
    valid: bool
    local_integrity: bool
    remote_integrity: bool
    signature_valid: bool
    errors: List[str]
    proof_bundle: Dict[str, Any]
```

### `validate()` - GAP Specification Validation

```python
def validate(
    target_uri: str,
    *,
    profile: Optional[str] = None,
    strict: bool = False,
    output_format: str = "json"
) -> ValidationReport
```

**Parameters:**
- `target_uri`: GAP shard path or URI (file://, s3://, hf://)
- `profile`: Validation profile ("wayfarer-owl", "standard")
- `strict`: Strict mode (enforce recommended values)
- `output_format`: Output format ("json", "text", "compact")

**Returns:**
```python
@dataclass
class ValidationReport:
    valid: bool
    profile: str
    schema_version: str
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    qat_results: QATResults
    sync_stats: SyncStats
```

## Policy Interfaces

### Idle Detection Policies

```python
class IdlePolicy(Enum):
    SMART = "smart"      # Auto-detect system idle state
    MANUAL = "manual"    # Upload only when env flag set
    ALWAYS = "always"    # Upload immediately (testing only)

class IdleDetector(ABC):
    @abstractmethod
    def is_system_idle(self) -> bool: ...
    
    @abstractmethod
    def wait_for_idle(self, timeout_sec: int) -> bool: ...
```

**Implementations:**
- `WindowsIdleDetector`: Uses performance counters
- `LinuxIdleDetector`: Uses netlink/proc
- `ManualIdleDetector`: Checks environment flags

### Storage Adapters

```python
class StorageAdapter(ABC):
    @abstractmethod
    def upload_multipart(
        self, 
        local_path: str, 
        remote_key: str,
        progress_callback: Optional[Callable] = None
    ) -> UploadResult: ...
    
    @abstractmethod
    def verify_object(self, remote_key: str, expected_hash: str) -> bool: ...
```

**Implementations:**
- `S3Adapter`: AWS S3
- `R2Adapter`: Cloudflare R2
- `B2Adapter`: Backblaze B2
- `MinIOAdapter`: Self-hosted MinIO

## Data Structures

### QAT Results

```python
@dataclass
class QATResults:
    timestamp_sanity: bool
    cfr_integrity: float  # Percentage
    sync_within_8ms_pct: float
    drops_pct: float
    coverage_pct: float
    timestamp_drift_ms: float
```

### Deduplication Score

```python
@dataclass
class DedupScore:
    phash_hamming_distance: int  # Perceptual hash similarity
    simhash_hamming_distance: int  # Control stream similarity
    risk_level: str  # "low", "medium", "high"
    similar_sessions: List[str]  # Known similar session IDs
```

### Server Receipt

```python
@dataclass
class ServerReceipt:
    schema: str  # "gap.receipt.v1"
    session_id: str
    segment_index: int
    object_uri: str
    sha256_plaintext: str
    sha256_ciphertext: str
    duration_s: float
    frames: int
    wm_detect_rate: float  # Watermark detection rate
    qat: QATResults
    dup_score: DedupScore
    por_root: Optional[str]  # Proof of Retrieval root
    ingested_at: str  # ISO timestamp
    ingest_sig: str  # ed25519 signature
```

## CLI Interface

The CLI provides the same functionality with locked argument names:

```bash
# Package shard
gap pack video.mkv controls.jsonl \
  --profile wayfarer-owl \
  --session-id uuid \
  --segment-index 12 \
  --output shard_dir/ \
  --encrypt

# Upload with policy
gap upload shard_dir/ \
  --endpoint s3://bucket/prefix \
  --idle-policy smart \
  --daily-cap 1GB \
  --max-rate 10MB/s

# Verify receipt
gap verify receipt.json \
  --remote \
  --deep \
  --check-signature

# Validate shard
gap validate s3://bucket/shard.tar.gz \
  --profile wayfarer-owl \
  --strict \
  --format json
```

## Error Handling

All API functions raise typed exceptions:

```python
class GAPError(Exception): ...
class ValidationError(GAPError): ...
class UploadError(GAPError): ...
class VerificationError(GAPError): ...
class StorageError(GAPError): ...
class IdleTimeoutError(GAPError): ...
```

## Versioning Contract

- **Major version change**: Breaking API changes
- **Minor version change**: New features, backward compatible
- **Patch version change**: Bug fixes only

Current version: `0.3.0`

**Compatibility promise:** Node Core integration will work across all `0.x.x` versions with the same major version.

## Testing Interface

For CI and integration testing:

```python
# Create synthetic test data
def create_test_shard(duration_sec: int, profile: str) -> str: ...

# Mock storage for testing
def mock_storage_adapter() -> StorageAdapter: ...

# Validate API compliance
def test_api_contract() -> bool: ...
```

---

**This API contract is locked and tested. Changes require major version bump and migration guide.** 