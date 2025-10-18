#!/usr/bin/env bash
# Run tests using the project's python interpreter and set PYTHONPATH to the project root.
set -euo pipefail

export PYTHONPATH=.
python -m pytest -q "$@"
