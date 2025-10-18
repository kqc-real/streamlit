"""Manual test helper: create a temporary cache directory, populate it and run
the eviction routine. Uses a temp dir so the real cache is not touched.

Run like:

  PYTHONPATH=. python3 scripts/test_evict.py

This script is intentionally conservative and safe to run locally.
"""

import tempfile
import time
from pathlib import Path

from pdf_export import _evict_formula_cache


def _run():
    with tempfile.TemporaryDirectory(prefix='mc_test_cache_') as td:
        cache_dir = Path(td)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # create dummy files
        (cache_dir / 'test_small.png').write_bytes(b'x' * 1024)  # 1 KB
        (cache_dir / 'test_large.png').write_bytes(b'x' * 1024 * 1024 * 2)  # 2 MB
        (old := cache_dir / 'test_old.png').write_bytes(b'x' * 512)  # tiny

        # make the old file actually old
        old_time = time.time() - (10 * 24 * 3600)
        os_utime = time.__dict__.get('utime', None)
        try:
            # Prefer os.utime if available
            import os

            os.utime(old, (old_time, old_time))
        except Exception:
            # If utime fails, ignore — file mtime won't be old but test still valid
            pass

        print('CACHE_DIR (temp):', cache_dir)
        print('Before eviction:')
        for p in sorted(cache_dir.iterdir()):
            try:
                print(' ', p.name, p.stat().st_size, 'bytes', 'mtime=', time.ctime(p.stat().st_mtime))
            except Exception:
                print(' ', p.name, '<stat-failed>')

        # Call eviction — instruct the function to operate on our temp cache by
        # temporarily overriding the global FORMULA_CACHE_DIR in the module.
        import pdf_export
        old_cache = getattr(pdf_export, 'FORMULA_CACHE_DIR', None)
        try:
            pdf_export.FORMULA_CACHE_DIR = cache_dir
            _evict_formula_cache(max_files=1, max_total_mb=1, ttl_days=7)
        finally:
            pdf_export.FORMULA_CACHE_DIR = old_cache

        print('\nAfter eviction:')
        for p in sorted(cache_dir.iterdir()):
            try:
                print(' ', p.name, p.stat().st_size, 'bytes', 'mtime=', time.ctime(p.stat().st_mtime))
            except Exception:
                print(' ', p.name, '<stat-failed>')

        print('\nDone')


if __name__ == '__main__':
    _run()
