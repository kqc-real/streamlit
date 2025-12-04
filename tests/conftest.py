import sys
import os

# Ensure tests run the same when executed individually by
# making the repository root importable (so `import config` works).
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
