"""
Modul zur Generierung von PDF-Berichten für die Testergebnisse.
"""
import io
import re
import base64
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import io

import streamlit as st
import requests
from weasyprint import HTML
import urllib.parse as _urlparse
import html as _html
from markdown_it import MarkdownIt

from logic import get_answer_for_question, calculate_score
from config import AppConfig
from pacing_helper import compute_total_cooldown_seconds
from helpers.text import format_decimal_locale, smart_quotes_de, normalize_detailed_explanation
from i18n.context import t as translate_ui
import os
import logging
import traceback
import threading
import hashlib
from pathlib import Path

# Global semaphore to limit concurrent formula renderers across jobs.
# Configure via environment variable FORMULA_RENDER_PARALLEL (default 6).
_MAX_FORMULA_PARALLEL = int(os.getenv('FORMULA_RENDER_PARALLEL', '6'))
_formula_semaphore = threading.Semaphore(_MAX_FORMULA_PARALLEL)

# Global lock to prevent race conditions during cache eviction.
_eviction_lock = threading.Lock()

# QR-Code Generation
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# Cache für bereits gerenderte Formeln (spart API-Calls bei duplizierten Formeln)
_formula_cache = {}

# Disk-backed formula image cache (stores PNG files). Directory configurable
# via FORMULA_CACHE_DIR env var. On Streamlit Community Cloud the filesystem
# is writable but ephemeral across deploys — this cache improves runtime
# performance but is not persistent across restarts.
FORMULA_CACHE_DIR = Path(os.getenv('FORMULA_CACHE_DIR', os.path.join(os.getcwd(), 'var', 'formula_cache')))
try:
    FORMULA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # If we cannot create the cache dir (read-only FS), we silently
    # continue and only use the in-memory cache.
    FORMULA_CACHE_DIR = None

# Configure module logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Basic config will be inherited by the app; keep formatting minimal
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')

# Suppress verbose fontTools debug logs (used by WeasyPrint)
logging.getLogger("fontTools").setLevel(logging.WARNING)


# Cache eviction configuration (can be overridden via env vars)
# Reduced defaults are safer for cloud deployments (ephemeral disks)
FORMULA_CACHE_MAX_FILES = int(os.getenv('FORMULA_CACHE_MAX_FILES', '100'))
FORMULA_CACHE_MAX_MB = int(os.getenv('FORMULA_CACHE_MAX_MB', '50'))
FORMULA_CACHE_TTL_DAYS = int(os.getenv('FORMULA_CACHE_TTL_DAYS', '7'))

DEFAULT_STAGE_LABEL = "Unbekannt"

_STAGE_ALIAS_MAP: Dict[str, str] = {
    "reproduktion": "Reproduktion",
    "reproduction": "Reproduktion",
    "wissen": "Reproduktion",
    "memorieren": "Reproduktion",
    "knowledge": "Reproduktion",
    "verstehen": "Verständnis",
    "verständnis": "Verständnis",
    "understanding": "Verständnis",
    "anwenden": "Anwendung",
    "anwendung": "Anwendung",
    "application": "Anwendung",
    "applying": "Anwendung",
    "analyse": "Analyse",
    "analysis": "Analyse",
    "analysieren": "Analyse",
    "analyzing": "Analyse",
}

BLOOM_STAGE_ORDER = ["Reproduktion", "Anwendung", "Analyse"]


def _normalize_stage_label(value: Any) -> str:
    if not value:
        return DEFAULT_STAGE_LABEL
    key = str(value).strip()
    if not key:
        return DEFAULT_STAGE_LABEL
    alias = _STAGE_ALIAS_MAP.get(key.lower())
    return alias if alias else key


def _get_bloom_stage_rank(stage_label: str) -> int:
    """Numerischer Rang für eine Bloom-Stufe (nicht erkannte Labels werden hinten einsortiert)."""
    try:
        return BLOOM_STAGE_ORDER.index(stage_label)
    except ValueError:
        return len(BLOOM_STAGE_ORDER)


def _markdown_to_html(text: str) -> str:
    """Convert simple markdown-style text to HTML for PDF rendering.
    
    Handles:
    - Headers (lines ending with :)
    - Bullet lists (• or - at start of line)
    - Paragraphs (double newlines)
    - Arrows (→) preserved
    """
    import re
    
    lines = text.strip().split('\n')
    html_parts = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines but close list if open
        if not stripped:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            continue
        
        # Check if line is a bullet point
        is_bullet = stripped.startswith('•') or stripped.startswith('- ') or stripped.startswith('* ')
        
        if is_bullet:
            # Start list if not in one
            if not in_list:
                html_parts.append('<ul style="margin:6px 0 6px 0; padding-left:18px; list-style-type:disc;">')
                in_list = True
            
            # Remove bullet marker and format
            bullet_text = re.sub(r'^[•\-\*]\s*', '', stripped)
            # Bold text before colon or arrow for pattern names
            bullet_text = re.sub(r'^([^:→]+)([:\u2192])', r'<strong>\1</strong>\2', bullet_text)
            html_parts.append(f'<li style="margin-bottom:3px;">{bullet_text}</li>')
        
        else:
            # Close list if we were in one
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            
            # Check if it's a header (ends with : or is short intro text)
            if stripped.endswith(':') or len(stripped) < 60:
                # It's a header or intro - make it bold
                html_parts.append(f'<p style="margin:8px 0 4px 0;"><strong>{_html.escape(stripped)}</strong></p>')
            else:
                # Regular paragraph
                html_parts.append(f'<p style="margin:4px 0;">{_html.escape(stripped)}</p>')
    
    # Close any remaining list
    if in_list:
        html_parts.append('</ul>')
    
    return ''.join(html_parts)


def _get_options(frage_obj: Dict[str, Any]) -> List[Any]:
    """Return a normalized list of options for a question object.

    Supports multiple schema variants: German `optionen`, English `options`
    or generic `answers`. If the value is a dict, try to preserve ordering
    by sorted keys (useful for A/B/C maps), otherwise return a list.
    """
    opts = frage_obj.get("optionen") or frage_obj.get("options") or frage_obj.get("answers") or []
    if opts is None:
        return []
    # If someone provided a mapping like {'A': '...', 'B': '...'}, convert
    # to a stable list in key order so downstream code can index by integer.
    if isinstance(opts, dict):
        try:
            keys = sorted(opts.keys())
            return [opts[k] for k in keys]
        except Exception:
            try:
                return list(opts.values())
            except Exception:
                return []
    if isinstance(opts, str):
        return [opts]
    try:
        return list(opts)
    except Exception:
        return []


def _resolve_correct_answer(frage: Dict[str, Any]) -> Optional[Any]:
    """Resolve the canonical correct answer value for a question.

    Tries these strategies in order:
    - If `loesung` is an index and options exist, return options[index]
    - If `answer` is an index, return options[index]
    - If `answer` or `loesung` is a string that matches an option, return that
    - If `loesung` is a single-letter ('A'..), map to index
    Returns None if no reliable mapping could be found.
    """
    options = _get_options(frage)

    # Try German `loesung` first (common in older sets)
    if "loesung" in frage:
        val = frage.get("loesung")
        # integer-like
        try:
            idx = int(val)
            if isinstance(options, list) and 0 <= idx < len(options):
                return options[idx]
        except Exception:
            pass
        # letter like 'A'/'B'
        try:
            if isinstance(val, str) and len(val.strip()) == 1 and val.strip().isalpha():
                idx = ord(val.strip().upper()) - ord('A')
                if 0 <= idx < len(options):
                    return options[idx]
        except Exception:
            pass
        # string match
        try:
            if isinstance(val, str) and isinstance(options, list):
                for opt in options:
                    try:
                        if isinstance(opt, str) and opt.strip() == val.strip():
                            return opt
                    except Exception:
                        continue
        except Exception:
            pass

    # Try English `answer`
    if "answer" in frage:
        val = frage.get("answer")
        try:
            idx = int(val)
            if isinstance(options, list) and 0 <= idx < len(options):
                return options[idx]
        except Exception:
            pass
        try:
            if isinstance(val, str) and isinstance(options, list):
                for opt in options:
                    try:
                        if isinstance(opt, str) and opt.strip() == val.strip():
                            return opt
                    except Exception:
                        continue
        except Exception:
            pass

    # Fallback: if loesung present but couldn't be mapped, return raw value
    try:
        if "loesung" in frage and frage.get("loesung") is not None:
            return frage.get("loesung")
    except Exception:
        pass

    return None


def _prepare_stage_sorted_questions(questions: List[Dict[str, Any]]) -> List[tuple[int, str, int, Dict[str, Any]]]:
    """Bereitet die Fragen-Liste nach Bloom-Stufen sortiert auf."""
    enriched: list[tuple[int, str, int, Dict[str, Any]]] = []
    for idx, frage in enumerate(questions):
        normalized_stage = _normalize_stage_label(frage.get("kognitive_stufe"))
        rank = _get_bloom_stage_rank(normalized_stage)
        enriched.append((rank, normalized_stage, idx, frage))
    enriched.sort(key=lambda entry: (entry[0], entry[1], entry[2]))
    return enriched


def _render_radar_svg(labels: List[str], values: List[float], size: int = 360) -> str:
    """Render a simple radar chart as SVG and return a data URI string.

    This is a lightweight renderer that avoids extra dependencies (works
    reliably with WeasyPrint). `labels` and `values` must have the same
    length; `values` are expected as percentages (0-100).
    """
    try:
        from math import sin, cos, pi
        from urllib.parse import quote
    except Exception:
        return ""

    n = max(1, len(labels))
    cx = cy = size // 2
    outer_r = size * 0.36
    # grid levels (percent) to draw
    levels = [0.25, 0.5, 0.75, 1.0]

    def pt(angle, radius):
        return cx + radius * cos(angle), cy + radius * sin(angle)

    angle_step = 2 * pi / n if n > 0 else 2 * pi

    # Build SVG parts
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    # background: use a light gray paper background for better UX on white PDFs
    parts.append(f'<rect width="100%" height="100%" fill="#f3f4f6"/>')

    # concentric distance rings (background) and polygon grid overlay
    # On a light background use neutral grays for rings/grid and darker axes
    ring_stroke = "#d1d5db"      # subtle gray for rings
    grid_stroke = "#d1d5db"      # same for polygon grid
    for lvl in levels:
        r = outer_r * lvl
        # draw a circular ring as distance marker
        parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" stroke="{ring_stroke}" stroke-width="1"/>')
        # polygon grid (connecting points at this level) on top of rings
        pts = []
        for i in range(n):
            a = -pi/2 + i * angle_step
            x, y = pt(a, r)
            pts.append(f'{x:.2f},{y:.2f}')
        parts.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{grid_stroke}" stroke-width="1"/>')

    # axes: slightly darker gray so radial lines are visible on light background
    axes_stroke = "#9ca3af"
    for i in range(n):
        a = -pi/2 + i * angle_step
        x, y = pt(a, outer_r)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="{axes_stroke}" stroke-width="1"/>')

    # polygon for values
    poly_pts = []
    for i, v in enumerate(values):
        a = -pi/2 + i * angle_step
        r = outer_r * max(0.0, min(1.0, v / 100.0))
        x, y = pt(a, r)
        poly_pts.append(f'{x:.2f},{y:.2f}')
    if poly_pts:
        parts.append(f'<polygon points="{" ".join(poly_pts)}" fill="rgba(21,128,61,0.20)" stroke="#15803d" stroke-width="2"/>')

    # value labels for concentric rings (25/50/75/100) placed at top center
    try:
        ring_values = [int(l * 100) for l in levels]
        for lvl, val in zip(levels, ring_values):
            r = outer_r * lvl
            vx = cx
            vy = cy - r - 4  # small offset above the ring
            parts.append(f'<text x="{vx:.2f}" y="{vy:.2f}" font-size="10" text-anchor="middle" fill="#0f172a">{val}</text>')
    except Exception:
        # If anything goes wrong with rendering number labels, skip silently
        pass

    # labels
    for i, lab in enumerate(labels):
        a = -pi/2 + i * angle_step
        # position labels further out so they don't overlap the top '100' ring label
        x, y = pt(a, outer_r * 1.22)
        # anchor adjustment
        anchor = 'middle'
        # label color for light background
        parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="11" text-anchor="{anchor}" fill="#0f172a">{_html.escape(str(lab))}</text>')

    parts.append('</svg>')
    svg = "".join(parts)
    data_uri = "data:image/svg+xml;utf8," + quote(svg)
    return data_uri


def _render_topic_stacked_bar_svg(themes: List[str], pct_correct: List[float], pct_wrong: List[float], pct_unanswered: List[float] | None = None, width: int = 700, height: int = 260) -> str:
    """Render a simple stacked vertical bar chart as SVG and return a data URI string.

    `themes` : list of topic labels
    `pct_correct` / `pct_wrong` : lists of floats (0-100) corresponding to each theme
    The bars are drawn vertically; stack is correct (green) at bottom and wrong (red) on top.
    """
    try:
        from urllib.parse import quote
    except Exception:
        quote = None

    n = len(themes)
    if n == 0:
        return ""

    # Layout - use separate top/bottom/left paddings so scale labels don't get clipped
    # Leave extra left margin so rotated first label doesn't stick out
    # Increase substantially to avoid clipping of long first theme labels
    margin_left = 140
    # Keep a smaller right margin so increasing left margin doesn't expand the
    # chart area to the right (previous code subtracted margin_left twice).
    margin_right = 14
    # Reduce top margin slightly to give more vertical room to the chart
    margin_top = 24
    # Increase bottom margin to accommodate rotated x-axis labels
    # (user requested more space to avoid clipping long theme names)
    margin_bottom = 160
    gutter = 16
    bar_area_width = width - margin_left - margin_right
    # compute bar width to fit all bars with gutters
    total_gutters = gutter * (n - 1)
    bar_w = max(10, int((bar_area_width - total_gutters) / n))
    # leave space for x labels and header; compute chart area between top and bottom margins
    chart_top = margin_top
    chart_bottom = height - margin_bottom
    # Make chart taller by using more of the available vertical space
    chart_height = max(80, chart_bottom - chart_top - 18)  # ensure minimum height

    # allow overflow so text near edges isn't clipped when embedded
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet" style="overflow:visible">']
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>')

    # Y axis grid lines (25/50/75/100)
    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = chart_top + (1.0 - frac) * chart_height
        parts.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_left}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        # place the label slightly inward so it never touches the SVG edge
        label_x = max(6, margin_left - 8)
        parts.append(f'<text x="{label_x}" y="{y + 5:.1f}" font-size="10" text-anchor="end" fill="#374151">{int(frac*100)}</text>')

    # Bars
    x = margin_left
    for i, theme in enumerate(themes):
        c = max(0.0, min(100.0, float(pct_correct[i] if i < len(pct_correct) else 0.0)))
        w = max(0.0, min(100.0, float(pct_wrong[i] if i < len(pct_wrong) else 0.0)))
        u = 0.0
        if pct_unanswered:
            u = max(0.0, min(100.0, float(pct_unanswered[i] if i < len(pct_unanswered) else 0.0)))
        # heights
        h_c = (c / 100.0) * chart_height
        h_w = (w / 100.0) * chart_height
        h_u = (u / 100.0) * chart_height
        # bottom y for the bar (chart bottom inside margins)
        y_bottom = chart_top + chart_height
        # correct (green) rectangle (drawn first at bottom)
        y_c = y_bottom - h_c
        parts.append(f'<rect x="{x}" y="{y_c:.1f}" width="{bar_w}" height="{h_c:.1f}" fill="#15803d" rx="4" ry="4" stroke="#ffffff" stroke-width="0.6"/>')
        # wrong (red) rectangle stacked on top
        y_w = y_c - h_w
        parts.append(f'<rect x="{x}" y="{y_w:.1f}" width="{bar_w}" height="{h_w:.1f}" fill="#b91c1c" rx="4" ry="4" stroke="#ffffff" stroke-width="0.6"/>')
        # unanswered (grey) rectangle stacked on top
        y_u = y_w - h_u
        parts.append(f'<rect x="{x}" y="{y_u:.1f}" width="{bar_w}" height="{h_u:.1f}" fill="#9ca3af" rx="4" ry="4" stroke="#ffffff" stroke-width="0.6"/>')

        # percent text inside each segment if there's enough vertical space
        try:
            # Correct label (white on green)
                # Use smaller percent labels so they don't crowd the bars in PDF
                pct_font_size = 9
                # Only render labels if segment is tall enough (lower threshold now)
                if h_c > 10:
                    parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y_c + 10:.1f}" font-size="{pct_font_size}" text-anchor="middle" fill="#ffffff">{int(c)}%</text>')
                # Wrong label (white on red)
                if h_w > 10:
                    parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y_w + 10:.1f}" font-size="{pct_font_size}" text-anchor="middle" fill="#ffffff">{int(w)}%</text>')
                # Unanswered label (white on grey)
                if h_u > 10:
                    parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y_u + 10:.1f}" font-size="{pct_font_size}" text-anchor="middle" fill="#ffffff">{int(u)}%</text>')
        except Exception:
            pass

        # x-axis label rotated -45deg to avoid overlap (matches UI behavior)
        label_x = x + bar_w / 2
        label_y = chart_top + chart_height + 40
        safe_label = _html.escape(str(theme))
        # Use text-anchor end so rotated labels align neatly under the bar
        parts.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" font-size="11" text-anchor="end" fill="#0f172a" '
            f'transform="rotate(-45 {label_x:.1f} {label_y:.1f})">{safe_label}</text>'
        )

        x += bar_w + gutter

    parts.append('</svg>')
    svg = ''.join(parts)

    # Return as data URI (WeasyPrint accepts inline SVG via data URI)
    try:
        if quote:
            return 'data:image/svg+xml;utf8,' + quote(svg)
    except Exception:
        pass
    return svg


