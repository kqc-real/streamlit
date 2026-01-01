#!/usr/bin/env python3
"""
Generate SVG bar chart for thematic competence.
"""

import random
from typing import List
import html

def render_topic_stacked_bar_svg(themes: List[str], pct_correct: List[float], pct_wrong: List[float], pct_unanswered: List[float] | None = None, width: int = 1000, height: int = 450) -> str:
    """Render a simple stacked vertical bar chart as SVG and return the SVG string."""
    n = len(themes)
    if n == 0:
        return ""

    offset_x = 100
    offset_y = 10

    margin_left = 160 - offset_x
    margin_right = 20
    margin_top = 50 - offset_y
    margin_bottom = 180
    gutter = 12
    bar_area_width = width - margin_left - margin_right
    total_gutters = gutter * (n - 1)
    bar_w = max(10, int((bar_area_width - total_gutters) / n))
    chart_top = margin_top
    chart_bottom = height - margin_bottom
    chart_height = max(120, chart_bottom - chart_top - 18)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="980" height="440" viewBox="0 0 980 440" preserveAspectRatio="xMidYMid meet" style="overflow:visible">']
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>')

    # Legend at top
    legend_x = (width - 200) - offset_x  # Top right
    legend_y = 20 - offset_y  # Top of the SVG
    legend_spacing = 25

    # Correct
    parts.append(f'<rect x="{legend_x}" y="{legend_y}" width="15" height="15" fill="#15803d" rx="2" ry="2"/>')
    parts.append(f'<text x="{legend_x + 20}" y="{legend_y + 12}" font-size="12" fill="#0f172a">Correct</text>')

    # Wrong
    parts.append(f'<rect x="{legend_x + 80}" y="{legend_y}" width="15" height="15" fill="#b91c1c" rx="2" ry="2"/>')
    parts.append(f'<text x="{legend_x + 100}" y="{legend_y + 12}" font-size="12" fill="#0f172a">Wrong</text>')

    # Unanswered
    parts.append(f'<rect x="{legend_x + 160}" y="{legend_y}" width="15" height="15" fill="#9ca3af" rx="2" ry="2"/>')
    parts.append(f'<text x="{legend_x + 180}" y="{legend_y + 12}" font-size="12" fill="#0f172a">Unanswered</text>')

    # Y-axis label
    y_label_x = margin_left - 30
    y_label_y = chart_top + chart_height / 2
    parts.append(f'<text x="{y_label_x}" y="{y_label_y}" font-size="12" text-anchor="middle" fill="#0f172a" transform="rotate(-90 {y_label_x} {y_label_y})">Percentage (%)</text>')

    # X-axis label
    x_label_x = margin_left + bar_area_width / 2
    x_label_y = (height - 20) - offset_y
    parts.append(f'<text x="{x_label_x:.1f}" y="{x_label_y}" font-size="12" text-anchor="middle" fill="#0f172a">Topics</text>')

    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = chart_top + (1.0 - frac) * chart_height
        parts.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right - offset_x}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        label_x = max(6, margin_left - 8)
        parts.append(f'<text x="{label_x}" y="{y + 5:.1f}" font-size="10" text-anchor="end" fill="#374151">{int(frac*100)}</text>')

    x = margin_left
    for i, theme in enumerate(themes):
        c = max(0.0, min(100.0, float(pct_correct[i] if i < len(pct_correct) else 0.0)))
        w = max(0.0, min(100.0, float(pct_wrong[i] if i < len(pct_wrong) else 0.0)))
        u = 0.0
        if pct_unanswered:
            u = max(0.0, min(100.0, float(pct_unanswered[i] if i < len(pct_unanswered) else 0.0)))
        h_c = (c / 100.0) * chart_height
        h_w = (w / 100.0) * chart_height
        h_u = (u / 100.0) * chart_height
        y_bottom = chart_top + chart_height
        y_c = y_bottom - h_c
        parts.append(f'<rect x="{x}" y="{y_c:.1f}" width="{bar_w}" height="{h_c:.1f}" fill="#15803d" rx="4" ry="4" stroke="#ffffff" stroke-width="0.6"/>')
        y_w = y_c - h_w
        parts.append(f'<rect x="{x}" y="{y_w:.1f}" width="{bar_w}" height="{h_w:.1f}" fill="#b91c1c" rx="4" ry="4" stroke="#ffffff" stroke-width="0.6"/>')
        y_u = y_w - h_u
        parts.append(f'<rect x="{x}" y="{y_u:.1f}" width="{bar_w}" height="{h_u:.1f}" fill="#9ca3af" rx="4" ry="4" stroke="#ffffff" stroke-width="0.6"/>')

        pct_font_size = 9
        if h_c > 10:
            parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y_c + 10:.1f}" font-size="{pct_font_size}" text-anchor="middle" fill="#ffffff">{int(c)}%</text>')
        if h_w > 10:
            parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y_w + 10:.1f}" font-size="{pct_font_size}" text-anchor="middle" fill="#ffffff">{int(w)}%</text>')
        if h_u > 10:
            parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y_u + 10:.1f}" font-size="{pct_font_size}" text-anchor="middle" fill="#ffffff">{int(u)}%</text>')

        label_x = x + bar_w / 2
        label_y = chart_top + chart_height + 40
        safe_label = html.escape(str(theme))
        parts.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" font-size="11" text-anchor="end" fill="#0f172a" '
            f'transform="rotate(-45 {label_x:.1f} {label_y:.1f})">{safe_label}</text>'
        )

        x += bar_w + gutter

    parts.append('</svg>')
    return ''.join(parts)

def main():
    # Themes from questions_klassisches_Machine_learning.json (translated to US English)
    themes = [
        "ML Fundamentals",
        "Supervised Learning",
        "Regression",
        "Unsupervised Learning",
        "Model Evaluation",
        "Classification",
        "Model Theory"
    ]
    # Generate percentages based on difficulty with some randomness
    random.seed(42)  # For reproducibility
    basis_correct_pct = [80, 70, 65, 60, 55, 50, 40]  # Base percentages decreasing with difficulty
    pct_correct = []
    pct_wrong = []
    pct_unanswered = []
    theme_labels = []
    for i, theme in enumerate(themes):
        total = random.randint(8, 12)  # Random total per theme
        base_correct = int(basis_correct_pct[i] * total / 100)
        correct = random.randint(max(1, base_correct - 1), min(total, base_correct + 1))  # Some randomness around base
        wrong = random.randint(0, total - correct)
        unanswered = total - correct - wrong
        pct_correct.append((correct / total) * 100)
        pct_wrong.append((wrong / total) * 100)
        pct_unanswered.append((unanswered / total) * 100)
        theme_labels.append(f"{theme} ({correct}/{total})")

    svg = render_topic_stacked_bar_svg(theme_labels, pct_correct, pct_wrong, pct_unanswered, width=900, height=450)
    with open("thematic_competence_bar.svg", 'w', encoding='utf-8') as f:
        f.write(svg)
    print("Generated thematic_competence_bar.svg")

if __name__ == "__main__":
    main()