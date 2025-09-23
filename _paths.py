import os


def get_package_dir() -> str:
    """Return the package directory where mc_test_app files live.

    Robust fallback order:
    - dirname(__file__) if available and not empty
    - pkgutil loader filename (if available)
    - current working directory
    """
    # 1) try __file__
    try:
        dp = os.path.dirname(__file__)
        if dp:
            return dp
    except Exception:
        pass
    # 2) try pkgutil
    try:
        import pkgutil

        spec = pkgutil.get_loader("mc_test_app")
        if spec and hasattr(spec, "get_filename"):
            try:
                fn = spec.get_filename()
                dp = os.path.dirname(fn)
                if dp:
                    return dp
            except Exception:
                pass
    except Exception:
        pass
    # 3) fallback to cwd
    return os.getcwd()
