"""
Statistics Calculator - Process Anki data into displayable statistics
"""
from datetime import datetime, timedelta
from anki_reader import AnkiReader


class StatsCalculator:
    """Calculate various statistics from Anki data"""

    def __init__(self, db_path=None):
        self.db_path = db_path

    def get_all_stats(self):
        """Get all statistics"""
        with AnkiReader(self.db_path) as reader:
            card_counts = reader.get_card_counts()
            decks = reader.get_decks()
            daily_reviews = reader.get_daily_review_counts(365)
            weekly_time = reader.get_total_review_time(7)

        return {
            'cards': card_counts,
            'decks': decks,
            'daily_reviews': daily_reviews,
            'streak': self._calculate_streak(daily_reviews),
            'weekly_reviews': self._calculate_weekly_reviews(daily_reviews),
            'weekly_time_minutes': weekly_time // 60000,
            'heatmap_data': self._prepare_heatmap_data(daily_reviews),
            'generated_at': datetime.now().isoformat()
        }

    def _calculate_streak(self, daily_reviews):
        """Calculate current study streak"""
        today = datetime.now().date()
        streak = 0

        # Check if studied today
        today_str = today.strftime('%Y-%m-%d')
        if today_str not in daily_reviews:
            # Check yesterday (streak might still be valid)
            yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
            if yesterday not in daily_reviews:
                return 0
            # Start counting from yesterday
            current = today - timedelta(days=1)
        else:
            current = today

        # Count consecutive days
        while True:
            date_str = current.strftime('%Y-%m-%d')
            if date_str in daily_reviews:
                streak += 1
                current -= timedelta(days=1)
            else:
                break

        return streak

    def _calculate_weekly_reviews(self, daily_reviews):
        """Calculate total reviews in the past 7 days"""
        today = datetime.now().date()
        total = 0

        for i in range(7):
            date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            total += daily_reviews.get(date_str, 0)

        return total

    def _prepare_heatmap_data(self, daily_reviews):
        """Prepare data for 52-week heatmap"""
        today = datetime.now().date()
        # Start from the beginning of the week, 52 weeks ago
        start = today - timedelta(days=today.weekday() + 52 * 7)

        heatmap = []
        current = start

        while current <= today:
            date_str = current.strftime('%Y-%m-%d')
            count = daily_reviews.get(date_str, 0)
            heatmap.append({
                'date': date_str,
                'count': count,
                'weekday': current.weekday(),
                'week': (current - start).days // 7
            })
            current += timedelta(days=1)

        return heatmap


if __name__ == "__main__":
    calc = StatsCalculator()
    stats = calc.get_all_stats()

    print(f"Total cards: {stats['cards']['total']}")
    print(f"Mature cards: {stats['cards']['mature']}")
    print(f"Current streak: {stats['streak']} days")
    print(f"Weekly reviews: {stats['weekly_reviews']}")
    print(f"Weekly time: {stats['weekly_time_minutes']} minutes")
    print(f"\nDecks ({len(stats['decks'])}):")
    for deck in list(stats['decks'].values())[:5]:
        print(f"  - {deck['name']}: {deck.get('total', 0)} cards")
