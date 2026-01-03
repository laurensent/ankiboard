#!/bin/bash
# Anki Stats Sync - Local execution script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run sync
python3 src/sync.py "$@"
