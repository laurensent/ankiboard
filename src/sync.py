#!/usr/bin/env python3
"""
Anki Stats Sync - Main synchronization script

Usage:
    python sync.py              # Run sync with default settings
    python sync.py --no-commit  # Export only, don't commit
    python sync.py --db /path   # Use specific database path
"""
import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_exporter import DataExporter
from heatmap_generator import HeatmapGenerator
from deck_svg_generator import DeckSvgGenerator
from weekly_bar_generator import WeeklyBarGenerator
from weekly_time_generator import WeeklyTimeGenerator
from deck_cards_generator import DeckCardsGenerator
from readme_generator import ReadmeGenerator


def run_git_command(args, cwd=None):
    """Run a git command and return success status"""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, "", "Git not found"


def sync_stats(db_path=None, commit=True, push=True, repo_root=None, repo_url=None, quiet=False):
    """Main sync function"""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent

    repo_root = Path(repo_root)
    data_dir = repo_root / "data"
    output_dir = repo_root / "output"

    def log(msg):
        if not quiet:
            print(msg)

    log("Anki Stats Sync")
    log("=" * 40)

    # Step 1: Export data from Anki
    log("\n[1/8] Exporting statistics...")
    try:
        exporter = DataExporter(data_dir)
        stats = exporter.export_all(db_path)
        log(f"  - Total cards: {stats['cards']['total']:,}")
        log(f"  - Current streak: {stats['streak']} days")
        log(f"  - Weekly reviews: {stats['weekly_reviews']:,}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False
    except sqlite3.OperationalError as e:
        if "locked" in str(e):
            print("Error: Database locked, close Anki first")
        else:
            print(f"Error: {e}")
        return False

    # Step 2: Generate heatmap
    log("\n[2/8] Generating heatmap...")
    generator = HeatmapGenerator(output_dir)
    light_file, dark_file = generator.generate_from_data(stats['heatmap_data'])
    log(f"  - Generated: {light_file.name}, {dark_file.name}")

    # Step 3: Generate deck progress SVG
    log("\n[3/8] Generating deck visualization...")
    deck_gen = DeckSvgGenerator(output_dir)
    deck_light, deck_dark = deck_gen.generate_all(stats['decks'])
    log(f"  - Generated: {deck_light.name}, {deck_dark.name}")

    # Step 4: Generate weekly bar chart
    log("\n[4/8] Generating weekly bar chart...")
    weekly_gen = WeeklyBarGenerator(output_dir)
    weekly_light, weekly_dark = weekly_gen.generate_from_data(stats['daily_reviews'])
    log(f"  - Generated: {weekly_light.name}, {weekly_dark.name}")

    # Step 5: Generate weekly time chart
    log("\n[5/8] Generating weekly time chart...")
    time_gen = WeeklyTimeGenerator(output_dir)
    time_light, time_dark = time_gen.generate_from_data(stats['daily_time'])
    log(f"  - Generated: {time_light.name}, {time_dark.name}")

    # Step 6: Generate monthly deck reviews ranking
    log("\n[6/8] Generating monthly deck reviews...")
    cards_gen = DeckCardsGenerator(output_dir)
    cards_light, cards_dark = cards_gen.generate_all(stats['monthly_deck_reviews'])
    log(f"  - Generated: {cards_light.name}, {cards_dark.name}")

    # Step 7: Generate README
    log("\n[7/8] Generating README...")
    readme_gen = ReadmeGenerator(data_dir, output_dir, repo_root, repo_url=repo_url, stats=stats)
    readme_path = readme_gen.write_readme()
    log(f"  - Generated: {readme_path.name}")

    # Step 8: Commit changes (optional)
    committed = False
    pushed = False

    if commit:
        log("\n[8/8] Committing changes...")

        # Check if in git repo
        success, _, _ = run_git_command(['status'], cwd=repo_root)
        if not success:
            log("  - Not a git repository, skipping commit")
        else:
            # Stage files
            files_to_stage = [
                "data/stats.json",
                "data/history.json",
                "data/heatmap.json",
                "output/heatmap.svg",
                "output/heatmap-dark.svg",
                "output/decks.svg",
                "output/decks-dark.svg",
                "output/weekly.svg",
                "output/weekly-dark.svg",
                "output/time.svg",
                "output/time-dark.svg",
                "output/cards.svg",
                "output/cards-dark.svg",
                "README.md"
            ]

            for f in files_to_stage:
                run_git_command(['add', f], cwd=repo_root)

            # Check if there are changes
            success, stdout, _ = run_git_command(['diff', '--cached', '--quiet'], cwd=repo_root)
            if success:
                log("  - No changes to commit")
            else:
                # Commit
                date_str = stats['generated_at'][:10]
                commit_msg = f"chore: sync anki stats ({date_str})"

                success, _, stderr = run_git_command(
                    ['commit', '-m', commit_msg],
                    cwd=repo_root
                )

                if success:
                    committed = True
                    log(f"  - Committed: {commit_msg}")
                else:
                    log(f"  - Commit failed: {stderr}")

            # Push (optional)
            if push:
                log("\n  Pushing to remote...")
                success, _, stderr = run_git_command(['push'], cwd=repo_root)
                if success:
                    pushed = True
                    log("  - Pushed successfully")
                else:
                    log(f"  - Push failed: {stderr}")
    else:
        log("\n[8/8] Skipping commit (--no-commit)")

    log("\n" + "=" * 40)
    log("Sync complete!")

    # Quiet mode: compact output for notifications
    if quiet:
        cards = stats['cards']['total']
        reviews = stats['weekly_reviews']
        streak = stats['streak']
        time_min = stats.get('weekly_time_minutes', 0)

        status = "Synced"
        if committed:
            status = "Pushed" if pushed else "Committed"

        print(f"Anki {status}")
        print(f"{cards:,} cards | {reviews} reviews | {streak} days | {time_min}min")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Sync Anki statistics to GitHub repository'
    )
    parser.add_argument(
        '--db', '-d',
        help='Path to Anki database (collection.anki2)',
        default=None
    )
    parser.add_argument(
        '--no-commit',
        action='store_true',
        help='Export data only, do not commit'
    )
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='Do not push after committing'
    )
    parser.add_argument(
        '--repo', '-r',
        help='Repository root directory',
        default=None
    )
    parser.add_argument(
        '--repo-url',
        help='GitHub repository URL (e.g., https://github.com/user/repo)',
        default=None
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Compact output for notifications (Keyboard Maestro, etc.)'
    )

    args = parser.parse_args()

    success = sync_stats(
        db_path=args.db,
        commit=not args.no_commit,
        push=not args.no_push,
        repo_root=args.repo,
        repo_url=args.repo_url,
        quiet=args.quiet
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
