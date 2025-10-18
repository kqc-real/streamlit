import os
import time
import pathlib

from pdf_export import FORMULA_CACHE_DIR, _evict_formula_cache

CACHE_DIR = pathlib.Path(FORMULA_CACHE_DIR)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# clean up any previous test artifacts
for p in CACHE_DIR.glob('test_*'):
    try:
        p.unlink()
    except Exception:
        pass

# create dummy files
(small := CACHE_DIR / 'test_small.png').write_bytes(b'x' * 1024)  # 1 KB
(large := CACHE_DIR / 'test_large.png').write_bytes(b'x' * 1024 * 1024 * 2)  # 2 MB
(old := CACHE_DIR / 'test_old.png').write_bytes(b'x' * 512)  # tiny

# make the old file actually old
old_time = time.time() - (10 * 24 * 3600)
os.utime(old, (old_time, old_time))

print('CACHE_DIR:', CACHE_DIR)
print('Before eviction:')
for p in sorted(CACHE_DIR.iterdir()):
    print(' ', p.name, p.stat().st_size, 'bytes', 'mtime=', time.ctime(p.stat().st_mtime))

# run eviction with very small limits to force deletions
_evict_formula_cache(max_files=1, max_total_mb=1, ttl_days=7)

print('\nAfter eviction:')
for p in sorted(CACHE_DIR.iterdir()):
    print(' ', p.name, p.stat().st_size, 'bytes', 'mtime=', time.ctime(p.stat().st_mtime))

print('\nDone')
