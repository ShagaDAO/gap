# Validation Methodology

GAP v0.2 validation uses a multi-layered approach to ensure specification compliance and data integrity.

## Validation Levels

### 1. Schema Validation
- **JSON Schema Draft-7** compliance for all metadata files
- Required fields enforcement per GAP v0.2 specification  
- Profile-specific validation (e.g., wayfarer-owl)

### 2. Quality Acceptance Tests (QAT)
- **Timestamp alignment:** ±8ms for 95% of frame/control pairs
- **File integrity:** SHA-256 hash verification
- **Resource limits:** Size and line count caps for security
- **Format compliance:** Video codec, frame rate, resolution checks

### 3. Security Validation
- **Path traversal protection:** Safe archive extraction
- **DoS prevention:** File size limits (512MB video, 100MB JSONL, 5M lines)
- **Input sanitization:** Schema-first JSON parsing

## Validation Commands

### Basic Validation
```bash
python tools/validate.py samples/star-atlas_100mb/
```

### Profile-Specific Validation
```bash
python tools/validate.py --profile wayfarer-owl samples/star-atlas_100mb/
```

### JSON Output (CI/automation)
```bash
python tools/validate.py --json --profile wayfarer-owl samples/star-atlas_100mb/
```

### Strict Mode (advisory → enforced)
```bash
python tools/validate.py --strict samples/star-atlas_100mb/
```

## Environment Overrides

Power users can adjust limits via environment variables:

- `GAP_MAX_VIDEO_BYTES` - Video file size limit (default: 512MB)
- `GAP_MAX_JSONL_MB` - Controls JSONL size limit (default: 100MB)  
- `GAP_MAX_JSONL_LINES` - Maximum JSONL lines (default: 5M)
- `GAP_SPACE_MAX_MB` - HuggingFace Space upload limit (default: 150MB)
- `GAP_SPACE_MAX_SECONDS` - HuggingFace Space timeout (default: 30s)

## Negative Testing

The validator includes built-in negative tests to ensure proper rejection of malformed inputs:

```bash
# CI automatically tests validator rejection of bad samples
# See .github/workflows/ci.yml for implementation
```

## Reproducibility

All validation benchmarks in [BENCHMARKS.md](../../BENCHMARKS.md) are reproducible using the above commands. Timing measurements are performed on the included 100MB reference sample.

## See Also

- [GAP v0.2 Specification](../../packages/gap-spec/GAP-v0.2.md)
- [CI Validation Workflow](../../.github/workflows/ci.yml)
- [Validator Source Code](../../tools/validate.py) 