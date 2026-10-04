#!/usr/bin/env bash
set -euo pipefail

# Resolve the repository from this file so callers can use any working directory.
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repo_root"

python_bin=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && \
        "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
        python_bin="$candidate"
        break
    fi
done

if [[ -z "$python_bin" ]]; then
    printf '%s\n' 'Python 3.11 or newer is required. Install Python with the venv module, then rerun this script.' >&2
    exit 1
fi

"$python_bin" --version
if [[ ! -d .venv ]]; then
    # All project tools use the standard library; no package downloads are needed.
    "$python_bin" -m venv --without-pip .venv
fi

if [[ ! -x .venv/bin/python ]]; then
    printf '%s\n' '.venv is not a usable Linux/macOS environment. Rename it and rerun this script to create a fresh environment.' >&2
    exit 1
fi

.venv/bin/python -c 'import sys; sys.exit(".venv requires Python 3.11 or newer; recreate it before running setup.") if sys.version_info < (3, 11) else None'
.venv/bin/python scripts/validate_data.py --quick
printf '%s\n' 'Setup complete. Use .venv/bin/python for project commands.'
