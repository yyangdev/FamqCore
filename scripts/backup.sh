#!/usr/bin/env bash
set -Eeuo pipefail

DB_PATH=${DB_PATH:-./src/app/database/database.db}
BACKUP_DIR=${BACKUP_DIR:-./backups}
RETENTION=${RETENTION:-14}

[[ -r "$DB_PATH" ]] || { echo "Database not found: $DB_PATH" >&2; exit 1; }
mkdir -p "$BACKUP_DIR"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
out="$BACKUP_DIR/database-$timestamp.db"
# SQLite's online backup API produces a consistent copy while the bot is live.
python - "$DB_PATH" "$out" <<'PY'
import sqlite3, sys
source, target = sys.argv[1:]
with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
    src.backup(dst)
PY

find "$BACKUP_DIR" -maxdepth 1 -type f -name 'database-*.db' -printf '%T@ %p\n' \
  | sort -nr | tail -n +$((RETENTION + 1)) | cut -d' ' -f2- \
  | xargs -r rm -f
printf 'Created %s (kept %s backups)\n' "$out" "$RETENTION"
