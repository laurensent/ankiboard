# Ankiboard

Track your Anki learning progress. [Live Demo](https://laurensent.github.io/ankiboard/)

## Features

- Review activity heatmap
- Weekly reviews and time charts
- Monthly deck ranking
- All decks progress visualization
- Auto-generated badges
- Light/Dark theme support

## Usage

```bash
./run_sync.sh [options]
```

| Option | Description |
|--------|-------------|
| `-d, --db PATH` | Use specific Anki database path |
| `--no-commit` | Export data only, don't commit |
| `--no-push` | Commit but don't push |
| `-q, --quiet` | Compact output for notifications |

## Setup

1. Clone this repository
2. Run `./run_sync.sh` (requires Anki to be closed)
3. Enable GitHub Pages: Settings > Pages > Source: GitHub Actions
