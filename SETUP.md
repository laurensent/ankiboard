# Anki Stats Sync - Setup Guide

## Quick Start

### Manual Sync

```bash
# Run sync (export + commit + push)
./run_sync.sh

# Export only, no commit/push
./run_sync.sh --no-commit

# Commit but don't push
./run_sync.sh --no-push
```

### Automation

Use your preferred automation tool (cron, Keyboard Maestro, etc.) to call:

```bash
/path/to/anki-stats-sync/run_sync.sh
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
│   ├── stats.json        # Current statistics
│   ├── history.json      # Historical data
│   └── heatmap.json      # Heatmap data
├── output/
│   ├── heatmap.svg       # Light theme heatmap
│   ├── heatmap-dark.svg  # Dark theme heatmap
│   ├── decks.svg         # Light theme deck progress
│   └── decks-dark.svg    # Dark theme deck progress
├── src/
│   ├── anki_reader.py       # Read-only Anki DB access
│   ├── stats_calculator.py  # Calculate statistics
│   ├── data_exporter.py     # Export to JSON
│   ├── heatmap_generator.py # Generate heatmap SVG
│   ├── deck_svg_generator.py # Generate deck progress SVG
│   ├── readme_generator.py  # Generate README
│   └── sync.py              # Main sync script
├── README.md                # Auto-generated stats display
└── run_sync.sh              # Convenience script
```

## Notes

- The script opens Anki database in **read-only mode** (no modifications)
- Make sure Anki is closed when running sync (to avoid database lock)
- Stats are based on your default Anki profile
