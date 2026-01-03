"""
Heatmap Generator - Create GitHub-style contribution heatmap SVG
"""
import json
from datetime import datetime, timedelta
from pathlib import Path


class HeatmapGenerator:
    """Generate SVG heatmap from review data"""

    # Color scheme (GitHub-style green)
    COLORS = {
        0: '#ebedf0',      # No activity
        1: '#9be9a8',      # Light
        2: '#40c463',      # Medium
        3: '#30a14e',      # High
        4: '#216e39',      # Very high
    }

    # Alternative dark theme colors
    COLORS_DARK = {
        0: '#161b22',
        1: '#0e4429',
        2: '#006d32',
        3: '#26a641',
        4: '#39d353',
    }

    CELL_SIZE = 11
    CELL_MARGIN = 3
    WEEKS = 53
    DAYS = 7

    MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # GitHub style: only Mon, Wed, Fri labels
    DAY_LABELS = ['', 'Mon', '', 'Wed', '', 'Fri', '']

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_color_level(self, count, max_count):
        """Determine color level based on count"""
        if count == 0:
            return 0
        if max_count == 0:
            return 1

        ratio = count / max_count
        if ratio < 0.25:
            return 1
        elif ratio < 0.5:
            return 2
        elif ratio < 0.75:
            return 3
        else:
            return 4

    def generate_svg(self, heatmap_data, dark_mode=False):
        """Generate SVG heatmap"""
        colors = self.COLORS_DARK if dark_mode else self.COLORS

        # Calculate dimensions
        left_margin = 40
        top_margin = 20
        width = left_margin + self.WEEKS * (self.CELL_SIZE + self.CELL_MARGIN) + 10
        height = top_margin + self.DAYS * (self.CELL_SIZE + self.CELL_MARGIN) + 30

        # Get max count for color scaling
        counts = [d['count'] for d in heatmap_data]
        max_count = max(counts) if counts else 1

        # Build data lookup
        data_by_date = {d['date']: d['count'] for d in heatmap_data}

        # Calculate start date (52 weeks ago, aligned to Sunday/Monday)
        today = datetime.now().date()
        # Start from the beginning of current week, then go back 52 weeks
        days_since_sunday = (today.weekday() + 1) % 7
        end_of_week = today + timedelta(days=(6 - days_since_sunday))
        start_date = end_of_week - timedelta(weeks=52, days=6)

        bg_color = '#0d1117' if dark_mode else '#ffffff'
        # GitHub uses lighter text in dark mode
        text_color = '#e6edf3' if dark_mode else '#1f2328'

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{bg_color}"/>',
            f'<g transform="translate({left_margin}, {top_margin})">',
        ]

        # Add day labels (left-aligned, like GitHub)
        for i, label in enumerate(self.DAY_LABELS):
            if label:
                y = i * (self.CELL_SIZE + self.CELL_MARGIN) + self.CELL_SIZE - 2
                svg_parts.append(
                    f'<text x="-38" y="{y}" fill="{text_color}" '
                    f'font-size="11" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">'
                    f'{label}</text>'
                )

        # Track months for labels
        current_month = -1
        month_positions = []

        # Draw cells - iterate by week and place each day in correct row
        current_date = start_date
        week = 0
        while current_date <= today and week < self.WEEKS:
            # Convert Python weekday (Mon=0) to GitHub style (Sun=0)
            github_weekday = (current_date.weekday() + 1) % 7

            # Track month changes (only on first day of week)
            if github_weekday == 0 and current_date.month != current_month:
                current_month = current_date.month
                month_positions.append((week, self.MONTH_LABELS[current_month - 1]))

            date_str = current_date.strftime('%Y-%m-%d')
            count = data_by_date.get(date_str, 0)
            level = self.get_color_level(count, max_count)
            color = colors[level]

            x = week * (self.CELL_SIZE + self.CELL_MARGIN)
            y = github_weekday * (self.CELL_SIZE + self.CELL_MARGIN)

            tooltip = f"{count} reviews on {date_str}"
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{self.CELL_SIZE}" '
                f'height="{self.CELL_SIZE}" fill="{color}" rx="2" ry="2">'
                f'<title>{tooltip}</title></rect>'
            )

            # Move to next day, and next week column if we hit Sunday
            current_date += timedelta(days=1)
            if github_weekday == 6:  # Saturday -> next week
                week += 1

        # Add month labels (filter out overlapping ones)
        last_label_week = -4  # Minimum 4 weeks between labels
        for week, month_name in month_positions:
            if week - last_label_week >= 4:
                x = week * (self.CELL_SIZE + self.CELL_MARGIN)
                svg_parts.append(
                    f'<text x="{x}" y="-5" fill="{text_color}" '
                    f'font-size="13" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">'
                    f'{month_name}</text>'
                )
                last_label_week = week

        svg_parts.append('</g>')

        # Add legend
        legend_y = height - 15
        legend_x = width - 120
        svg_parts.append(
            f'<text x="{legend_x - 30}" y="{legend_y + 8}" fill="{text_color}" '
            f'font-size="11" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">Less</text>'
        )

        for i in range(5):
            svg_parts.append(
                f'<rect x="{legend_x + i * 14}" y="{legend_y}" '
                f'width="{self.CELL_SIZE}" height="{self.CELL_SIZE}" '
                f'fill="{colors[i]}" rx="2" ry="2"/>'
            )

        svg_parts.append(
            f'<text x="{legend_x + 75}" y="{legend_y + 8}" fill="{text_color}" '
            f'font-size="11" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">More</text>'
        )

        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def generate_from_file(self, heatmap_file="data/heatmap.json"):
        """Generate SVG from heatmap JSON file"""
        heatmap_path = Path(heatmap_file)

        if not heatmap_path.exists():
            raise FileNotFoundError(f"Heatmap data not found: {heatmap_file}")

        with open(heatmap_path, 'r') as f:
            heatmap_data = json.load(f)

        # Generate both light and dark versions
        light_svg = self.generate_svg(heatmap_data, dark_mode=False)
        dark_svg = self.generate_svg(heatmap_data, dark_mode=True)

        light_file = self.output_dir / "heatmap.svg"
        dark_file = self.output_dir / "heatmap-dark.svg"

        with open(light_file, 'w') as f:
            f.write(light_svg)

        with open(dark_file, 'w') as f:
            f.write(dark_svg)

        return light_file, dark_file

    def generate_from_data(self, heatmap_data):
        """Generate SVG directly from data"""
        light_svg = self.generate_svg(heatmap_data, dark_mode=False)
        dark_svg = self.generate_svg(heatmap_data, dark_mode=True)

        light_file = self.output_dir / "heatmap.svg"
        dark_file = self.output_dir / "heatmap-dark.svg"

        with open(light_file, 'w') as f:
            f.write(light_svg)

        with open(dark_file, 'w') as f:
            f.write(dark_svg)

        return light_file, dark_file


if __name__ == "__main__":
    generator = HeatmapGenerator()
    try:
        light, dark = generator.generate_from_file()
        print(f"Generated: {light}, {dark}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run data_exporter.py first to generate heatmap data")
