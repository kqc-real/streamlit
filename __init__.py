"""mc_test_app package initializer.

Expose internal submodules (mc_test_app, core, leaderboard, review) as
attributes on the package object. This uses importlib to avoid circular
import issues when the package is being initialized during tests.

If loading submodules fails (flat layout or other import issues), we
silently continue — tests will fall back to flat imports.
"""
from importlib import import_module
import sys
import importlib.util
import os

_SUBMODULES = [
    "mc_test_app",
    "core",
    "leaderboard",
    "review",
]

# Ensure the package object itself (sys.modules[__name__]) receives attributes
_pkg = sys.modules.get(__name__)
for _m in _SUBMODULES:
    try:
        mod = import_module(f"mc_test_app.{_m}")
        # assign both to globals() and to the package module object
        globals()[_m] = mod
        if _pkg is not None:
            setattr(_pkg, _m, mod)
    except Exception:
        # If importing the submodule fails, attempt a file-based fallback
        # for the main script module (`mc_test_app.py`) so patch() can
        # resolve `mc_test_app.mc_test_app` during tests.
        if _m == "mc_test_app":
            try:
                base_dir = os.path.dirname(__file__)
                file_path = os.path.join(base_dir, "mc_test_app.py")
                if os.path.isfile(file_path):
                    spec = importlib.util.spec_from_file_location("mc_test_app.mc_test_app", file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # Ensure sys.modules entry for import mechanisms
                        sys.modules["mc_test_app.mc_test_app"] = module
                        spec.loader.exec_module(module)  # type: ignore[attr-defined]
                        globals()[_m] = module
                        if _pkg is not None:
                            setattr(_pkg, _m, module)
                        continue
            except Exception:
                pass
        # ignore other submodule import errors (flat layout supported)
        pass

__all__ = ["mc_test_app", "core", "leaderboard", "review"]

