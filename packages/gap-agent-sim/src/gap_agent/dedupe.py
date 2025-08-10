"""
GAP Deduplication Module

Implements perceptual hashing (pHash) and control stream similarity hashing (SimHash)
for detecting duplicate and similar GAP content.
"""

import json
import hashlib
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import math

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class PHashError(Exception):
    """Error in perceptual hashing operations."""
    pass


class SimHashError(Exception):
    """Error in similarity hashing operations."""
    pass


def phash(image: 'np.ndarray', hash_size: int = 8) -> int:
    """
    Compute perceptual hash (pHash) of an image.
    
    Based on DCT (Discrete Cosine Transform) method.
    Returns integer representation of hash for fast comparison.
    """
    if not HAS_CV2:
        raise PHashError("OpenCV not available for perceptual hashing")
    
    # Resize to hash_size x hash_size
    resized = cv2.resize(image, (hash_size * 4, hash_size * 4))
    
    # Convert to grayscale if needed
    if len(resized.shape) == 3:
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    else:
        gray = resized
    
    # Apply DCT
    dct = cv2.dct(np.float32(gray))
    
    # Extract top-left 8x8 of DCT (low frequencies)
    dct_low = dct[:hash_size, :hash_size]
    
    # Calculate median (excluding DC component)
    dct_flat = dct_low.flatten()
    median = np.median(dct_flat[1:])  # Skip DC component
    
    # Generate hash bits
    hash_bits = []
    for val in dct_flat:
        hash_bits.append(1 if val > median else 0)
    
    # Convert to integer
    hash_int = 0
    for i, bit in enumerate(hash_bits):
        if bit:
            hash_int |= (1 << i)
    
    return hash_int


def hamming_distance(hash1: int, hash2: int) -> int:
    """Calculate Hamming distance between two hash integers."""
    return bin(hash1 ^ hash2).count('1')


