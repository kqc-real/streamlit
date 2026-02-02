#!/usr/bin/env python3
"""
Generate SVG radar charts for different learner archetypes.
"""

import sys
import os
from typing import List
from math import sin, cos, pi
from urllib.parse import quote
import html

def render_radar_svg(labels: List[str], values: List[float], size: int = 360) -> str:
    """Render a simple radar chart as SVG and return the SVG string.

    Adapted from pdf_export.py _render_radar_svg.
    """
    n = max(1, len(labels))
    cx = cy = size // 2
    outer_r = size * 0.36
    levels = [0.25, 0.5, 0.75, 1.0]

    def pt(angle, radius):
        return cx + radius * cos(angle), cy + radius * sin(angle)

    angle_step = 2 * pi / n if n > 0 else 2 * pi

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    parts.append(f'<rect width="100%" height="100%" fill="#f3f4f6"/>')

    ring_stroke = "#d1d5db"
    grid_stroke = "#d1d5db"
    for lvl in levels:
        r = outer_r * lvl
        parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" stroke="{ring_stroke}" stroke-width="1"/>')
        pts = []
        for i in range(n):
            a = -pi/2 + i * angle_step
            x, y = pt(a, r)
            pts.append(f'{x:.2f},{y:.2f}')
        parts.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{grid_stroke}" stroke-width="1"/>')

    axes_stroke = "#9ca3af"
    for i in range(n):
        a = -pi/2 + i * angle_step
        x, y = pt(a, outer_r)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="{axes_stroke}" stroke-width="1"/>')

    poly_pts = []
    for i, v in enumerate(values):
        a = -pi/2 + i * angle_step
        r = outer_r * max(0.0, min(1.0, v / 100.0))
        x, y = pt(a, r)
        poly_pts.append(f'{x:.2f},{y:.2f}')
    if poly_pts:
        parts.append(f'<polygon points="{" ".join(poly_pts)}" fill="rgba(21,128,61,0.20)" stroke="#15803d" stroke-width="2"/>')

    ring_values = [int(l * 100) for l in levels]
    for lvl, val in zip(levels, ring_values):
        r = outer_r * lvl
        vx = cx
        vy = cy - r - 4
        parts.append(f'<text x="{vx:.2f}" y="{vy:.2f}" font-size="10" text-anchor="middle" fill="#0f172a">{val}</text>')

    for i, lab in enumerate(labels):
        a = -pi/2 + i * angle_step
        x, y = pt(a, outer_r * 1.22)
        anchor = 'middle'
        parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="11" text-anchor="{anchor}" fill="#0f172a">{html.escape(str(lab))}</text>')

    parts.append('</svg>')
    return "".join(parts)

def main():
    labels = ["Reproduction", "Application", "Analysis"]

    archetypes = {
        "crammer": [90, 30, 20],
        "theorist": [40, 60, 90],
        "practitioner": [50, 90, 30]
    }

    for name, values in archetypes.items():
        svg = render_radar_svg(labels, values, size=400)
        filename = f"{name}_radar.svg"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()