# Ankiboard

A minimal dashboard for tracking Anki learning progress.

[Live Demo](https://laurensent.github.io/ankiboard/)

## Features

- 52-week activity heatmap
- Weekly deck study chart
- Top deck rankings
- All decks progress overview
- Auto-generated status badges
- Dark theme

## Usage

```bash
./run_sync.sh [options]
```

| Option | Description |
|--------|-------------|
| `-d, --db PATH` | Custom Anki database path |
| `--no-commit` | Export only, skip git commit |
| `--no-push` | Commit but skip push |
| `-q, --quiet` | Compact output |
| `-f, --force` | Force sync even if unchanged |

## Setup

1. Clone this repository
2. Run `./run_sync.sh` (Anki must be closed)
3. Enable GitHub Pages: Settings > Pages > Source: GitHub Actions

## Acknowledgments

Design inspired by [opencode-wrapped](https://github.com/moddi3/opencode-wrapped)

## License

MIT
