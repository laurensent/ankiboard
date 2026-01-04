"""
Deck Cards Generator - Generate vertical bar chart for monthly deck reviews ranking
"""
from pathlib import Path


class DeckCardsGenerator:
    """Generate SVG bar chart for monthly deck reviews ranking"""

    # Fixed dimensions
    TOTAL_WIDTH = 792  # Fixed width to match heatmap
    MAX_BAR_HEIGHT = 80
    MIN_BAR_HEIGHT = 3
    MIN_BAR_WIDTH = 20  # Minimum bar width
    BAR_GAP_RATIO = 0.2  # Gap is 20% of bar width

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_svg(self, monthly_reviews, dark_mode=False):
        """Generate SVG vertical bar chart for monthly deck reviews"""
        # Use all decks (no max limit)
        sorted_decks = monthly_reviews

        if not sorted_decks:
            return self._generate_empty_svg(dark_mode)

        # Theme colors
        if dark_mode:
            bg_color = '#0d1117'
            bar_color = '#f78166'  # Orange for cards
            bar_empty_color = '#21262d'  # Empty bar color
            text_color = '#e6edf3'
            label_color = '#8b949e'
        else:
            bg_color = '#ffffff'
            bar_color = '#fb8f44'  # Orange
            bar_empty_color = '#ebedf0'  # Empty bar color
            text_color = '#1f2328'
            label_color = '#656d76'

        # Calculate dimensions
        num_bars = len(sorted_decks)
        left_margin = 40
        top_margin = 20
        bottom_margin = 60
        width = self.TOTAL_WIDTH
        height = top_margin + self.MAX_BAR_HEIGHT + bottom_margin

        # Calculate adaptive bar width
        available_width = width - left_margin - 20  # 20px right margin
        # bar_width + gap = bar_width * (1 + GAP_RATIO)
        bar_width = available_width / (num_bars * (1 + self.BAR_GAP_RATIO))
        bar_width = max(self.MIN_BAR_WIDTH, bar_width)
        bar_gap = bar_width * self.BAR_GAP_RATIO

        # Get max count for scaling
        max_count = max(d.get('reviews', 0) for d in sorted_decks)
        if max_count == 0:
            max_count = 1

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{bg_color}"/>',
            f'<g transform="translate({left_margin}, {top_margin})">',
        ]

        for i, deck in enumerate(sorted_decks):
            x = i * (bar_width + bar_gap)
            count = deck.get('reviews', 0)

            # Calculate bar height and color
            if count == 0:
                bar_height = self.MIN_BAR_HEIGHT
                color = bar_empty_color
            else:
                bar_height = max(
                    self.MIN_BAR_HEIGHT,
                    int((count / max_count) * self.MAX_BAR_HEIGHT)
                )
                color = bar_color
            bar_y = self.MAX_BAR_HEIGHT - bar_height

            # Value label above bar
            label_y = bar_y - 8
            if count > 0:
                svg_parts.append(
                    f'<text x="{x + bar_width / 2}" y="{label_y}" '
                    f'fill="{text_color}" font-size="10" text-anchor="middle" '
                    f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" '
                    f'font-weight="600">{count}</text>'
                )
            else:
                # Show 0 in label color (less prominent)
                svg_parts.append(
                    f'<text x="{x + bar_width / 2}" y="{self.MAX_BAR_HEIGHT - 10}" '
                    f'fill="{label_color}" font-size="10" text-anchor="middle" '
                    f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">'
                    f'0</text>'
                )

            # Bar
            rx = 2 if bar_height > 4 else 1
            svg_parts.append(
                f'<rect x="{x}" y="{bar_y}" width="{bar_width}" '
                f'height="{bar_height}" fill="{color}" rx="{rx}" ry="{rx}">'
                f'<title>{count} reviews - {deck["name"]}</title></rect>'
            )

            # Deck name label (rotated 45 degrees)
            name = deck['name']
            if '::' in name:
                name = name.split('::')[-1]
            # Truncate based on bar width
            max_chars = max(5, int(bar_width / 6))
            if len(name) > max_chars:
                name = name[:max_chars - 2] + '..'

            label_x = x + bar_width / 2
            label_y = self.MAX_BAR_HEIGHT + 12
            svg_parts.append(
                f'<text x="{label_x}" y="{label_y}" '
                f'fill="{label_color}" font-size="10" '
                f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" '
                f'transform="rotate(45, {label_x}, {label_y})">'
                f'{name}</text>'
            )

        svg_parts.append('</g>')
        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def _generate_empty_svg(self, dark_mode=False):
        """Generate empty state SVG"""
        bg = "#0d1117" if dark_mode else "#ffffff"
        text = "#8b949e" if dark_mode else "#656d76"

        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="792" height="40">
<rect width="792" height="40" fill="{bg}"/>
<text x="396" y="24" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif"
font-size="13" fill="{text}">No data</text>
</svg>'''

    def generate_all(self, monthly_reviews):
        """Generate both light and dark versions"""
        light_svg = self.generate_svg(monthly_reviews, dark_mode=False)
        dark_svg = self.generate_svg(monthly_reviews, dark_mode=True)

        light_file = self.output_dir / "cards.svg"
        dark_file = self.output_dir / "cards-dark.svg"

        with open(light_file, 'w') as f:
            f.write(light_svg)

        with open(dark_file, 'w') as f:
            f.write(dark_svg)

        return light_file, dark_file


if __name__ == "__main__":
    import json
    from pathlib import Path

    data_dir = Path(__file__).parent.parent / "data"
    stats_file = data_dir / "stats.json"

    if not stats_file.exists():
        print(f"Error: {stats_file} not found")
        exit(1)

    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    monthly_reviews = stats.get('monthly_deck_reviews', [])
    generator = DeckCardsGenerator()
    light_file, dark_file = generator.generate_all(monthly_reviews)
    print(f"Generated: {light_file.name}, {dark_file.name}")
