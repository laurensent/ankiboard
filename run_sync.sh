#!/bin/bash
# Anki Stats Sync - Local execution script

# Set project path (override if needed for automation tools)
ANKI_SYNC_DIR="${ANKI_SYNC_DIR:-}"

# Fall back to script location if not set
if [ -z "$ANKI_SYNC_DIR" ]; then
    ANKI_SYNC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

cd "$ANKI_SYNC_DIR"

# Run sync
python3 src/sync.py "$@"
