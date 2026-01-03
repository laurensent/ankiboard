"""
Data Exporter - Export Anki statistics to JSON files
"""
import json
import os
from datetime import datetime
from pathlib import Path
from stats_calculator import StatsCalculator


class DataExporter:
    """Export statistics to JSON files for persistence and display"""

    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_stats(self, stats):
        """Export current stats to JSON file"""
        stats_file = self.output_dir / "stats.json"

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        return stats_file

    def export_history(self, stats):
        """Append current stats to history file"""
        history_file = self.output_dir / "history.json"

        # Load existing history
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []

        # Add current snapshot (only key metrics to keep file small)
        snapshot = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_cards': stats['cards']['total'],
            'mature_cards': stats['cards']['mature'],
            'new_cards': stats['cards']['new'],
            'streak': stats['streak'],
            'weekly_reviews': stats['weekly_reviews'],
            'weekly_time_minutes': stats['weekly_time_minutes']
        }

        # Only add if different from last entry (same day update)
        if history and history[-1]['date'] == snapshot['date']:
            history[-1] = snapshot
        else:
            history.append(snapshot)

        # Keep last 365 days
        history = history[-365:]

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)

        return history_file

    def export_heatmap_data(self, stats):
        """Export heatmap data separately for easier processing"""
        heatmap_file = self.output_dir / "heatmap.json"

        with open(heatmap_file, 'w', encoding='utf-8') as f:
            json.dump(stats['heatmap_data'], f, indent=2)

        return heatmap_file

    def export_all(self, db_path=None):
        """Export all statistics"""
        calc = StatsCalculator(db_path)
        stats = calc.get_all_stats()

        self.export_stats(stats)
        self.export_history(stats)
        self.export_heatmap_data(stats)

        return stats


if __name__ == "__main__":
    exporter = DataExporter()
    stats = exporter.export_all()
    print(f"Exported stats: {stats['cards']['total']} total cards")
