"""
Stats SVG Generator - Generate visual badges and charts for statistics
"""
from pathlib import Path
import math


class StatsSvgGenerator:
    """Generate SVG visualizations for Anki statistics"""

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_badge(self, label, value, color="#4c1"):
        """Generate a shields.io style badge"""
        label_width = len(label) * 7 + 10
        value_width = len(str(value)) * 7 + 10
        total_width = label_width + value_width

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
  <linearGradient id="smooth" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="round">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#round)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#smooth)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_width/2}" y="14" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width/2}" y="13" fill="#fff">{label}</text>
    <text x="{label_width + value_width/2}" y="14" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{label_width + value_width/2}" y="13" fill="#fff">{value}</text>
  </g>
</svg>'''
        return svg

    def generate_progress_ring(self, percentage, size=120, stroke_width=12,
                                color="#4c1", bg_color="#e0e0e0", label=""):
        """Generate a circular progress ring"""
        center = size / 2
        radius = (size - stroke_width) / 2
        circumference = 2 * math.pi * radius
        dash_offset = circumference * (1 - percentage / 100)

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{bg_color}" stroke-width="{stroke_width}"/>
  <circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke_width}"
    stroke-linecap="round" stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}"
    transform="rotate(-90 {center} {center})"/>
  <text x="{center}" y="{center}" text-anchor="middle" dominant-baseline="middle"
    font-family="system-ui, -apple-system, sans-serif" font-size="24" font-weight="bold" fill="#333">{percentage}%</text>
  <text x="{center}" y="{center + 18}" text-anchor="middle" dominant-baseline="middle"
    font-family="system-ui, -apple-system, sans-serif" font-size="10" fill="#666">{label}</text>
</svg>'''
        return svg

    def generate_stats_card(self, stats, dark_mode=False):
        """Generate a stats overview card"""
        cards = stats['cards']
        total = cards['total']
        mature = cards['mature']
        learning = cards['learning']
        new = cards['new']
        suspended = cards['suspended']
        streak = stats['streak']
        weekly_reviews = stats['weekly_reviews']

        # Colors
        if dark_mode:
            bg = "#0d1117"
            border = "#30363d"
            text = "#c9d1d9"
            subtext = "#8b949e"
        else:
            bg = "#ffffff"
            border = "#e1e4e8"
            text = "#24292f"
            subtext = "#57606a"

        # Card colors
        mature_color = "#40c463"
        learning_color = "#ffc107"
        new_color = "#58a6ff"
        suspended_color = "#6e7681"

        # Calculate percentages for pie chart
        active = total - suspended
        mature_pct = (mature / active * 100) if active > 0 else 0
        learning_pct = (learning / active * 100) if active > 0 else 0
        new_pct = (new / active * 100) if active > 0 else 0

        width = 400
        height = 200

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="{bg}" rx="6"/>
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" fill="none" stroke="{border}" rx="6"/>

  <!-- Title -->
  <text x="20" y="30" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="600" fill="{text}">Card Statistics</text>

  <!-- Pie Chart -->
  {self._generate_pie_chart(150, 110, 50, [
      (mature_pct, mature_color),
      (learning_pct, learning_color),
      (new_pct, new_color)
  ])}

  <!-- Legend -->
  <g transform="translate(220, 55)">
    <rect width="12" height="12" fill="{mature_color}" rx="2"/>
    <text x="18" y="10" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="{text}">Mature: {mature:,}</text>

    <rect y="20" width="12" height="12" fill="{learning_color}" rx="2"/>
    <text x="18" y="30" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="{text}">Learning: {learning:,}</text>

    <rect y="40" width="12" height="12" fill="{new_color}" rx="2"/>
    <text x="18" y="50" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="{text}">New: {new:,}</text>

    <rect y="60" width="12" height="12" fill="{suspended_color}" rx="2"/>
    <text x="18" y="70" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="{subtext}">Suspended: {suspended:,}</text>
  </g>

  <!-- Stats Row -->
  <g transform="translate(20, 175)">
    <text font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="{subtext}">
      Total: {total:,} | Streak: {streak} days | Weekly: {weekly_reviews:,} reviews
    </text>
  </g>
</svg>'''
        return svg

    def _generate_pie_chart(self, cx, cy, r, segments):
        """Generate pie chart segments"""
        parts = []
        start_angle = -90  # Start from top

        for pct, color in segments:
            if pct <= 0:
                continue

            angle = pct * 3.6  # 360 / 100
            end_angle = start_angle + angle

            # Convert to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)

            # Calculate arc points
            x1 = cx + r * math.cos(start_rad)
            y1 = cy + r * math.sin(start_rad)
            x2 = cx + r * math.cos(end_rad)
            y2 = cy + r * math.sin(end_rad)

            # Large arc flag
            large_arc = 1 if angle > 180 else 0

            path = f'<path d="M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z" fill="{color}"/>'
            parts.append(path)

            start_angle = end_angle

        return '\n  '.join(parts)

    def generate_progress_bar_svg(self, current, total, width=300, height=30,
                                   color="#40c463", bg_color="#e0e0e0", label=""):
        """Generate a horizontal progress bar"""
        percentage = (current / total * 100) if total > 0 else 0
        fill_width = (width - 4) * (percentage / 100)

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height + 20}" viewBox="0 0 {width} {height + 20}">
  <text x="0" y="12" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="#57606a">{label}</text>
  <rect x="0" y="18" width="{width}" height="{height}" fill="{bg_color}" rx="4"/>
  <rect x="2" y="20" width="{fill_width}" height="{height - 4}" fill="{color}" rx="3"/>
  <text x="{width/2}" y="{18 + height/2 + 5}" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="500" fill="#fff">{current:,} / {total:,} ({percentage:.1f}%)</text>
</svg>'''
        return svg

    def generate_all(self, stats):
        """Generate all stats SVGs"""
        cards = stats['cards']
        total_active = cards['total'] - cards['suspended']
        percentage = int(cards['mature'] / total_active * 100) if total_active > 0 else 0

        # Stats card (light and dark)
        stats_card_light = self.generate_stats_card(stats, dark_mode=False)
        stats_card_dark = self.generate_stats_card(stats, dark_mode=True)

        with open(self.output_dir / "stats-card.svg", 'w') as f:
            f.write(stats_card_light)

        with open(self.output_dir / "stats-card-dark.svg", 'w') as f:
            f.write(stats_card_dark)

        # Progress ring
        progress_ring = self.generate_progress_ring(percentage, label="Mastery")
        with open(self.output_dir / "progress-ring.svg", 'w') as f:
            f.write(progress_ring)

        # Progress bar
        progress_bar = self.generate_progress_bar_svg(
            cards['mature'], total_active,
            label=f"Mastery Progress"
        )
        with open(self.output_dir / "progress-bar.svg", 'w') as f:
            f.write(progress_bar)

        return {
            'stats_card': self.output_dir / "stats-card.svg",
            'stats_card_dark': self.output_dir / "stats-card-dark.svg",
            'progress_ring': self.output_dir / "progress-ring.svg",
            'progress_bar': self.output_dir / "progress-bar.svg"
        }


if __name__ == "__main__":
    import json

    with open("data/stats.json", 'r') as f:
        stats = json.load(f)

    generator = StatsSvgGenerator()
    files = generator.generate_all(stats)
    print("Generated:", list(files.keys()))
