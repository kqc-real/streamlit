"""Simple background job manager for long-running exports.

This module provides a tiny in-memory job manager that runs export jobs
in separate processes (multiprocessing). A finished PDF is written to
the `exports/` directory and the parent process monitors the child and
updates an in-memory job table. The design intentionally avoids
cross-process callbacks or shared memory — the child simply writes its
result to disk and the monitor thread marks the job finished.
"""

from typing import Callable, Optional, Dict
import threading
import uuid
import os
from pathlib import Path
import multiprocessing
import sys
import concurrent.futures

# Configurable worker count (not used for processes; kept for compatibility)
_MAX_WORKERS = int(os.getenv('EXPORT_JOB_WORKERS', '2'))

# Jobs stored in-memory: job_id -> metadata
_jobs: Dict[str, Dict] = {}
_jobs_lock = threading.Lock()

# Directory to persist finished export PDFs so results survive restarts
_EXPORTS_DIR = Path(
    os.getenv('EXPORTS_DIR', os.path.join(os.getcwd(), 'exports'))
)
_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _make_job_id() -> str:
    return uuid.uuid4().hex


def _proc_runner(
    job_id: str, func: Callable, args: tuple, kwargs: dict
) -> None:
    """Module-level function executed inside the child process.

    It calls the provided `func` with the given args/kwargs. If the
    function returns bytes, those are written to the exports directory
    as `muster_{job_id}.pdf`.
    """
    result = func(*args, **kwargs)
    if isinstance(result, (bytes, bytearray)) and len(result) > 0:
        filename = f"muster_{job_id}.pdf"
        result_path = str(_EXPORTS_DIR.joinpath(filename))
        with open(result_path, 'wb') as f:
            f.write(result)


def start_musterloesung_job(func: Callable, *args, **kwargs) -> str:
    """Start a background export job running `func(*args, **kwargs)`.

    The function runs in a separate process. Returns the job_id which
    can be polled with `get_job_status`.
    """
    job_id = _make_job_id()

    job_entry = {
        "status": "queued",
        "progress": 0,
        "message": "queued",
        # On finish we will write result to disk and set 'result_path'
        "result": None,
        "result_path": None,
        "exception": None,
        "process": None,
        "future": None,
    }

    with _jobs_lock:
        _jobs[job_id] = job_entry
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["message"] = "started"

    # If running from an interactive stdin (no __main__.__file__), the
    # 'spawn' start method cannot locate the main script — fall back to
    # a thread-based execution for this environment so tests can run.
    main_file = getattr(sys.modules.get('__main__'), '__file__', None)
    if not main_file:
        # Interactive / stdin-based environment: run exporter in a
        # background thread so tests can execute in this environment.
        def _start_interactive_thread():
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = executor.submit(_proc_runner, job_id, func, args, kwargs)
            # Store the future so cancel_job can attempt cancellation.
            with _jobs_lock:
                _jobs[job_id]["future"] = future

            # Start a monitor thread to wait for the future and update
            # status.
            def _monitor_future():
                try:
                    future.result()
                    path_obj = _EXPORTS_DIR.joinpath(
                        f"muster_{job_id}.pdf"
                    )
                    result_path = str(path_obj)
                    with _jobs_lock:
                        if path_obj.exists():
                            _jobs[job_id]["status"] = "finished"
                            _jobs[job_id]["progress"] = 100
                            _jobs[job_id]["message"] = "finished"
                            _jobs[job_id]["result_path"] = result_path
                        else:
                            _jobs[job_id]["status"] = "failed"
                            _jobs[job_id]["message"] = "no_result_file"
                except Exception as e:
                    with _jobs_lock:
                        _jobs[job_id]["status"] = "failed"
                        _jobs[job_id]["message"] = f"exception:{e}"

            threading.Thread(target=_monitor_future, daemon=True).start()

        _start_interactive_thread()
    else:
        # Spawn a separate process to run the exporter. Prefer the 'fork'
        # start method when available (useful for interactive / stdin-based
        # runs). Fall back to the default context otherwise.
        try:
            ctx = multiprocessing.get_context('fork')
        except (ValueError, RuntimeError):
            # Fallback to default context if 'fork' isn't available.
            ctx = multiprocessing.get_context()

        proc = ctx.Process(
            target=_proc_runner, args=(job_id, func, args, kwargs)
        )
        proc.daemon = True
        proc.start()

        with _jobs_lock:
            _jobs[job_id]["process"] = proc

        # Monitor the process in a background thread — when it exits we
        # check for the produced file and update job metadata.
        def _monitor_proc():
            proc.join()
            path_obj = _EXPORTS_DIR.joinpath(f"muster_{job_id}.pdf")
            result_path = str(path_obj)
            with _jobs_lock:
                if proc.exitcode == 0 and path_obj.exists():
                    _jobs[job_id]["status"] = "finished"
                    _jobs[job_id]["progress"] = 100
                    _jobs[job_id]["message"] = "finished"
                    _jobs[job_id]["result"] = None
                    _jobs[job_id]["result_path"] = result_path
                else:
                    _jobs[job_id]["status"] = "failed"
                    _jobs[job_id]["message"] = (
                        f"process_exitcode={proc.exitcode}"
                    )

        threading.Thread(target=_monitor_proc, daemon=True).start()

    return job_id


def get_job_status(job_id: str) -> Optional[dict]:
    """Return a small status view for the given job_id.

    Returns a dict with keys 'status','progress','message','result'
    where 'result' for finished jobs is either an in-memory value or
    the filesystem path to the persisted PDF.
    """
    with _jobs_lock:
        je = _jobs.get(job_id)
        if not je:
            return None
        out = {
            "status": je.get("status"),
            "progress": je.get("progress", 0),
            "message": je.get("message", ""),
            "exception": je.get("exception"),
        }
        if je.get("status") == "finished":
            out["result"] = je.get("result") or je.get("result_path")
        else:
            out["result"] = None
        return out


def cancel_job(job_id: str) -> bool:
    """Attempt to cancel a job.

    Best-effort: only returns True if the job exists and the process has
    not yet started. We avoid forcibly terminating child processes by
    default.
    """
    with _jobs_lock:
        je = _jobs.get(job_id)
        if not je:
            return False
        proc = je.get("process")
        if proc is None:
            # Not started yet — remove from table
            _jobs.pop(job_id, None)
            return True
        # If process exists and is alive we do not cancel it here.
        if proc.is_alive():
            return False
        # Process finished; cannot cancel.
        return False
