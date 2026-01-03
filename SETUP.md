# Anki Stats Sync - Setup Guide

## Quick Start

### Manual Sync

```bash
# Run sync (export + commit)
./run_sync.sh

# Export only, no commit
./run_sync.sh --no-commit

# Export, commit and push
./run_sync.sh --push
```

### Automated Sync (macOS)

To automatically sync daily at 23:00:

1. Copy the LaunchAgent plist:
   ```bash
   cp setup/com.anki.stats-sync.plist ~/Library/LaunchAgents/
   ```

2. Update paths in the plist if needed:
   ```bash
   # Edit the file to match your paths
   nano ~/Library/LaunchAgents/com.anki.stats-sync.plist
   ```

3. Load the LaunchAgent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.anki.stats-sync.plist
   ```

4. To unload:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.anki.stats-sync.plist
   ```

### View Logs

```bash
# View stdout log
cat /tmp/anki-stats-sync.log

# View stderr log
cat /tmp/anki-stats-sync.err
```

## GitHub Repository Setup

1. Create a new GitHub repository

2. Initialize git and push:
   ```bash
   cd /path/to/anki-stats-sync
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/anki-stats-sync.git
   git push -u origin main
   ```

3. The GitHub Action will automatically regenerate the display when data is pushed

## File Structure

```
anki-stats-sync/
├── data/
│   ├── stats.json      # Current statistics
│   ├── history.json    # Historical data
│   └── heatmap.json    # Heatmap data
├── output/
│   ├── heatmap.svg     # Light theme heatmap
│   └── heatmap-dark.svg # Dark theme heatmap
├── src/
│   ├── anki_reader.py     # Read-only Anki DB access
│   ├── stats_calculator.py # Calculate statistics
│   ├── data_exporter.py   # Export to JSON
│   ├── heatmap_generator.py # Generate SVG heatmap
│   ├── readme_generator.py  # Generate README
│   └── sync.py            # Main sync script
├── README.md              # Auto-generated stats display
└── run_sync.sh            # Convenience script
```

## Notes

- The script opens Anki database in **read-only mode** (no modifications)
- Make sure Anki is closed when running sync (to avoid database lock)
- Stats are based on your default Anki profile
