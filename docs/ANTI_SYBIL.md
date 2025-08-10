# Anti-Sybil Defense Strategy

**Protecting GAP data quality through phased gating and statistical verification**

This document outlines the defense mechanisms against fake data, re-encoded content, and sybil attacks. The strategy scales from strict allowlisting to automated statistical verification.

## Threat Model

### Primary Threats

1. **Re-encoded YouTube/Twitch content**
   - Downloaded streams re-encoded with fake controls
   - Easy to generate at scale, hard to detect without watermarks

2. **Loop/duplicate content**
   - Same gameplay session uploaded multiple times
   - Minor variations to evade simple hash detection

3. **Synthetic/AI-generated content**
   - Fully artificial gameplay footage
   - Unnaturally smooth controls, unrealistic patterns

4. **Coordinated sybil networks**
   - Multiple nodes uploading variations of same content
   - Distributed to appear legitimate

### Cost/Reward Analysis

**Cost of faking must exceed reward:**
- High-quality fakes require significant compute/time
- Detection penalties should eliminate profit motive
- Legitimate nodes should be clearly more profitable

## Phase-In Plan

### Phase 0: Strict Allowlist (Weeks 0-2)

**Access Control:**
- Manual node onboarding with KYC verification
- Each node gets registered pubkey + hardware fingerprint
- Short-lived, scoped credentials per segment upload
- Zero rewards during development phase

**Verification:**
```json
{
  "node_registration": {
    "pubkey_ed25519": "...",
    "hardware_fingerprint": {
      "gpu_pci_ids": ["10de:2684"],
      "driver_hash": "sha256:...",
      "os_build": "Windows 11 22H2"
    },
    "vouched_by": ["trusted_node_1", "trusted_node_2"],
    "registration_date": "2024-08-11T00:00:00Z"
  }
}
```

**Upload Flow:**
1. Node requests upload token with session manifest
2. Coordinator issues pre-signed PUT URL (24h expiry)
3. Node uploads encrypted segment + manifest
4. Server-side QAT + anti-dup checks
5. Receipt issued only after validation passes

### Phase 1: Guarded Growth (Weeks 3-8)

**Vouching System:**
- Existing nodes can vouch for new nodes (n-of-m threshold)
- Non-transferable credits earned after server-side validation
- Soft stake (credit bond) required for high-volume uploads

**Upload Economics:**
```json
{
  "daily_limits": {
    "new_node": "100MB/day",
    "vouched_node": "1GB/day", 
    "trusted_node": "10GB/day"
  },
  "credit_requirements": {
    "bond_per_gb": 100,
    "earned_per_valid_gb": 10,
    "slashed_per_violation": 1000
  }
}
```

### Phase 2: Automated Gating (Post-POC)

**Statistical Verification:**
- Real-time detection pipeline on all uploads
- Challenge frames injected by closed Node Core
- Graduate to stake-to-upload with token slashing

**Defense Layers:**
1. Local pre-checks (client-side, this repo)
2. Server-side statistical analysis (ingest pipeline)
3. Challenge verification (closed Node Core)
4. Community reporting + appeals

## Server-Side Detection Pipeline

### 1. Duplication & Loop Detection

**Perceptual Hashing:**
```python
def detect_duplicates(video_path: str) -> DuplicateScore:
    # aHash: average hash (lighting invariant)
    # pHash: perceptual hash (rotation/scale invariant)  
    # dHash: difference hash (compression robust)
    
    frames = extract_keyframes(video_path, interval=5.0)
    hashes = [phash(frame) for frame in frames]
    
    # Check against daily bloom filter
    duplicates = []
    for h in hashes:
        if bloom_filter.check(h, hamming_threshold=8):
            duplicates.append(h)
    
    return DuplicateScore(
        duplicate_frames=len(duplicates),
        similarity_score=max(hamming_distances),
        risk_level="high" if len(duplicates) > 10 else "low"
    )
```

**Control Stream SimHash:**
```python
def simhash_controls(controls_path: str) -> int:
    # Extract features: key frequencies, mouse patterns, timing
    events = load_controls(controls_path)
    
    features = []
    features.extend(extract_key_ngrams(events, n=3))
    features.extend(extract_mouse_velocity_bins(events))
    features.extend(extract_timing_patterns(events))
    
    return simhash(features, hash_bits=128)

def check_control_similarity(new_simhash: int, threshold: int = 16) -> bool:
    # Query recent uploads for similar control patterns
    similar = query_recent_simhashes(new_simhash, threshold)
    return len(similar) > 0
```

