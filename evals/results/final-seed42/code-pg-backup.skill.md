I'll skip the scratchpad and just deliver the script directly in my reply.

Here's a complete, cron-ready nightly Postgres backup script:

```bash
#!/usr/bin/env bash
# backup_postgres.sh — nightly pg_dump with rotation, locking, and logging.
set -euo pipefail

# ---- Config (override via env vars or a /etc/postgres-backup.env file) ----
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-mydb}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
LOCK_FILE="${LOCK_FILE:-/var/run/postgres_backup.lock}"
LOG_FILE="${LOG_FILE:-/var/log/postgres_backup.log}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DUMP_FILE="${BACKUP_DIR}/${PGDATABASE}_${TIMESTAMP}.dump"

log() { echo "$(date '+%F %T') $*" | tee -a "$LOG_FILE" >&2; }

# ---- Prevent overlapping runs (e.g. if last night's backup is still running) ----
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
  log "ERROR: another backup is already running, exiting."
  exit 1
fi

mkdir -p "$BACKUP_DIR"

trap 'log "ERROR: backup failed (line $LINENO)."' ERR

log "Starting backup of database '$PGDATABASE' -> $DUMP_FILE"

# -Fc = custom format: compressed, supports parallel & selective restore.
pg_dump \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --format=custom \
  --file="$DUMP_FILE" \
  "$PGDATABASE"

log "Backup finished successfully ($(du -h "$DUMP_FILE" | cut -f1))."

# ---- Retention: delete dumps older than N days ----
find "$BACKUP_DIR" -name "${PGDATABASE}_*.dump" -mtime +"$RETENTION_DAYS" -print -delete \
  | while read -r f; do log "Deleted old backup: $f"; done

log "Retention cleanup done (keeping last ${RETENTION_DAYS} days)."
```

**Setup**

1. Auth without a password prompt — add a line to `~/.pgpass` (chmod `600`) instead of putting `PGPASSWORD` in the script or crontab:
   ```
   localhost:5432:mydb:postgres:yourpassword
   ```
2. Make it executable: `chmod +x backup_postgres.sh`
3. Cron entry for 2 AM nightly, with config overrides and output captured:
   ```cron
   0 2 * * * PGDATABASE=mydb BACKUP_DIR=/var/backups/postgres RETENTION_DAYS=14 /path/to/backup_postgres.sh >> /var/log/postgres_backup.log 2>&1
   ```

**Restore**

```bash
pg_restore --host=localhost --username=postgres --dbname=mydb --clean /var/backups/postgres/mydb_20261116_020000.dump
```

**Off-site copy** — a local backup doesn't survive a disk failure. Add a line after the dump succeeds, e.g. `aws s3 cp "$DUMP_FILE" s3://your-bucket/postgres-backups/` or `rclone copy "$BACKUP_DIR" remote:postgres-backups`.

Assumed: single database named `mydb` on localhost, Linux host with cron, auth via `.pgpass`, 14-day local retention. Adjust `PGDATABASE`/`RETENTION_DAYS`/paths or add `--all` dumps for multiple databases as needed.
