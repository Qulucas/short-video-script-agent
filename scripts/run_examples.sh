#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m src.cli batch --cases examples/cases --provider fixture --out-root runs