def _evict_formula_cache(max_files: int = 200, max_total_mb: int = 200, ttl_days: int = 7) -> None:
    """Evict old entries from the disk formula cache.

    Strategy:
    - Remove files older than ttl_days.
    - If total files > max_files or total size > max_total_mb, remove
      oldest files until under limits.
    """
    try:
        if not FORMULA_CACHE_DIR:
            return

        import time

        files = list(FORMULA_CACHE_DIR.glob('*.png'))
        # Filter out any entries that don't currently exist to avoid
        # races where another process removed files between glob() and stat().
        files = [f for f in files if f.exists()]
        if not files:
            return
        pre_count = len(files)
        # Use a safe stat pattern: individually try stat() and ignore files that
        # disappeared between listing and stat() to avoid FileNotFoundError.
        pre_total_bytes = 0
        safe_files = []
        for f in files:
            try:
                stsz = f.stat().st_size
                pre_total_bytes += stsz
                safe_files.append(f)
            except FileNotFoundError:
                # file vanished concurrently; skip it
                continue
            except Exception:
                # Any other stat error: skip file but keep going
                continue
        files = safe_files
        pre_total_mb = pre_total_bytes / (1024 * 1024)

        logger.info('Eviction: starting with %d files, %.2f MiB (limits: files=%d, MB=%d, ttl_days=%d)',
                    pre_count, pre_total_mb, max_files, max_total_mb, ttl_days)

        # Remove any lingering temporary files first (from previous interrupted writes)
        tmp_files = list(FORMULA_CACHE_DIR.glob('*.tmp'))
        for tf in tmp_files:
            try:
                b = tf.stat().st_size if tf.exists() else 0
                tf.unlink()
                logger.info('Eviction: removed lingering tmp file %s (%.1f KiB)', tf, b / 1024.0)
            except Exception:
                logger.warning('Eviction: failed to remove tmp file %s', tf)

        # Remove files older than ttl_days
        now = time.time()
        ttl_seconds = ttl_days * 86400
        survivors = []
        removed_files = []
        removed_bytes = 0

        for f in files:
            try:
                mtime = f.stat().st_mtime
            except FileNotFoundError:
                # File disappeared; skip it
                continue
            except Exception:
                # Any other stat error: skip this file
                continue

            if now - mtime > ttl_seconds:
                try:
                    try:
                        b = f.stat().st_size
                    except Exception:
                        b = 0
                    f.unlink()
                    removed_files.append(f)
                    removed_bytes += b
                    logger.info('Eviction: removed old file %s (%.1f KiB)', f, b / 1024.0)
                except Exception:
                    logger.warning('Eviction: failed to remove old file %s', f)
            else:
                survivors.append(f)

        # If we still exceed limits, sort by mtime ascending and delete oldest
        # Recompute total_size defensively: ignore files that vanish during this step
        total_size = 0
        fresh_survivors = []
        for f in survivors:
            try:
                if not f.exists():
                    continue
                total_size += f.stat().st_size
                fresh_survivors.append(f)
            except FileNotFoundError:
                continue
            except Exception:
                continue
        survivors = fresh_survivors
        total_mb = total_size / (1024 * 1024)

        if len(survivors) > max_files or total_mb > max_total_mb:
            # Sorting must tolerate files that disappear between calls to stat()
            try:
                survivors_sorted = sorted(
                    survivors,
                    key=lambda p: p.stat().st_mtime if p.exists() else 0
                )
            except FileNotFoundError:
                # As a fallback, filter and re-sort
                survivors = [p for p in survivors if p.exists()]
                survivors_sorted = sorted(survivors, key=lambda p: p.stat().st_mtime)
            # Delete until under both thresholds
            for f in survivors_sorted:
                try:
                    if not f.exists():
                        continue
                    b = f.stat().st_size
                    f.unlink()
                    removed_files.append(f)
                    removed_bytes += b
                    total_size -= b
                    total_mb = total_size / (1024 * 1024)
                    logger.info('Eviction: pruned file %s (%.1f KiB). New total: %.2f MiB', f, b / 1024.0, total_mb)
                except Exception:
                    logger.warning('Eviction: failed to prune file %s', f)

                current_count = len(list(FORMULA_CACHE_DIR.glob('*.png')))
                if current_count <= max_files and total_mb <= max_total_mb:
                    break

        post_files = list(FORMULA_CACHE_DIR.glob('*.png'))
        post_count = len(post_files)
        post_total_bytes = sum((f.stat().st_size for f in post_files if f.exists()))
        post_total_mb = post_total_bytes / (1024 * 1024)

        removed_count = len(removed_files)

        if removed_count > 0:
            logger.info('Eviction summary: removed %d files (%.2f MiB). Before: %d files / %.2f MiB; After: %d files / %.2f MiB',
                        removed_count, removed_bytes / (1024 * 1024), pre_count, pre_total_mb, post_count, post_total_mb)

    except Exception:
        # Be conservative: failure to evict is non-fatal
        logger.exception('Eviction failed')

# Default total timeout (seconds) for parallel formula rendering per parse call.
# This prevents a single export from blocking indefinitely when external LaTeX
# services are slow or rate-limited.
FORMULA_RENDER_TOTAL_TIMEOUT = 15.0


def _render_latex_to_image(formula: str, is_block: bool) -> str:
    """
    Rendert LaTeX-Formel zu PNG-Bild via QuickLaTeX API.
    Mit Caching für bessere Performance.
    """
    # Cache-Key erstellen
    cache_key = (formula, is_block)
    if cache_key in _formula_cache:
        return _formula_cache[cache_key]

    # Attempt disk-backed cache: derive filename from sha1(formula+flag)
    cache_filename = None
    try:
        if FORMULA_CACHE_DIR:
            h = hashlib.sha1((formula + ('@block' if is_block else '@inline')).encode('utf-8')).hexdigest()
            cache_filename = FORMULA_CACHE_DIR.joinpath(f"{h}.png")
            if cache_filename.exists():
                # Read file and return as data URI img tag (prefer block/inline styles)
                try:
                    with open(cache_filename, 'rb') as cf:
                        img_bytes = cf.read()
                        img_data = base64.b64encode(img_bytes).decode()
                        logger.info('Formula disk cache HIT: %s', cache_filename)
                        image_url = f'data:image/png;base64,{img_data}'
                        if is_block:
                            result = (f'<div style="text-align: center; margin: 1.2em 0; '
                                      f'padding: 0.5em; background-color: #f8f9fa;">'
                                      f'<img src="{image_url}" alt="LaTeX formula" '
                                      f'style="max-width: 100%; height: auto; vertical-align: middle;">'
                                      f'</div>')
                        else:
                            result = (f'<img src="{image_url}" alt="LaTeX formula" '
                                      f'style="vertical-align: middle; margin: 0 0.15em; max-height: 1.2em;">')
                        _formula_cache[cache_key] = result
                        return result
                except Exception:
                    # If reading cache fails, continue to generate anew
                    logger.warning('Failed to read formula cache file %s, will regenerate', cache_filename)
                    cache_filename = None
                    pass
    except Exception:
        cache_filename = None
    
    try:
        # Kleinere Schriftgröße aber extrem hohe DPI für beste Qualität
        font_size = '12px' if is_block else '14px'
        
        # WICHTIG: Erst alle Newlines entfernen
        cleaned_formula = formula.strip()
        
        # QuickLaTeX API aufrufen mit amsmath für Matrizen
        # Sehr hohe DPI für gestochen scharfe Bilder
        # Encode form data using percent-encoding (quote) instead of
        # the default application/x-www-form-urlencoded behavior which
        # encodes spaces as '+' (quote_plus). Some remote renderers
        # interpret '+' literally which can produce stray '+' signs in
        # resulting images. Use urllib.parse.urlencode with quote_via
        # to emit %20 for spaces.
        payload = {
            'formula': cleaned_formula,
            'fsize': font_size,
            'fcolor': '000000',
            'mode': '0',
            'out': '1',
            'remhost': 'quicklatex.com',
            'dpi': '1200',
            'preamble': (r'\usepackage{amsmath}'
                        r'\usepackage{amsfonts}'
                        r'\usepackage{amssymb}'),
        }
        encoded = _urlparse.urlencode(payload, quote_via=_urlparse.quote)
        response = requests.post(
            'https://quicklatex.com/latex3.f',
            data=encoded,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10,
        )
        
        if response.ok:
            lines = response.text.strip().replace('\r', '').split('\n')
            if len(lines) >= 2 and lines[0] == '0':
                parts = lines[1].split()
                image_url = parts[0]
                
                # Lade Bild herunter und konvertiere zu Base64 für beste Qualität
                try:
                    img_response = requests.get(image_url, timeout=10)
                    if img_response.ok:
                        img_bytes = img_response.content
                        # If disk cache is available, write the PNG atomically
                        try:
                            if cache_filename is not None and FORMULA_CACHE_DIR is not None:
                                # Run eviction before writing to keep cache within limits
                                _evict_formula_cache(
                                    max_files=FORMULA_CACHE_MAX_FILES,
                                    max_total_mb=FORMULA_CACHE_MAX_MB,
                                    ttl_days=FORMULA_CACHE_TTL_DAYS,
                                )
                                tmp_path = cache_filename.with_suffix('.tmp')
                                with open(tmp_path, 'wb') as tf:
                                    tf.write(img_bytes)
                                os.replace(tmp_path, cache_filename)
                                logger.info('Wrote formula image to disk cache: %s (bytes=%d)', cache_filename, len(img_bytes))
                        except Exception:
                            # Ignore disk write errors; proceed with in-memory result
                            logger.warning('Failed to write formula cache file %s: %s', cache_filename, traceback.format_exc())
                            pass
                        img_data = base64.b64encode(img_bytes).decode()
                        image_url = f'data:image/png;base64,{img_data}'
                except Exception:
                    pass  # Fallback auf direkte URL
                
                # Erstelle img-Tag mit besserer Skalierung
                if is_block:
                    return (f'<div style="text-align: center; '
                            f'margin: 1.2em 0; '
                            f'padding: 0.5em; '
                            f'background-color: #f8f9fa;">'
                            f'<img src="{image_url}" '
                            f'alt="LaTeX formula" '
                            f'style="max-width: 100%; height: auto; '
                            f'vertical-align: middle;"></div>')
                else:
                    # Unterscheide: Matrizen/Vektoren vs. einfache Formeln
                    has_matrix = ('pmatrix' in cleaned_formula or 
                                  'bmatrix' in cleaned_formula or 
                                  'vmatrix' in cleaned_formula)
                    if has_matrix:
                        # Matrizen: keine Höhenbeschränkung
                        return (f'<img src="{image_url}" '
                                f'alt="LaTeX formula" '
                                f'style="vertical-align: middle; '
                                f'margin: 0 0.15em; '
                                f'max-width: 90%;">')
                    else:
                        # Einfache Formeln: Höhe begrenzen
                        result = (f'<img src="{image_url}" '
                                  f'alt="LaTeX formula" '
                                  f'style="vertical-align: middle; '
                                  f'margin: 0 0.15em; '
                                  f'max-height: 1.2em;">')
                        _formula_cache[cache_key] = result
                        return result
    except Exception:
        pass
    
    # Fallback bei Fehlern
    error = f'[Formel: {formula}]'
    if is_block:
        result = f'<div style="text-align: center;">{error}</div>'
    else:
        result = f'<span>{error}</span>'
    _formula_cache[cache_key] = result
    return result


def _strip_leading_dict_prefix(text: str) -> str:
    """
    If `text` begins with a Python/JSON-like object followed by a colon or dash,
    extract and return the remainder after the first top-level closing brace
    + separator. This handles cases like:
      "{'title': 'Titel', 'steps': 'Schritte'}: Resttext..."

    The implementation walks the string to find the matching closing brace
    while respecting quotes so we don't stop on braces inside strings.
    If no safe split is found, the original text is returned unchanged.
    """
    if not text or not isinstance(text, str):
        return text

    s = text.lstrip()
    if not s.startswith('{'):
        return text

    # Walk the string to find matching top-level '}' while skipping over
    # quoted segments to avoid mismatching braces inside strings.
    depth = 0
    i = 0
    in_single = False
    in_double = False
    esc = False
    while i < len(s):
        ch = s[i]
        if esc:
            esc = False
        elif ch == '\\':
            esc = True
        elif in_single:
            if ch == "'":
                in_single = False
        elif in_double:
            if ch == '"':
                in_double = False
        else:
            if ch == "'":
                in_single = True
            elif ch == '"':
                in_double = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    # Found top-level closing brace at position i
                    j = i + 1
                    # Skip whitespace
                    while j < len(s) and s[j].isspace():
                        j += 1
                    # If next char is a separator (colon or dash variants), skip it
                    if j < len(s) and s[j] in ':-–—':
                        # Skip the separator and any following whitespace
                        k = j + 1
                        while k < len(s) and s[k].isspace():
                            k += 1
                        return s[k:]
                    break
        i += 1

    return text

def _render_formulas_parallel(formulas: List[tuple], total_timeout: float | None = None) -> Dict[int, str]:
    """
    Rendert mehrere Formeln parallel für bessere Performance.
    Verwendet dynamische Worker-Anzahl basierend auf CPU-Kernen.
    """
    results = {}
    
    def render_one(idx, formula_type, formula):
        # Respect the global semaphore so we don't saturate remote LaTeX API
        # when many users run exports concurrently.
        is_block = (formula_type == 'block')
        with _formula_semaphore:
            return idx, _render_latex_to_image(formula, is_block)
    
    # Dynamische Worker-Anzahl: 2x CPU-Kerne, max 20 (für I/O-bound tasks)
    import os
    max_workers = min(20, (os.cpu_count() or 4) * 2)
    
    import time

    # Parallele Ausführung mit ThreadPool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(render_one, i, ftype, form): i
            for i, (ftype, form) in enumerate(formulas)
        }
        start = time.time()
        per_future_max = 5.0

        pending = set(futures.keys())
        # Loop until all done or overall timeout exceeded
        while pending:
            elapsed = time.time() - start
            if total_timeout is not None:
                remaining = total_timeout - elapsed
            else:
                remaining = None

            if remaining is not None and remaining <= 0:
                # Overall timeout: mark all pending as timeout
                for fut in pending:
                    idx = futures[fut]
                    results[idx] = '[Formel-Timeout]'
                break

            wait_t = per_future_max if remaining is None else min(per_future_max, remaining)
            done, pending = wait(pending, timeout=wait_t, return_when=FIRST_COMPLETED)

            for fut in done:
                idx = futures[fut]
                try:
                    idx_ret, rendered = fut.result()
                    results[idx_ret] = rendered
                except Exception:
                    results[idx] = '[Formel-Fehler]'
                # Optional: we could report per-formula progress here via
                # a callback; generate_musterloesung_pdf uses coarse reports.

        # Any remaining futures after loop -> mark as timeout
        for fut in list(pending):
            idx = futures[fut]
            if idx not in results:
                results[idx] = '[Formel-Timeout]'

    return results


def _render_latex_in_html(html_text: str, total_timeout: float | None = None, md_inline: bool = False) -> str:
    """
    Findet LaTeX-Ausdrücke in einem HTML-String, rendert sie als Bilder
    und ersetzt die ursprünglichen Ausdrücke durch die Bild-Tags.

    Nimmt an, dass der Input bereits valides, sauberes HTML ist.
    """
    # Apply module default timeout when none provided to avoid indefinite waits
    if total_timeout is None:
        total_timeout = FORMULA_RENDER_TOTAL_TIMEOUT

    # 1. Formeln extrahieren und durch Platzhalter ersetzen
    formulas = []

    # NOTE: normalization of literal escape sequences (e.g. turning the two-
    # character sequence "\\n" into a real newline) must NOT run before
    # LaTeX extraction. Doing so will accidentally turn LaTeX commands that
    # begin with a backslash and an ASCII-letter (for example "\\nabla")
    # into a real newline followed by the rest of the token. We therefore
    # perform any such normalization only after formulas have been replaced
    # by stable placeholders below.

    def save_block_formula(match):
        formula = match.group(1).strip()
        placeholder = f"__FORMULA_BLOCK_{len(formulas)}__"
        formulas.append(('block', formula))
        return placeholder

    def save_inline_formula(match):
        formula = match.group(1).strip()
        placeholder = f"__FORMULA_INLINE_{len(formulas)}__"
        formulas.append(('inline', formula))
        return placeholder

    # Wir suchen nach allen gängigen LaTeX-Formaten.
    # Die Reihenfolge ist wichtig: Zuerst die längeren Block-Formate.
    processed_text = re.sub(r'\$\$(.*?)\$\$', save_block_formula, html_text, flags=re.DOTALL)
    processed_text = re.sub(r'\\\[(.*?)\\\]', save_block_formula, processed_text, flags=re.DOTALL)
    processed_text = re.sub(r'\$([^$]+?)\$', save_inline_formula, processed_text)
    processed_text = re.sub(r'\\\((.*?)\\\)', save_inline_formula, processed_text, flags=re.DOTALL)

    # 2. Markdown-Formatierungen wie Listen und Zeilenumbrüche in HTML umwandeln.
    # Dies ist immer noch notwendig, da die zentrale Bereinigung kein Markdown nach HTML konvertiert.
    # Wir entfernen aber das HTML-Escaping und die manuelle Tag-Ersetzung.
    # Normalize literal escape sequences now that LaTeX formulas are safely
    # extracted into placeholders. This converts pasted/serialized "\\n"
    # sequences into actual newlines without touching backslash-escapes
    # inside formulas (which are stored separately in `formulas`).
    try:
        if isinstance(processed_text, str) and ('\\r\\n' in processed_text or '\\n' in processed_text):
            processed_text = processed_text.replace('\\r\\n', '\n').replace('\\n', '\n')
    except Exception:
        pass

    lines = processed_text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        # Treat both '*' and '-' as unordered-list markers (e.g. '- item')
        if stripped.startswith(('* ', '- ')):
            content = stripped[2:]
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if stripped:  # Nur nicht-leere Zeilen hinzufügen
                html_lines.append(stripped)
    
    if in_list:
        html_lines.append('</ul>')

    # Preserve line breaks so Markdown block elements (like ```code```) are
    # recognized by the Markdown renderer. Previously we concatenated lines
    # which removed separators and caused code fences to collapse into a
    # single inline string (e.g. "line1line2"). Joining with '\n' keeps
    # the original structure intact for the downstream Markdown parser.
    processed_text = '\n'.join(html_lines)

    # Convert basic Markdown (italic, bold, links, etc.) to HTML while
    # keeping our LaTeX placeholders intact. Protect placeholders from
    # Markdown (which might treat underscores as emphasis) by wrapping
    # them in a temporary <span> before rendering and unwrapping after.
    try:
        # Find placeholders like __FORMULA_0__, __FORMULA_INLINE_0__, __FORMULA_BLOCK_0__
        placeholder_pattern = re.compile(r'(__FORMULA(?:_INLINE|_BLOCK)?_\d+__)')
        placeholders = placeholder_pattern.findall(processed_text)
        token_map: dict[str, str] = {}
        if placeholders:
            for idx, ph in enumerate(set(placeholders)):
                token = f'@@FORMULA_TOKEN_{idx}@@'
                token_map[token] = ph
                processed_text = processed_text.replace(ph, token)

        _md = MarkdownIt()
        if md_inline and hasattr(_md, 'renderInline'):
            # Render only inline elements (no surrounding <p>), useful for
            # list items and short previews where block-level margins are undesired.
            processed_text = _md.renderInline(processed_text)
        else:
            processed_text = _md.render(processed_text)

        # Restore tokens back to the original placeholders so the
        # later formula-render replacement can find them
        if token_map:
            for token, ph in token_map.items():
                processed_text = processed_text.replace(token, ph)
    except Exception:
        # If Markdown processing fails for any reason, continue with raw text.
        pass

    # 3. Formeln parallel rendern und wieder einsetzen
    if formulas:
        rendered_formulas = _render_formulas_parallel(formulas, total_timeout=total_timeout)
        
        for i in range(len(formulas)):
            placeholder_block = f"__FORMULA_BLOCK_{i}__"
            placeholder_inline = f"__FORMULA_INLINE_{i}__"
            rendered = rendered_formulas.get(i)
            # Defensive fallback: if rendering failed or returned an empty
            # value, keep the original LaTeX source visible so it is not
            # silently lost (prevents outputs like "Form ; ..."). We
            # escape the source to avoid accidental HTML injection.
            if not rendered:
                # formulas[i] is a tuple (type, formula)
                ftype, ftext = formulas[i]
                if ftype == 'block':
                    rendered = f'<div class="formula-fallback">{_html.escape(ftext)}</div>'
                else:
                    rendered = f'<code class="formula-fallback">{_html.escape(ftext)}</code>'

            if placeholder_block in processed_text:
                processed_text = processed_text.replace(placeholder_block, rendered)
            if placeholder_inline in processed_text:
                processed_text = processed_text.replace(placeholder_inline, rendered)
    
    if md_inline:
        # Inline rendering should not convert newlines to <br> globally
        return processed_text
    return processed_text.replace('\n', '<br>')


def _steps_have_numbering(steps: List[str]) -> bool:
    """
    Prüft, ob eine gegebene Liste von Schritten eine führende Nummerierung enthält.
    Liefert True, wenn mindestens ein Schritt mit z.B. "1. " oder "1) " beginnt.
    """
    if not steps:
        return False
    num_re = re.compile(r"^\s*\d+[\.\)]\s+")
    for s in steps:
        if isinstance(s, str) and num_re.match(s):
            return True
    return False


def _strip_leading_numbering(text: str) -> str:
    """
    Entfernt führende Nummerierungen wie "1. " oder "1) " aus einem Schritt-String.
    Wird verwendet, wenn wir eine geordnete Liste (<ol>) rendern und die
    Quelltexte bereits Nummern enthalten, damit nicht doppelt nummeriert wird.
    """
    if not isinstance(text, str):
        return text
    return re.sub(r'^\s*\d+[\.\)]\s+', '', text)