### 2. Input↔Motion Coherence

**Mouse Delta vs Optical Flow:**
```python
def check_motion_coherence(video_path: str, controls_path: str) -> CoherenceScore:
    # Extract optical flow magnitude from video
    flow_data = extract_optical_flow(video_path, sample_rate=10.0)
    
    # Extract mouse movement from controls
    mouse_events = extract_mouse_deltas(controls_path)
    
    # Align timestamps and compute correlation
    aligned_flow, aligned_mouse = align_timeseries(flow_data, mouse_events)
    correlation = pearson_correlation(aligned_flow, aligned_mouse)
    
    # Unnaturally smooth controls with high motion = red flag
    mouse_entropy = shannon_entropy(aligned_mouse)
    
    return CoherenceScore(
        correlation=correlation,
        mouse_entropy=mouse_entropy,
        suspicion_level="high" if correlation < 0.3 and mouse_entropy < 2.0 else "low"
    )
```

**Keyboard Keymask Entropy:**
```python
def check_keyboard_entropy(controls_path: str) -> float:
    events = load_controls(controls_path)
    
    # Extract keymask changes over time
    keymask_sequence = extract_keymask_sequence(events, window_ms=100)
    
    # Measure entropy in key combination patterns
    # Real gameplay: high entropy, varied combinations
    # Fake data: often low entropy, repetitive patterns
    return shannon_entropy(keymask_sequence)
```

### 3. Timing Sanity Checks

**Frame/Control Alignment:**
```python
def check_alignment_quality(video_path: str, controls_path: str) -> AlignmentScore:
    video_timestamps = extract_frame_timestamps(video_path)
    control_timestamps = extract_control_timestamps(controls_path)
    
    # Find nearest control for each frame
    deltas = []
    for frame_ts in video_timestamps:
        nearest_control = find_nearest_timestamp(control_timestamps, frame_ts)
        delta_ms = abs(frame_ts - nearest_control) / 1000
        deltas.append(delta_ms)
    
    # GAP spec requires ±8ms for 95% of pairs
    within_8ms_pct = sum(1 for d in deltas if d <= 8.0) / len(deltas) * 100
    
    return AlignmentScore(
        within_8ms_pct=within_8ms_pct,
        mean_delta_ms=statistics.mean(deltas),
        p95_delta_ms=statistics.quantiles(deltas, n=20)[18],  # 95th percentile
        passes_qat=within_8ms_pct >= 95.0
    )
```

### 4. Liveness Challenges (Node Core Integration)

**Watermark Injection:**
```python
# This logic stays in closed Node Core
def inject_challenge_frames(session_id: str, segment_index: int) -> ChallengeNonce:
    nonce = generate_secure_nonce()
    overlay_frames = select_random_frames(segment_index, count=5)
    
    # Embed invisible watermark with nonce
    for frame_idx in overlay_frames:
        embed_watermark(frame_idx, nonce, session_id)
    
    return ChallengeNonce(
        nonce=nonce,
        target_frames=overlay_frames,
        expires_at=time.time() + 3600
    )

# This verification happens server-side
def verify_watermark_challenge(video_path: str, expected_nonce: str) -> bool:
    detected_nonces = extract_watermarks(video_path)
    return expected_nonce in detected_nonces
```

### 5. Title Server Cross-Checks

**Session Verification (when available):**
```python
def verify_with_title_server(session_id: str, metadata: dict) -> VerificationResult:
    # For Star Atlas, Wayfarer, or other partner titles
    # Verify session exists and metadata matches
    
    title_server_api = get_title_server(metadata["title"]["name"])
    
    if title_server_api:
        server_session = title_server_api.get_session(session_id)
        
        # Check timestamp alignment
        timestamp_match = abs(
            server_session.start_time - metadata["timing"]["t0_us"]
        ) < 60_000_000  # Within 60 seconds
        
        # Check duration consistency  
        duration_match = abs(
            server_session.duration_sec - metadata["video"]["duration_sec"]
        ) < 5.0  # Within 5 seconds
        
        return VerificationResult(
            server_verified=True,
            timestamp_match=timestamp_match,
            duration_match=duration_match
        )
    
    return VerificationResult(server_verified=False)
```

## Local Pre-Check Utilities

Partners can run the same checks locally to avoid wasting bandwidth:

