"""
README Generator - Generate README.md with Anki statistics display
"""
import json
from pathlib import Path


class ReadmeGenerator:
    """Generate README.md with statistics and heatmap"""

    def __init__(self, data_dir="data", output_dir="output", repo_root="."):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.repo_root = Path(repo_root)

    def load_stats(self):
        """Load stats from JSON file"""
        stats_file = self.data_dir / "stats.json"
        if not stats_file.exists():
            raise FileNotFoundError(f"Stats file not found: {stats_file}")

        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_badges(self, stats):
        """Generate shields.io style badges"""
        cards = stats['cards']
        date = stats['generated_at'][:10]

        badges = []

        # Last sync badge (shields.io uses -- for hyphen)
        date_encoded = date.replace("-", "--")
        badges.append(
            f"![Last Sync](https://img.shields.io/badge/Last_Sync-{date_encoded}-blue)"
        )

        # Total cards
        total_str = f"{cards['total']:,}".replace(",", "_")
        badges.append(
            f"![Total Cards](https://img.shields.io/badge/Total_Cards-{total_str}-informational)"
        )

        # Streak
        streak = stats['streak']
        streak_color = "brightgreen" if streak >= 7 else ("green" if streak >= 3 else "yellow")
        badges.append(
            f"![Streak](https://img.shields.io/badge/Streak-{streak}_days-{streak_color})"
        )

        # Mastery percentage
        total_active = cards['total'] - cards['suspended']
        mastery_pct = int(cards['mature'] / total_active * 100) if total_active > 0 else 0
        mastery_color = "brightgreen" if mastery_pct >= 80 else ("green" if mastery_pct >= 50 else "yellow")
        badges.append(
            f"![Mastery](https://img.shields.io/badge/Mastery-{mastery_pct}%25-{mastery_color})"
        )

        return " ".join(badges)

    def generate_decks_table(self, stats, max_decks=10):
        """Generate table of top decks in collapsible section"""
        decks = stats.get('decks', {})

        sorted_decks = sorted(
            decks.values(),
            key=lambda d: d.get('total', 0),
            reverse=True
        )[:max_decks]

        if not sorted_decks:
            return ""

        lines = [
            "",
            "<details>",
            "<summary><strong>Top Decks</strong></summary>",
            "",
            "| Deck | Total | Mature | New |",
            "|------|-------|--------|-----|"
        ]

        for deck in sorted_decks:
            name = deck['name']
            if len(name) > 40:
                name = name[:37] + "..."
            lines.append(
                f"| {name} | {deck.get('total', 0):,} | "
                f"{deck.get('mature', 0):,} | {deck.get('new', 0):,} |"
            )

        lines.append("")
        lines.append("</details>")

        return '\n'.join(lines)

    def generate_readme(self):
        """Generate full README.md content"""
        stats = self.load_stats()

        readme = f"""# Anki Statistics

{self.generate_badges(stats)}

## Review Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="output/heatmap-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="output/heatmap.svg">
  <img alt="Review Heatmap" src="output/heatmap.svg">
</picture>

## Statistics

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="output/stats-card-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="output/stats-card.svg">
  <img alt="Statistics" src="output/stats-card.svg">
</picture>

## Progress

<img src="output/progress-bar.svg" alt="Progress" width="300">

{self.generate_decks_table(stats)}
"""

        return readme

    def write_readme(self, output_path=None):
        """Write README to file"""
        if output_path is None:
            output_path = self.repo_root / "README.md"
        else:
            output_path = Path(output_path)

        readme_content = self.generate_readme()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        return output_path


if __name__ == "__main__":
    generator = ReadmeGenerator()
    try:
        readme_path = generator.write_readme()
        print(f"Generated: {readme_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run data_exporter.py first to generate stats data")
