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


def sync_stats(db_path=None, commit=True, push=False, repo_root=None):
    """Main sync function"""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent

    repo_root = Path(repo_root)
    data_dir = repo_root / "data"
    output_dir = repo_root / "output"

    print("Anki Stats Sync")
    print("=" * 40)

    # Step 1: Export data from Anki
    print("\n[1/5] Exporting statistics...")
    try:
        exporter = DataExporter(data_dir)
        stats = exporter.export_all(db_path)
        print(f"  - Total cards: {stats['cards']['total']:,}")
        print(f"  - Current streak: {stats['streak']} days")
        print(f"  - Weekly reviews: {stats['weekly_reviews']:,}")
    except FileNotFoundError as e:
        print(f"  Error: {e}")
        print("  Make sure Anki is installed and you have a profile")
        return False
    except sqlite3.OperationalError as e:
        if "locked" in str(e):
            print("  Error: Database is locked")
            print("  Please close Anki before running sync")
        else:
            print(f"  Database error: {e}")
        return False

    # Step 2: Generate heatmap
    print("\n[2/5] Generating heatmap...")
    generator = HeatmapGenerator(output_dir)
    light_file, dark_file = generator.generate_from_data(stats['heatmap_data'])
    print(f"  - Generated: {light_file.name}, {dark_file.name}")

    # Step 3: Generate deck progress SVG
    print("\n[3/5] Generating deck visualization...")
    deck_gen = DeckSvgGenerator(output_dir)
    deck_light, deck_dark = deck_gen.generate_all(stats['decks'])
    print(f"  - Generated: {deck_light.name}, {deck_dark.name}")

    # Step 4: Generate README
    print("\n[4/5] Generating README...")
    readme_gen = ReadmeGenerator(data_dir, output_dir, repo_root)
    readme_path = readme_gen.write_readme()
    print(f"  - Generated: {readme_path.name}")

    # Step 5: Commit changes (optional)
    if commit:
        print("\n[5/5] Committing changes...")

        # Check if in git repo
        success, _, _ = run_git_command(['status'], cwd=repo_root)
        if not success:
            print("  - Not a git repository, skipping commit")
            return True

        # Stage files
        files_to_stage = [
            "data/stats.json",
            "data/history.json",
            "data/heatmap.json",
            "output/heatmap.svg",
            "output/heatmap-dark.svg",
            "output/decks.svg",
            "output/decks-dark.svg",
            "README.md"
        ]

        for f in files_to_stage:
            run_git_command(['add', f], cwd=repo_root)

        # Check if there are changes
        success, stdout, _ = run_git_command(['diff', '--cached', '--quiet'], cwd=repo_root)
        if success:
            print("  - No changes to commit")
        else:
            # Commit
            date_str = stats['generated_at'][:10]
            commit_msg = f"chore: sync anki stats ({date_str})"

            success, _, stderr = run_git_command(
                ['commit', '-m', commit_msg],
                cwd=repo_root
            )

            if success:
                print(f"  - Committed: {commit_msg}")
            else:
                print(f"  - Commit failed: {stderr}")

        # Push (optional)
        if push:
            print("\n  Pushing to remote...")
            success, _, stderr = run_git_command(['push'], cwd=repo_root)
            if success:
                print("  - Pushed successfully")
            else:
                print(f"  - Push failed: {stderr}")
    else:
        print("\n[5/5] Skipping commit (--no-commit)")

    print("\n" + "=" * 40)
    print("Sync complete!")
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
        '--push',
        action='store_true',
        help='Push after committing'
    )
    parser.add_argument(
        '--repo', '-r',
        help='Repository root directory',
        default=None
    )

    args = parser.parse_args()

    success = sync_stats(
        db_path=args.db,
        commit=not args.no_commit,
        push=args.push,
        repo_root=args.repo
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
