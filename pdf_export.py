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

from logic import get_answer_for_question, calculate_score
from config import AppConfig
from helpers import format_decimal_de
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


def _render_latex_in_html(html_text: str, total_timeout: float | None = None) -> str:
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
    processed_text = re.sub(r'\\\\\[(.*?)\\\\\]', save_block_formula, processed_text, flags=re.DOTALL)
    processed_text = re.sub(r'\$([^$]+?)\$', save_inline_formula, processed_text)
    processed_text = re.sub(r'\\\\\((.*?)\\\\\)', save_inline_formula, processed_text, flags=re.DOTALL)

    # 2. Markdown-Formatierungen wie Listen und Zeilenumbrüche in HTML umwandeln.
    # Dies ist immer noch notwendig, da die zentrale Bereinigung kein Markdown nach HTML konvertiert.
    # Wir entfernen aber das HTML-Escaping und die manuelle Tag-Ersetzung.
    lines = processed_text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* '):
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
        
    except Exception as e:
        print(f"Error calculating average stats: {e}")
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
        glossary_html_parts.append('<h2 class="section-title">Mini-Glossar</h2>')
        intro = intro_text or 'Wichtige Begriffe aus diesem Test, gruppiert nach Themen'
        glossary_html_parts.append(f'<p class="glossary-intro">{intro}</p>')

    for thema, terms in glossary_by_theme.items():
        parsed_thema = _render_latex_in_html(thema)
        glossary_html_parts.append('<div class="glossary-section">')
        glossary_html_parts.append(f'<h3 class="glossary-theme">{parsed_thema}</h3>')
        glossary_html_parts.append('<div class="glossary-grid">')

        for term, definition in terms.items():
            parsed_term = _render_latex_in_html(term)
            parsed_definition = _render_latex_in_html(definition)

            glossary_html_parts.append('<div class="glossary-item">')
            glossary_html_parts.append(f'<div class="glossary-term">{parsed_term}</div>')
            glossary_html_parts.append(f'<div class="glossary-definition">{parsed_definition}</div>')
            glossary_html_parts.append('</div>')

        glossary_html_parts.append('</div>')
        glossary_html_parts.append('</div>')

    if include_header:
        glossary_html_parts.append('</div>')

    return ''.join(glossary_html_parts)


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
        from helpers import format_datetime_de
        generated_at_str = format_datetime_de(datetime.now().isoformat(), fmt='%d.%m.%Y %H:%M')
    except Exception:
        generated_at_str = datetime.now().strftime('%d.%m.%Y %H:%M')
    user_name = st.session_state.get("user_id", "Unbekannt")
    q_file = st.session_state.get("selected_questions_file", "Unbekanntes Set")
    set_name = str(q_file).replace("questions_", "").replace(".json", "").replace("_", " ")

    # Prüfen, ob der Test vorzeitig beendet wurde
    test_manually_ended = st.session_state.get("test_manually_ended", False)
    header_title = set_name
    header_subtitle = ""
    if test_manually_ended:
        header_subtitle = '<p class="header-subtitle">(Test vorzeitig beendet)</p>'

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
    
    rank_text = f" • Platz {user_rank} im Ranking" if user_rank else ""

    # Statistiken berechnen
    antworten = [get_answer_for_question(i) for i in range(len(questions))]
    richtige = sum(1 for i, ant in enumerate(antworten) if ant is not None and ant == questions[i]["optionen"][questions[i]["loesung"]])
    unbeantwortet = sum(1 for ant in antworten if ant is None)
    falsche = len(questions) - richtige - unbeantwortet
    
    # Bearbeitungszeit berechnen
    start_time = st.session_state.get("test_start_time")
    end_time = st.session_state.get("test_end_time", datetime.now())
    duration_str = ""
    if start_time:
        duration = end_time - start_time
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
        weak_topics_html += '<h3>Verbesserungspotenzial</h3>'
        weak_topics_html += '<ul>'
        for topic, question_numbers in weak_topics:
            # Formatiere Fragennummern (z.B. "Fragen 3, 7, 12")
            if len(question_numbers) == 1:
                fragen_text = f"Frage {question_numbers[0]}"
            else:
                fragen_text = f"Fragen {', '.join(map(str, question_numbers))}"
            weak_topics_html += f'<li><strong>{topic}</strong><br><span class="question-refs">{fragen_text}</span></li>'
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
    
    # HTML für Schwierigkeits-Übersicht
    difficulty_rows = []
    if difficulty_stats["easy"]["gesamt"] > 0:
        easy_percent = (difficulty_stats["easy"]["richtig"] / difficulty_stats["easy"]["gesamt"] * 100)
        difficulty_rows.append((
            "★ Leicht",
            f'{difficulty_stats["easy"]["richtig"]}/{difficulty_stats["easy"]["gesamt"]}',
            easy_percent,
        ))
    if difficulty_stats["medium"]["gesamt"] > 0:
        medium_percent = (difficulty_stats["medium"]["richtig"] / difficulty_stats["medium"]["gesamt"] * 100)
        difficulty_rows.append((
            "★★ Mittel",
            f'{difficulty_stats["medium"]["richtig"]}/{difficulty_stats["medium"]["gesamt"]}',
            medium_percent,
        ))
    if difficulty_stats["hard"]["gesamt"] > 0:
        hard_percent = (difficulty_stats["hard"]["richtig"] / difficulty_stats["hard"]["gesamt"] * 100)
        difficulty_rows.append((
            "★★★ Schwer",
            f'{difficulty_stats["hard"]["richtig"]}/{difficulty_stats["hard"]["gesamt"]}',
            hard_percent,
        ))

    difficulty_html = ""
    if difficulty_rows:
        difficulty_html = '<div class="difficulty-analysis">'
        difficulty_html += '<h3>Performance nach Schwierigkeit</h3>'
        difficulty_html += '<table class="difficulty-table">'
        difficulty_html += '<thead><tr><th>Schwierigkeit</th><th>Treffer</th><th>Quote</th></tr></thead>'
        difficulty_html += '<tbody>'
        for label, ratio_text, percent_value in difficulty_rows:
            difficulty_html += (
                f'<tr>'
                f'<th scope="row">{label}</th>'
                f'<td>{ratio_text}</td>'
                f'<td class="quota-cell">{percent_value:.0f} %</td>'
                f'</tr>'
            )
        difficulty_html += '</tbody></table></div>'

    # Vergleich mit Durchschnitt
    comparison_html = ""
    if avg_stats and avg_stats['total_users'] > 1:  # Mindestens 2 User (inkl. aktuellem)
        def _diff_meta(value: float) -> tuple[str, str, str]:
            if value > 0:
                return "diff-positive", "↑", "über Durchschnitt"
            if value < 0:
                return "diff-negative", "↓", "unter Durchschnitt"
            return "diff-neutral", "=", "auf Durchschnittsniveau"

        comparison_html = '<div class="comparison-box">'
        comparison_html += '<h3>Vergleich mit Durchschnitt</h3>'

        diff_value = prozent - avg_stats['avg_percent']
        diff_class, diff_symbol, diff_phrase = _diff_meta(diff_value)
        comparison_html += '<table class="comparison-table">'
        comparison_html += '<thead><tr><th>Ebene</th><th>Du</th><th>Ø</th><th>Abweichung</th></tr></thead>'
        comparison_html += '<tbody>'
        diff_value_str = format_decimal_de(abs(diff_value), 1)
        comparison_html += (
            f'<tr>'
            f'<th scope="row">Gesamtergebnis</th>'
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
                difficulty_comparison_rows.append((
                    "★ Leicht",
                    easy_percent,
                    avg_stats["avg_difficulty"]["easy"],
                    easy_diff,
                ))
            if difficulty_stats["medium"]["gesamt"] > 0 and avg_stats['avg_difficulty']['medium'] > 0:
                medium_percent = (difficulty_stats["medium"]["richtig"] / difficulty_stats["medium"]["gesamt"] * 100)
                medium_diff = medium_percent - avg_stats['avg_difficulty']['medium']
                difficulty_comparison_rows.append((
                    "★★ Mittel",
                    medium_percent,
                    avg_stats["avg_difficulty"]["medium"],
                    medium_diff,
                ))
            if difficulty_stats["hard"]["gesamt"] > 0 and avg_stats['avg_difficulty']['hard'] > 0:
                hard_percent = (difficulty_stats["hard"]["richtig"] / difficulty_stats["hard"]["gesamt"] * 100)
                hard_diff = hard_percent - avg_stats['avg_difficulty']['hard']
                difficulty_comparison_rows.append((
                    "★★★ Schwer",
                    hard_percent,
                    avg_stats["avg_difficulty"]["hard"],
                    hard_diff,
                ))

            if difficulty_comparison_rows:
                comparison_html += '<table class="comparison-table comparison-difficulty-table">'
                comparison_html += '<caption class="comparison-subtitle">Nach Schwierigkeit</caption>'
                comparison_html += '<thead><tr><th>Schwierigkeit</th><th>Du</th><th>Ø</th><th>Abweichung</th></tr></thead>'
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

        comparison_html += f'<p class="comparison-footer">Basierend auf {avg_stats["total_users"]} Teilnehmer(n).<br>Stand der Vergleichsdaten: {generated_at_str}.</p>'
        comparison_html += '</div>'
    
    # Mini-Glossar erstellen (nach Themen gruppiert)
    glossary_by_theme = _extract_glossary_terms(questions)
    glossary_html = _build_glossary_html(glossary_by_theme)
    
    # Lesezeichen-Übersicht erstellen
    bookmarked_indices = st.session_state.get("bookmarked_questions", [])
    bookmarks_html = ""
    if bookmarked_indices:
        bookmarks_html = '<div class="bookmarks-overview">'
        bookmarks_html += '<h3>Markierte Fragen</h3>'
        bookmarks_html += '<p class="bookmark-intro">'
        bookmarks_html += 'Du hast folgende Fragen zur Wiederholung markiert:'
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
                    orig_num = int(questions[idx]["frage"].split(".", 1)[0])
                except (ValueError, IndexError):
                    orig_num = idx + 1
                # Kurzer Fragen-Preview
                frage_text = questions[idx]["frage"]
                frage_preview = frage_text.split(".", 1)[-1].strip()
                if len(frage_preview) > 60:
                    frage_preview = frage_preview[:60] + "..."

                # Parse Markdown und LaTeX im Preview
                frage_preview_parsed = _render_latex_in_html(frage_preview)

                bookmarks_html += f'<li><strong>Frage {test_num}</strong> '
                bookmarks_html += f'<span class="bookmark-ref">'
                bookmarks_html += f'(Fragenset-Nr. {orig_num})</span><br>'
                bookmarks_html += f'<span class="bookmark-preview">'
                bookmarks_html += f'{frage_preview_parsed}</span></li>'
        
        bookmarks_html += '</ul></div>'

    # Baue den HTML-Body mit professionellem Header
    score_percent_str = format_decimal_de(prozent, 1)
    
    rank_html = ''
    if user_rank:
        rank_html = f'<div class="stat-item"><div class="stat-value rank">#{user_rank}</div><div class="stat-label">Ranking (Stand: {generated_at_str.split(" ")[0]})</div></div>'
    html_body = f'''
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <h1>{header_title}</h1>{header_subtitle}
                    <div class="meta-info">
                        <span><strong>Teilnehmer:</strong> {user_name}</span>
                        <span><strong>Testdatum:</strong> {generated_at_str}</span>
                        {f'<span><strong>Dauer:</strong> {duration_str}</span>' if duration_str else ''}
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
                <div class="score-label">von {max_score} Punkten</div>
                <div class="score-percent">{score_percent_str} %</div>
            </div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value correct">✓ {richtige}</div>
                    <div class="stat-label">Richtig</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value wrong">✗ {falsche}</div>
                    <div class="stat-label">Falsch</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value unanswered">? {unbeantwortet}</div>
                    <div class="stat-label">Unbeantwortet</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(questions)}</div>
                    <div class="stat-label">Gesamt</div>
                </div>
                {rank_html}
            </div>
        </div>
        
        {weak_topics_html}
        
        {difficulty_html}
        
        {comparison_html}
        
        {bookmarks_html}
        
        <h2 class="section-title">Detaillierte Auswertung</h2>
    '''
    
    # initial_indices wurde bereits oben geholt für Lesezeichen
    # Sortiere Fragen nach Testreihenfolge (initial_indices)
    # Erstelle Liste von (test_position, original_index, frage_obj)
    questions_with_order = []
    for i, frage_obj in enumerate(questions):
        if i in initial_indices:
            test_position = initial_indices.index(i)
            questions_with_order.append((test_position, i, frage_obj))
    
    # Sortiere nach test_position
    questions_with_order.sort(key=lambda x: x[0])

    # Iteriere über sortierte Fragen
    for test_number, original_index, frage_obj in questions_with_order:
        # test_number ist bereits 0-basiert, also +1 für Anzeige
        display_test_number = test_number + 1
        
        # Original-Nummer (aus dem Fragentext)
        try:
            original_number = int(frage_obj["frage"].split(".", 1)[0])
        except (ValueError, IndexError):
            original_number = original_index + 1
        
        frage_text = _render_latex_in_html(frage_obj["frage"].split(". ", 1)[-1])
        
        # Bestimme Farbe und Status basierend auf richtig/falsch/unbeantwortet
        gegebene_antwort = get_answer_for_question(original_index)
        richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
        
        is_unanswered = gegebene_antwort is None
        ist_richtig = not is_unanswered and (gegebene_antwort == richtige_antwort_text)
        
        status_text = ""
        status_icon = ""
        status_class = ""
        if is_unanswered:
            border_color = "#0284c7"  # Blau für unbeantwortet
            status_text = "Unbeantwortet"
            status_icon = "?"
            status_class = "unanswered"
        elif ist_richtig:
            border_color = "#15803d"  # Dunkelgrün
            status_text = "Richtig"
            status_icon = "✔"
            status_class = "correct"
        else:
            border_color = "#b91c1c"  # Dunkelrot
            status_text = "Falsch"
            status_icon = "✗"
            status_class = "wrong"
        
        # NEU: Prüfen, ob die Frage markiert ist und Icon hinzufügen
        is_bookmarked = original_index in bookmarked_indices
        bookmark_icon_html = '<span class="bookmark-icon">🔖</span>' if is_bookmarked else ''
        
        # Schwierigkeits-Badge basierend auf Gewichtung
        gewichtung = frage_obj.get("gewichtung", 1)
        if gewichtung == 1:
            difficulty_badge = '<span class="difficulty-badge easy">★ Leicht</span>'
        elif gewichtung == 2:
            difficulty_badge = '<span class="difficulty-badge medium">★★ Mittel</span>'
        else:  # gewichtung >= 3
            difficulty_badge = '<span class="difficulty-badge hard">★★★ Schwer</span>'
        
        # Hole Thema
        thema = frage_obj.get("thema", "")
        
        # Starte Question-Box mit farbigem Rahmen
        html_body += f'<div class="question-box" style="border-left: 4px solid {border_color};">'
        
        # Status-Anzeige (Richtig, Falsch, Unbeantwortet)
        html_body += f'<div class="question-status {status_class}"><span class="status-icon">{status_icon}</span> {status_text}</div>'
        
        html_body += f'<div class="question-header">'
        html_body += f'Frage {display_test_number} / {len(questions)} '
        html_body += f'<span style="color:#6c757d; font-size:9pt; font-weight:400;">'
        html_body += f'(Fragenset-Nr. {original_number})</span> '
        html_body += f'{difficulty_badge}'
        html_body += bookmark_icon_html  # Füge das Lesezeichen-Icon hinzu
        html_body += f'</div>'
        
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

            html_body += f'<li class="{class_name}"><span class="prefix">{prefix}</span> {_render_latex_in_html(option)}</li>'
        html_body += "</ul>"

        erklaerung = frage_obj.get("erklaerung")
        if erklaerung:
            html_body += f'<div class="explanation"><strong>Erklärung:</strong> {_render_latex_in_html(erklaerung)}</div>'

        extended_explanation = frage_obj.get("extended_explanation")
        if extended_explanation and isinstance(extended_explanation, dict):
            title = extended_explanation.get('title') or extended_explanation.get('titel') or ''
            content = extended_explanation.get('content')
            steps = extended_explanation.get('schritte') if isinstance(extended_explanation.get('schritte'), list) else None

            explanation_html = '<div class="explanation"><strong>Detaillierte Erklärung'
            if title:
                explanation_html += f": {_render_latex_in_html(title)}"
            explanation_html += "</strong>"

            if steps:
                # Choose ordered vs unordered list depending on whether
                # the source steps contain explicit numbering (e.g. "1. ").
                list_tag = 'ol' if _steps_have_numbering(steps) else 'ul'
                explanation_html += f"<{list_tag} class='extended-steps'>"
                for step in steps:
                    item = _strip_leading_numbering(step) if list_tag == 'ol' else step
                    explanation_html += f"<li>{_render_latex_in_html(item)}</li>"
                explanation_html += f"</{list_tag}>"
            elif isinstance(content, str) and content.strip():
                explanation_html += "<br>" + _render_latex_in_html(content)

            explanation_html += "</div>"
            html_body += explanation_html
        
        # Schließe Question-Box
        html_body += '</div>'

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
                    content: "Seite " counter(page) " von " counter(pages);
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
        print(f"📊 PDF-Export abgeschlossen: {cache_size} Formeln gecacht")
    
    return pdf_bytes


def generate_mini_glossary_pdf(q_file: str, questions: List[Dict[str, Any]]) -> bytes:
    """
    Erstellt ein PDF mit allen Mini-Glossar-Einträgen eines Fragensets.
    """
    glossary_by_theme = _extract_glossary_terms(questions)
    if not glossary_by_theme:
        raise ValueError("Kein Mini-Glossar in diesem Fragenset vorhanden.")

    set_name = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    try:
        from helpers import format_datetime_de

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
        intro = (
            f'Schlüsselbegriffe aus dem Fragenset "{set_name}"'
            if includes_header
            else None
        )
        page_html = _build_glossary_html(
            page_themes,
            intro_text=intro,
            include_header=includes_header,
        )
        paginated_html.append(f'<div class="glossary-page">{page_html}</div>')

    glossary_html = "".join(paginated_html)

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
                    content: "Seite " counter(page) " von " counter(pages);
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
            <h1>Mini-Glossar</h1>
            <div class="meta-info">
                <span><strong>Fragenset:</strong> {set_name}</span>
                <span><strong>Stand:</strong> {generated_at}</span>
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
    set_name = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    try:
        from helpers import format_datetime_de

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
        f'<div class="header"><h1>Musterlösung</h1>'
        f'<div class="meta-info"><span><strong>Fragenset:</strong> {set_name}</span>'
        f'<span><strong>Erstellt:</strong> {generated_at}</span></div></div>'
    )
    html_parts.append('<div class="section">')

    # Nummeriere die Fragen fortlaufend in der Reihenfolge, wie sie hier übergeben werden
    for display_num, frage in enumerate(questions, start=1):
        # coarse progress report: parsing/rendering block per question
        _report(int((display_num - 1) / max(1, len(questions)) * 60), f"Verarbeite Frage {display_num}/{len(questions)}")
        frage_text = frage.get("frage", "")
        # Parst Markdown/LaTeX in sicheres HTML
        parsed_frage = _render_latex_in_html(
            frage_text.split('. ', 1)[-1] if '. ' in frage_text else frage_text,
            total_timeout=total_timeout,
        )

        html_parts.append('<div class="question">')
        html_parts.append(f'<h3>Frage {display_num} / {len(questions)}</h3>')
        html_parts.append(f'<div class="question-text">{parsed_frage}</div>')
        html_parts.append('<ul class="options">')

        correct_idx = frage.get("loesung")
        opts = frage.get("optionen", [])
        for oi, opt in enumerate(opts):
            parsed_opt = _render_latex_in_html(opt, total_timeout=total_timeout)
            if oi == correct_idx:
                html_parts.append(f'<li class="option correct">✔ {parsed_opt}</li>')
            else:
                html_parts.append(f'<li class="option">{parsed_opt}</li>')

        html_parts.append('</ul>')

        # Erklärung anzeigen, falls vorhanden
        erklaerung = frage.get("erklaerung")
        if erklaerung:
            html_parts.append(
                f'<div class="explanation"><strong>Erklärung:</strong> {_render_latex_in_html(erklaerung, total_timeout=total_timeout)}</div>'
            )

        # Erweiterte Erklärung
        extended_explanation = frage.get("extended_explanation")
        if extended_explanation and isinstance(extended_explanation, dict):
            title = extended_explanation.get('title') or extended_explanation.get('titel') or ''
            content = extended_explanation.get('content')
            steps = extended_explanation.get('schritte') if isinstance(extended_explanation.get('schritte'), list) else None

            explanation_html = '<div class="explanation"><strong>Detaillierte Erklärung'
            if title:
                explanation_html += f": {_render_latex_in_html(title)}"
            explanation_html += '</strong>'

            if steps:
                list_tag = 'ol' if _steps_have_numbering(steps) else 'ul'
                explanation_html += f'<{list_tag} class="extended-steps">'
                for step in steps:
                    item = _strip_leading_numbering(step) if list_tag == 'ol' else step
                    explanation_html += f'<li>{_render_latex_in_html(item, total_timeout=total_timeout)}</li>'
                explanation_html += f'</{list_tag}>'
            elif isinstance(content, str) and content.strip():
                explanation_html += '<br>' + _render_latex_in_html(content, total_timeout=total_timeout)

            explanation_html += '</div>'
            html_parts.append(explanation_html)

        html_parts.append('</div>')

    # report that question parsing is mostly done (~60%)
    _report(65, "Fragen verarbeitet, baue Glossar und HTML")

    html_parts.append('</div>')

    # Glossar anhängen
    glossary_by_theme = _extract_glossary_terms(questions)
    glossary_html = _build_glossary_html(glossary_by_theme)
    html_parts.append(glossary_html)

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
                    content: "Seite " counter(page) " von " counter(pages);
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