def extract_keyframes(video_path: str, interval: float = 5.0) -> List['np.ndarray']:
    """
    Extract keyframes from video at specified interval.
    
    Args:
        video_path: Path to video file
        interval: Interval in seconds between frames
        
    Returns:
        List of frame images as numpy arrays
    """
    if not HAS_CV2:
        raise PHashError("OpenCV not available for video processing")
    
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise PHashError(f"Could not open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            frames.append(frame.copy())
            
        frame_count += 1
        
        # Limit to prevent excessive memory usage
        if len(frames) >= 100:
            break
    
    cap.release()
    return frames


def detect_video_duplicates(video_path: str, cache_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Detect if video content is similar to previously seen content.
    
    Args:
        video_path: Path to video file
        cache_path: Optional path to cache of known hashes
        
    Returns:
        Dictionary with duplicate detection results
    """
    try:
        # Extract keyframes
        frames = extract_keyframes(video_path, interval=5.0)
        
        if not frames:
            return {
                "error": "No frames extracted from video",
                "phash_distances": [],
                "min_distance": 128,
                "risk_level": "unknown"
            }
        
        # Compute pHash for each frame
        hashes = []
        for frame in frames:
            try:
                hash_val = phash(frame)
                hashes.append(hash_val)
            except Exception as e:
                # Skip problematic frames
                continue
        
        if not hashes:
            return {
                "error": "No valid hashes computed",
                "phash_distances": [],
                "min_distance": 128,
                "risk_level": "unknown"
            }
        
        # Check against cache if provided
        min_distance = 128
        similar_hashes = []
        
        if cache_path and Path(cache_path).exists():
            try:
                with open(cache_path, 'r') as f:
                    known_hashes = json.load(f)
                
                for new_hash in hashes:
                    for known_hash in known_hashes.get('video_hashes', []):
                        distance = hamming_distance(new_hash, known_hash)
                        if distance < min_distance:
                            min_distance = distance
                            similar_hashes.append((new_hash, known_hash, distance))
                            
            except Exception:
                # Cache read failed, continue without cache check
                pass
        
        # Determine risk level
        if min_distance <= 8:
            risk_level = "high"
        elif min_distance <= 16:
            risk_level = "medium" 
        else:
            risk_level = "low"
        
        return {
            "frame_count": len(frames),
            "hash_count": len(hashes),
            "phash_distances": [s[2] for s in similar_hashes],
            "min_distance": min_distance,
            "risk_level": risk_level,
            "similar_content": len(similar_hashes) > 0
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "phash_distances": [],
            "min_distance": 128,
            "risk_level": "unknown"
        }


def simhash(features: List[str], hash_bits: int = 64) -> int:
    """
    Compute SimHash for a list of features.
    
    Args:
        features: List of feature strings
        hash_bits: Number of bits in hash (default 64)
        
    Returns:
        Integer representation of SimHash
    """
    # Initialize bit vector
    bit_vector = [0] * hash_bits
    
    for feature in features:
        # Hash the feature
        feature_hash = hashlib.md5(feature.encode()).hexdigest()
        feature_int = int(feature_hash, 16)
        
        # Add/subtract from bit vector based on hash bits
        for i in range(hash_bits):
            if (feature_int >> i) & 1:
                bit_vector[i] += 1
            else:
                bit_vector[i] -= 1
    
    # Convert to final hash
    simhash_val = 0
    for i, val in enumerate(bit_vector):
        if val > 0:
            simhash_val |= (1 << i)
    
    return simhash_val


def extract_control_features(controls_path: str) -> List[str]:
    """
    Extract features from control events for similarity hashing.
    
    Args:
        controls_path: Path to controls JSONL file
        
    Returns:
        List of feature strings
    """
    features = []
    
    try:
        with open(controls_path, 'r') as f:
            events = [json.loads(line.strip()) for line in f if line.strip()]
    except Exception:
        return features
    
    if not events:
        return features
    
    # Extract key n-grams (sequences of key presses)
    key_sequence = []
    for event in events:
        if event.get('type') == 'key' and event.get('state') == 'down':
            key_sequence.append(event.get('key', ''))
    
    # Add key 3-grams
    for i in range(len(key_sequence) - 2):
        trigram = '-'.join(key_sequence[i:i+3])
        features.append(f"key_trigram:{trigram}")
    
    # Extract mouse velocity bins
    mouse_events = [e for e in events if e.get('type') == 'mouse']
    if mouse_events:
        velocities = []
        for event in mouse_events:
            dx = event.get('dx', 0)
            dy = event.get('dy', 0)
            velocity = math.sqrt(dx*dx + dy*dy)
            velocities.append(velocity)
        
        if velocities:
            # Bin velocities
            max_vel = max(velocities)
            bin_size = max_vel / 10 if max_vel > 0 else 1
            
            for vel in velocities:
                bin_idx = int(vel / bin_size) if bin_size > 0 else 0
                features.append(f"mouse_vel_bin:{bin_idx}")
    
    # Extract timing patterns (intervals between events)
    timestamps = [e.get('t_us', 0) for e in events]
    intervals = []
    for i in range(1, len(timestamps)):
        interval_ms = (timestamps[i] - timestamps[i-1]) / 1000
        intervals.append(interval_ms)
    
    if intervals:
        # Bin timing intervals
        avg_interval = statistics.mean(intervals)
        for interval in intervals:
            if interval < avg_interval * 0.5:
                features.append("timing:fast")
            elif interval < avg_interval * 1.5:
                features.append("timing:normal")
            else:
                features.append("timing:slow")
    
    return features


def detect_control_duplicates(controls_path: str, cache_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Detect if control patterns are similar to previously seen patterns.
    
    Args:
        controls_path: Path to controls JSONL file
        cache_path: Optional path to cache of known hashes
        
    Returns:
        Dictionary with duplicate detection results
    """
    try:
        # Extract features
        features = extract_control_features(controls_path)
        
        if not features:
            return {
                "error": "No features extracted from controls",
                "simhash_distances": [],
                "min_distance": 64,
                "risk_level": "unknown"
            }
        
        # Compute SimHash
        control_simhash = simhash(features)
        
        # Check against cache if provided
        min_distance = 64
        similar_hashes = []
        
        if cache_path and Path(cache_path).exists():
            try:
                with open(cache_path, 'r') as f:
                    known_hashes = json.load(f)
                
                for known_hash in known_hashes.get('control_hashes', []):
                    distance = hamming_distance(control_simhash, known_hash)
                    if distance < min_distance:
                        min_distance = distance
                        similar_hashes.append((control_simhash, known_hash, distance))
                        
            except Exception:
                # Cache read failed, continue without cache check
                pass
        
        # Determine risk level
        if min_distance <= 8:
            risk_level = "high"
        elif min_distance <= 16:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "feature_count": len(features),
            "simhash": control_simhash,
            "simhash_distances": [s[2] for s in similar_hashes],
            "min_distance": min_distance,
            "risk_level": risk_level,
            "similar_controls": len(similar_hashes) > 0
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "simhash_distances": [],
            "min_distance": 64,
            "risk_level": "unknown"
        }


def precheck_shard(shard_dir: str, cache_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run local duplicate and quality checks before upload.
    
    Args:
        shard_dir: Path to GAP shard directory
        cache_path: Optional path to cache of known hashes
        
    Returns:
        Precheck results with recommendations
    """
    shard_path = Path(shard_dir)
    
    # Find video and controls files
    video_files = list(shard_path.glob("video.*"))
    controls_files = list(shard_path.glob("controls.*"))
    
    if not video_files:
        return {
            "error": "No video file found",
            "should_upload": False,
            "video_check": {"error": "No video file"},
            "controls_check": {"error": "No video file"}
        }
    
    if not controls_files:
        return {
            "error": "No controls file found", 
            "should_upload": False,
            "video_check": {"error": "No controls file"},
            "controls_check": {"error": "No controls file"}
        }
    
    video_path = str(video_files[0])
    controls_path = str(controls_files[0])
    
    # Run duplicate checks
    video_check = detect_video_duplicates(video_path, cache_path)
    controls_check = detect_control_duplicates(controls_path, cache_path)
    
    # Determine overall recommendation
    video_risk = video_check.get('risk_level', 'unknown')
    controls_risk = controls_check.get('risk_level', 'unknown')
    
    # Conservative recommendation
    should_upload = (
        video_risk in ['low', 'medium'] and 
        controls_risk in ['low', 'medium'] and
        not video_check.get('error') and
        not controls_check.get('error')
    )
    
    # Calculate estimated acceptance probability
    if video_risk == 'low' and controls_risk == 'low':
        acceptance_prob = 0.95
    elif video_risk == 'medium' or controls_risk == 'medium':
        acceptance_prob = 0.75
    elif video_risk == 'high' or controls_risk == 'high':
        acceptance_prob = 0.25
    else:
        acceptance_prob = 0.5  # Unknown
    
    return {
        "should_upload": should_upload,
        "estimated_acceptance": acceptance_prob,
        "video_check": video_check,
        "controls_check": controls_check,
        "recommendation": (
            "Upload recommended" if should_upload 
            else "Upload not recommended - high duplicate risk"
        )
    }


def update_cache(shard_dir: str, cache_path: str) -> bool:
    """
    Update local cache with hashes from a new shard.
    
    Args:
        shard_dir: Path to GAP shard directory
        cache_path: Path to cache file
        
    Returns:
        True if cache updated successfully
    """
    try:
        shard_path = Path(shard_dir)
        
        # Load existing cache
        cache_data = {"video_hashes": [], "control_hashes": []}
        if Path(cache_path).exists():
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
        
        # Extract new hashes
        video_files = list(shard_path.glob("video.*"))
        controls_files = list(shard_path.glob("controls.*"))
        
        if video_files and HAS_CV2:
            video_path = str(video_files[0])
            frames = extract_keyframes(video_path, interval=5.0)
            for frame in frames:
                try:
                    hash_val = phash(frame)
                    if hash_val not in cache_data["video_hashes"]:
                        cache_data["video_hashes"].append(hash_val)
                except Exception:
                    continue
        
        if controls_files:
            controls_path = str(controls_files[0])
            features = extract_control_features(controls_path)
            if features:
                control_hash = simhash(features)
                if control_hash not in cache_data["control_hashes"]:
                    cache_data["control_hashes"].append(control_hash)
        
        # Save updated cache
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        return True
        
    except Exception:
        return False 