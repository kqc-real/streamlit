import os
import sys

# Ensure repository root is on sys.path so that `mc_test_app` package resolves
TESTS_DIR = os.path.dirname(__file__)
PKG_DIR = os.path.dirname(TESTS_DIR)          # .../mc_test_app
REPO_ROOT = os.path.dirname(PKG_DIR)          # repository root
for p in (PKG_DIR, REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)
