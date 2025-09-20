import os
import sys

"""Test path setup.

Previously we prepended both the package directory and repository root to sys.path.
On GitHub Actions the repository folder name is `streamlit`, which shadows the real
third-party `streamlit` library when placed at the front of sys.path, leading to:
    AttributeError: module 'streamlit' has no attribute 'set_page_config'

Fix: Prepend only the mc_test_app package directory. Append (not prepend) the repo
root only if needed for the flat-layout fallback AND if its basename does not clash
with an installed dependency we rely on (e.g. 'streamlit').
"""

TESTS_DIR = os.path.dirname(__file__)
PKG_DIR = os.path.dirname(TESTS_DIR)   # .../mc_test_app
REPO_ROOT = os.path.dirname(PKG_DIR)

if PKG_DIR not in sys.path:
    sys.path.insert(0, PKG_DIR)

# Add repo root only if mc_test_app is not a subdir there (flat layout case)
# and avoid adding if it would shadow the external streamlit package.
root_name = os.path.basename(REPO_ROOT)
if (root_name != "streamlit") and (REPO_ROOT not in sys.path):
    sys.path.append(REPO_ROOT)
