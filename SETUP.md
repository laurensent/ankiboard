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

# Quiet mode (compact output for notifications)
./run_sync.sh -q
```

### Keyboard Maestro Integration

The script auto-detects non-terminal environments and uses quiet mode automatically.

1. Create a new macro in Keyboard Maestro
2. Add action: "Execute Shell Script" or "Execute script file"
3. Script path: `~/Workspace/VSCodeProjects/anki-stats-sync/run_sync.sh`
4. Output: "Display results in a notification"

Notification output example:
```
Anki Pushed
2,479 cards | 17 reviews | 2 days | 12min
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

3. GitHub Actions is disabled (local generation is used instead)

## GitHub Actions Management

GitHub Actions is disabled by default since all generation happens locally.

### Delete old workflow runs

```bash
gh run list --limit 100 --json databaseId -q '.[].databaseId' | xargs -I {} gh run delete {}
```

### Re-enable Actions (if needed)

Edit `.github/workflows/sync.yml` and remove the `if: false` line.

## File Structure

```
anki-stats-sync/
├── data/
│   ├── stats.json        # Current statistics
│   ├── history.json      # Historical data
│   └── heatmap.json      # Heatmap data
├── output/
│   ├── heatmap.svg       # Review heatmap (light)
│   ├── heatmap-dark.svg  # Review heatmap (dark)
│   ├── decks.svg         # All decks progress (light)
│   ├── decks-dark.svg    # All decks progress (dark)
│   ├── weekly.svg        # Weekly reviews chart (light)
│   ├── weekly-dark.svg   # Weekly reviews chart (dark)
│   ├── time.svg          # Weekly time chart (light)
│   ├── time-dark.svg     # Weekly time chart (dark)
│   ├── cards.svg         # Monthly deck ranking (light)
│   └── cards-dark.svg    # Monthly deck ranking (dark)
├── src/
│   ├── anki_reader.py       # Read-only Anki DB access
│   ├── stats_calculator.py  # Calculate statistics
│   ├── data_exporter.py     # Export to JSON
│   ├── heatmap_generator.py # Generate heatmap SVG
│   ├── deck_svg_generator.py    # Generate deck progress SVG
│   ├── weekly_bar_generator.py  # Generate weekly reviews SVG
│   ├── weekly_time_generator.py # Generate weekly time SVG
│   ├── deck_cards_generator.py  # Generate monthly ranking SVG
│   ├── readme_generator.py      # Generate README with badges
│   └── sync.py                  # Main sync script
├── .github/workflows/
│   └── sync.yml          # GitHub Actions (disabled)
├── README.md             # Auto-generated stats display
├── SETUP.md              # This file
└── run_sync.sh           # Main entry script
```

## Command Line Options

```
./run_sync.sh [options]

Options:
  --no-commit    Export data only, don't commit
  --no-push      Commit but don't push to remote
  -q, --quiet    Compact output for notifications
  -d, --db PATH  Use specific Anki database path
  -r, --repo DIR Repository root directory
  --repo-url URL GitHub repository URL for badge links
```

## Notes

- The script opens Anki database in **read-only mode** (no modifications)
- Make sure Anki is closed when running sync (to avoid database lock)
- Stats are based on your default Anki profile
- All decks with cards are displayed (no limit)
- Supports both light and dark themes via `<picture>` tags
