"""
Deck SVG Generator - Generate horizontal progress bars for deck statistics
"""
from pathlib import Path


class DeckSvgGenerator:
    """Generate SVG visualization for deck progress"""

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_svg(self, decks_data, dark_mode=False, max_decks=None):
        """Generate SVG with deck progress bars (gradient style)

        Args:
            decks_data: Dict of deck data
            dark_mode: Use dark theme
            max_decks: Maximum number of decks to show (None = show all with cards)
        """
        # Filter decks that have cards (total > 0)
        decks_with_cards = [d for d in decks_data.values() if d.get('total', 0) > 0]
        sorted_decks = sorted(
            decks_with_cards,
            key=lambda d: d.get('total', 0),
            reverse=True
        )
        if max_decks:
            sorted_decks = sorted_decks[:max_decks]

        if not sorted_decks:
            return ""

        max_total = sorted_decks[0].get('total', 1) if sorted_decks else 1

        # Colors
        if dark_mode:
            bg = "#0d1117"
            text = "#e6edf3"
            subtext = "#8b949e"
            bar_bg = "#21262d"
            grad_start = "#238636"
            grad_end = "#2ea043"
        else:
            bg = "#ffffff"
            text = "#24292f"
            subtext = "#656d76"
            bar_bg = "#eaeef2"
            grad_start = "#2da44e"
            grad_end = "#3fb950"

        # Layout (792px width matching heatmap)
        row_height = 38
        bar_height = 6
        bar_width = 792
        width = bar_width
        height = len(sorted_decks) * row_height

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            '<defs>',
            f'  <linearGradient id="barGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
            f'    <stop offset="0%" style="stop-color:{grad_start}"/>',
            f'    <stop offset="100%" style="stop-color:{grad_end}"/>',
            '  </linearGradient>',
            '</defs>',
            f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        ]

        for i, deck in enumerate(sorted_decks):
            y = i * row_height + 14

            name = deck['name']
            if len(name) > 36:
                name = name[:33] + "..."

            total = deck.get('total', 0)
            mature = deck.get('mature', 0)
            pct = int(mature / total * 100) if total > 0 else 0

            # Deck name
            svg_parts.append(
                f'<text x="0" y="{y}" font-family="system-ui, -apple-system, sans-serif" '
                f'font-size="13" fill="{text}">{name}</text>'
            )

            # Mature/Total (right-aligned)
            svg_parts.append(
                f'<text x="{bar_width}" y="{y}" text-anchor="end" '
                f'font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="{subtext}">{mature:,}/{total:,}</text>'
            )

            # Progress bar background
            bar_y = y + 10
            svg_parts.append(
                f'<rect x="0" y="{bar_y}" width="{bar_width}" height="{bar_height}" '
                f'fill="{bar_bg}" rx="3"/>'
            )

            # Progress bar (mastery progress: mature/total)
            if total > 0:
                bar_w = (mature / total) * bar_width
                if bar_w > 0:
                    svg_parts.append(
                        f'<rect x="0" y="{bar_y}" width="{bar_w}" height="{bar_height}" '
                        f'fill="url(#barGrad)" rx="3"/>'
                    )

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def generate_all(self, decks_data, max_decks=None):
        """Generate both light and dark versions"""
        light_svg = self.generate_svg(decks_data, dark_mode=False, max_decks=max_decks)
        dark_svg = self.generate_svg(decks_data, dark_mode=True, max_decks=max_decks)

        light_file = self.output_dir / "decks.svg"
        dark_file = self.output_dir / "decks-dark.svg"

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
        print("Run data_exporter.py first to generate stats data")
        exit(1)

    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    generator = DeckSvgGenerator()
    light_file, dark_file = generator.generate_all(stats['decks'])
    print(f"Generated: {light_file.name}, {dark_file.name}")
