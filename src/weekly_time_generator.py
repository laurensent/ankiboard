"""
Weekly Time Chart Generator - Create weekly review time bar chart SVG
"""
import json
from datetime import datetime, timedelta
from pathlib import Path


class WeeklyTimeGenerator:
    """Generate SVG bar chart for weekly review time (minutes)"""

    BAR_WIDTH = 36
    BAR_GAP = 8
    MAX_BAR_HEIGHT = 80
    MIN_BAR_HEIGHT = 3

    DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_weekly_data(self, daily_time):
        """Get review time for the current week (Mon-Sun)"""
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())

        weekly_data = []
        for i in range(7):
            day = monday + timedelta(days=i)
            date_str = day.strftime('%Y-%m-%d')
            minutes = daily_time.get(date_str, 0)
            weekly_data.append({
                'date': date_str,
                'day': self.DAY_LABELS[i],
                'minutes': minutes
            })

        return weekly_data

    def generate_svg(self, weekly_data, dark_mode=False):
        """Generate SVG bar chart for review time"""
        if dark_mode:
            bg_color = '#0d1117'
            bar_color = '#8957e5'  # Purple for time (different from green reviews)
            bar_empty_color = '#161b22'
            text_color = '#e6edf3'
            label_color = '#8b949e'
        else:
            bg_color = '#ffffff'
            bar_color = '#8250df'  # Purple
            bar_empty_color = '#ebedf0'
            text_color = '#1f2328'
            label_color = '#656d76'

        # Calculate dimensions (match weekly.svg for alignment)
        left_margin = 25
        top_margin = 20
        bottom_margin = 60
        chart_width = 7 * (self.BAR_WIDTH + self.BAR_GAP) - self.BAR_GAP
        width = left_margin + chart_width + 25
        height = top_margin + self.MAX_BAR_HEIGHT + bottom_margin

        # Get max time for scaling
        times = [d['minutes'] for d in weekly_data]
        max_time = max(times) if times and max(times) > 0 else 1

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{bg_color}"/>',
            f'<g transform="translate({left_margin}, {top_margin})">',
        ]

        for i, data in enumerate(weekly_data):
            x = i * (self.BAR_WIDTH + self.BAR_GAP)
            minutes = data['minutes']

            if minutes == 0:
                bar_height = self.MIN_BAR_HEIGHT
                color = bar_empty_color
            else:
                bar_height = max(
                    self.MIN_BAR_HEIGHT,
                    int((minutes / max_time) * self.MAX_BAR_HEIGHT)
                )
                color = bar_color

            bar_y = self.MAX_BAR_HEIGHT - bar_height

            # Value label above bar (show minutes with 'm' suffix)
            label_y = bar_y - 8
            if minutes > 0:
                svg_parts.append(
                    f'<text x="{x + self.BAR_WIDTH / 2}" y="{label_y}" '
                    f'fill="{text_color}" font-size="10" text-anchor="middle" '
                    f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" '
                    f'font-weight="600">{minutes}m</text>'
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
                f'<title>{minutes} min on {data["date"]}</title></rect>'
            )

            # Day label below bar
            svg_parts.append(
                f'<text x="{x + self.BAR_WIDTH / 2}" y="{self.MAX_BAR_HEIGHT + 18}" '
                f'fill="{label_color}" font-size="11" text-anchor="middle" '
                f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">'
                f'{data["day"]}</text>'
            )

        svg_parts.append('</g>')
        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def generate_from_data(self, daily_time):
        """Generate SVG files from daily time data"""
        weekly_data = self.get_weekly_data(daily_time)

        light_svg = self.generate_svg(weekly_data, dark_mode=False)
        dark_svg = self.generate_svg(weekly_data, dark_mode=True)

        light_file = self.output_dir / "time.svg"
        dark_file = self.output_dir / "time-dark.svg"

        with open(light_file, 'w') as f:
            f.write(light_svg)

        with open(dark_file, 'w') as f:
            f.write(dark_svg)

        return light_file, dark_file

    def generate_from_file(self, stats_file="data/stats.json"):
        """Generate SVG from stats JSON file"""
        stats_path = Path(stats_file)

        if not stats_path.exists():
            raise FileNotFoundError(f"Stats data not found: {stats_file}")

        with open(stats_path, 'r') as f:
            stats = json.load(f)

        daily_time = stats.get('daily_time', {})
        return self.generate_from_data(daily_time)


if __name__ == "__main__":
    generator = WeeklyTimeGenerator()
    try:
        light, dark = generator.generate_from_file()
        print(f"Generated: {light}, {dark}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run data_exporter.py first to generate stats data")
