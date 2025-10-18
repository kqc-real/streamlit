import threading
import tempfile
import time
from pathlib import Path

import pdf_export


def _populate_cache(dirpath: Path, count: int = 10):
    for i in range(count):
        p = dirpath / f'test_{i}.png'
        p.write_bytes(b'x' * (512 + (i % 5) * 100))


def test_eviction_tolerates_concurrent_deletes():
    """Simulate concurrent deletions while eviction runs; eviction must not raise."""
    with tempfile.TemporaryDirectory(prefix='mc_test_cache_') as td:
        cache_dir = Path(td)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # populate with files
        _populate_cache(cache_dir, count=30)

        # start a deleter thread that will remove files while eviction runs
        def deleter():
            # wait a tiny bit for eviction to start
            time.sleep(0.02)
            for idx, p in enumerate(list(cache_dir.glob('*.png'))):
                try:
                    if idx % 3 == 0:
                        p.unlink()
                except Exception:
                    pass
                # small pause to increase interleaving
                time.sleep(0.001)

        deleter_thread = threading.Thread(target=deleter)
        deleter_thread.start()

        # Temporarily switch module cache dir to our temp dir
        old_cache = getattr(pdf_export, 'FORMULA_CACHE_DIR', None)
        try:
            pdf_export.FORMULA_CACHE_DIR = cache_dir
            # Should complete without raising
            pdf_export._evict_formula_cache(max_files=5, max_total_mb=1, ttl_days=7)
        finally:
            pdf_export.FORMULA_CACHE_DIR = old_cache

        deleter_thread.join()
