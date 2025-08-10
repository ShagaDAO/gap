# Changelog

All notable changes to the GAP (Gameplay-Action Pairs) specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-01-15

### Added
- Formal GAP v0.2 specification with publishable draft status
- Quality Acceptance Tests (QAT) with measurable requirements
- Fixed keymask mapping for consistent partner integration
- Size calculations and realistic storage estimates
- Python tooling: loader, validator, and examples
- Sample data files (5-row examples) for immediate testing
- JSON schema validation support
- File integrity verification with SHA-256 hashes
- Frame watermarking requirements
- Network statistics support (optional)
- Privacy-first engagement labels (optional)

### Changed
- **BREAKING**: Dropped raw frames as baseline format for Phase-0
- **BREAKING**: Standardized on AV1/HEVC CFR (Constant Frame Rate)
- **BREAKING**: Minimum 60Hz controls, recommended 120Hz/240Hz for mouse
- Formal alignment guarantee: ±8ms for 95% of frame-control pairs
- Structured shard duration: 30-120 minutes continuous gameplay
- Enhanced metadata schema with capture, display, and rights info

### Removed
- Raw frame support (moved to optional lossless gold tier)
- Variable control rates without alignment guarantees
- Unstructured timestamp formats

### Technical Details
- Schema version: `0.2.0`
- Video size @ 720p60: ~1.8-3.6 GB/hour (AV1/HEVC)
- Controls size @ 60-120Hz: ~3-15 MB/hour
- Total overhead: <10 MB/hour for metadata + optional files

## [0.1.x] - 2023-12-XX (Legacy)

### Added
- Initial GAP specification concepts
- Raw frame support experiments
- Variable control rate capture
- Basic metadata structure

### Issues Fixed in v0.2.0
- Storage explosion with raw frames (570 GB/hour @ 720p60)
- Inconsistent timing alignment between partners
- Missing formal validation requirements
- Undefined keymask bit mappings
- No standardized QAT procedures

---

## Phase-0 Readiness Checklist

✅ **Formal specification** - Complete GAP v0.2 document  
✅ **Sample data** - 5-row examples for frames and controls  
✅ **Size calculations** - Realistic storage estimates provided  
✅ **Python tooling** - Loader, validator, and examples  
✅ **QAT requirements** - Measurable acceptance criteria  
✅ **Partner integration** - Fixed schemas for production pilots

**Ready for production pilots and v0.2.0 tag.**

## [0.2.2] - 2024-01-15

### Changed
- Removed references to non-partner vendors; storage is provider-agnostic
- Reframed 100MB sample as vendor-neutral reference implementation
- Validator: bitrate checks now advisory unless --strict mode enabled
- Storage references clarified as S3-compatible (AWS S3, Cloudflare R2, MinIO, etc.)

### Added
- LICENSE-data.md for sample rights and usage restrictions
- NOTICE.md clarifying vendor neutrality and open standards
- download.sh + MANIFEST.json for release-hosted sample files
- --strict flag for validator to enforce recommended bitrates

### Fixed
- Sample metadata uses research-appropriate license references
- Profile documentation clarifies OWL audio handling
- Watermark proofs use neutral reference naming 