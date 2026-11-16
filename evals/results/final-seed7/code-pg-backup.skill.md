Here's a complete, runnable nightly PostgreSQL backup script with rotation, locking, and logging:

```bash
#!/usr/bin/env bash
# pg_backup.sh - nightly PostgreSQL backup with rotation and locking.
set -euo pipefail

# ---- Configuration (override via env vars or a sourced .env file) ----
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-mydb}"            # a real db name, or "all" to dump every db
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
LOG_FILE="${LOG_FILE:-/var/log/pg_backup.log}"
LOCK_FILE="${LOCK_FILE:-/var/lock/pg_backup.lock}"

# Auth: put host:port:db:user:password lines in ~/.pgpass (chmod 600) instead
# of a password env var here. PGPASSFILE defaults to that file automatically.

mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

log() {
  echo "$(date +%Y-%m-%d_%H:%M:%S) [$$] $*" | tee -a "$LOG_FILE"
}

cleanup_old_backups() {
  find "$BACKUP_DIR" -maxdepth 1 -name "*.dump" -mtime +"$RETENTION_DAYS" -print -delete \
    | while read -r f; do log "Deleted old backup: $f"; done
}

run_backup() {
  local db=$1
  local timestamp
  timestamp=$(date +%Y%m%d_%H%M%S)
  local outfile="$BACKUP_DIR/${db}_${timestamp}.dump"
  local tmpfile="$outfile.tmp"

  log "Starting backup of database $db to $outfile"

  if pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$db" -F c --compress=9 -f "$tmpfile"; then
    mv "$tmpfile" "$outfile"
    log "Backup succeeded: $outfile ($(du -h "$outfile" | cut -f1))"
  else
    rm -f "$tmpfile"
    log "ERROR: pg_dump failed for database $db"
    return 1
  fi
}

backup_globals() {
  # Per-database dumps don't include roles/tablespaces - capture them separately.
  local outfile="$BACKUP_DIR/globals_$(date +%Y%m%d_%H%M%S).sql"
  if pg_dumpall -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" --globals-only -f "$outfile"; then
    log "Globals backup succeeded: $outfile"
  else
    log "ERROR: pg_dumpall --globals-only failed"
    return 1
  fi
}

main() {
  log "=== Backup job started ==="

  local databases=()
  if [[ "$PGDATABASE" == "all" ]]; then
    mapfile -t databases < <(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -Atc \
      "SELECT datname FROM pg_database WHERE datistemplate = false;")
  else
    databases=("$PGDATABASE")
  fi

  local failures=0

  if [[ "$PGDATABASE" == "all" ]]; then
    backup_globals || failures=$((failures + 1))
  fi

  for db in "${databases[@]}"; do
    run_backup "$db" || failures=$((failures + 1))
  done

  cleanup_old_backups

  if [[ "$failures" -gt 0 ]]; then
    log "=== Backup job finished with $failures failure(s) ==="
    exit 1
  fi

  log "=== Backup job finished successfully ==="
}

# Prevent overlapping runs if a previous backup is still in progress.
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  log "Another backup run is already in progress - exiting."
  exit 1
fi

main
```

**Setup:**
```bash
chmod +x pg_backup.sh
# ~/.pgpass (chmod 600): localhost:5432:*:postgres:yourpassword
```

**Cron (nightly at 2:15 AM)** — edit with `crontab -e`:
```
15 2 * * * PGDATABASE=all BACKUP_DIR=/var/backups/postgres /path/to/pg_backup.sh
```
Locking is handled inside the script, so no `flock` wrapper is needed in the crontab line itself.

**Restore:**
```bash
pg_restore -h localhost -U postgres -d targetdb --clean --if-exists /var/backups/postgres/mydb_20261116_021500.dump
```
Custom format (`-F c`) is used instead of plain SQL or an external gzip step because it's already compressed, supports parallel restore (`-j 4`) and selective table/schema restore via `-l`/`-L`.

**Off-site copy:** this script only protects against local disk/accidental-delete failure. Add a line after `cleanup_old_backups` (or a separate cron job) to push `$BACKUP_DIR` to remote storage, e.g. `aws s3 sync "$BACKUP_DIR" s3://[your-bucket]/pg-backups/` or `rclone sync`.

Assumed: single Postgres instance with `.pgpass`-based auth, local disk retention of 14 days, and that you'll add your own off-site sync target — none of these were specified.
