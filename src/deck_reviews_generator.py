"""
Deck Reviews Generator - Generate vertical bar chart for weekly deck review ranking
"""
from pathlib import Path


class DeckReviewsGenerator:
    """Generate SVG bar chart for deck review ranking"""

    BAR_WIDTH = 36
    BAR_GAP = 8
    MAX_BAR_HEIGHT = 80
    MIN_BAR_HEIGHT = 3

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_svg(self, deck_reviews, dark_mode=False, max_decks=7):
        """Generate SVG vertical bar chart"""
        sorted_decks = deck_reviews[:max_decks]

        if not sorted_decks:
            return self._generate_empty_svg(dark_mode)

        # Theme colors
        if dark_mode:
            bg_color = '#0d1117'
            bar_color = '#26a641'
            bar_empty_color = '#161b22'
            text_color = '#e6edf3'
            label_color = '#8b949e'
        else:
            bg_color = '#ffffff'
            bar_color = '#40c463'
            bar_empty_color = '#ebedf0'
            text_color = '#1f2328'
            label_color = '#656d76'

        # Calculate dimensions
        num_bars = len(sorted_decks)
        left_margin = 25
        top_margin = 20
        bottom_margin = 60  # More space for rotated labels
        chart_width = num_bars * (self.BAR_WIDTH + self.BAR_GAP) - self.BAR_GAP
        width = left_margin + chart_width + 50  # Extra width for rotated text
        height = top_margin + self.MAX_BAR_HEIGHT + bottom_margin

        # Get max count for scaling
        max_count = max(d['reviews'] for d in sorted_decks) if sorted_decks else 1
        if max_count == 0:
            max_count = 1

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{bg_color}"/>',
            f'<g transform="translate({left_margin}, {top_margin})">',
        ]

        for i, deck in enumerate(sorted_decks):
            x = i * (self.BAR_WIDTH + self.BAR_GAP)
            count = deck['reviews']

            # Calculate bar height
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
                    f'<text x="{x + self.BAR_WIDTH / 2}" y="{label_y}" '
                    f'fill="{text_color}" font-size="10" text-anchor="middle" '
                    f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" '
                    f'font-weight="600">{count}</text>'
                )
            else:
                svg_parts.append(
                    f'<text x="{x + self.BAR_WIDTH / 2}" y="{self.MAX_BAR_HEIGHT - 10}" '
                    f'fill="{label_color}" font-size="10" text-anchor="middle" '
                    f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">'
                    f'0</text>'
                )

            # Bar
            rx = 2 if bar_height > 4 else 1
            svg_parts.append(
                f'<rect x="{x}" y="{bar_y}" width="{self.BAR_WIDTH}" '
                f'height="{bar_height}" fill="{color}" rx="{rx}" ry="{rx}">'
                f'<title>{count} reviews - {deck["name"]}</title></rect>'
            )

            # Deck name label (rotated 45 degrees)
            name = deck['name']
            if '::' in name:
                name = name.split('::')[-1]
            if len(name) > 10:
                name = name[:9] + '..'

            label_x = x + self.BAR_WIDTH / 2
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

        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="40">
<rect width="300" height="40" fill="{bg}"/>
<text x="150" y="24" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif"
font-size="13" fill="{text}">No data</text>
</svg>'''

    def generate_all(self, deck_reviews, max_decks=7):
        """Generate both light and dark versions"""
        light_svg = self.generate_svg(deck_reviews, dark_mode=False, max_decks=max_decks)
        dark_svg = self.generate_svg(deck_reviews, dark_mode=True, max_decks=max_decks)

        light_file = self.output_dir / "reviews.svg"
        dark_file = self.output_dir / "reviews-dark.svg"

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

    deck_reviews = stats.get('deck_reviews', [])
    generator = DeckReviewsGenerator()
    light_file, dark_file = generator.generate_all(deck_reviews)
    print(f"Generated: {light_file.name}, {dark_file.name}")
