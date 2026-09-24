#!/usr/bin/env bash
set -euo pipefail

SRC="${1:?usage: backup.sh SRC DEST}"
DEST="${2:?usage: backup.sh SRC DEST}"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$DEST"
tar -czf "$DEST/backup-$STAMP.tar.gz" -C "$SRC" .
echo "wrote $DEST/backup-$STAMP.tar.gz"
find "$DEST" -name 'backup-*.tar.gz' -mtime +14 -delete
