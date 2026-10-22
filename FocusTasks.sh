#!/usr/bin/env bash
set -e
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$APP_DIR/focus_tasks.py" "$@"
