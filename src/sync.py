#!/usr/bin/env python3
"""
Ankiboard - Main synchronization script

Usage:
    python sync.py              # Run sync with default settings
    python sync.py --no-commit  # Export only, don't commit
    python sync.py --db /path   # Use specific database path
    python sync.py --force      # Force sync even if no changes
"""
import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

from anki_reader import get_default_anki_db_path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_exporter import DataExporter


def load_existing_stats(data_dir):
    """Load existing stats.json if it exists"""
    stats_file = Path(data_dir) / "stats.json"
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def stats_changed(old_stats, new_stats):
    """Check if stats have meaningful changes (ignore generated_at timestamp)"""
    if old_stats is None:
        return True

    # Compare key fields that indicate actual data changes
    keys_to_compare = ['cards', 'streak', 'weekly_reviews', 'weekly_time_minutes']
    for key in keys_to_compare:
        if old_stats.get(key) != new_stats.get(key):
            return True

    return False


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


def sync_stats(db_path=None, commit=True, push=True, repo_root=None, quiet=False, force=False):
    """Main sync function"""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent

    repo_root = Path(repo_root)
    data_dir = repo_root / "data"
    docs_dir = repo_root / "docs"

    def log(msg):
        if not quiet:
            print(msg)

    # Resolve database path
    if db_path is None:
        db_path = get_default_anki_db_path()

    # Step 1: Calculate statistics from Anki
    try:
        from stats_calculator import StatsCalculator
        calc = StatsCalculator(db_path)
        stats = calc.get_all_stats()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False
    except sqlite3.OperationalError as e:
        if "locked" in str(e):
            print("Error: Database locked, close Anki first")
        else:
            print(f"Error: {e}")
        return False

    # Check if stats have actually changed
    old_stats = load_existing_stats(data_dir)
    if not force and not stats_changed(old_stats, stats):
        print("Ankiboard: No changes")
        return True

    log("Ankiboard")
    log("=" * 40)

    # Export stats to files
    log("\n[1/2] Exporting statistics...")
    exporter = DataExporter(data_dir)
    exporter.export_stats(stats)
    exporter.export_history(stats)
    log(f"  - Total cards: {stats['cards']['total']:,}")
    log(f"  - Current streak: {stats['streak']} days")
    log(f"  - Weekly reviews: {stats['weekly_reviews']:,}")

    # Copy stats.json to docs/ for GitHub Pages
    if docs_dir.exists():
        shutil.copy(data_dir / "stats.json", docs_dir / "stats.json")
        log(f"  - Updated: docs/stats.json")

    # Step 2: Commit changes (optional)
    committed = False
    pushed = False

    if commit:
        log("\n[2/2] Committing changes...")

        # Check if in git repo
        success, _, _ = run_git_command(['status'], cwd=repo_root)
        if not success:
            log("  - Not a git repository, skipping commit")
        else:
            # Stage files
            files_to_stage = [
                "data/stats.json",
                "data/history.json",
                "docs/stats.json"
            ]

            for f in files_to_stage:
                run_git_command(['add', f], cwd=repo_root)

            # Check if there are changes
            success, stdout, _ = run_git_command(['diff', '--cached', '--quiet'], cwd=repo_root)
            if success:
                log("  - No changes to commit")
            else:
                # Commit with stats summary
                date_str = stats['generated_at'][:10]
                cards = stats['cards']['total']
                reviews = stats['weekly_reviews']
                streak = stats['streak']
                time_min = stats.get('weekly_time_minutes', 0)
                commit_msg = f"chore: sync anki stats ({date_str})\n\n{cards:,} cards | {reviews} reviews | {streak} days | {time_min}min"

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
        log("\n[2/2] Skipping commit (--no-commit)")

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

        print(f"Ankiboard {status}")
        print(f"{cards:,} cards | {reviews} reviews | {streak} days | {time_min}min")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Sync Anki statistics to GitHub Pages'
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
        '-q', '--quiet',
        action='store_true',
        help='Compact output for notifications (Keyboard Maestro, etc.)'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force sync even if database has not changed'
    )

    args = parser.parse_args()

    success = sync_stats(
        db_path=args.db,
        commit=not args.no_commit,
        push=not args.no_push,
        repo_root=args.repo,
        quiet=args.quiet,
        force=args.force
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
