"""
Anki Database Reader - Read-only access to Anki SQLite database
"""
import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import quote


def get_anki_base_path():
    """Get the Anki base directory for the current platform"""
    if sys.platform == 'darwin':
        return Path.home() / "Library" / "Application Support" / "Anki2"
    elif sys.platform == 'win32':
        return Path(os.environ.get('APPDATA', '')) / "Anki2"
    else:  # Linux and others
        return Path.home() / ".local" / "share" / "Anki2"


def get_default_anki_db_path():
    """Get the default Anki database path

    Priority:
    1. ANKI_DB_PATH environment variable
    2. Auto-detect based on platform
    """
    # Check environment variable first
    env_path = os.environ.get('ANKI_DB_PATH')
    if env_path:
        path = Path(env_path)
        if path.exists():
            return str(path)
        raise FileNotFoundError(f"ANKI_DB_PATH not found: {env_path}")

    # Auto-detect based on platform
    anki_base = get_anki_base_path()

    if not anki_base.exists():
        raise FileNotFoundError(f"Anki directory not found: {anki_base}")

    # Find profiles with valid collection.anki2
    profiles = [d for d in anki_base.iterdir()
                if d.is_dir() and not d.name.startswith('.')
                and d.name not in ('addons21', 'logs')
                and (d / "collection.anki2").exists()]

    if not profiles:
        raise FileNotFoundError("No Anki profile with collection.anki2 found")

    # Use first valid profile
    profile = profiles[0]
    db_path = profile / "collection.anki2"

    return str(db_path)


class AnkiReader:
    """Read-only Anki database reader"""

    def __init__(self, db_path=None):
        self.db_path = db_path or get_default_anki_db_path()
        self.conn = None

    def __enter__(self):
        # Open in immutable mode - works with WAL databases and prevents any writes
        encoded_path = quote(self.db_path, safe='/:')
        uri = f"file:{encoded_path}?immutable=1"
        self.conn = sqlite3.connect(uri, uri=True)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def get_review_history(self, days=365):
        """Get review history for the past N days"""
        cursor = self.conn.cursor()

        # revlog.id is timestamp in milliseconds
        cutoff = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        cursor.execute("""
            SELECT
                id,
                cid,
                ease,
                ivl,
                time,
                type
            FROM revlog
            WHERE id > ?
            ORDER BY id
        """, (cutoff,))

        return cursor.fetchall()

    def get_daily_review_counts(self, days=365):
        """Get review counts grouped by day"""
        cursor = self.conn.cursor()

        cutoff = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        # Group by day (convert ms timestamp to date)
        cursor.execute("""
            SELECT
                date(id/1000, 'unixepoch', 'localtime') as review_date,
                COUNT(*) as count
            FROM revlog
            WHERE id > ?
            GROUP BY review_date
            ORDER BY review_date
        """, (cutoff,))

        return {row['review_date']: row['count'] for row in cursor.fetchall()}

    def get_card_counts(self):
        """Get card counts by state"""
        cursor = self.conn.cursor()

        # Card types: 0=new, 1=learning, 2=review, 3=relearning
        # Queue: -1=suspended, -2=buried, 0=new, 1=learning, 2=review, 3=day learn, 4=preview
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN type = 0 THEN 1 ELSE 0 END) as new_cards,
                SUM(CASE WHEN type = 1 OR type = 3 THEN 1 ELSE 0 END) as learning,
                SUM(CASE WHEN type = 2 THEN 1 ELSE 0 END) as review,
                SUM(CASE WHEN queue < 0 THEN 1 ELSE 0 END) as suspended
            FROM cards
        """)

        row = cursor.fetchone()
        return {
            'total': row['total'],
            'new': row['new_cards'],
            'learning': row['learning'],
            'mature': row['review'],
            'suspended': row['suspended']
        }

    def get_decks(self):
        """Get all decks with their card counts"""
        cursor = self.conn.cursor()
        decks = {}

        # Try new Anki schema (separate decks table)
        try:
            cursor.execute("SELECT id, name FROM decks")
            for row in cursor.fetchall():
                # Deck names use \x1f as hierarchy separator
                name = row['name'].replace('\x1f', '::')
                decks[str(row['id'])] = {
                    'name': name,
                    'id': str(row['id'])
                }
        except sqlite3.OperationalError:
            # Fall back to old schema (decks in col table as JSON)
            cursor.execute("SELECT decks FROM col")
            row = cursor.fetchone()
            if row and row['decks']:
                decks_json = json.loads(row['decks'])
                for deck_id, deck_info in decks_json.items():
                    decks[deck_id] = {
                        'name': deck_info['name'],
                        'id': deck_id
                    }

        # Get card counts per deck
        cursor.execute("""
            SELECT
                did,
                COUNT(*) as total,
                SUM(CASE WHEN type = 0 THEN 1 ELSE 0 END) as new_cards,
                SUM(CASE WHEN type = 2 THEN 1 ELSE 0 END) as mature
            FROM cards
            GROUP BY did
        """)

        for row in cursor.fetchall():
            deck_id = str(row['did'])
            if deck_id in decks:
                decks[deck_id]['total'] = row['total']
                decks[deck_id]['new'] = row['new_cards']
                decks[deck_id]['mature'] = row['mature']

        return decks

    def get_total_review_time(self, days=7):
        """Get total review time in milliseconds for past N days"""
        cursor = self.conn.cursor()

        cutoff = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        cursor.execute("""
            SELECT SUM(time) as total_time
            FROM revlog
            WHERE id > ?
        """, (cutoff,))

        row = cursor.fetchone()
        return row['total_time'] or 0

    def get_daily_review_time(self, days=365):
        """Get review time in minutes grouped by day"""
        cursor = self.conn.cursor()

        cutoff = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        cursor.execute("""
            SELECT
                date(id/1000, 'unixepoch', 'localtime') as review_date,
                SUM(time) as total_time
            FROM revlog
            WHERE id > ?
            GROUP BY review_date
            ORDER BY review_date
        """, (cutoff,))

        # Convert milliseconds to minutes
        return {row['review_date']: (row['total_time'] or 0) // 60000
                for row in cursor.fetchall()}

    def get_deck_review_counts(self, days=7):
        """Get review counts per deck for past N days"""
        cursor = self.conn.cursor()

        cutoff = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        # Join revlog with cards to get deck info
        cursor.execute("""
            SELECT
                c.did as deck_id,
                COUNT(*) as review_count
            FROM revlog r
            JOIN cards c ON r.cid = c.id
            WHERE r.id > ?
            GROUP BY c.did
            ORDER BY review_count DESC
        """, (cutoff,))

        return {str(row['deck_id']): row['review_count'] for row in cursor.fetchall()}

    def get_daily_deck_counts(self, days=365):
        """Get count of unique decks studied per day"""
        cursor = self.conn.cursor()

        cutoff = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        cursor.execute("""
            SELECT
                date(r.id/1000, 'unixepoch', 'localtime') as review_date,
                COUNT(DISTINCT c.did) as deck_count
            FROM revlog r
            JOIN cards c ON r.cid = c.id
            WHERE r.id > ?
            GROUP BY review_date
            ORDER BY review_date
        """, (cutoff,))

        return {row['review_date']: row['deck_count'] for row in cursor.fetchall()}


if __name__ == "__main__":
    # Test the reader
    with AnkiReader() as reader:
        print("Card counts:", reader.get_card_counts())
        print("\nDecks:", list(reader.get_decks().values())[:3])

        daily = reader.get_daily_review_counts(30)
        print(f"\nDaily reviews (last 30 days): {len(daily)} days with reviews")
