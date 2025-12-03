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
from helpers.text import format_decimal_de, smart_quotes_de, normalize_detailed_explanation
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

    # Normalize literal escape sequences: if the input contains the two-character
    # sequence "\\n" (e.g. from pasted/serialized content), convert it to an
    # actual newline so subsequent list/paragraph and Markdown processing works.
    try:
        if isinstance(html_text, str) and ('\\n' in html_text or '\\r\\n' in html_text):
            html_text = html_text.replace('\\r\\n', '\n').replace('\\n', '\n')
    except Exception:
        # Non-fatal: if normalization fails, continue with the original text
        pass

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
    
    processed_text = ''.join(html_lines) # Verwende join ohne <br>, da p-Tags oder li-Tags für Struktur sorgen

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
                gewichtung = frage.get("gewichtung", 1)
                if i in question_rates:
                    rate = question_rates[i] * 100
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
            
            if isinstance(mini_gloss, dict):
                # Initialisiere Thema, falls noch nicht vorhanden
                if thema not in glossary_by_theme:
                    glossary_by_theme[thema] = {}
                
                # Füge alle Begriffe aus diesem mini_glossary hinzu
                for term, definition in mini_gloss.items():
                    # Verhindere globale Duplikate
                    if term not in seen_terms:
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

            for opt in frage.get("optionen", []):
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
        richtige_antwort = frage_obj["optionen"][frage_obj["loesung"]]
        
        # Nur zählen wenn Frage beantwortet wurde UND falsch war
        if gegebene_antwort is not None and gegebene_antwort != richtige_antwort:
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
        from helpers.text import format_datetime_de
        generated_at_str = format_datetime_de(datetime.now().isoformat(), fmt='%d.%m.%Y %H:%M')
    except Exception:
        generated_at_str = datetime.now().strftime('%d.%m.%Y %H:%M')

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
    header_title = set_name
    header_subtitle = ""
    if test_manually_ended:
        header_subtitle = f'<p class="header-subtitle">({_html.escape(translate_ui("pdf.header.manual_end", default="Test vorzeitig beendet"))})</p>'

    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions, app_config.scoring_mode
    )
    prozent = (current_score / max_score * 100) if max_score > 0 else 0

    # Hole Ranking-Position
    from database import get_all_logs_for_leaderboard
    leaderboard_data = get_all_logs_for_leaderboard(q_file)
    user_rank = None
    if leaderboard_data:
        for idx, entry in enumerate(leaderboard_data, start=1):
            if entry['user_pseudonym'] == user_name:
                user_rank = idx
                break
    
    rank_text = translate_ui("pdf.rank_text", default=" • Platz {rank} im Ranking").format(rank=user_rank) if user_rank else ""

    # Statistiken berechnen
    antworten = [get_answer_for_question(i) for i in range(len(questions))]
    richtige = sum(1 for i, ant in enumerate(antworten) if ant is not None and ant == questions[i]["optionen"][questions[i]["loesung"]])
    unbeantwortet = sum(1 for ant in antworten if ant is None)
    falsche = len(questions) - richtige - unbeantwortet
    
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
        return None

    s_dt = _to_datetime(start_time)
    e_dt = _to_datetime(end_time)

    if s_dt and e_dt:
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
    
    # Durchschnittsvergleich berechnen
    avg_stats = _calculate_average_stats(q_file, questions)
    
    # Schwierigkeits-Analyse erstellen
    difficulty_stats = {"easy": {"richtig": 0, "gesamt": 0},
                       "medium": {"richtig": 0, "gesamt": 0},
                       "hard": {"richtig": 0, "gesamt": 0}}
    
    for i, frage in enumerate(questions):
        gewichtung = frage.get("gewichtung", 1)
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort = frage["optionen"][frage["loesung"]]
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
        richtige_antwort = frage["optionen"][frage["loesung"]]
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
            stage_html += (
                f'<tr>'
                f'<th scope="row">{_html.escape(translated_label)}</th>'
                f'<td>{ratio_text}</td>'
                f'<td class="quota-cell">{percent_value:.0f} %</td>'
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
        diff_value_str = format_decimal_de(abs(diff_value), 1)
        comparison_html += (
            f'<tr>'
            f'<th scope="row">{translate_ui("pdf.comparison.row.overall", default="Gesamtergebnis")}</th>'
            f'<td>{prozent:.0f} %</td>'
            f'<td>{avg_stats["avg_percent"]:.0f} %</td>'
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
                    diff_str = format_decimal_de(abs(diff), 1)
                    comparison_html += (
                        f'<tr>'
                        f'<th scope="row">{label}</th>'
                        f'<td>{user_percent:.0f} %</td>'
                        f'<td>{avg_percent:.0f} %</td>'
                        f'<td class="diff-cell {diff_class}">{diff_symbol} {diff_str} % {diff_phrase}</td>'
                        f'</tr>'
                    )
                comparison_html += '</tbody></table>'

        footer_text = translate_ui("pdf.comparison.footer", default="Based on {n} participants. Comparison data as of: {date}.")
        comparison_html += f'<p class="comparison-footer">{_html.escape(footer_text.format(n=avg_stats["total_users"], date=generated_at_str))}</p>'
        comparison_html += '</div>'
    
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

    # Baue den HTML-Body mit professionellem Header
    score_percent_str = format_decimal_de(prozent, 1)
    
    rank_html = ''
    if user_rank:
        rank_label = translate_ui('pdf.rank_label', default='Ranking (Stand: {date})').format(date=generated_at_str.split(' ')[0])
        rank_html = f'<div class="stat-item"><div class="stat-value rank">#{user_rank}</div><div class="stat-label">{_html.escape(rank_label)}</div></div>'
    score_label = translate_ui('pdf.score_label', default='von {n} Punkten').format(n=max_score)

    # Only show the detailed-analysis heading when there are completed
    # test runs for this question set. `_calculate_average_stats` returns
    # `None` when no complete sessions exist, otherwise it contains
    # a `total_users` count. Require more than one participant to show
    # the comparison section (otherwise there's nothing to compare).
    show_detailed_analysis = bool(avg_stats and (avg_stats.get('total_users', 0) > 1))
    detailed_heading = (
        f'<h2 class="section-title">{_html.escape(translate_ui("pdf.detailed_analysis", default="Detaillierte Auswertung"))}</h2>'
        if show_detailed_analysis else ''
    )

    html_body = f'''
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <h1>{_html.escape(header_title)}</h1>{header_subtitle}
                    <div class="meta-info">
                        <span><strong>{translate_ui('pdf.meta.participant', default='Teilnehmer:')}</strong> {user_name}</span>
                        <span><strong>{translate_ui('pdf.meta.test_date', default='Testdatum:')}</strong> {generated_at_str}</span>
                        {f"<span><strong>{translate_ui('pdf.meta.duration', default='Dauer:')}</strong> {duration_str}</span>" if duration_str else ''}
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
        
        {weak_topics_html}
        
        {difficulty_html}
        
        {stage_html}
        
        {comparison_html}
        
        {bookmarks_html}
        
        {detailed_heading}
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
        richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
        
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
        
        html_body += f'<div class="question-text">{frage_text}</div>'

        html_body += '<ul class="options">'
        for option in frage_obj["optionen"]:
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
                color: #ffc107;
                margin: 4px 0 0 0;
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
        {glossary_html}
    </body>
    </html>
    '''

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
        from helpers.text import format_datetime_de

        generated_at = format_datetime_de(datetime.now().isoformat(), fmt='%d.%m.%Y')
    except Exception:
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
        from helpers.text import format_datetime_de

        generated_at = format_datetime_de(datetime.now().isoformat(), fmt='%d.%m.%Y %H:%M')
    except Exception:
        generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")

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
        f'<span><strong>{translate_ui("pdf.meta.generated_at", default="Erstellt:")}</strong> {generated_at}</span></div></div>'
    )
    html_parts.append('<div class="section">')
    sorted_entries = _prepare_stage_sorted_questions(questions)

    # Nummeriere die Fragen nach Bloom-Taxonomie geordnet
    for display_num, (_, stage_label, _, frage) in enumerate(sorted_entries, start=1):
        # coarse progress report: parsing/rendering block per question
        _report(int((display_num - 1) / max(1, len(questions)) * 60), f"Verarbeite Frage {display_num}/{len(questions)}")
        frage_text = frage.get("question", frage.get("frage", ""))
        # Parst Markdown/LaTeX in sicheres HTML
        parsed_frage = _render_latex_in_html(
            smart_quotes_de(frage_text.split('. ', 1)[-1] if '. ' in frage_text else frage_text),
            total_timeout=total_timeout,
        )

        html_parts.append('<div class="question">')
        q_header = translate_ui("pdf.question_header", default="Frage {current} / {total}").format(current=display_num, total=len(questions))
        html_parts.append(f'<h3>{_html.escape(q_header)}</h3>')
        raw_stage_value = frage.get("kognitive_stufe")
        has_stage_label = bool(raw_stage_value and str(raw_stage_value).strip())
        if has_stage_label:
            if stage_label == DEFAULT_STAGE_LABEL:
                display_stage = translate_ui("pdf.stage_unknown", default="Unbekannt")
            else:
                display_stage = translate_ui(f"pdf.stage_name.{stage_label}", default=stage_label)
            stage_template = translate_ui("pdf.stage_label", default="Kognitive Stufe: {stage}")
            html_parts.append(f'<div class="stage-label">{_html.escape(stage_template.format(stage=display_stage))}</div>')
        html_parts.append(f'<div class="question-text">{parsed_frage}</div>')
        html_parts.append('<ul class="options">')

        correct_idx = frage.get("loesung")
        opts = frage.get("optionen", [])
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

    # Glossar anhängen
    glossary_by_theme = _extract_glossary_terms(questions)
    glossary_html = _build_glossary_html(glossary_by_theme)
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
            .stage-label {{
                font-size: 9pt;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 6px;
                font-weight: 500;
            }}
            .stage-label span {{
                color: #1f2937;
                font-weight: 700;
                letter-spacing: normal;
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
    _report(80, "Konvertiere HTML zu PDF")
    pdf_bytes = HTML(string=full_html, base_url=__file__).write_pdf(optimize_images=True)

    # Final progress update
    _report(100, "Fertig")
    return pdf_bytes