def _build_css_footer(footer_template: str) -> str:
    """
    Build a valid CSS `content` expression from a localized footer template.

    The template contains placeholders `{page}` and `{pages}` which are
    replaced with the CSS `counter(page)` and `counter(pages)` expressions.
    Literal parts are properly quoted so WeasyPrint doesn't reject the value.
    """
    # Split into literal and placeholder parts
    parts = re.split(r'(\{page\}|\{pages\})', footer_template)
    tokens: list[str] = []
    for p in parts:
        if p == '{page}':
            tokens.append('counter(page)')
        elif p == '{pages}':
            tokens.append('counter(pages)')
        elif p:
            # Quote literal segments and escape any internal quotes
            literal = p.replace('"', '\\"')
            tokens.append(f'"{literal}"')
    # Join tokens directly; adjacent strings/counters form the CSS content
    return ' '.join(tokens)


def _generate_qr_code(url: str) -> str:
    """Generiert QR-Code als Base64-String."""
    if not QR_AVAILABLE:
        return ""
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        return f'data:image/png;base64,{img_base64}'
    except Exception:
        return ""


def _calculate_average_stats(questions_file: str, questions: List[Dict[str, Any]]) -> dict:
    """
    Berechnet Durchschnittsstatistiken aller User für das gegebene Fragenset.
    
    Returns:
        dict mit 'avg_percent', 'avg_score', 'total_users', 'avg_difficulty'
    """
    from database import get_db_connection
    
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Ermittle erwartete Anzahl Fragen für Vollständigkeitsprüfung
        expected_questions = len(questions)
        
        # Berechne Durchschnittspunktzahl: nur beste Session pro User + nur komplette Tests
        cursor.execute("""
            WITH complete_sessions AS (
                -- Nur Sessions mit allen Fragen beantwortet
                SELECT 
                    s.session_id,
                    s.user_id,
                    SUM(a.points) as session_score,
                    COUNT(a.answer_id) as answered_questions
                FROM test_sessions s
                INNER JOIN answers a ON s.session_id = a.session_id
                WHERE s.questions_file = ?
                GROUP BY s.session_id, s.user_id
                HAVING COUNT(a.answer_id) = ?
            ),
            best_per_user AS (
                -- Nur beste Session pro User (höchste Punktzahl)
                SELECT 
                    user_id,
                    MAX(session_score) as best_score
                FROM complete_sessions
                GROUP BY user_id
            )
            SELECT 
                COUNT(DISTINCT user_id) as total_users,
                AVG(best_score) as avg_score
            FROM best_per_user
        """, (questions_file, expected_questions))
        
        result = cursor.fetchone()
        if result and result['total_users'] and result['total_users'] > 0:
            # Berechne maximale Punktzahl
            from logic import calculate_score
            from config import AppConfig
            app_config = AppConfig()
            _, max_score = calculate_score([None] * len(questions), questions, app_config.scoring_mode)
            
            avg_score = result['avg_score'] or 0
            avg_percent = (avg_score / max_score * 100) if max_score > 0 else 0
            
            # Berechne durchschnittliche Performance nach Schwierigkeit
            # Auch hier: nur beste Sessions pro User + nur komplette Tests
            cursor.execute("""
                WITH complete_sessions AS (
                    SELECT 
                        s.session_id,
                        s.user_id,
                        SUM(a.points) as session_score
                    FROM test_sessions s
                    INNER JOIN answers a ON s.session_id = a.session_id
                    WHERE s.questions_file = ?
                    GROUP BY s.session_id, s.user_id
                    HAVING COUNT(a.answer_id) = ?
                ),
                best_sessions AS (
                    -- Finde beste Session-ID pro User
                    SELECT 
                        cs.user_id,
                        cs.session_id,
                        cs.session_score
                    FROM complete_sessions cs
                    INNER JOIN (
                        SELECT user_id, MAX(session_score) as max_score
                        FROM complete_sessions
                        GROUP BY user_id
                    ) best ON cs.user_id = best.user_id 
                           AND cs.session_score = best.max_score
                )
                SELECT 
                    a.question_nr,
                    AVG(CASE WHEN a.is_correct = 1 THEN 1.0 ELSE 0.0 END) as success_rate
                FROM answers a
                INNER JOIN best_sessions bs ON a.session_id = bs.session_id
                GROUP BY a.question_nr
            """, (questions_file, expected_questions))
            
            question_rates = {row['question_nr']: row['success_rate'] for row in cursor.fetchall()}
            
            # Gruppiere nach Schwierigkeit
            diff_stats = {"easy": [], "medium": [], "hard": []}
            for i, frage in enumerate(questions):
                try:
                    q_text = frage.get("question", frage.get("frage", ""))
                    q_nr = int(str(q_text).split(".", 1)[0])
                except (ValueError, IndexError):
                    q_nr = i + 1

                gewichtung = frage.get("gewichtung", 1)
                if q_nr in question_rates:
                    rate = question_rates[q_nr] * 100
                    if gewichtung == 1:
                        diff_stats["easy"].append(rate)
                    elif gewichtung == 2:
                        diff_stats["medium"].append(rate)
                    else:
                        diff_stats["hard"].append(rate)
            
            avg_difficulty = {
                "easy": sum(diff_stats["easy"]) / len(diff_stats["easy"]) if diff_stats["easy"] else 0,
                "medium": sum(diff_stats["medium"]) / len(diff_stats["medium"]) if diff_stats["medium"] else 0,
                "hard": sum(diff_stats["hard"]) / len(diff_stats["hard"]) if diff_stats["hard"] else 0
            }
            
            return {
                "avg_percent": avg_percent,
                "avg_score": avg_score,
                "total_users": result['total_users'],
                "avg_difficulty": avg_difficulty
            }
        
        return None
        
    except Exception:
        logger.exception('Error calculating average stats')
        return None


def _extract_glossary_terms(
    questions: List[Dict[str, Any]]
) -> Dict[str, Dict[str, str]]:
    """
    Extrahiert Mini-Glossar-Einträge aus den Fragen,
    gruppiert nach Themen.
    Sammelt alle 'mini_glossary' Felder und entfernt Duplikate.

    Returns:
        Dict mit {Thema: {Begriff: Definition}} -
        Begriffe innerhalb Thema alphabetisch sortiert
    """
    glossary_by_theme: Dict[str, Dict[str, str]] = {}
    seen_terms = set()  # Tracking für globale Duplikate
    
    # Durchsuche alle Fragen nach mini_glossary Einträgen
    for frage_obj in questions:
        if "mini_glossary" in frage_obj:
            mini_gloss = frage_obj["mini_glossary"]
            # Fallback zu "Allgemein" wenn kein Thema
            thema = frage_obj.get("thema", "Allgemein")
            
            # Support two common formats used in question sets:
            # 1) dict mapping term -> definition
            # 2) list of objects [{"term": "...", "definition": "..."}, ...]
            if isinstance(mini_gloss, dict):
                # Initialisiere Thema, falls noch nicht vorhanden
                if thema not in glossary_by_theme:
                    glossary_by_theme[thema] = {}

                # Füge alle Begriffe aus diesem mini_glossary hinzu
                for term, definition in mini_gloss.items():
                    # Verhindere globale Duplikate
                    if isinstance(term, str) and term not in seen_terms and isinstance(definition, str):
                        glossary_by_theme[thema][term] = definition
                        seen_terms.add(term)

            elif isinstance(mini_gloss, list):
                # List-of-objects format (common in some exports):
                if thema not in glossary_by_theme:
                    glossary_by_theme[thema] = {}

                for entry in mini_gloss:
                    try:
                        if isinstance(entry, dict):
                            # Typical shape: {"term": "Sensor", "definition": "..."}
                            if 'term' in entry and 'definition' in entry:
                                term = entry.get('term')
                                definition = entry.get('definition')
                            else:
                                # Fallback: single-key dict mapping term->definition
                                if len(entry) == 1:
                                    term, definition = next(iter(entry.items()))
                                else:
                                    # Try common alternate keys
                                    term = entry.get('Begriff') or entry.get('Term') or entry.get('key')
                                    definition = entry.get('definition') or entry.get('Definition') or entry.get('def')
                        else:
                            # unsupported entry type
                            term = None
                            definition = None
                    except Exception:
                        term = None
                        definition = None

                    if isinstance(term, str) and isinstance(definition, str) and term and term not in seen_terms:
                        glossary_by_theme[thema][term] = definition
                        seen_terms.add(term)
    
    # Sortiere Themen alphabetisch und Begriffe innerhalb jedes Themas
    sorted_glossary = {}
    for thema in sorted(glossary_by_theme.keys()):
        sorted_glossary[thema] = dict(sorted(
            glossary_by_theme[thema].items(),
            key=lambda x: x[0].lower()
        ))
    
    return sorted_glossary


# NOTE: UX tweak (2025-10-14): The mini-glossary in the user-facing PDF
# now uses subtle category dividers (same visual style as the admin
# mini-glossary export) instead of heavy bordered panels. The change
# was implemented by updating the glossary CSS rules to use lighter
# separators and remove the strong background/border that was used
# previously for the user report.


def _build_glossary_html(
    glossary_by_theme: Dict[str, Dict[str, str]],
    intro_text: str | None = None,
    include_header: bool = True,
) -> str:
    if not glossary_by_theme:
        return ""

    glossary_html_parts: list[str] = []

    if include_header:
        glossary_html_parts.append('<div class="glossary-section">')
        glossary_html_parts.append(f'<h2 class="section-title">{_html.escape(translate_ui("pdf.glossary.title", default="Mini-Glossar"))}</h2>')
        # Prefer an alternate, shorter intro if provided in translations
        alt_intro = translate_ui('pdf.glossary.alt_intro', default='')
        default_intro = translate_ui('pdf.glossary.intro', default='Wichtige Begriffe aus diesem Test, gruppiert nach Themen')
        if intro_text:
            intro = intro_text
        elif alt_intro:
            intro = alt_intro
        else:
            intro = default_intro
        glossary_html_parts.append(f'<p class="glossary-intro">{_html.escape(intro)}</p>')

    for thema, terms in glossary_by_theme.items():
        parsed_thema = _render_latex_in_html(smart_quotes_de(thema), md_inline=True)
        glossary_html_parts.append('<div class="glossary-section">')
        glossary_html_parts.append(f'<h3 class="glossary-theme">{parsed_thema}</h3>')
        glossary_html_parts.append('<div class="glossary-grid">')

        for term, definition in terms.items():
            parsed_term = _render_latex_in_html(smart_quotes_de(term), md_inline=True)
            parsed_definition = _render_latex_in_html(smart_quotes_de(definition), md_inline=True)

            glossary_html_parts.append('<div class="glossary-item">')
            glossary_html_parts.append(f'<div class="glossary-term">{parsed_term}</div>')
            glossary_html_parts.append(f'<div class="glossary-definition">{parsed_definition}</div>')
            glossary_html_parts.append('</div>')

        glossary_html_parts.append('</div>')
        glossary_html_parts.append('</div>')

    if include_header:
        glossary_html_parts.append('</div>')

    return ''.join(glossary_html_parts)


def estimate_formula_render(questions: List[Dict[str, Any]], locale: Optional[str] = None) -> tuple[int, int]:
    """
    Schätzt die Anzahl einzigartiger LaTeX-Formeln in einem Fragenset und
    wie viele davon noch gerendert werden müssen (nicht im Cache vorhanden).

    Optional kann ein `locale`-String (z.B. 'de' oder 'en') übergeben werden.
    Bei lokalisierten Frageobjekten priorisiert die Funktion dann die
    landesspezifischen Feldnamen (z.B. 'frage'/'erklaerung' für Deutsch
    gegenüber 'question'/'explanation' für Englisch). Dies beeinflusst nur
    die Erkennungsreihenfolge; die Rückgabe bleibt ein Tupel
    `(unique_formula_count, to_render_count)` um Abwärtskompatibilität zu
    gewährleisten.

    Returns: (unique_formula_count, to_render_count)
    """
    try:
        INLINE_PAT = re.compile(r"\$([^$]+?)\$|\\\((.*?)\\\)", flags=re.DOTALL)
        BLOCK_PAT = re.compile(r"\$\$(.*?)\$\$|\\\[(.*?)\\\]", flags=re.DOTALL)

        formulas = []
        # Determine preferred field order depending on locale to support
        # localized question objects. Default behavior remains backwards-compatible
        # and checks both German and English keys.
        lang = (locale or '').lower()
        if lang.startswith('de'):
            question_keys = ['frage', 'question']
            explanation_keys = ['erklaerung', 'explanation']
        else:
            # default: prefer English-style keys
            question_keys = ['question', 'frage']
            explanation_keys = ['explanation', 'erklaerung']
        for frage in questions:
            # Support localized field names; prefer keys based on locale
            txt = ''
            for k in question_keys:
                v = frage.get(k)
                if isinstance(v, str) and v.strip():
                    txt = v
                    break
            txt = txt or ""
            for m in BLOCK_PAT.findall(txt):
                # findall returns tuples for alternation groups
                grp = next((g for g in m if g), '')
                if grp:
                    formulas.append(('block', grp.strip()))
            for m in INLINE_PAT.findall(txt):
                grp = next((g for g in m if g), '')
                if grp:
                    formulas.append(('inline', grp.strip()))

            erk = ''
            for k in explanation_keys:
                v = frage.get(k)
                if isinstance(v, str) and v.strip():
                    erk = v
                    break
            erk = erk or ""
            if isinstance(erk, str):
                for m in BLOCK_PAT.findall(erk):
                    grp = next((g for g in m if g), '')
                    if grp:
                        formulas.append(('block', grp.strip()))
                for m in INLINE_PAT.findall(erk):
                    grp = next((g for g in m if g), '')
                    if grp:
                        formulas.append(('inline', grp.strip()))

            for opt in _get_options(frage):
                if isinstance(opt, str):
                    for m in BLOCK_PAT.findall(opt):
                        grp = next((g for g in m if g), '')
                        if grp:
                            formulas.append(('block', grp.strip()))
                    for m in INLINE_PAT.findall(opt):
                        grp = next((g for g in m if g), '')
                        if grp:
                            formulas.append(('inline', grp.strip()))

        # Deduplicate while preserving order
        unique = list(dict.fromkeys(formulas))
        total_unique = len(unique)

        # Check cache presence per formula
        to_render = 0
        try:
            import hashlib as _hashlib
            for kind, formula in unique:
                cache_key = (formula, True if kind == 'block' else False)
                in_memory = cache_key in _formula_cache
                on_disk = False
                if not in_memory and FORMULA_CACHE_DIR:
                    try:
                        suffix = '@block' if kind == 'block' else '@inline'
                        h = _hashlib.sha1((formula + suffix).encode('utf-8')).hexdigest()
                        if FORMULA_CACHE_DIR.joinpath(f"{h}.png").exists():
                            on_disk = True
                    except Exception:
                        on_disk = False

                if not (in_memory or on_disk):
                    to_render += 1
        except Exception:
            # If anything goes wrong, return conservative estimate
            return total_unique, total_unique

        return total_unique, to_render
    except Exception:
        return 0, 0


def _analyze_weak_topics(questions: List[Dict[str, Any]]) -> List[tuple]:
    """
    Analysiert die schwächsten Themen basierend auf falschen Antworten.
    Gruppiert nach dem 'thema'-Feld der Fragen.
    Gibt Liste von (Thema, [Fragennummern]) zurück.
    """
    topic_errors = {}
    
    # Hole initial_indices für korrekte Fragennummerierung
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    
    for i, frage_obj in enumerate(questions):
        gegebene_antwort = get_answer_for_question(i)

        # Defensive: support multiple schema variants. Some datasets use
        # German keys ('optionen', 'loesung'), others use English
        # ('options', 'answer'). Accept either and try to derive a
        # canonical correct answer string for comparison.
        options = _get_options(frage_obj)

        richtige_antwort = None

        # Try German index key first (common in localized files)
        if "loesung" in frage_obj:
            try:
                idx = int(frage_obj.get("loesung"))
            except Exception:
                idx = None
            if idx is not None and isinstance(options, list) and 0 <= idx < len(options):
                richtige_antwort = options[idx]

        # Try English index/key variants
        if richtige_antwort is None:
            if "answer" in frage_obj:
                val = frage_obj.get("answer")
                # If it's numeric, treat as index
                try:
                    idx2 = int(val)
                except Exception:
                    idx2 = None
                if idx2 is not None and isinstance(options, list) and 0 <= idx2 < len(options):
                    richtige_antwort = options[idx2]
                elif isinstance(val, str) and isinstance(options, list):
                    # Try to match by string equality
                    for opt in options:
                        try:
                            if isinstance(opt, str) and opt.strip() == val.strip():
                                richtige_antwort = opt
                                break
                        except Exception:
                            continue

        # As a last resort, if 'loesung' is a string containing the correct
        # answer directly, use it.
        if richtige_antwort is None:
            loes = frage_obj.get("loesung")
            if isinstance(loes, str) and loes.strip():
                richtige_antwort = loes

        # Only count when we have both a given answer and a canonical correct
        # answer to compare against.
        if gegebene_antwort is not None and richtige_antwort is not None and gegebene_antwort != richtige_antwort:
            # Extrahiere Thema aus dem 'thema'-Feld der Frage
            topic = frage_obj.get("thema", "Allgemein")

            # Berechne die Display-Fragennummer (wie im PDF angezeigt)
            display_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1

            if topic not in topic_errors:
                topic_errors[topic] = []
            topic_errors[topic].append(display_number)
    
    # Sortiere nach Anzahl der Fehler, gib ALLE Themen zurück (nicht nur Top 3)
    sorted_topics = sorted(topic_errors.items(), key=lambda x: len(x[1]), reverse=True)
    return sorted_topics


def _build_extended_explanation_html(frage_obj: Dict[str, Any], total_timeout: float | None = None) -> str:
    """
    Baut den HTML-Block für die erweiterte Erklärung aus einem Frage-Objekt.
    Diese Funktion konsolidiert die Logik für 'generate_pdf_report' und 'generate_musterloesung_pdf'.
    Gibt einen leeren String zurück, wenn keine gültige erweiterte Erklärung vorhanden ist.
    """
    extended_explanation = normalize_detailed_explanation(frage_obj.get("extended_explanation"))

    if not (extended_explanation and isinstance(extended_explanation, dict)):
        return ""

    title = extended_explanation.get('title') or extended_explanation.get('titel') or ''
    content = extended_explanation.get('content')
    steps = (
        extended_explanation.get('schritte')
        if isinstance(extended_explanation.get('schritte'), list)
        else (extended_explanation.get('steps') if isinstance(extended_explanation.get('steps'), list) else None)
    )

    # Only render if there's something to show
    if not (title or content or steps):
        return ""

    detailed_label = translate_ui("test_view.extended_panel", default="Detaillierte Erklärung")
    explanation_html = f'<div class="explanation"><strong>{_html.escape(detailed_label)}'
    if title:
        explanation_html += f": {_render_latex_in_html(smart_quotes_de(title), md_inline=True, total_timeout=total_timeout)}"
    explanation_html += "</strong>"

    if isinstance(content, str) and content.strip():
        safe_content = _strip_leading_dict_prefix(content)
        explanation_html += "<br>" + _render_latex_in_html(smart_quotes_de(safe_content), total_timeout=total_timeout)

    if steps:
        list_tag = 'ol' if _steps_have_numbering(steps) else 'ul'
        explanation_html += f"<{list_tag} class='extended-steps'>"
        for step in steps:
            item = _strip_leading_numbering(step) if list_tag == 'ol' else step
            explanation_html += f"<li>{_render_latex_in_html(smart_quotes_de(item), md_inline=True, total_timeout=total_timeout)}</li>"
        explanation_html += f"</{list_tag}>"

    explanation_html += "</div>"
    return explanation_html