```python
# packages/gap-agent/src/gap_agent/dedupe.py
def precheck_shard(shard_dir: str) -> PrecheckResult:
    """Run local duplicate and quality checks before upload."""
    
    video_path = find_video_file(shard_dir)
    controls_path = find_controls_file(shard_dir)
    
    # Basic quality checks
    qat_results = run_local_qat(shard_dir)
    
    # Duplicate detection (against local cache)
    dup_score = check_local_duplicates(video_path, controls_path)
    
    # Motion coherence
    coherence = check_motion_coherence(video_path, controls_path)
    
    return PrecheckResult(
        should_upload=qat_results.passes and dup_score.risk_level == "low",
        qat_results=qat_results,
        duplicate_score=dup_score,
        coherence_score=coherence,
        estimated_server_acceptance=estimate_acceptance_probability(...)
    )
```

## Detection Thresholds

### Risk Level Scoring

```python
def calculate_risk_score(signals: DetectionSignals) -> RiskScore:
    score = 0
    
    # Duplication signals (0-40 points)
    if signals.phash_similarity > 0.9:
        score += 40
    elif signals.phash_similarity > 0.7:
        score += 20
    
    # Motion coherence (0-30 points)
    if signals.motion_correlation < 0.3:
        score += 30
    elif signals.motion_correlation < 0.5:
        score += 15
    
    # Timing alignment (0-20 points)
    if signals.alignment_quality < 0.8:
        score += 20
    elif signals.alignment_quality < 0.9:
        score += 10
    
    # Control entropy (0-10 points)
    if signals.keyboard_entropy < 1.0:
        score += 10
    elif signals.keyboard_entropy < 2.0:
        score += 5
    
    return RiskScore(
        total_score=score,
        risk_level="high" if score > 60 else "medium" if score > 30 else "low",
        action="reject" if score > 80 else "flag" if score > 50 else "accept"
    )
```

### Action Thresholds

- **Score 0-30**: Auto-accept, normal processing
- **Score 31-50**: Flag for manual review, reduced rewards
- **Score 51-80**: Queue for enhanced verification, hold rewards
- **Score 81-100**: Auto-reject, potential node penalty

## Ingest Receipt Format

```json
{
  "schema": "gap.receipt.v1",
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "segment_index": 12,
  "object_uri": "s3://gap-hot/us-east-1/node_abc123/seg_1210_0012.gap",
  "sha256_plaintext": "e3b0c44298fc1c149afbf4c8996fb924...",
  "sha256_ciphertext": "a665a45920422f9d417e4867efdc4fb8...",
  "duration_s": 600.02,
  "frames": 36001,
  "wm_detect_rate": 0.973,
  "qat": {
    "timestamp_sanity": true,
    "cfr_integrity": 99.8,
    "sync_within_8ms_pct": 96.3,
    "drops_pct": 0.3,
    "coverage_pct": 99.1,
    "timestamp_drift_ms": 0.8
  },
  "dup_score": {
    "phash_hamming_distance": 41,
    "simhash_hamming_distance": 18,
    "risk_level": "low",
    "similar_sessions": []
  },
  "coherence": {
    "motion_correlation": 0.72,
    "keyboard_entropy": 3.4,
    "suspicion_level": "low"
  },
  "verification": {
    "watermark_verified": true,
    "title_server_verified": true,
    "risk_score": 15
  },
  "por_root": "d4735e3a265e16eee03f59718b9b5d03...",
  "ingested_at": "2024-08-11T03:41:22Z",
  "ingest_sig": "ed25519:a1b2c3d4e5f6..."
}
```

## Implementation Priorities

1. **Week 1**: Perceptual hashing + bloom filters for duplicate detection
2. **Week 2**: Control stream SimHash + motion coherence analysis  
3. **Week 3**: Local pre-check utilities in gap-agent
4. **Week 4**: Ingest receipt format + signature verification
5. **Future**: Watermark challenges + title server integration

## Monitoring & Tuning

**Detection Metrics:**
- False positive rate (legitimate uploads flagged)
- False negative rate (fake uploads accepted)
- Processing latency per upload
- Storage costs for bloom filters/caches

**Adversarial Response:**
- Regular threshold adjustments based on attack evolution
- A/B testing of detection parameters
- Community reporting integration
- Appeal process for false positives

---

**The cost of faking must always exceed the reward. These defenses scale with network value.** 