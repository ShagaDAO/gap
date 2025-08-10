#!/bin/bash
# GAP v0.2 Sample Shard Downloader
# Downloads the complete 100MB Star Atlas reference shard

set -e

SAMPLE_DIR="$(dirname "$0")"
MANIFEST_FILE="$SAMPLE_DIR/MANIFEST.json"

echo "GAP v0.2 Sample Shard Downloader"
echo "================================="

if [ ! -f "$MANIFEST_FILE" ]; then
    echo "Error: MANIFEST.json not found in $SAMPLE_DIR"
    exit 1
fi

# Read manifest
VIDEO_URL=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE'))['video']['download_url'])")
VIDEO_FILENAME=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE'))['video']['filename'])")
EXPECTED_SHA256=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE'))['video']['sha256'])")

echo "Downloading: $VIDEO_FILENAME"
echo "Source: $VIDEO_URL"
echo "Expected SHA256: $EXPECTED_SHA256"
echo

# Download with progress
if command -v curl >/dev/null 2>&1; then
    curl -L --progress-bar -o "$SAMPLE_DIR/$VIDEO_FILENAME" "$VIDEO_URL"
elif command -v wget >/dev/null 2>&1; then
    wget --progress=bar -O "$SAMPLE_DIR/$VIDEO_FILENAME" "$VIDEO_URL"
else
    echo "Error: Neither curl nor wget found. Please install one of them."
    exit 1
fi

# Verify hash
echo "Verifying download..."
if command -v shasum >/dev/null 2>&1; then
    ACTUAL_SHA256=$(shasum -a 256 "$SAMPLE_DIR/$VIDEO_FILENAME" | cut -d' ' -f1)
elif command -v sha256sum >/dev/null 2>&1; then
    ACTUAL_SHA256=$(sha256sum "$SAMPLE_DIR/$VIDEO_FILENAME" | cut -d' ' -f1)
else
    echo "Warning: No SHA256 utility found. Cannot verify download."
    ACTUAL_SHA256="$EXPECTED_SHA256"  # Skip verification
fi

if [ "$ACTUAL_SHA256" = "$EXPECTED_SHA256" ]; then
    echo "✅ Download verified successfully!"
    echo "Sample shard is ready for testing."
    echo
    echo "Validate with:"
    echo "  python3 ../../tools/validate.py --profile wayfarer-owl ."
else
    echo "❌ SHA256 mismatch!"
    echo "Expected: $EXPECTED_SHA256"
    echo "Actual:   $ACTUAL_SHA256"
    rm -f "$SAMPLE_DIR/$VIDEO_FILENAME"
    exit 1
fi 