def _cooldown_adjusted_total_minutes(
    questions: List[Dict[str, Any]],
    app_config: AppConfig,
    question_set: Any | None = None,
) -> float | None:
    """
    Compute the base test duration (in minutes) including cooldowns for reading/next.
    Mirrors the logic used during session initialization so PDFs reflect the real limit.
    """
    try:
        # Base minutes from question set or app config
        if question_set:
            base_minutes = question_set.get_test_duration_minutes(app_config.test_duration_minutes)
        else:
            base_minutes = getattr(app_config, "test_duration_minutes", None)
        if base_minutes is None:
            return None

        # Resolve per-weight minute configuration from metadata when available
        per_weight_minutes: Dict[int, float] = {}
        try:
            qmeta = getattr(question_set, "meta", None) if question_set else None
            per_weight_raw = None
            if isinstance(qmeta, dict):
                per_weight_raw = qmeta.get("time_per_weight_minutes") or qmeta.get("time_per_weight")
            if isinstance(per_weight_raw, dict):
                for k, v in per_weight_raw.items():
                    try:
                        per_weight_minutes[int(k)] = float(v)
                    except Exception:
                        continue
        except Exception:
            # If metadata parsing fails, fall back to defaults below
            per_weight_minutes = {}
        if not per_weight_minutes:
            per_weight_minutes = {1: 0.5, 2: 0.75, 3: 1.0}

        total_cooldown_seconds = compute_total_cooldown_seconds(
            list(questions),
            per_weight_minutes,
            reading_cooldown_base_per_weight=app_config.reading_cooldown_base_per_weight,
            next_cooldown_extra_standard=app_config.next_cooldown_extra_standard,
            next_cooldown_extra_extended=app_config.next_cooldown_extra_extended,
        )
        return base_minutes + (total_cooldown_seconds / 60.0)
    except Exception:
        return None


