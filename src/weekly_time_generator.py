"""
Weekly Time Line Chart Generator - Create weekly review time line chart SVG
"""
import json
from datetime import datetime, timedelta
from pathlib import Path


class WeeklyTimeGenerator:
    """Generate SVG line chart for weekly review time (minutes)"""

    CHART_WIDTH = 330  # Wider to fill 390px width
    CHART_HEIGHT = 80
    POINT_RADIUS = 4

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_weekly_data(self, daily_time):
        """Get review time for the last 7 days (rolling window)"""
        today = datetime.now().date()

        weekly_data = []
        for i in range(6, -1, -1):  # 6 days ago to today
            day = today - timedelta(days=i)
            date_str = day.strftime('%Y-%m-%d')
            minutes = daily_time.get(date_str, 0)
            label = day.strftime('%m/%d')
            weekly_data.append({
                'date': date_str,
                'day': label,
                'minutes': minutes
            })

        return weekly_data

    def generate_svg(self, weekly_data, dark_mode=False):
        """Generate SVG line chart for review time"""
        if dark_mode:
            bg_color = '#0d1117'
            line_color = '#8957e5'
            point_color = '#8957e5'
            point_fill = '#0d1117'
            grid_color = '#21262d'
            text_color = '#e6edf3'
            label_color = '#8b949e'
        else:
            bg_color = '#ffffff'
            line_color = '#8250df'
            point_color = '#8250df'
            point_fill = '#ffffff'
            grid_color = '#ebedf0'
            text_color = '#1f2328'
            label_color = '#656d76'

        # Dimensions (390px width for side-by-side layout)
        left_margin = 35
        right_margin = 25
        top_margin = 25
        bottom_margin = 30
        width = 390  # Fixed width for consistent layout
        height = top_margin + self.CHART_HEIGHT + bottom_margin

        # Get max time for scaling
        times = [d['minutes'] for d in weekly_data]
        max_time = max(times) if times and max(times) > 0 else 1

        # Calculate point positions
        x_step = self.CHART_WIDTH / 6  # 7 points, 6 gaps
        points = []
        for i, data in enumerate(weekly_data):
            x = left_margin + i * x_step
            if max_time > 0:
                y = top_margin + self.CHART_HEIGHT - (data['minutes'] / max_time * self.CHART_HEIGHT)
            else:
                y = top_margin + self.CHART_HEIGHT
            points.append((x, y, data))

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{bg_color}"/>',
        ]

        # Draw horizontal grid lines
        for i in range(5):
            y = top_margin + (i * self.CHART_HEIGHT / 4)
            svg_parts.append(
                f'<line x1="{left_margin}" y1="{y}" x2="{left_margin + self.CHART_WIDTH}" y2="{y}" '
                f'stroke="{grid_color}" stroke-width="1"/>'
            )

        # Draw baseline
        baseline_y = top_margin + self.CHART_HEIGHT
        svg_parts.append(
            f'<line x1="{left_margin}" y1="{baseline_y}" x2="{left_margin + self.CHART_WIDTH}" y2="{baseline_y}" '
            f'stroke="{grid_color}" stroke-width="1"/>'
        )

        # Draw line path
        if len(points) > 1:
            path_d = f'M {points[0][0]} {points[0][1]}'
            for x, y, _ in points[1:]:
                path_d += f' L {x} {y}'
            svg_parts.append(
                f'<path d="{path_d}" fill="none" stroke="{line_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            )

        # Draw points and labels
        for x, y, data in points:
            minutes = data['minutes']

            # Point
            svg_parts.append(
                f'<circle cx="{x}" cy="{y}" r="{self.POINT_RADIUS}" fill="{point_fill}" stroke="{point_color}" stroke-width="2">'
                f'<title>{minutes} min on {data["date"]}</title></circle>'
            )

            # Value label above point (only if > 0)
            if minutes > 0:
                svg_parts.append(
                    f'<text x="{x}" y="{y - 10}" fill="{text_color}" font-size="9" text-anchor="middle" '
                    f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" '
                    f'font-weight="600">{minutes}m</text>'
                )

            # Date label below
            svg_parts.append(
                f'<text x="{x}" y="{baseline_y + 15}" fill="{label_color}" font-size="9" text-anchor="middle" '
                f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">'
                f'{data["day"]}</text>'
            )

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
