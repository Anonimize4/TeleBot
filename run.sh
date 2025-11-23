#!/usr/bin/env bash
set -euo pipefail

# Run script for KrisBot.
# Usage:
#   - Create a `.env` file containing TELEGRAM_BOT_API_TOKEN=your_token and run ./run.sh
#   - Or export TELEGRAM_BOT_API_TOKEN in your shell and run ./run.sh

# Load .env if present (simple KEY=VALUE parser, ignores comments)
if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "${TELEGRAM_BOT_API_TOKEN}" ]; then
  echo "ERROR: TELEGRAM_BOT_API_TOKEN is not set. Add it to .env or export it in your shell."
  exit 1
fi

PYTHON=./.venv/bin/python
if [ ! -x "$PYTHON" ]; then
  echo "Virtualenv python not found at $PYTHON. Activate your venv or run: python3 -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

exec "$PYTHON" "$(dirname "$0")/KrisBot.py"
