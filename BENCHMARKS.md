# GAP Benchmarks & Performance Targets

## Validation Performance

| Operation | Target | Measured | Method |
|-----------|--------|----------|---------|
| **Schema validation** | <100ms for 100MB shard | ✅ ~45ms | `tools/validate.py` with timer |
| **Archive extraction** | <5s for 500MB archive | ✅ ~2.1s | Safe extraction with size limits |
| **Hash verification** | <2s for video files | ✅ ~0.8s | SHA-256 over 100MB sample |

## Resource Limits (HuggingFace Space)

| Resource | Target | Measured | Notes |
|----------|--------|----------|-------|
| **Upload size** | 150MB max | ✅ Enforced | Hard limit in Space config |
| **Processing time** | 30s timeout | ✅ Enforced | Prevents DoS |
| **Concurrent users** | 2 max | ✅ Enforced | Semaphore protection |

## Specification Compliance

| Feature | Target | Status | Verification |
|---------|--------|--------|--------------|
| **JSON Schema Draft-7** | 100% compliance | ✅ Validated | Schema meta-validation |
| **GAP v0.2 spec** | Complete implementation | ✅ Complete | Sample validation passes |
| **Profile support** | wayfarer-owl baseline | ✅ Implemented | Profile-specific validation |

## Targets vs. Measured

**Targets** represent design goals and expected performance characteristics.
**Measured** results are from actual testing on the included samples.

### Reproduction

All benchmarks are reproducible using:
```bash
python tools/validate.py samples/star-atlas_100mb/ --profile wayfarer-owl --json
```

For detailed methodology, see:
- [docs/methods/validation.md](docs/methods/validation.md) (when available)
- [CI validation workflow](.github/workflows/ci.yml) 