def generate_pdf_report(questions: List[Dict[str, Any]], app_config: AppConfig) -> bytes:
    """
    Generiert einen PDF-Bericht, indem zuerst ein HTML-Dokument erstellt
    und dieses dann mit WeasyPrint in PDF konvertiert wird.
    
    Performance-Optimierungen:
    - Paralleles Formel-Rendering (dynamische Worker-Anzahl)
    - Formula-Caching (keine doppelten API-Calls)
    - Batch-Verarbeitung für QuickLaTeX API
    """
    try:
        from helpers.text import format_datetime_locale, FMT_DATETIME
    except Exception:
        format_datetime_locale = None  # type: ignore[assignment]
        FMT_DATETIME = "%d.%m.%Y %H:%M"  # type: ignore[assignment]

    # Always use current date/time for PDF generation
    if format_datetime_locale:
        try:
            # Pass datetime object directly (not ISO string) to avoid parsing issues
            generated_at_str = format_datetime_locale(datetime.now(), fmt=FMT_DATETIME)
        except Exception:
            # Fallback: manual formatting with German date/time format
            generated_at_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    else:
        # Fallback: manual formatting with German date/time format
        generated_at_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Ensure tests or environments without a fully-featured streamlit
    # module still work: provide a safe session_state dict if missing.
    if not hasattr(st, "session_state"):
        try:
            st.session_state = {}
        except Exception:
            # Last-resort: create a local fallback to avoid AttributeError
            class _LocalState(dict):
                pass

            st.session_state = _LocalState()

    user_name = st.session_state.get("user_id", "Unbekannt")
    q_file = st.session_state.get("selected_questions_file", "Unbekanntes Set")

    set_name = None
    try:
        from config import load_questions
        question_set = load_questions(q_file, silent=True)
        if question_set and question_set.meta:
            set_name = question_set.meta.get("title") or question_set.meta.get("thema")
    except Exception:
        set_name = None

    if not set_name:
        try:
            from user_question_sets import pretty_label_from_identifier_string
            set_name = pretty_label_from_identifier_string(q_file)
        except (ImportError, AttributeError):
            set_name = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    set_name = set_name or translate_ui("pdf.unnamed_set", default="Ungenanntes Fragenset")

    # Prüfen, ob der Test vorzeitig beendet wurde
    test_manually_ended = st.session_state.get("test_manually_ended", False)
    current_mode = st.session_state.get('selected_mode', 'exam')

    header_title = set_name
    header_subtitle = ""
    subtitle_parts = []

    if current_mode == 'practice':
        mode_text = translate_ui("pdf.header.mode.practice", default="Übungsbericht")
        subtitle_parts.append(f'<span class="header-mode">{_html.escape(mode_text)}</span>')
    else:
        mode_text = translate_ui("pdf.header.mode.exam", default="Testbericht")
        subtitle_parts.append(f'<span class="header-mode">{_html.escape(mode_text)}</span>')

    if test_manually_ended:
        manual_text = translate_ui("pdf.header.manual_end", default="Test vorzeitig beendet")
        subtitle_parts.append(f'<span class="header-warning"> ({_html.escape(manual_text)})</span>')

    if subtitle_parts:
        header_subtitle = f'<p class="header-subtitle">{"".join(subtitle_parts)}</p>'

    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions, app_config.scoring_mode
    )
    prozent = (current_score / max_score * 100) if max_score > 0 else 0

    # Hole Ranking-Position
    from database import get_all_logs_for_leaderboard
    leaderboard_data = get_all_logs_for_leaderboard(q_file)
    user_rank = None
    user_tempo_from_leaderboard = None
    if leaderboard_data:
        for idx, entry in enumerate(leaderboard_data, start=1):
            if entry['user_pseudonym'] == user_name:
                user_rank = idx
                # capture tempo for this user's best session from leaderboard
                try:
                    user_tempo_from_leaderboard = entry.get('tempo')
                except Exception:
                    user_tempo_from_leaderboard = None
                break
    
    rank_text = translate_ui("pdf.rank_text", default=" • Platz {rank} im Ranking").format(rank=user_rank) if user_rank else ""

    # Statistiken berechnen
    antworten = [get_answer_for_question(i) for i in range(len(questions))]
    richtige = 0
    for i, ant in enumerate(antworten):
        if ant is None:
            continue
        try:
            correct_val = _resolve_correct_answer(questions[i])
        except Exception:
            correct_val = None
        if correct_val is not None and ant == correct_val:
            richtige += 1
    unbeantwortet = sum(1 for ant in antworten if ant is None)
    falsche = len(questions) - richtige - unbeantwortet

    # --- Confidence / Gefühl vs. Ergebnis (optional) ---
    confidence_html = ""
    try:
        from database import get_answers_for_session
    except Exception:
        get_answers_for_session = None  # type: ignore[assignment]

    confidence_counts = {
        "sure_correct": 0,
        "sure_wrong": 0,
        "unsure_correct": 0,
        "unsure_wrong": 0,
    }
    try:
        session_id = st.session_state.get("session_id")
        if session_id and callable(get_answers_for_session):
            answers = get_answers_for_session(int(session_id))
            for row in answers:
                conf = row.get("confidence") if isinstance(row, dict) else None
                if not conf:
                    continue
                conf_norm = str(conf).strip().lower()
                if conf_norm not in ("sure", "unsure"):
                    continue
                is_correct = row.get("is_correct") if isinstance(row, dict) else None
                correct = bool(is_correct)
                if conf_norm == "sure":
                    if correct:
                        confidence_counts["sure_correct"] += 1
                    else:
                        confidence_counts["sure_wrong"] += 1
                else:
                    if correct:
                        confidence_counts["unsure_correct"] += 1
                    else:
                        confidence_counts["unsure_wrong"] += 1
    except Exception:
        pass

    total_confidence = sum(confidence_counts.values())
    if total_confidence > 0:
        conf_title = translate_ui("pdf.confidence.title", default="Gefühl vs. Ergebnis")
        conf_caption = translate_ui("pdf.confidence.caption", default="So gut passt dein Gefühl zu den Ergebnissen.")
        sure_label = translate_ui("pdf.confidence.sure", default="Sicher")
        unsure_label = translate_ui("pdf.confidence.unsure", default="Unsicher")
        correct_label = translate_ui("pdf.confidence.correct", default="Richtig")
        wrong_label = translate_ui("pdf.confidence.wrong", default="Falsch")
        totals_tpl = translate_ui(
            "pdf.confidence.totals",
            default="Summen: Sicher {sure} | Unsicher {unsure} | Richtig {correct} | Falsch {wrong}",
        )
        sure_total = confidence_counts["sure_correct"] + confidence_counts["sure_wrong"]
        unsure_total = confidence_counts["unsure_correct"] + confidence_counts["unsure_wrong"]
        correct_total = confidence_counts["sure_correct"] + confidence_counts["unsure_correct"]
        wrong_total = confidence_counts["sure_wrong"] + confidence_counts["unsure_wrong"]
        totals_text = totals_tpl.format(
            sure=sure_total,
            unsure=unsure_total,
            correct=correct_total,
            wrong=wrong_total,
        )

        def _cell(count: int, good: bool) -> tuple[str, str]:
            pct = int(round(count / total_confidence * 100.0)) if total_confidence else 0
            cls = "good" if good else "bad"
            if count == 0:
                cls = "neutral"
            return f"{count} ({pct}%)", cls

        sc_text, sc_cls = _cell(confidence_counts["sure_correct"], True)
        sw_text, sw_cls = _cell(confidence_counts["sure_wrong"], False)
        uc_text, uc_cls = _cell(confidence_counts["unsure_correct"], False)
        uw_text, uw_cls = _cell(confidence_counts["unsure_wrong"], True)

        hints_html = ""
        try:
            overconfidence_pct = confidence_counts["sure_wrong"] / total_confidence if total_confidence else 0.0
            underconfidence_pct = confidence_counts["unsure_correct"] / total_confidence if total_confidence else 0.0
            calibrated_pct = (
                (confidence_counts["sure_correct"] + confidence_counts["unsure_wrong"]) / total_confidence
                if total_confidence else 0.0
            )
            hint_threshold = 0.2
            hints: list[tuple[str, str]] = []
            if overconfidence_pct >= hint_threshold:
                hints.append((
                    "warn",
                    translate_ui(
                        "pdf.confidence.hint_overconfidence",
                        default="Übervertrauen: {percent}% deiner Einschätzungen waren sicher, aber falsch. Tipp: nimm dir kurz mehr Prüfzeit.",
                    ).format(percent=int(round(overconfidence_pct * 100))),
                ))
            if underconfidence_pct >= hint_threshold:
                hints.append((
                    "info",
                    translate_ui(
                        "pdf.confidence.hint_underconfidence",
                        default="Untervertrauen: {percent}% deiner Einschätzungen waren unsicher, aber richtig. Tipp: vertraue deinem Wissen etwas mehr.",
                    ).format(percent=int(round(underconfidence_pct * 100))),
                ))
            if calibrated_pct >= 0.8:
                hints.append((
                    "good",
                    translate_ui(
                        "pdf.confidence.hint_calibration_good",
                        default="Einschätzung passt gut: {percent}%.",
                    ).format(percent=int(round(calibrated_pct * 100))),
                ))
            elif calibrated_pct <= 0.5:
                hints.append((
                    "warn",
                    translate_ui(
                        "pdf.confidence.hint_calibration_low",
                        default="Einschätzung passt selten: {percent}%.",
                    ).format(percent=int(round(calibrated_pct * 100))),
                ))
            if hints:
                hints_html = '<ul class="confidence-hints">'
                for cls, text in hints:
                    hints_html += f'<li class="confidence-hint {cls}">{_html.escape(text)}</li>'
                hints_html += '</ul>'
        except Exception:
            hints_html = ""

        confidence_html = f'''
            <div class="confidence-box">
                <h3>{_html.escape(conf_title)}</h3>
                <div class="confidence-caption">{_html.escape(conf_caption)}</div>
                <table class="confidence-table">
                    <thead>
                        <tr>
                            <th></th>
                            <th>{_html.escape(correct_label)}</th>
                            <th>{_html.escape(wrong_label)}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <th>{_html.escape(sure_label)}</th>
                            <td class="confidence-cell {sc_cls}">{_html.escape(sc_text)}</td>
                            <td class="confidence-cell {sw_cls}">{_html.escape(sw_text)}</td>
                        </tr>
                        <tr>
                            <th>{_html.escape(unsure_label)}</th>
                            <td class="confidence-cell {uc_cls}">{_html.escape(uc_text)}</td>
                            <td class="confidence-cell {uw_cls}">{_html.escape(uw_text)}</td>
                        </tr>
                    </tbody>
                </table>
                <div class="confidence-totals">{_html.escape(totals_text)}</div>
                {hints_html}
            </div>
        '''
    
    # Bearbeitungszeit berechnen
    start_time = st.session_state.get("test_start_time")
    # If the key exists but is set to None, fall back to now.
    end_time = st.session_state.get("test_end_time") or datetime.now()
    duration_str = ""

    # Helper: coerce pandas.Timestamp to native datetime if necessary
    def _to_datetime(obj):
        if obj is None:
            return None
        # pandas Timestamp has to_pydatetime()
        try:
            if hasattr(obj, "to_pydatetime"):
                return obj.to_pydatetime()
        except Exception:
            pass
        if isinstance(obj, datetime):
            return obj
        # Accept ISO-format strings (with or without timezone) and common
        # naive datetime string formats so stored string timestamps are
        # correctly converted when sessions were persisted as text.
        if isinstance(obj, str):
            try:
                # Python 3.7+ supports fromisoformat for many ISO strings
                return datetime.fromisoformat(obj)
            except Exception:
                # Try dateutil if available for broader parsing support
                try:
                    from dateutil import parser as _dparser

                    return _dparser.isoparse(obj)
                except Exception:
                    # Last-resort common formats
                    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                        try:
                            return datetime.strptime(obj, fmt)
                        except Exception:
                            continue
        return None

    s_dt = _to_datetime(start_time)
    e_dt = _to_datetime(end_time)

    if s_dt and e_dt:
        # Normalize timezone-awareness robustly:
        # - If one datetime is aware and the other naive, assume the naive
        #   timestamp was recorded in the same timezone as the aware one and
        #   attach that tzinfo to the naive value. This preserves the
        #   original wall-clock meaning instead of dropping offsets.
        # - If both are aware but with different zones, convert both to UTC
        #   before subtracting to get a correct delta.
        try:
            s_aware = s_dt.tzinfo is not None
            e_aware = e_dt.tzinfo is not None
            if s_aware and not e_aware:
                # Heuristic: try to interpret the naive end_time in multiple ways
                # and pick the interpretation that yields a sensible (non-negative)
                # duration. First try treating naive as UTC (common when
                # timestamps were written without local offset), then fall back
                # to attaching the start tzinfo if that gives a positive delta.
                try:
                    from datetime import timezone as _tz
                    e_as_utc = e_dt.replace(tzinfo=_tz.utc)
                    s_utc = s_dt.astimezone(_tz.utc)
                    delta_utc = (e_as_utc - s_utc).total_seconds()
                except Exception:
                    delta_utc = None

                try:
                    e_as_local = e_dt.replace(tzinfo=s_dt.tzinfo)
                    delta_local = (e_as_local - s_dt).total_seconds()
                except Exception:
                    delta_local = None

        

                # Prefer a non-negative delta; if both non-negative choose the
                # smaller absolute difference (more plausible). Otherwise prefer
                # the non-negative one.
                chosen = None
                if delta_utc is not None and delta_utc >= 0:
                    chosen = 'utc'
                if delta_local is not None and delta_local >= 0:
                    if chosen is None:
                        chosen = 'local'
                    else:
                        # both non-negative -> pick smaller delta
                        chosen = 'utc' if abs(delta_utc) <= abs(delta_local) else 'local'

                if chosen == 'utc':
                    from datetime import timezone as _tz
                    e_dt = e_dt.replace(tzinfo=_tz.utc)
                    # ensure s_dt is in UTC too for subtraction
                    s_dt = s_dt.astimezone(_tz.utc)
                elif chosen == 'local':
                    e_dt = e_dt.replace(tzinfo=s_dt.tzinfo)
                else:
                    # fallback: attach start tzinfo
                    e_dt = e_dt.replace(tzinfo=s_dt.tzinfo)
            elif e_aware and not s_aware:
                # Mirror the heuristic for the opposite case
                try:
                    from datetime import timezone as _tz
                    s_as_utc = s_dt.replace(tzinfo=_tz.utc)
                    e_utc = e_dt.astimezone(_tz.utc)
                    delta_utc = (e_utc - s_as_utc).total_seconds()
                except Exception:
                    delta_utc = None

                try:
                    s_as_local = s_dt.replace(tzinfo=e_dt.tzinfo)
                    delta_local = (e_dt - s_as_local).total_seconds()
                except Exception:
                    delta_local = None

                chosen = None
                if delta_utc is not None and delta_utc >= 0:
                    chosen = 'utc'
                if delta_local is not None and delta_local >= 0:
                    if chosen is None:
                        chosen = 'local'
                    else:
                        chosen = 'utc' if abs(delta_utc) <= abs(delta_local) else 'local'

                if chosen == 'utc':
                    from datetime import timezone as _tz
                    s_dt = s_dt.replace(tzinfo=_tz.utc)
                    e_dt = e_dt.astimezone(_tz.utc)
                elif chosen == 'local':
                    s_dt = s_dt.replace(tzinfo=e_dt.tzinfo)
                else:
                    s_dt = s_dt.replace(tzinfo=e_dt.tzinfo)
            elif s_aware and e_aware:
                # convert both to UTC to avoid mismatched offsets
                try:
                    s_dt = s_dt.astimezone(datetime.timezone.utc)
                    e_dt = e_dt.astimezone(datetime.timezone.utc)
                except Exception:
                    pass
        except Exception:
            pass

        # --- Schema normalization: ensure every question uses canonical keys ---
        def normalize_question_schema(q: Dict[str, Any]) -> Dict[str, Any]:
            """
            Normalizes common alias keys between datasets so downstream code can
            rely on canonical keys.

            Canonical keys produced/ensured:
            - 'text' (str): question text
            - 'options' (List[str]): list of option strings
            - 'answer' (int | str | None): index into options or answer text
            - 'explanation' (str | None)
            - 'extended_explanation' (dict | None)
            - 'concept' (str | None)
            - 'topic' (str | None)
            - 'weight' (int | float | None)
            - 'cognitive_level' (str | None)
            """
            if not isinstance(q, dict):
                return q

            # text / question
            if 'text' not in q:
                if 'question' in q:
                    q['text'] = q.get('question')
                elif 'frage' in q:
                    q['text'] = q.get('frage')

            # options (ensure list)
            opts = None
            for k in ('options', 'optionen', 'answers'):
                if k in q and q.get(k) is not None:
                    opts = q.get(k)
                    break
            # If options are dict-like (e.g., {'A': '...', 'B': '...'}), convert to list
            if isinstance(opts, dict):
                # preserve natural sorted order by key if keys like 'A','B',... exist
                try:
                    ordered = [opts[k] for k in sorted(opts.keys())]
                except Exception:
                    ordered = list(opts.values())
                q['options'] = ordered
            elif isinstance(opts, list):
                q['options'] = opts
            elif opts is None:
                q.setdefault('options', [])

            # answer / loesung
            if 'answer' not in q:
                if 'loesung' in q:
                    q['answer'] = q.get('loesung')
                elif 'antwort' in q:
                    q['answer'] = q.get('antwort')

            # explanation variants
            if 'explanation' not in q:
                for k in ('erklaerung', 'erklaerung_html'):
                    if k in q:
                        q['explanation'] = q.get(k)
                        break

            # extended explanation
            if 'extended_explanation' not in q and 'extended_explanation' in q:
                q['extended_explanation'] = q.get('extended_explanation')

            # concept / konzept
            if 'concept' not in q:
                if 'konzept' in q:
                    q['concept'] = q.get('konzept')

            # topic / thema
            if 'topic' not in q:
                if 'topic' in q:
                    pass
                elif 'thema' in q:
                    q['topic'] = q.get('thema')

            # weight / gewichtung
            if 'weight' not in q:
                if 'weight' in q:
                    pass
                elif 'gewichtung' in q:
                    q['weight'] = q.get('gewichtung')

            # cognitive level variants
            if 'cognitive_level' not in q:
                for k in ('kognitive_stufe', 'cognitive_level', 'cognitiveLevel'):
                    if k in q:
                        q['cognitive_level'] = q.get(k)
                        break

            return q

        # Apply normalization once (in-place) to all questions so downstream code
        # can depend on canonical keys and avoid scattered defensive lookups.
        try:
            for idx, q in enumerate(questions):
                questions[idx] = normalize_question_schema(q or {})
        except Exception:
            # If something unexpected happens, continue — later code is defensive too.
            pass

        duration = e_dt - s_dt
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        duration_parts = []
        if minutes:
            duration_parts.append(f"{minutes} min")
        if seconds or not duration_parts:
            duration_parts.append(f"{seconds} s")
        duration_str = " ".join(duration_parts)
    
    # QR-Code generieren (Link zum Test)
    # URL kann über Umgebungsvariable APP_URL konfiguriert werden
    import os
    base_url = os.getenv("APP_URL", "https://mc-test-amalea.streamlit.app")
    test_url = f"{base_url}/?test={q_file}"
    qr_code_data = _generate_qr_code(test_url) if QR_AVAILABLE else ""
    qr_html = f'<img src="{qr_code_data}" alt="QR-Code">' if qr_code_data else ""
    
    # Top 3 schwächste Themen analysieren
    weak_topics = _analyze_weak_topics(questions)
    weak_topics_html = ""
    if weak_topics:
        weak_topics_html = '<div class="weak-topics">'
        weak_topics_html += f'<h3>{_html.escape(translate_ui("pdf.weak_topics.title", default="Verbesserungspotenzial"))}</h3>'
        weak_topics_html += '<ul>'
        for topic, question_numbers in weak_topics:
            # Format question numbers (e.g. single or list)
            if len(question_numbers) == 1:
                fragen_text = translate_ui("pdf.question_short", default="Frage {n}").format(n=question_numbers[0])
            else:
                numbers_list = ', '.join(map(str, question_numbers))
                fragen_text = translate_ui("pdf.weak_topics.multiple", default="Fragen {list}").format(list=numbers_list)
            weak_topics_html += f'<li><strong>{_html.escape(topic)}</strong><br><span class="question-refs">{_html.escape(fragen_text)}</span></li>'
        weak_topics_html += '</ul></div>'
    
    # Hole initial_indices für Lesezeichen
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    
    # NEU: Hole die Liste der markierten Fragen-Indizes
    bookmarked_indices = st.session_state.get("bookmarked_questions", [])
    # Tempo metadata for header (best-effort: prefer session-state selection)
    try:
        tempo_code = st.session_state.get('selected_tempo') or st.session_state.get('tempo') or None
    except Exception:
        tempo_code = None

    # If the session doesn't contain a tempo selection, try to read it from
    # the question set metadata (some workflows persist the chosen tempo there).
    try:
        if not tempo_code and 'question_set' in locals() and question_set and getattr(question_set, 'meta', None):
            meta = question_set.meta
            tempo_code = meta.get('tempo') or meta.get('selected_tempo') or tempo_code
    except Exception:
        # ignore and keep existing tempo_code
        pass

    tempo_span = ''
    if tempo_code:
        try:
            tempo_display = translate_ui(f"tempo.{tempo_code}", default='')
            if not tempo_display:
                # Fallback to the raw code when no translation exists
                tempo_display = tempo_code
        except Exception:
            tempo_display = tempo_code
        try:
            tempo_span = f'<span><strong>{translate_ui("pdf.meta.tempo", default="Tempo:")}</strong> {_html.escape(str(tempo_display))}</span>'
        except Exception:
            tempo_span = f'<span><strong>Tempo:</strong> {_html.escape(str(tempo_display))}</span>'

    # Build duration HTML fragment; include tempo label and allowed minutes when applicable
    duration_html = ''
    if duration_str:
        try:
            # Determine allowed minutes with cooldowns (prefer live session data)
            session_limit_minutes = None
            try:
                ttl_seconds = st.session_state.get("test_time_limit")
                if ttl_seconds:
                    session_limit_minutes = max(1, int(round(float(ttl_seconds) / 60.0)))
            except Exception:
                session_limit_minutes = None
            if session_limit_minutes is None:
                try:
                    sess_duration_min = st.session_state.get("test_duration_minutes")
                    if sess_duration_min is not None:
                        session_limit_minutes = max(1, int(round(float(sess_duration_min))))
                except Exception:
                    pass

            sess_effective = None
            sess_allowed_min = None
            try:
                sess_effective = st.session_state.get('effective_allowed')
            except Exception:
                sess_effective = None
            try:
                sess_allowed_min = st.session_state.get('allowed_min')
            except Exception:
                sess_allowed_min = None

            # If the session state didn't include persisted values, try to
            # load them from the `test_session_summaries` snapshot in the DB.
            if (sess_effective is None or sess_allowed_min is None) or tempo_code is None:
                try:
                    from database import get_db_connection
                    conn = get_db_connection()
                    if conn is not None:
                        cur = conn.cursor()
                        # Prefer explicit session_id in session_state
                        sess_id = None
                        try:
                            sess_id = st.session_state.get('session_id')
                        except Exception:
                            sess_id = None

                        row = None
                        if sess_id:
                            cur.execute("SELECT allowed_min, effective_allowed, tempo FROM test_session_summaries WHERE session_id = ?", (int(sess_id),))
                            row = cur.fetchone()

                        # Fallback: try to match by pseudonym + start_time
                        if row is None:
                            try:
                                pseud = st.session_state.get('user_pseudonym') or st.session_state.get('user_id')
                                start_t = st.session_state.get('test_start_time')
                            except Exception:
                                pseud = None
                                start_t = None
                            if pseud and start_t:
                                # match approximate ISO prefix to be robust
                                start_prefix = str(start_t)[:19]
                                cur.execute("SELECT allowed_min, effective_allowed, tempo FROM test_session_summaries WHERE user_pseudonym = ? AND start_time LIKE ? ORDER BY start_time DESC LIMIT 1", (pseud, f'{start_prefix}%'))
                                row = cur.fetchone()

                        if row:
                            try:
                                if sess_allowed_min is None and row['allowed_min'] is not None:
                                    sess_allowed_min = int(row['allowed_min'])
                            except Exception:
                                pass
                            try:
                                if sess_effective is None and row['effective_allowed'] is not None and str(row['effective_allowed']).strip():
                                    sess_effective = int(row['effective_allowed'])
                            except Exception:
                                pass
                            try:
                                # If we didn't have a tempo_code from session_state,
                                # prefer the stored tempo from the snapshot.
                                if not tempo_code and row['tempo']:
                                    tempo_code = row['tempo']
                            except Exception:
                                pass
                except Exception:
                    # ignore DB lookup failures (best-effort)
                    pass

            question_set_obj = question_set if 'question_set' in locals() else None
            cooldown_total_minutes = _cooldown_adjusted_total_minutes(questions, app_config, question_set_obj)

            # Base allowed_min: prefer cooldown-aware computation, then snapshot/session value, then question_set, then app_config
            if cooldown_total_minutes is not None:
                allowed_min = int(max(1, round(cooldown_total_minutes)))
            elif sess_allowed_min is not None:
                allowed_min = sess_allowed_min
            else:
                try:
                    if question_set_obj:
                        allowed_min = question_set_obj.get_test_duration_minutes(app_config.test_duration_minutes)
                    else:
                        allowed_min = getattr(app_config, "test_duration_minutes", None)
                except Exception:
                    allowed_min = getattr(app_config, "test_duration_minutes", None)

            tempo_factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}
            factor = tempo_factor_map.get(tempo_code or 'normal', 1.0)

            # If an explicit effective value was stored for the session, use it as display_allowed
            display_allowed = None
            if session_limit_minutes is not None:
                display_allowed = session_limit_minutes
            elif cooldown_total_minutes is not None:
                display_allowed = int(max(1, round(cooldown_total_minutes * factor)))
            elif sess_effective is not None:
                try:
                    display_allowed = int(sess_effective)
                except Exception:
                    display_allowed = sess_effective
            elif allowed_min is not None:
                try:
                    display_allowed = int(max(1, round(float(allowed_min) * factor)))
                except Exception:
                    display_allowed = allowed_min

            duration_html = f'<span><strong>{translate_ui("pdf.meta.duration", default="Dauer:")}</strong> {duration_str}'

            # Prepare tempo label for display (prefer explicit session selection if available)
            tempo_label = None
            try:
                sess_sel_tempo = None
                try:
                    sess_sel_tempo = st.session_state.get('selected_tempo') or st.session_state.get('selected_tempo_session') or st.session_state.get('tempo')
                except Exception:
                    sess_sel_tempo = None

                use_tempo_code = sess_sel_tempo or tempo_code
                if use_tempo_code and use_tempo_code != 'normal':
                    try:
                        tempo_label = translate_ui(f"tempo.{use_tempo_code}", default=use_tempo_code.title())
                    except Exception:
                        tempo_label = use_tempo_code
            except Exception:
                tempo_label = tempo_code

            # Append allowed minutes and tempo info in parentheses when available
            if display_allowed is not None:
                # If we already rendered a dedicated tempo span (`tempo_span`),
                # avoid repeating the tempo label inside the parenthesized
                # allowed-time fragment to prevent redundancy.
                if tempo_label and (not tempo_span or not tempo_span.strip()):
                    duration_html += f' ({translate_ui("pdf.meta.allowed", default="erlaubt:")} {display_allowed} min, {translate_ui("pdf.meta.tempo", default="Tempo:")} {_html.escape(str(tempo_label))})'
                else:
                    duration_html += f' ({translate_ui("pdf.meta.allowed", default="erlaubt:")} {display_allowed} min)'
            else:
                # fallback: if no allowed info but tempo label exists, append tempo only
                if tempo_label:
                    duration_html += f', {translate_ui("pdf.meta.tempo", default="Tempo:")} {_html.escape(str(tempo_label))}'

            duration_html += '</span>'
        except Exception:
            duration_html = f'<span><strong>{translate_ui("pdf.meta.duration", default="Dauer:")}</strong> {duration_str}</span>'

    # Durchschnittsvergleich berechnen
    avg_stats = _calculate_average_stats(q_file, questions)
    
    # Schwierigkeits-Analyse erstellen
    difficulty_stats = {
        "easy": {"richtig": 0, "gesamt": 0},
        "medium": {"richtig": 0, "gesamt": 0},
        "hard": {"richtig": 0, "gesamt": 0},
    }
    
    for i, frage in enumerate(questions):
        gewichtung = frage.get("gewichtung", 1)
        gegebene_antwort = get_answer_for_question(i)

        # Defensive resolution of the correct answer similar to _analyze_weak_topics
        options = _get_options(frage)
        richtige_antwort = None
        if "loesung" in frage:
            try:
                idx = int(frage.get("loesung"))
            except Exception:
                idx = None
            if idx is not None and isinstance(options, list) and 0 <= idx < len(options):
                richtige_antwort = options[idx]

        if richtige_antwort is None and "answer" in frage:
            val = frage.get("answer")
            try:
                idx2 = int(val)
            except Exception:
                idx2 = None
            if idx2 is not None and isinstance(options, list) and 0 <= idx2 < len(options):
                richtige_antwort = options[idx2]
            elif isinstance(val, str) and isinstance(options, list):
                for opt in options:
                    try:
                        if isinstance(opt, str) and opt.strip() == val.strip():
                            richtige_antwort = opt
                            break
                    except Exception:
                        continue

        if richtige_antwort is None:
            loes = frage.get("loesung")
            if isinstance(loes, str) and loes.strip():
                richtige_antwort = loes

        ist_richtig = (gegebene_antwort == richtige_antwort)
        
        if gewichtung == 1:
            difficulty_stats["easy"]["gesamt"] += 1
            if ist_richtig:
                difficulty_stats["easy"]["richtig"] += 1
        elif gewichtung == 2:
            difficulty_stats["medium"]["gesamt"] += 1
            if ist_richtig:
                difficulty_stats["medium"]["richtig"] += 1
        else:  # >= 3
            difficulty_stats["hard"]["gesamt"] += 1
            if ist_richtig:
                difficulty_stats["hard"]["richtig"] += 1
    
    stage_stats: Dict[str, Dict[str, int]] = {}
    for i, frage in enumerate(questions):
        raw_stage = frage.get("kognitive_stufe")
        stage = _normalize_stage_label(raw_stage)
        if not stage:
            continue
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort = _resolve_correct_answer(frage)
        ist_richtig = (gegebene_antwort == richtige_antwort)

        if stage not in stage_stats:
            stage_stats[stage] = {"gesamt": 0, "richtig": 0}
        stage_stats[stage]["gesamt"] += 1
        if ist_richtig:
            stage_stats[stage]["richtig"] += 1
    
    # HTML für Schwierigkeits-Übersicht (sichtbare Labels als kognitive Stufen)
    difficulty_rows = []
    # Verwende kanonische Stage-Bezeichnungen kombiniert mit lokalisierten Namen
    canonical_english = {'reproduction': 'Reproduction', 'application': 'Application', 'analysis': 'Analysis'}
    canonical_to_i18n = {'reproduction': 'Reproduktion', 'application': 'Anwendung', 'analysis': 'Analyse'}

    if difficulty_stats["easy"]["gesamt"] > 0:
        easy_percent = (difficulty_stats["easy"]["richtig"] / difficulty_stats["easy"]["gesamt"] * 100)
        canon = 'reproduction'
        i18n_key = canonical_to_i18n.get(canon, canon)
        localized_stage = translate_ui(f"pdf.stage_name.{i18n_key}", default=canonical_english.get(canon, i18n_key))
        label = localized_stage
        difficulty_rows.append((
            label,
            f'{difficulty_stats["easy"]["richtig"]}/{difficulty_stats["easy"]["gesamt"]}',
            easy_percent,
        ))
    if difficulty_stats["medium"]["gesamt"] > 0:
        medium_percent = (difficulty_stats["medium"]["richtig"] / difficulty_stats["medium"]["gesamt"] * 100)
        canon = 'application'
        i18n_key = canonical_to_i18n.get(canon, canon)
        localized_stage = translate_ui(f"pdf.stage_name.{i18n_key}", default=canonical_english.get(canon, i18n_key))
        label = f"{canonical_english.get(canon)} / {localized_stage}"
        difficulty_rows.append((
            label,
            f'{difficulty_stats["medium"]["richtig"]}/{difficulty_stats["medium"]["gesamt"]}',
            medium_percent,
        ))
    if difficulty_stats["hard"]["gesamt"] > 0:
        hard_percent = (difficulty_stats["hard"]["richtig"] / difficulty_stats["hard"]["gesamt"] * 100)
        canon = 'analysis'
        i18n_key = canonical_to_i18n.get(canon, canon)
        localized_stage = translate_ui(f"pdf.stage_name.{i18n_key}", default=canonical_english.get(canon, i18n_key))
        label = f"{canonical_english.get(canon)} / {localized_stage}"
        difficulty_rows.append((
            label,
            f'{difficulty_stats["hard"]["richtig"]}/{difficulty_stats["hard"]["gesamt"]}',
            hard_percent,
        ))

    # The per-difficulty summary table was intentionally removed from the
    # test report PDF. Keep `difficulty_rows` available for other comparisons
    # (if needed) but do not render a dedicated difficulty HTML block here.
    difficulty_html = ""

    stage_rows = []
    ordered_stages = [stage for stage in BLOOM_STAGE_ORDER if stage in stage_stats]
    ordered_stages.extend([stage for stage in stage_stats if stage not in ordered_stages])
    for stage in ordered_stages:
        stats = stage_stats[stage]
        gesamt = stats["gesamt"]
        if gesamt <= 0:
            continue
        richtig = stats["richtig"]
        percent = (richtig / gesamt * 100) if gesamt > 0 else 0
        stage_rows.append((stage, f'{richtig}/{gesamt}', percent))

    stage_html = ""
    if stage_rows:
        stage_html = '<div class="difficulty-analysis">'
        stage_html += f'<h3>{translate_ui("pdf.stage_section_title", default="Performance nach kognitiver Stufe")}</h3>'

        # Prepare radar image (SVG data URI) and embed above the table
        try:
            labels = [translate_ui(f"pdf.stage_name.{label}", default=label) for label, _, _ in stage_rows]
            values = [float(percent_value) for _, _, percent_value in stage_rows]
            radar_uri = _render_radar_svg(labels, values, size=360)
            if radar_uri:
                stage_html += '<div class="radar-figure" style="margin-bottom:12px; text-align:center;">'
                stage_html += f'<img src="{radar_uri}" alt="radar" style="max-width:360px; width:100%; height:auto;"/>'
                stage_html += '</div>'
                
                # Add radar chart explanation with pattern interpretations (localized)
                # Use a shorter PDF-specific key to avoid overwhelming the report
                radar_explanation = translate_ui(
                    "pdf.cognition_radar.explanation_short",
                    default=(
                        "Das Radar zeigt den Anteil korrekt erzielter Punkte pro kognitiver Stufe (Bloom).\n\n"
                        "Typische Muster:\n"
                        "• Bulimie-Lernen (Spitze bei Reproduktion): Starkes Auswendiglernen → Mehr Anwendungsaufgaben üben.\n"
                        "• Oberflächenprofil (nur Reproduktion hoch): Konzepte bekannt, Anwendung fehlt → Fallbeispiele einbauen.\n"
                        "• Anwendungsfokus (Anwendung hoch): Gute Praxis, Faktenwissen lückenhaft → Grundlagen auffrischen.\n"
                        "• Analysestärke (Analyse hoch): Starke Problemlösung, Basislücken → Grundlagen wiederholen.\n"
                        "• Ausgewogen (rundes Polygon): Solide Kompetenz → Weiter so!\n"
                        "• Zickzack-Profil (unregelmäßig): Inkonsistente Strategie → Gezielt Lücken schließen."
                    ),
                )
                # Convert markdown-style text to proper HTML
                radar_explanation_html = _markdown_to_html(radar_explanation)
                stage_html += '<div class="radar-explanation" style="margin-top:8px; margin-bottom:40px !important; padding-bottom:16px; font-size:0.85em; color:#555; text-align:left; border-bottom:1px solid #e0e0e0;">'
                stage_html += radar_explanation_html
                stage_html += '</div>'
                # Add spacer between explanation and table
                stage_html += '<div style="height:20px;"></div>'
        except Exception:
            # Non-fatal: if radar generation fails, continue without it
            pass

        stage_html += '<table class="difficulty-table" style="margin-top:16px;">'
        stage_html += (
            '<thead><tr>'
            f'<th>{translate_ui("pdf.stage_table.header.stage", default="Stufe")}</th>'
            f'<th>{translate_ui("pdf.stage_table.header.hits", default="Treffer")}</th>'
            f'<th>{translate_ui("pdf.stage_table.header.quota", default="Quote")}</th>'
            '</tr></thead>'
        )
        stage_html += '<tbody>'
        for label, ratio_text, percent_value in stage_rows:
            translated_label = translate_ui(f"pdf.stage_name.{label}", default=label)
            percent_str = format_decimal_locale(percent_value, 0)
            stage_html += (
                f'<tr>'
                f'<th scope="row">{_html.escape(translated_label)}</th>'
                f'<td>{ratio_text}</td>'
                f'<td class="quota-cell">{percent_str} %</td>'
                f'</tr>'
            )
        stage_html += '</tbody></table></div>'

    # Comparison with averages
    comparison_html = ""
    if avg_stats and avg_stats['total_users'] > 1:  # at least 2 users inclusive
        def _diff_meta(value: float) -> tuple[str, str, str]:
            if value > 0:
                return "diff-positive", "↑", translate_ui("pdf.comparison.above", default="über Durchschnitt")
            if value < 0:
                return "diff-negative", "↓", translate_ui("pdf.comparison.below", default="unter Durchschnitt")
            return "diff-neutral", "=", translate_ui("pdf.comparison.neutral", default="auf Durchschnittsniveau")

        comparison_html = '<div class="comparison-box">'
        comparison_html += f'<h3>{translate_ui("pdf.comparison.title", default="Vergleich mit Durchschnitt")}</h3>'

        diff_value = prozent - avg_stats['avg_percent']
        diff_class, diff_symbol, diff_phrase = _diff_meta(diff_value)
        comparison_html += '<table class="comparison-table">'
        comparison_html += (
            '<thead><tr>'
            f'<th>{translate_ui("pdf.comparison.table.header.level", default="Ebene")}</th>'
            f'<th>{translate_ui("pdf.comparison.table.header.you", default="Du")}</th>'
            f'<th>{translate_ui("pdf.comparison.table.header.avg", default="Ø")}</th>'
            f'<th>{translate_ui("pdf.comparison.table.header.diff", default="Abweichung")}</th>'
            '</tr></thead>'
        )
        comparison_html += '<tbody>'
        diff_value_str = format_decimal_locale(abs(diff_value), 1)
        prozent_str = format_decimal_locale(prozent, 0)
        avg_percent_str = format_decimal_locale(avg_stats["avg_percent"], 0)
        comparison_html += (
            f'<tr>'
            f'<th scope="row">{translate_ui("pdf.comparison.row.overall", default="Gesamtergebnis")}</th>'
            f'<td>{prozent_str} %</td>'
            f'<td>{avg_percent_str} %</td>'
            f'<td class="diff-cell {diff_class}">{diff_symbol} {diff_value_str} % {diff_phrase}</td>'
            f'</tr>'
        )
        comparison_html += '</tbody></table>'

        if avg_stats['avg_difficulty']:
            difficulty_comparison_rows = []
            if difficulty_stats["easy"]["gesamt"] > 0 and avg_stats['avg_difficulty']['easy'] > 0:
                easy_percent = (difficulty_stats["easy"]["richtig"] / difficulty_stats["easy"]["gesamt"] * 100)
                easy_diff = easy_percent - avg_stats['avg_difficulty']['easy']
                # Use canonical cognitive stage labels instead of star badges
                canon = 'reproduction'
                canonical_english = {'reproduction': 'Reproduction', 'application': 'Application', 'analysis': 'Analysis'}
                canonical_to_i18n = {'reproduction': 'Reproduktion', 'application': 'Anwendung', 'analysis': 'Analyse'}
                i18n_key = canonical_to_i18n.get(canon, canon)
                localized_stage = translate_ui(f"pdf.stage_name.{i18n_key}", default=canonical_english.get(canon, i18n_key))
                label = localized_stage
                difficulty_comparison_rows.append((
                    label,
                    easy_percent,
                    avg_stats["avg_difficulty"]["easy"],
                    easy_diff,
                ))
            if difficulty_stats["medium"]["gesamt"] > 0 and avg_stats['avg_difficulty']['medium'] > 0:
                medium_percent = (difficulty_stats["medium"]["richtig"] / difficulty_stats["medium"]["gesamt"] * 100)
                medium_diff = medium_percent - avg_stats['avg_difficulty']['medium']
                canon = 'application'
                canonical_english = {'reproduction': 'Reproduction', 'application': 'Application', 'analysis': 'Analysis'}
                canonical_to_i18n = {'reproduction': 'Reproduktion', 'application': 'Anwendung', 'analysis': 'Analyse'}
                i18n_key = canonical_to_i18n.get(canon, canon)
                localized_stage = translate_ui(f"pdf.stage_name.{i18n_key}", default=canonical_english.get(canon, i18n_key))
                label = localized_stage
                difficulty_comparison_rows.append((
                    label,
                    medium_percent,
                    avg_stats["avg_difficulty"]["medium"],
                    medium_diff,
                ))
            if difficulty_stats["hard"]["gesamt"] > 0 and avg_stats['avg_difficulty']['hard'] > 0:
                hard_percent = (difficulty_stats["hard"]["richtig"] / difficulty_stats["hard"]["gesamt"] * 100)
                hard_diff = hard_percent - avg_stats['avg_difficulty']['hard']
                canon = 'analysis'
                canonical_english = {'reproduction': 'Reproduction', 'application': 'Application', 'analysis': 'Analysis'}
                canonical_to_i18n = {'reproduction': 'Reproduktion', 'application': 'Anwendung', 'analysis': 'Analyse'}
                i18n_key = canonical_to_i18n.get(canon, canon)
                localized_stage = translate_ui(f"pdf.stage_name.{i18n_key}", default=canonical_english.get(canon, i18n_key))
                label = localized_stage
                difficulty_comparison_rows.append((
                    label,
                    hard_percent,
                    avg_stats["avg_difficulty"]["hard"],
                    hard_diff,
                ))

            if difficulty_comparison_rows:
                comparison_html += '<table class="comparison-table comparison-difficulty-table">'
                comparison_html += f'<caption class="comparison-subtitle">{translate_ui("pdf.comparison.by_stage", default="Nach kognitiver Stufe")}</caption>'
                comparison_html += ('<thead><tr>'
                                     f'<th>{translate_ui("pdf.stage_table.header.stage", default="Kognitive Stufe")}</th>'
                                     f'<th>{translate_ui("pdf.comparison.table.header.you", default="Du")}</th>'
                                     f'<th>{translate_ui("pdf.comparison.table.header.avg", default="Ø")}</th>'
                                     f'<th>{translate_ui("pdf.comparison.table.header.diff", default="Abweichung")}</th>'
                                     '</tr></thead>')
                comparison_html += '<tbody>'
                for label, user_percent, avg_percent, diff in difficulty_comparison_rows:
                    diff_class, diff_symbol, diff_phrase = _diff_meta(diff)
                    diff_str = format_decimal_locale(abs(diff), 1)
                    user_percent_str = format_decimal_locale(user_percent, 0)
                    avg_percent_str = format_decimal_locale(avg_percent, 0)
                    comparison_html += (
                        f'<tr>'
                        f'<th scope="row">{label}</th>'
                        f'<td>{user_percent_str} %</td>'
                        f'<td>{avg_percent_str} %</td>'
                        f'<td class="diff-cell {diff_class}">{diff_symbol} {diff_str} % {diff_phrase}</td>'
                        f'</tr>'
                    )
                comparison_html += '</tbody></table>'

        footer_text = translate_ui("pdf.comparison.footer", default="Based on {n} participants. Comparison data as of: {date}.")
        comparison_html += f'<p class="comparison-footer">{_html.escape(footer_text.format(n=avg_stats["total_users"], date=generated_at_str))}</p>'
        comparison_html += '</div>'
        # Only show the detailed-analysis heading when the comparison_html exists
        detailed_heading = f'<h2 class="section-title">{_html.escape(translate_ui("pdf.detailed_analysis", default="Detaillierte Auswertung"))}</h2>'
    
    # Mini-Glossar erstellen (nach Themen gruppiert)
    glossary_by_theme = _extract_glossary_terms(questions)
    glossary_html = _build_glossary_html(glossary_by_theme)
    
    # Lesezeichen-Übersicht erstellen
    bookmarked_indices = st.session_state.get("bookmarked_questions", [])
    bookmarks_html = ""
    if bookmarked_indices:
        bookmarks_html = '<div class="bookmarks-overview">'
        bookmarks_html += f'<h3>{translate_ui("pdf.bookmarks_title", default="Markierte Fragen")}</h3>'
        bookmarks_html += '<p class="bookmark-intro">'
        bookmarks_intro = translate_ui("pdf.bookmarks_intro", default="Du hast folgende Fragen zur Wiederholung markiert:")
        bookmarks_html += bookmarks_intro
        bookmarks_html += '</p>'
        bookmarks_html += '<ul class="bookmark-list">'
        
        for idx in bookmarked_indices:
            if idx < len(questions):
                # Finde die Test-Nummer für diese Frage
                if idx in initial_indices:
                    test_num = initial_indices.index(idx) + 1
                else:
                    test_num = idx + 1
                # Original-Nummer
                try:
                    orig_num = int((questions[idx].get("question", questions[idx].get("frage", ""))).split(".", 1)[0])
                except (ValueError, IndexError):
                    orig_num = idx + 1
                # Kurzer Fragen-Preview
                frage_text = questions[idx].get("question", questions[idx].get("frage", ""))
                frage_preview = frage_text.split(".", 1)[-1].strip()
                if len(frage_preview) > 60:
                    frage_preview = frage_preview[:60] + "..."

                # Parse Markdown und LaTeX im Preview
                frage_preview_parsed = _render_latex_in_html(smart_quotes_de(frage_preview), md_inline=True)

                q_short = translate_ui("pdf.question_short", default="Frage {n}").format(n=test_num)
                bookmarks_html += f'<li><strong>{_html.escape(q_short)}</strong> '
                bookmarks_html += '<span class="bookmark-ref">'
                qset_ref = translate_ui("pdf.questionset_number", default="(Fragenset-Nr. {n})").format(n=orig_num)
                bookmarks_html += f'{_html.escape(qset_ref)}</span><br>'
                bookmarks_html += '<span class="bookmark-preview">'
                bookmarks_html += f'{frage_preview_parsed}</span></li>'
        
        bookmarks_html += '</ul></div>'

    # Prepare topic performance chart for PDF (stacked: correct + wrong)
    try:
        # Aggregate correct/wrong/total per Thema similar to main UI
        tp = {}
        for idx, frage in enumerate(questions):
            thema = frage.get("thema", "Allgemein")
            if thema not in tp:
                tp[thema] = {"correct": 0, "wrong": 0, "answered": 0, "total": 0}
            # count total questions per topic
            tp[thema]["total"] += 1
            given = get_answer_for_question(idx)
            if given is None:
                # unanswered: don't increment answered count
                continue
            # count answered
            tp[thema]["answered"] += 1
            # Compare to solution text where possible
            try:
                loes_text = _resolve_correct_answer(frage)
                if loes_text is not None and given == loes_text:
                    tp[thema]["correct"] += 1
                else:
                    tp[thema]["wrong"] += 1
            except Exception:
                # Fallback: treat non-matching as wrong
                try:
                    if given:
                        tp[thema]["wrong"] += 1
                except Exception:
                    pass

        themes = []
        pct_correct = []
        pct_wrong = []
        pct_unanswered = []
        for thema, vals in tp.items():
            total_cnt = vals.get("total", 0) or 0
            if total_cnt <= 0:
                continue
            themes.append(thema)
            correct = vals.get("correct", 0)
            wrong = vals.get("wrong", 0)
            answered_cnt = vals.get("answered", 0) or 0
            pct_correct.append((correct / total_cnt) * 100.0)
            pct_wrong.append((wrong / total_cnt) * 100.0)
            pct_unanswered.append(((total_cnt - answered_cnt) / total_cnt) * 100.0)

        # Render a taller chart for PDF so labels and bars have more space
        topic_chart_svg = _render_topic_stacked_bar_svg(themes, pct_correct, pct_wrong, pct_unanswered, width=700, height=360) if themes else ""
        if topic_chart_svg:
            # Build legend and explanation for the chart (static in PDF)
            legend_items = [
                ("#15803d", translate_ui('performance_chart.legend.correct', default='Richtig')),
                ("#b91c1c", translate_ui('performance_chart.legend.wrong', default='Falsch')),
                ("#9ca3af", translate_ui('performance_chart.legend.unanswered', default='Unbeantwortet')),
            ]
            legend_html_parts = ['<div class="topic-legend">']
            for color, label in legend_items:
                legend_html_parts.append(
                    f'<div class="legend-item"><span class="legend-swatch" style="background:{color}"></span> <span class="legend-label">{_html.escape(label)}</span></div>'
                )
            legend_html_parts.append('</div>')
            legend_html = ''.join(legend_html_parts)

            # small caption explaining the metric
            caption = _html.escape(translate_ui("pdf.topic_chart.caption", default="Anteil pro Thema (100 % = alle Fragen des Themas)"))

            topics_chart_html = (
                f'<div class="topic-chart">'
                f'<h3>{_html.escape(translate_ui("pdf.topic_chart.title", default="Leistung nach Thema"))}</h3>'
                f'{legend_html}'
                f'<div class="topic-chart-caption">{caption}</div>'
                f'<img src="{topic_chart_svg}" alt="Themenperformance"/>'
                '</div>'
            )
        else:
            topics_chart_html = ''
    except Exception:
        topics_chart_html = ''

    # Baue den HTML-Body mit professionellem Header
    score_percent_str = format_decimal_locale(prozent, 1)
    
    rank_html = ''
    if user_rank:
        rank_label = translate_ui('pdf.rank_label', default='Ranking (Stand: {date})').format(date=generated_at_str.split(' ')[0])
        rank_html = f'<div class="stat-item"><div class="stat-value rank">#{user_rank}</div><div class="stat-label">{_html.escape(rank_label)}</div></div>'
    score_label = translate_ui('pdf.score_label', default='von {n} Punkten').format(n=max_score)

    # Detailed heading will be shown only if comparison_html (details) is present.
    # Initialize to empty; will be set after comparison_html is constructed.
    detailed_heading = ''

    html_body = f'''
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <h1>{_html.escape(header_title)}</h1>{header_subtitle}
                    <div class="meta-info">
                        <span><strong>{translate_ui('pdf.meta.participant', default='Teilnehmer:')}</strong> {user_name}</span>
                        <span><strong>{translate_ui('pdf.meta.test_date', default='Testdatum:')}</strong> {generated_at_str}</span>
                        {tempo_span}
                        {duration_html if duration_str else ''}
                    </div>
                </div>
                <div class="header-right">
                    {qr_html}
                </div>
            </div>
        </div>
        
        <div class="summary-box">
            <div class="score-main">
                <div class="score-number">{current_score}</div>
                <div class="score-label">{_html.escape(score_label)}</div>
                <div class="score-percent">{score_percent_str} %</div>
            </div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value correct">✓ {richtige}</div>
                    <div class="stat-label">{translate_ui('pdf.stat.correct', default='Richtig')}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value wrong">✗ {falsche}</div>
                    <div class="stat-label">{translate_ui('pdf.stat.wrong', default='Falsch')}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value unanswered">? {unbeantwortet}</div>
                    <div class="stat-label">{translate_ui('pdf.stat.unanswered', default='Unbeantwortet')}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(questions)}</div>
                    <div class="stat-label">{translate_ui('pdf.stat.total', default='Gesamt')}</div>
                </div>
                {rank_html}
            </div>
        </div>

        {confidence_html}
        
        {topics_chart_html}
        {weak_topics_html}
        
        {difficulty_html}
        
        {stage_html}
        
        {detailed_heading}
        
        {comparison_html}
        
        {bookmarks_html}
    '''
    
    sorted_questions = _prepare_stage_sorted_questions(questions)

    for display_test_number, (_, stage_label, original_index, frage_obj) in enumerate(sorted_questions, start=1):
        # display_test_number zählt schon ab 1
        
        # Original-Nummer (aus dem Fragentext)
        try:
            original_number = int((frage_obj.get("question", frage_obj.get("frage", ""))).split(".", 1)[0])
        except (ValueError, IndexError):
            original_number = original_index + 1
        
        frage_text = _render_latex_in_html(smart_quotes_de((frage_obj.get("question", frage_obj.get("frage", ""))).split(". ", 1)[-1]))
        
        # Bestimme Farbe und Status basierend auf richtig/falsch/unbeantwortet
        gegebene_antwort = get_answer_for_question(original_index)
        richtige_antwort_text = _resolve_correct_answer(frage_obj)
        
        is_unanswered = gegebene_antwort is None
        ist_richtig = not is_unanswered and (gegebene_antwort == richtige_antwort_text)
        
        status_text = ""
        status_icon = ""
        status_class = ""
        # Ensure unanswered is handled exclusively and not overwritten by the
        # 'wrong' branch: use if/elif/else so only one branch applies.
        if is_unanswered:
            border_color = "#0284c7"  # Blau für unbeantwortet
            status_text = translate_ui("pdf.status.unanswered", default="Unbeantwortet")
            status_icon = "?"
            status_class = "unanswered"
        elif ist_richtig:
            border_color = "#15803d"  # Dunkelgrün
            status_text = translate_ui("pdf.status.correct", default="Richtig")
            status_icon = "✔"
            status_class = "correct"
        else:
            border_color = "#b91c1c"  # Dunkelrot
            status_text = translate_ui("pdf.status.wrong", default="Falsch")
            status_icon = "✗"
            status_class = "wrong"
        
        # NEU: Prüfen, ob die Frage markiert ist und Icon hinzufügen
        is_bookmarked = original_index in bookmarked_indices
        bookmark_icon_html = '<span class="bookmark-icon">🔖</span>' if is_bookmarked else ''
        
        # Schwierigkeits-Badge basierend auf Gewichtung
        # Note: we intentionally do not render a visual ★-badge in the per-question
        # header of the test report PDF. The cognitive stage is shown separately
        # (see `stage_label` below) and numeric weight should not be emphasised
        # as a star-badge in exported PDFs.
        gewichtung = frage_obj.get("gewichtung", 1)
        
        # Hole Thema
        thema = frage_obj.get("thema", "")
        
        # Starte Question-Box mit farbigem Rahmen
        # Page-breaks between question boxes are controlled by CSS
        # (use .question-box + .question-box). Remove the decorative
        # separator here to avoid orphaned divider lines at the end
        # of questions when explanations fall at a page boundary.
        html_body += f'<div class="question-box" style="border-left: 4px solid {border_color};">'
        
        # Status-Anzeige (Richtig, Falsch, Unbeantwortet)
        html_body += f'<div class="question-status {status_class}"><span class="status-icon">{status_icon}</span> {status_text}</div>'
        
        html_body += '<div class="question-header">'
        raw_stage_value = frage_obj.get("kognitive_stufe")
        has_stage_label = bool(raw_stage_value and str(raw_stage_value).strip())
        header_label = translate_ui("pdf.question_header", default="Frage {current} / {total}").format(current=display_test_number, total=len(questions))
        html_body += header_label + ' '
        qset_label = _html.escape(translate_ui("pdf.questionset_number", default="(Fragenset-Nr. {n})").format(n=original_number))
        html_body += f'<span style="color:#6c757d; font-size:9pt; font-weight:400;">{qset_label}</span> '
        # Intentionally omit per-question difficulty badge from the PDF header
        html_body += bookmark_icon_html  # Füge das Lesezeichen-Icon hinzu
        html_body += '</div>'
        if has_stage_label:
            if stage_label == DEFAULT_STAGE_LABEL:
                display_stage = translate_ui("pdf.stage_unknown", default="Unbekannt")
            else:
                display_stage = translate_ui(f"pdf.stage_name.{stage_label}", default=stage_label)
            stage_template = translate_ui("pdf.stage_label", default="Kognitive Stufe: {stage}")
            html_body += f'<div class="stage-label">{_html.escape(stage_template.format(stage=display_stage))}</div>'
        
        # Thema-Badge (falls vorhanden)
        if thema:
            html_body += f'<div class="question-topic">{thema}</div>'
        # Konzept anzeigen (falls vorhanden)
        try:
            concept_val = frage_obj.get("concept") or frage_obj.get("konzept")
        except Exception:
            concept_val = None
        if concept_val:
            try:
                label = translate_ui('metadata.concept', default='Konzept')
            except Exception:
                label = 'Konzept'
            html_body += f"<div style='margin-top:6px;margin-bottom:8px;color:#555;font-size:0.95em;'><strong>{_html.escape(label)}:</strong> {smart_quotes_de(str(concept_val))}</div>"
            # Decorative separator after meta-lines to visually separate
            # the concept line from the question text (kept aria-hidden).
            try:
                html_body += '<div class="muster-concept-sep" aria-hidden="true"></div>'
            except Exception:
                pass
        
        html_body += f'<div class="question-text">{frage_text}</div>'

        html_body += '<ul class="options">'
        for option in _get_options(frage_obj):
            is_correct = (option == richtige_antwort_text)
            is_selected = (option == gegebene_antwort)
            
            class_name = ''
            prefix = '○'
            
            if is_unanswered:
                if is_correct:
                    class_name = 'correct-unanswered'
                    prefix = '➜'
            else:
                if is_correct and is_selected:
                    class_name = 'correct-selected'
                    prefix = '✔'
                elif is_correct:
                    class_name = 'correct'
                    prefix = '✔'
                elif is_selected:
                    class_name = 'wrong-selected'
                    prefix = '✗'

            html_body += f'<li class="{class_name}"><span class="prefix">{prefix}</span> {_render_latex_in_html(smart_quotes_de(option), md_inline=True)}</li>'
        html_body += "</ul>"

        erklaerung = frage_obj.get("erklaerung")
        if erklaerung:
            label = translate_ui("test_view.explanation_label", default="Erklärung:")
            html_body += f'<div class="explanation"><strong>{_html.escape(label)}</strong> {_render_latex_in_html(smart_quotes_de(erklaerung))}</div>'

        html_body += _build_extended_explanation_html(frage_obj)
        
        # Schließe Question-Box
        html_body += '</div>'

    # Build localized CSS footer for pages (allows translations like "Seite {page} von {pages}")
    footer_template = translate_ui('pdf.page_footer', default='Seite {page} von {pages}')
    # Build a valid CSS `content` expression from the localized template
    css_footer = _build_css_footer(footer_template)

    # Vollständiges HTML-Dokument (Formeln sind bereits als Bilder)
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm 2cm 3cm 2cm;
                @bottom-center {{
                    content: {css_footer};
                    font-size: 9pt;
                    color: #666;
                }}
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                             'Helvetica Neue', Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.7;
                color: #2d3748;
                letter-spacing: 0.01em;
            }}
            
            /* Header Styling */
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 28px 24px;
                margin: -20px -20px 24px -20px;
                border-radius: 8px 8px 0 0;
            }}
            .header-content {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 20px;
            }}
            .header-left {{
                flex: 1;
                min-width: 0;
            }}
            .header-right {{
                flex-shrink: 0;
                width: 90px;
                text-align: right;
            }}
            .header-right img {{
                display: block;
                width: 80px;
                height: 80px;
                border: 3px solid white;
                border-radius: 8px;
                background: white;
            }}
            .header h1 {{
                margin: 0 0 12px 0;
                font-size: 26pt;
                font-weight: 600;
                letter-spacing: -0.02em;
                display: flex;
                align-items: flex-start;
                flex-direction: column;
            }}
            .header-subtitle {{
                font-size: 12pt;
                font-weight: 500;
                color: #e2e8f0;
                margin: 4px 0 0 0;
            }}
            .header-warning {{
                color: #ffc107;
                font-weight: 600;
            }}
            .meta-info {{
                display: flex;
                flex-direction: column;
                gap: 4px;
                font-size: 9pt;
                opacity: 0.95;
            }}
            
            /* Summary Box */
            .summary-box {{
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 28px;
                margin: 24px 0 32px 0;
                page-break-inside: avoid;
            }}
            .score-main {{
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 2px solid #dee2e6;
            }}
            .score-number {{
                font-size: 36pt;
                font-weight: bold;
                color: #667eea;
            }}
            .score-label {{
                font-size: 11pt;
                color: #6c757d;
                margin: 5px 0;
            }}
            .score-percent {{
                font-size: 18pt;
                font-weight: 600;
                color: #495057;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 15px;
            }}
            .stat-item {{
                text-align: center;
                padding: 10px;
                background: white;
                border-radius: 6px;
            }}
            .stat-value {{
                font-size: 20pt;
                font-weight: bold;
                color: #495057;
            }}
            .stat-value.correct {{ color: #15803d; }}
            .stat-value.wrong {{ color: #b91c1c; }}
            .stat-value.unanswered {{ color: #0284c7; }}
            .stat-value.rank {{ color: #b45309; }}
            .stat-label {{
                font-size: 9pt;
                color: #6c757d;
                margin-top: 5px;
            }}

            /* Confidence Box */
            .confidence-box {{
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 18px 22px;
                margin: 18px 0 24px 0;
                page-break-inside: avoid;
            }}
            .confidence-box h3 {{
                margin: 0 0 6px 0;
                font-size: 12pt;
                color: #1f2937;
                font-weight: 600;
            }}
            .confidence-caption {{
                font-size: 9.5pt;
                color: #6b7280;
                margin-bottom: 10px;
            }}
            .confidence-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 10pt;
                background: white;
                border: 1px solid #e2e8f0;
            }}
            .confidence-table thead th {{
                background: #eef2f7;
                color: #1f2937;
                font-weight: 600;
                padding: 6px 10px;
                text-align: center;
            }}
            .confidence-table tbody th {{
                background: #f8fafc;
                font-weight: 600;
                padding: 6px 10px;
                text-align: left;
            }}
            .confidence-table tbody td {{
                padding: 6px 10px;
                text-align: center;
            }}
            .confidence-cell {{
                font-weight: 600;
            }}
            .confidence-cell.good {{
                background: #ecfdf3;
                color: #15803d;
            }}
            .confidence-cell.bad {{
                background: #fef2f2;
                color: #b91c1c;
            }}
            .confidence-cell.neutral {{
                background: #f1f5f9;
                color: #475569;
            }}
            .confidence-totals {{
                margin-top: 8px;
                font-size: 9pt;
                color: #4b5563;
            }}
            .confidence-hints {{
                margin: 10px 0 0 0;
                padding-left: 18px;
                font-size: 9.5pt;
                color: #374151;
            }}
            .confidence-hint {{
                margin: 4px 0;
            }}
            .confidence-hint.good {{
                color: #15803d;
            }}
            .confidence-hint.warn {{
                color: #b45309;
            }}
            .confidence-hint.info {{
                color: #2563eb;
            }}

            /* Topic stacked-bar chart */
            .topic-chart {{
                margin: 18px 0;
                page-break-inside: avoid;
            }}
            .topic-chart h3 {{
                font-size: 12pt;
                margin-bottom: 8px;
            }}
            .topic-chart img {{
                width: 100%;
                max-width: 700px;
                height: auto;
                display: block;
                margin: 0 auto 12px auto;
                border: 1px solid #e6e6e6;
                background: white;
            }}
            .topic-legend {{
                display: flex;
                flex-wrap: wrap;
                gap: 14px 18px;
                align-items: center;
                margin-bottom: 8px;
            }}
            .topic-legend .legend-item {{
                display: flex;
                gap: 8px;
                align-items: center;
                font-size: 10pt;
                color: #0f172a;
                white-space: nowrap;
            }}
            .topic-legend .legend-swatch {{
                width: 14px;
                height: 14px;
                display: inline-block;
                border-radius: 3px;
                border: 1px solid rgba(15,23,42,0.06);
                box-shadow: 0 0 0 1px rgba(0,0,0,0.02) inset;
            }}
            .topic-chart-caption {{
                font-size: 9pt;
                color: #6b7280;
                margin: 6px 0 10px 0;
            }}
            /* explanatory paragraph removed — legend provides the necessary info */
            .comparison-box {{
                page-break-inside: avoid;
            }}
            .section-title {{
                page-break-after: avoid;
            }}
            /* Weak Topics Box */
            .weak-topics {{
                background: #fff3cd;
                border: 2px solid #b45309;
                border-radius: 8px;
                padding: 20px 24px;
                margin: 24px 0;
                page-break-inside: avoid;
            }}
            .weak-topics h3 {{
                margin: 0 0 12px 0;
                font-size: 14pt;
                color: #856404;
                font-weight: 600;
            }}
            .weak-topics ul {{
                margin: 0;
                padding-left: 20px;
                list-style-type: none;
            }}
            .weak-topics li {{
                padding: 8px 0 8px 20px;
                font-size: 11pt;
                color: #856404;
                line-height: 1.6;
                list-style-type: disc;
                list-style-position: outside;
                margin-bottom: 8px;
            }}
            .weak-topics .question-refs {{
                font-size: 10pt;
                color: #6c757d;
                font-weight: normal;
                font-style: italic;
            }}
            
            /* Difficulty Table */
            .difficulty-analysis {{
                margin: 28px 0;
                page-break-inside: avoid;
            }}
            .difficulty-analysis h3 {{
                margin: 0 0 12px 0;
                font-size: 14pt;
                color: #2d3748;
                font-weight: 600;
            }}
            .difficulty-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 10pt;
                border: 1px solid #dee2e6;
            }}
            .difficulty-table thead th {{
                background: #edf2f7;
                color: #2d3748;
                font-weight: 600;
                padding: 8px 12px;
                text-align: left;
            }}
            .difficulty-table tbody th,
            .difficulty-table tbody td {{
                padding: 8px 12px;
                border-top: 1px solid #dee2e6;
                text-align: left;
            }}
            .difficulty-table tbody tr:nth-child(even) {{
                background: #f8fafc;
            }}
            .difficulty-table .quota-cell {{
                font-weight: 600;
            }}

            /* Comparison Tables */
            .comparison-box {{
                margin: 32px 0;
                padding: 24px 28px;
                background: #f8f9fb;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                page-break-inside: avoid;
            }}
            .comparison-box h3 {{
                margin: 0;
                font-size: 14pt;
                color: #2d3748;
                font-weight: 600;
            }}
            .comparison-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 14px;
                font-size: 10pt;
            }}
            .comparison-table caption {{
                caption-side: top;
                text-align: left;
                font-weight: 600;
                color: #495057;
                padding-bottom: 6px;
            }}
            .comparison-table thead th {{
                background: #edf2f7;
                color: #2d3748;
                text-align: left;
                padding: 8px 12px;
                border-bottom: 2px solid #cbd5e0;
            }}
            .comparison-table tbody th {{
                text-align: left;
                font-weight: 600;
                padding: 8px 12px;
                border-bottom: 1px solid #dee2e6;
            }}
            .comparison-table tbody td {{
                text-align: left;
                padding: 8px 12px;
                border-bottom: 1px solid #dee2e6;
            }}
            .comparison-table tbody tr:nth-child(even) {{
                background: #f8fafc;
            }}
            .comparison-subtitle {{
                font-size: 11pt;
                color: #495057;
            }}
            .diff-cell {{
                font-weight: 600;
            }}
            .diff-cell.diff-positive {{
                color: #15803d;
            }}
            .diff-cell.diff-negative {{
                color: #c62828;
            }}
            .diff-cell.diff-neutral {{
                color: #495057;
            }}
            .comparison-footer {{
                margin-top: 12px;
                font-size: 9pt;
                color: #6c757d;
                text-align: right;
                font-style: italic;
            }}

            /* Section Title */
            .section-title {{
                font-size: 18pt;
                color: #2d3748;
                margin: 40px 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 2px solid #e9ecef;
                font-weight: 600;
                letter-spacing: -0.01em;
            }}
            .bookmark-icon {{
                display: inline-block;
                margin-left: 10px;
                font-size: 24pt;
                color: #b45309; /* dunkleres Amber für Aufmerksamkeit */
                vertical-align: middle;
            }}
            
            /* Question Box */
            .question-box {{
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 24px 28px;
                margin: 20px 0;
                /* box-shadow removed: WeasyPrint doesn't support this property and emits warnings */
                page-break-inside: avoid;
            }}
            .question-header {{
                font-size: 10pt;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }}
            .question-topic {{
                display: inline-block;
                background: #e3f2fd;
                color: #1565c0;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 9pt;
                font-weight: 500;
                margin-bottom: 12px;
                border: 1px solid #90caf9;
            }}
            .question-text {{
                font-size: 12pt;
                font-weight: 500;
                color: #2d3748;
                margin-bottom: 18px;
                line-height: 1.7;
            }}
            /* Prevent large default <p> margins inside question/explanation items
               by resetting paragraph margins in these scoped containers. This
               preserves block semantics but avoids extra vertical gaps. */
            .question-text p, .explanation p, ul.options li p, .bookmark-preview p {{
                margin: 0;
                padding: 0;
                display: inline;
            }}
            /* Also reset paragraph margins inside glossary items to avoid
               large gaps before the first glossary entry when authors
               supply paragraphs in definitions. */
            .glossary-item p, .glossary-definition p, .glossary-term p {{
                margin: 0;
                padding: 0;
                display: inline;
            }}
            .stage-label {{
                font-size: 9pt;
                color: #475569;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                margin-bottom: 8px;
                font-weight: 500;
            }}
            .stage-label span {{
                font-weight: 600;
                color: #0f172a;
                letter-spacing: normal;
            }}
            
            /* Options */
            ul.options {{
                list-style-type: none;
                padding-left: 0;
                margin: 16px 0;
            }}
            ul.options li {{
                margin-bottom: 12px;
                padding: 12px 16px 12px 45px;
                text-indent: -38px;
                line-height: 1.7;
                border-radius: 6px;
                background: #f8f9fa;
                font-size: 11pt;
            }}
            .prefix {{
                display: inline-block;
                width: 28px;
                text-align: center;
                font-weight: bold;
                margin-right: 10px;
            }}
            li.correct-selected, li.correct, li.correct-unanswered {{
                background: #C5E1A5 !important; /* hellgrün */
            }}
            /* Neutralize inherited bold on the list item, but allow
               intentionally marked <strong> or <b> inside the option to
               remain bold. This keeps the option text plain by default
               while preserving explicit emphasis. */
            li.correct {{
                font-weight: normal !important;
            }}
            li.correct strong, li.correct b {{
                font-weight: 700 !important;
            }}
            li.correct {{
                /* Korrekte Antwort (nicht ausgewählt) */
            }}
            li.wrong-selected {{
                font-weight: 500;
            }}
            
            /* Explanation Box */
            .explanation {{
                background: #fff3cd;
                border-left: 4px solid #b45309;
                padding: 16px 20px;
                margin-top: 16px;
                border-radius: 0 6px 6px 0;
                page-break-inside: avoid;
                line-height: 1.7;
            }}
            .explanation strong {{
                color: #856404;
                font-weight: 600;
            }}
            .extended-steps {{
                margin: 8px 0 0 1.2rem;
                padding: 0;
            }}
            .extended-steps li {{
                margin-bottom: 6px;
            }}
            
            /* Code */
            code {{
                background-color: #f1f3f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
                font-size: 9pt;
                color: #e83e8c;
            }}
            
            /* Page Break Control */
            .question-box {{ page-break-inside: avoid; }}
            .explanation {{ page-break-inside: avoid; }}
            h2, h3 {{ page-break-after: avoid; }}
            /* Start each subsequent question on a new page in the PDF output. */
            .question-box + .question-box {{
                page-break-before: always;
                break-before: page;
            }}
            /* Ensure the mini-glossary starts on its own page. */
            .glossary-page-break {{
                page-break-before: always;
                break-before: page;
                height: 0;
                margin: 0;
                padding: 0;
            }}
            /* A subtle separator used after certain concept lines (e.g. "Definition IoT")
               so the reader gets a light visual break. Kept very subtle to not distract. */
            .muster-concept-sep {{
                height: 1px;
                background: #e6e6e6;
                margin: 6px 0 8px 0;
            }}
            
            /* Glossary section: subtle dividers (admin style) */
            .glossary-section {{
                margin: 32px 0;
            }}
            .glossary-section h2 {{
                margin: 0 0 8px 0;
                color: #2d3748;
                font-size: 18pt;
                font-weight: 700;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .glossary-intro {{
                font-size: 10pt;
                color: #4a5568;
                margin: 0 0 24px 0;
                text-align: center;
                font-weight: 500;
            }}
            .glossary-theme {{
                font-size: 14pt;
                font-weight: 700;
                color: #1a202c;
                margin-top: 24px;
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 2px solid #4299e1;
            }}
            .glossary-theme:first-of-type {{
                margin-top: 12px;
            }}
            .glossary-grid {{
                display: grid;
                /* Avoid auto-fit/auto-fill which WeasyPrint warns about; choose a conservative 2-column layout for PDF */
                grid-template-columns: repeat(2, minmax(100px, 1fr));
                gap: 0;
                margin-bottom: 16px;
            }}
            .glossary-item {{
                padding: 16px 20px;
                border-bottom: 1px solid #cbd5e0;
            }}
            .glossary-item:nth-child(odd) {{
                background: #ffffff;
            }}
            .glossary-item:nth-child(even) {{
                background: #f7fafc;
            }}
            .glossary-item:first-child {{
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            .glossary-item:last-child {{
                border-bottom: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            .glossary-term {{
                font-size: 12pt;
                font-weight: 800;
                color: #2d3748;
                margin-bottom: 6px;
                display: block;
            }}
            .glossary-definition {{
                font-size: 10pt;
                color: #4a5568;
                line-height: 1.7;
                font-weight: 400;
            }}
        </style>
    </head>
    <body>
        {html_body}
        <div class="glossary-page-break" aria-hidden="true"></div>
        {glossary_html}
    </body>
    </html>
    '''

    # Optionally dump the assembled HTML to `exports/` for inspection
    try:
        if os.environ.get('DUMP_PDF_HTML'):
            dump_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(dump_dir, exist_ok=True)
            safe_name = 'report_' + os.path.basename(st.session_state.get('selected_questions_file', 'questions')).replace('.json', '')
            dump_path = os.path.join(dump_dir, f'{safe_name}.html')
            with open(dump_path, 'w', encoding='utf-8') as fh:
                fh.write(full_html)
    except Exception:
        pass

    # Konvertiere HTML zu PDF mit WeasyPrint (mit Optimierungen)
    # optimize_images=True reduziert Dateigröße ohne Qualitätsverlust
    pdf_bytes = HTML(string=full_html, base_url=__file__).write_pdf(
        optimize_images=True
    )
    
    # Cache-Statistiken ausgeben (für Debugging/Monitoring)
    cache_size = len(_formula_cache)
    if cache_size > 0:
        logger.info(translate_ui('pdf.log.formula_cache', default='📊 PDF export completed: {n} formulas cached').format(n=cache_size))
    
    return pdf_bytes


def generate_mini_glossary_pdf(q_file: str, questions: List[Dict[str, Any]]) -> bytes:
    """
    Erstellt ein PDF mit allen Mini-Glossar-Einträgen eines Fragensets.
    """
    glossary_by_theme = _extract_glossary_terms(questions)
    if not glossary_by_theme:
        raise ValueError(translate_ui('mini_glossary.empty_error', default='Kein Mini-Glossar in diesem Fragenset vorhanden.'))

    set_name = None
    try:
        from config import load_questions
        question_set = load_questions(q_file, silent=True)
        if question_set and question_set.meta:
            set_name = question_set.meta.get("title") or question_set.meta.get("thema")
    except Exception:
        set_name = None

    if not set_name:
        try:
            from user_question_sets import pretty_label_from_identifier_string
            set_name = pretty_label_from_identifier_string(q_file)
        except (ImportError, AttributeError):
            set_name = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    set_name = set_name or translate_ui("pdf.unnamed_set", default="Ungenanntes Fragenset")

    try:
        from helpers.text import format_datetime_locale, FMT_DATE
    except Exception:
        format_datetime_locale = None  # type: ignore[assignment]
        FMT_DATE = "%d.%m.%Y"  # type: ignore[assignment]

    # Always use current date/time for PDF generation
    if format_datetime_locale:
        try:
            # Pass datetime object directly (not ISO string) to avoid parsing issues
            generated_at = format_datetime_locale(datetime.now(), fmt=FMT_DATE)
        except Exception:
            # Fallback: manual formatting with German date format
            generated_at = datetime.now().strftime("%d.%m.%Y")
    else:
        # Fallback: manual formatting with German date format
        generated_at = datetime.now().strftime("%d.%m.%Y")
    theme_items = sorted(glossary_by_theme.items(), key=lambda x: x[0].casefold())

    # Paginierung konfigurieren
    max_items_per_page = 25
    paginated_html = []

    for page_start in range(0, len(theme_items), max_items_per_page):
        page_end = page_start + max_items_per_page
        page_themes = dict(theme_items[page_start:page_end])
        includes_header = page_start == 0
        if includes_header:
            intro = translate_ui('mini_glossary.title', default='Schlüsselbegriffe aus dem Fragenset "{name}"').format(name=set_name)
        else:
            intro = None
        page_html = _build_glossary_html(
            page_themes,
            intro_text=intro,
            include_header=includes_header,
        )
        paginated_html.append(f'<div class="glossary-page">{page_html}</div>')

    glossary_html = "".join(paginated_html)

    # Localized footer for pages
    footer_template = translate_ui('pdf.page_footer', default='Seite {page} von {pages}')
    css_footer = _build_css_footer(footer_template)

    full_html = f'''
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm 2cm 3cm 2cm;
                @bottom-center {{
                    content: {css_footer};
                    font-size: 9pt;
                    color: #666666;
                }}
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                             'Helvetica Neue', Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.7;
                color: #2d3748;
                letter-spacing: 0.01em;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 28px 24px;
                margin: -20px -20px 24px -20px;
                border-radius: 8px 8px 0 0;
            }}
            .header h1 {{
                margin: 0 0 12px 0;
                font-size: 26pt;
                font-weight: 600;
                letter-spacing: -0.02em;
            }}
            .meta-info {{
                display: flex;
                flex-direction: column;
                gap: 4px;
                font-size: 10pt;
                opacity: 0.95;
            }}
            .meta-info span {{
                display: block;
            }}
            .glossary-section {{
                margin-top: 24px;
            }}
            .glossary-section h2 {{
                margin: 0 0 8px 0;
                color: #2d3748;
                font-size: 18pt;
                font-weight: 700;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .glossary-intro {{
                font-size: 10pt;
                color: #4a5568;
                margin: 0 0 24px 0;
                text-align: center;
                font-weight: 500;
            }}
            .glossary-theme {{
                font-size: 14pt;
                font-weight: 700;
                color: #1a202c;
                margin-top: 24px;
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 2px solid #4299e1;
            }}
            .glossary-theme:first-of-type {{
                margin-top: 12px;
            }}
            .glossary-grid {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 0;
                margin-bottom: 16px;
            }}
            .glossary-item {{
                padding: 16px 20px;
                border-bottom: 1px solid #cbd5e0;
            }}
            .glossary-item:nth-child(odd) {{
                background: #ffffff;
            }}
            .glossary-item:nth-child(even) {{
                background: #f7fafc;
            }}
            .glossary-item:first-child {{
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            .glossary-item:last-child {{
                border-bottom: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            .glossary-term {{
                font-size: 12pt;
                font-weight: 800;
                color: #2d3748;
                margin-bottom: 6px;
                display: block;
            }}
            .glossary-definition {{
                font-size: 10pt;
                color: #4a5568;
                line-height: 1.7;
                font-weight: 400;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{_html.escape(translate_ui('pdf.glossary.title', default='Mini-Glossar'))}</h1>
            <div class="meta-info">
                <span><strong>{translate_ui('pdf.meta.questionset', default='Fragenset:')}</strong> {set_name}</span>
                <span><strong>{translate_ui('pdf.meta.generated_at', default='Stand:')}</strong> {generated_at}</span>
            </div>
        </div>
        {glossary_html}
    </body>
    </html>
    '''

    return HTML(string=full_html, base_url=__file__).write_pdf(optimize_images=True)


def generate_musterloesung_pdf(q_file: str, questions: List[Dict[str, Any]], app_config: AppConfig, total_timeout: float | None = None, progress_callback: Optional[Callable] = None) -> bytes:
    """
    Generiert ein PDF mit der Musterlösung (nur korrekte Antworten) und hängt das Mini-Glossar an.
    Dies ist ein schlankeres Format als der vollständige Nutzerbericht und eignet sich für Admin-Downloads.
    """
    from config import load_questions

    set_name = None
    try:
        # Lade das QuestionSet-Objekt neu, um sicher auf die Metadaten zugreifen zu können.
        # Das übergebene `questions`-Objekt ist oft nur eine Liste.
        question_set = load_questions(q_file, silent=True)
        if question_set and question_set.meta:
            set_name = question_set.meta.get("title") or question_set.meta.get("thema")
    except Exception:
        set_name = None

    if not set_name:
        try:
            from user_question_sets import pretty_label_from_identifier_string
            set_name = pretty_label_from_identifier_string(q_file)
        except (ImportError, AttributeError):
            set_name = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    set_name = set_name or translate_ui("pdf.unnamed_set", default="Ungenanntes Fragenset")

    try:
        from helpers.text import format_datetime_locale, FMT_DATETIME
    except Exception:
        format_datetime_locale = None  # type: ignore[assignment]
        FMT_DATETIME = "%d.%m.%Y %H:%M"  # type: ignore[assignment]

    # Always use current date/time for PDF generation
    if format_datetime_locale:
        try:
            # Pass datetime object directly (not ISO string) to avoid parsing issues
            generated_at = format_datetime_locale(datetime.now(), fmt=FMT_DATETIME)
        except Exception:
            # Fallback: manual formatting with German date/time format
            generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")
    else:
        # Fallback: manual formatting with German date/time format
        generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Ensure canonical question schema for this run too
    def normalize_question_schema(q: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(q, dict):
            return q
        if 'text' not in q:
            if 'question' in q:
                q['text'] = q.get('question')
            elif 'frage' in q:
                q['text'] = q.get('frage')
        opts = None
        for k in ('options', 'optionen', 'answers'):
            if k in q and q.get(k) is not None:
                opts = q.get(k)
                break
        if isinstance(opts, dict):
            try:
                ordered = [opts[k] for k in sorted(opts.keys())]
            except Exception:
                ordered = list(opts.values())
            q['options'] = ordered
        elif isinstance(opts, list):
            q['options'] = opts
        elif opts is None:
            q.setdefault('options', [])
        if 'answer' not in q:
            if 'loesung' in q:
                q['answer'] = q.get('loesung')
            elif 'antwort' in q:
                q['answer'] = q.get('antwort')
        if 'explanation' not in q:
            for k in ('erklaerung', 'erklaerung_html'):
                if k in q:
                    q['explanation'] = q.get(k)
                    break
        if 'concept' not in q and 'konzept' in q:
            q['concept'] = q.get('konzept')
        if 'topic' not in q and 'thema' in q:
            q['topic'] = q.get('thema')
        if 'weight' not in q and 'gewichtung' in q:
            q['weight'] = q.get('gewichtung')
        if 'cognitive_level' not in q:
            for k in ('kognitive_stufe', 'cognitive_level', 'cognitiveLevel'):
                if k in q:
                    q['cognitive_level'] = q.get(k)
                    break
        return q

    try:
        for i, q in enumerate(questions):
            questions[i] = normalize_question_schema(q or {})
    except Exception:
        pass

    # Tempo metadata (best-effort)
    try:
        tempo_code = st.session_state.get('selected_tempo') or st.session_state.get('tempo') or None
    except Exception:
        tempo_code = None
    tempo_span = ''
    if tempo_code:
        try:
            tempo_display = translate_ui(f"tempo.{tempo_code}", default='')
            if not tempo_display:
                # fallback map if translation missing
                tempo_map = {
                    'normal': translate_ui('tempo.normal', default='Normal'),
                    'speed': translate_ui('tempo.speed', default='Speed (1/2)'),
                    'power': translate_ui('tempo.power', default='Power (1/4)'),
                }
                tempo_display = tempo_map.get(tempo_code, tempo_code)
        except Exception:
            tempo_display = tempo_code
        try:
            tempo_span = f'<span><strong>{translate_ui("pdf.meta.tempo", default="Tempo:")}</strong> {_html.escape(str(tempo_display))}</span>'
        except Exception:
            tempo_span = f'<span><strong>Tempo:</strong> {_html.escape(str(tempo_display))}</span>'

    def _report(pct: int, msg: str = ""):
        try:
            if progress_callback:
                progress_callback(pct, msg)
        except Exception:
            pass

    # Baue einfachen HTML-Report mit markierten korrekten Antworten
    html_parts: list[str] = []
    html_parts.append(
        f'<div class="header"><h1>{_html.escape(translate_ui("pdf.musterloesung.title", default="Musterlösung"))}</h1>'
        f'<div class="meta-info"><span><strong>{translate_ui("pdf.meta.questionset", default="Fragenset:")}</strong> {set_name}</span>'
        f'{tempo_span}'
        f'<span><strong>{translate_ui("pdf.meta.generated_at", default="Erstellt:")}</strong> {generated_at}</span></div></div>'
    )
    html_parts.append('<div class="section">')
    sorted_entries = _prepare_stage_sorted_questions(questions)

    # Nummeriere die Fragen nach Bloom-Taxonomie geordnet
    # Use the sorted/filtered entries for all display-related counting so
    # we don't accidentally compare the rendered index against the raw
    # `questions` list (which may differ in length). This avoids appending
    # the trailing separator when the last *displayed* question is reached.
    for display_num, (_, stage_label, _, frage) in enumerate(sorted_entries, start=1):
        # coarse progress report: parsing/rendering block per question
        _report(int((display_num - 1) / max(1, len(questions)) * 60), f"Verarbeite Frage {display_num}/{len(questions)}")
        frage_text = frage.get("question", frage.get("frage", ""))
        # Parst Markdown/LaTeX in sicheres HTML
        parsed_frage = _render_latex_in_html(
            smart_quotes_de(frage_text.split('. ', 1)[-1] if '. ' in frage_text else frage_text),
            total_timeout=total_timeout,
        )

        # Insert a subtle separator before each question so the PDF shows
        # a consistent divider line prior to every question block. Only
        # insert this separator for questions after the first so we can
        # safely use it as a page-break anchor without creating a blank
        # first page.
        try:
            if display_num > 1:
                html_parts.append('<div class="muster-concept-sep" aria-hidden="true"></div>')
        except Exception:
            pass
        html_parts.append('<div class="question">')
        q_header = translate_ui("pdf.question_header", default="Frage {current} / {total}").format(current=display_num, total=len(questions))
        html_parts.append(f'<h3>{_html.escape(q_header)}</h3>')

        # Render meta-info lines (Cognitive Stage, Topic, Concept) for Musterlösung.
        # These should be normal font-weight, light gray and NOT uppercased.
        raw_stage_value = frage.get("kognitive_stufe")
        has_stage_label = bool(raw_stage_value and str(raw_stage_value).strip())

        # Stage line
        if has_stage_label:
            if stage_label == DEFAULT_STAGE_LABEL:
                display_stage = translate_ui("pdf.stage_unknown", default="Unknown")
            else:
                display_stage = translate_ui(f"pdf.stage_name.{stage_label}", default=stage_label)
            # Use an English-friendly default label but keep translations if available
            stage_template = translate_ui("pdf.stage_label", default="Cognitive Stage: {stage}")
            html_parts.append(f'<div class="muster-meta-line">{_html.escape(stage_template.format(stage=display_stage))}</div>')

        # Topic line (if present)
        topic_val = frage.get("topic") or frage.get("thema") or ''
        if topic_val:
            topic_label = translate_ui('pdf.meta.topic', default='Topic:')
            html_parts.append(f'<div class="muster-meta-line">{_html.escape(topic_label)} {_html.escape(str(topic_val))}</div>')

        # Concept line (if present) — otherwise insert a subtle separator
        try:
            concept_val = frage.get("concept") or frage.get("konzept")
        except Exception:
            concept_val = None

        # Treat blank/whitespace-only concept values as missing
        has_concept = bool(concept_val and str(concept_val).strip())

        if has_concept:
            try:
                c_label = translate_ui('metadata.concept', default='Concept')
            except Exception:
                c_label = 'Concept'
            html_parts.append(f'<div class="muster-meta-line">{_html.escape(c_label)}: {smart_quotes_de(str(concept_val))}</div>')

        # Always insert a very light separator after the meta-lines.
        # Decorative only; keep `aria-hidden` so screen readers ignore it.
        try:
            html_parts.append('<div class="muster-concept-sep" aria-hidden="true"></div>')
        except Exception:
            # Be defensive: if appending fails for any reason, continue without crashing.
            pass

        html_parts.append(f'<div class="question-text">{parsed_frage}</div>')
        html_parts.append('<ul class="options">')

        opts = _get_options(frage)
        correct_idx_raw = frage.get("loesung")
        correct_idx = None
        try:
            correct_idx = int(correct_idx_raw)
        except Exception:
            try:
                if isinstance(correct_idx_raw, str) and len(correct_idx_raw.strip()) == 1 and correct_idx_raw.strip().isalpha():
                    correct_idx = ord(correct_idx_raw.strip().upper()) - ord('A')
            except Exception:
                correct_idx = None
        # If raw value is a string equal to an option, map to that index
        if correct_idx is None and correct_idx_raw is not None:
            try:
                for i, o in enumerate(opts):
                    try:
                        if isinstance(o, str) and isinstance(correct_idx_raw, str) and o.strip() == correct_idx_raw.strip():
                            correct_idx = i
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        for oi, opt in enumerate(opts):
            parsed_opt = _render_latex_in_html(smart_quotes_de(opt), total_timeout=total_timeout, md_inline=True)
            if oi == correct_idx:
                html_parts.append(f'<li class="option correct">✔ {parsed_opt}</li>')
            else:
                html_parts.append(f'<li class="option">{parsed_opt}</li>')

        html_parts.append('</ul>')

        # Erklärung anzeigen, falls vorhanden
        erklaerung = frage.get("erklaerung")
        if erklaerung:
            label = translate_ui("test_view.explanation_label", default="Erklärung:")
            html_parts.append(
                f'<div class="explanation"><strong>{_html.escape(label)}</strong> {_render_latex_in_html(smart_quotes_de(erklaerung), total_timeout=total_timeout)}</div>'
            )

        html_parts.append(_build_extended_explanation_html(frage, total_timeout=total_timeout))

        html_parts.append('</div>')

    # report that question parsing is mostly done (~60%)
    _report(65, "Fragen verarbeitet, baue Glossar und HTML")

    html_parts.append('</div>')

    # Glossar anhängen — force new page before glossary
    glossary_by_theme = _extract_glossary_terms(questions)
    glossary_html = _build_glossary_html(glossary_by_theme)
    # Ensure the mini-glossary starts on a new page in the PDF output.
    # Decorative empty div with page-break CSS (aria-hidden for screen readers).
    html_parts.append('<div class="glossary-page-break" aria-hidden="true"></div>')
    html_parts.append(glossary_html)

    # Localized footer for pages
    footer_template = translate_ui('pdf.page_footer', default='Seite {page} von {pages}')
    css_footer = _build_css_footer(footer_template)

    # Full HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm 2cm 3cm 2cm;
                @bottom-center {{
                    content: {css_footer};
                    font-size: 9pt;
                    color: #666;
                }}
            }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; color: #222; line-height:1.6; }}
            .header {{ background: #f1f5f9; padding: 18px; border-radius: 6px; margin-bottom: 12px; }}
            .header h1 {{ margin: 0 0 6px 0; font-size: 22pt; }}
            .meta-info span {{ display:block; font-size: 10pt; color: #555; }}
            .question {{ margin: 18px 0; padding: 12px; border:1px solid #e6eef8; border-radius:6px; background: #ffffff; }}
            .question h3 {{ margin: 0 0 8px 0; color: #1f6feb; font-size: 12pt; }}
            /* Start each subsequent question on a new page in the PDF output.
               We insert a decorative `.muster-concept-sep` before questions
               (except the first) and use it as the page-break anchor. This
               avoids creating an empty first page while ensuring every
               following question starts fresh. */
            .muster-concept-sep + .question {{
                page-break-before: always;
                break-before: page;
            }}
            /* Avoid splitting a single question across pages where possible. */
            .question {{ page-break-inside: avoid; break-inside: avoid; }}
            /* Ensure the mini-glossary starts on its own page. */
            .glossary-page-break {{
                page-break-before: always;
                break-before: page;
                height: 0;
                margin: 0;
                padding: 0;
            }}
            .question-text {{ margin-bottom: 8px; font-size: 11pt; }}
            /* Reset paragraph margins inside question/explanation/option containers
               to avoid large vertical gaps from Markdown-produced <p> tags. */
            .question-text p, .explanation p, ul.options li p, .bookmark-preview p {{
                margin: 0;
                padding: 0;
                display: inline;
            }}
            /* Also reset paragraph margins inside glossary items to avoid
               large gaps before the first glossary entry when authors
               supply paragraphs in definitions. */
            .glossary-item p, .glossary-definition p, .glossary-term p {{
                margin: 0;
                padding: 0;
                display: inline;
            }}
            /* For the Musterlösung we render meta-info lines (stage/topic/concept)
               as normal-weight, light-gray text (not uppercased). */
            .stage-label {{
                font-size: 9pt;
                color: #6b7280;
                text-transform: none;
                letter-spacing: 0.02em;
                margin-bottom: 6px;
                font-weight: 400;
            }}
            .stage-label span {{
                color: #1f2937;
                font-weight: 600;
                letter-spacing: normal;
            }}
            .muster-meta-line {{
                font-size: 9pt;
                color: #6b7280; /* light gray */
                margin-bottom: 4px;
                font-weight: 400;
            }}
            /* A subtle separator used after certain concept lines (e.g. "Definition IoT")
               so the reader gets a light visual break. Kept very subtle to not distract. */
            .muster-concept-sep {{
                height: 1px;
                background: #e6e6e6;
                margin: 6px 0 8px 0;
            }}
            ul.options {{ list-style: disc; padding-left: 1.2rem; margin: 0 0 8px 0; }}
            ul.options li.option {{ padding: 4px 6px; margin-bottom:6px; background: transparent; border-radius:4px; }}
            ul.options li.option .opt-content {{ display: inline; }}
            ul.options li.correct {{ background: #ecfdf5; border-left: 4px solid #15803d; padding-left: 8px; }}
                /* Neutralize inherited bold on the correct option but keep
                    explicit <strong>/<b> tags bold so authors can highlight
                    individual words intentionally. */
                ul.options li.correct {{ font-weight: normal !important; }}
                ul.options li.correct strong, ul.options li.correct b {{ font-weight: 700 !important; }}
            .explanation {{ background: #fff8e1; border-left: 4px solid #b45309; padding: 10px 12px; margin-top: 8px; border-radius: 4px; }}
            .explanation strong {{ color: #856404; }}

            /* Glossary styling (match admin/user glossary style) */
            .glossary-section {{ margin: 24px 0; }}
            .glossary-section h2 {{ margin: 0 0 8px 0; color: #2d3748; font-size: 18pt; font-weight: 700; text-align: center; text-transform: uppercase; letter-spacing: 1px; }}
            .glossary-intro {{ font-size: 10pt; color: #4a5568; margin: 0 0 24px 0; text-align: center; font-weight: 500; }}
            .glossary-theme {{ font-size: 14pt; font-weight: 700; color: #1a202c; margin-top: 24px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #4299e1; }}
            .glossary-grid {{ display: grid; grid-template-columns: 1fr; gap: 0; margin-bottom: 16px; }}
            .glossary-item {{ padding: 12px 14px; border-bottom: 1px solid #cbd5e0; }}
            .glossary-item:nth-child(odd) {{ background: #ffffff; }}
            .glossary-item:nth-child(even) {{ background: #f7fafc; }}
            .glossary-term {{ font-size: 12pt; font-weight: 800; color: #2d3748; margin-bottom: 6px; display: block; }}
            .glossary-definition {{ font-size: 10pt; color: #4a5568; line-height: 1.6; font-weight: 400; }}
        </style>
    </head>
    <body>
        {''.join(html_parts)}
    </body>
    </html>
    """

    # Before writing PDF, report that we're starting the final render
    # Optionally dump the assembled HTML to `exports/` for inspection
    try:
        if os.environ.get('DUMP_PDF_HTML'):
            dump_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(dump_dir, exist_ok=True)
            safe_name = os.path.basename(q_file).replace('.json', '')
            dump_path = os.path.join(dump_dir, f'muster_{safe_name}.html')
            with open(dump_path, 'w', encoding='utf-8') as fh:
                fh.write(full_html)
    except Exception:
        pass

    _report(80, "Konvertiere HTML zu PDF")
    pdf_bytes = HTML(string=full_html, base_url=__file__).write_pdf(optimize_images=True)

    # Final progress update
    _report(100, "Fertig")
    return pdf_bytes
