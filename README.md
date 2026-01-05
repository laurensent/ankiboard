# Ankiboard

Anki statistics dashboard with beautiful visualizations.

## Features

- Review activity heatmap (GitHub contribution style)
- Weekly reviews and time charts
- Monthly deck ranking
- All decks progress visualization
- Auto-generated badges
- Light/Dark theme support

## Live Dashboard

[https://laurensent.github.io/ankiboard/](https://laurensent.github.io/ankiboard/)

## Usage

```bash
# Run sync (export + commit + push)
./run_sync.sh

# Export only, no commit
./run_sync.sh --no-commit

# Quiet mode (for automation)
./run_sync.sh -q
```

### Options

| Option | Description |
|--------|-------------|
| `--no-commit` | Export data only, don't commit |
| `--no-push` | Commit but don't push |
| `-q, --quiet` | Compact output for notifications |
| `-d, --db PATH` | Use specific Anki database path |

### Keyboard Maestro Integration

1. Create a new macro
2. Add "Execute Shell Script" action
3. Script: `~/path/to/ankiboard/run_sync.sh`
4. Output: "Display results in a notification"

## Setup

1. Clone this repository
2. Run `./run_sync.sh` (requires Anki to be closed)
3. Enable GitHub Pages: Settings > Pages > Source: `docs/`

## Notes

- Opens Anki database in **read-only mode**
- Close Anki before running sync to avoid database lock
- Supports both light and dark themes
