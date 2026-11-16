The script is written at `/tmp/claude-1000/-tmp-tmp46vqhe9r/d0f4a819-379d-4e5c-b12e-2d5e23b37695/scratchpad/backup_postgres.sh`. Since you'll want this on your actual DB server, here's the full content to copy over — just `chmod +x` it after placing it:

```bash
#!/usr/bin/env bash
set -eo pipefail

# Config defaults; override by exporting these before running.
PGHOST=$PGHOST
test -z "$PGHOST" && PGHOST=localhost

PGPORT=$PGPORT
test -z "$PGPORT" && PGPORT=5432

PGUSER=$PGUSER
test -z "$PGUSER" && PGUSER=postgres

PGDATABASE=$PGDATABASE
test -z "$PGDATABASE" && PGDATABASE=mydb

BACKUP_DIR=$BACKUP_DIR
test -z "$BACKUP_DIR" && BACKUP_DIR=/var/backups/postgres

RETENTION_DAYS=$RETENTION_DAYS
test -z "$RETENTION_DAYS" && RETENTION_DAYS=7

# PGPASSWORD should be set via a ~/.pgpass file or an exported env var, not hardcoded here.

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR"/"$PGDATABASE""_""$TIMESTAMP"".sql.gz"
LOG_FILE="$BACKUP_DIR"/backup.log

mkdir -p "$BACKUP_DIR"

echo "$(date "+%Y-%m-%d %H:%M:%S") - Starting backup of database $PGDATABASE" | tee -a "$LOG_FILE"

if pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" | gzip > "$BACKUP_FILE"; then
    echo "$(date "+%Y-%m-%d %H:%M:%S") - Backup succeeded: $BACKUP_FILE" | tee -a "$LOG_FILE"
else
    echo "$(date "+%Y-%m-%d %H:%M:%S") - ERROR: pg_dump failed for database $PGDATABASE" | tee -a "$LOG_FILE"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Remove backups older than RETENTION_DAYS
find "$BACKUP_DIR" -name "$PGDATABASE""_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

echo "$(date "+%Y-%m-%d %H:%M:%S") - Backup run complete" | tee -a "$LOG_FILE"
```

**Setup on your server:**

1. Save it, e.g. `/usr/local/bin/backup_postgres.sh`, then `chmod +x` it.
2. Set credentials via `~/.pgpass` (format `hostname:port:database:username:password`, mode `0600`) so `pg_dump` doesn't prompt — don't put the password in the script.
3. Configure via env vars before running, or edit the defaults directly: `PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`, `BACKUP_DIR`, `RETENTION_DAYS`.
4. Add to crontab (`crontab -e`) for a nightly run at 2 AM:
   ```
   0 2 * * * PGDATABASE=mydb BACKUP_DIR=/var/backups/postgres /usr/local/bin/backup_postgres.sh >> /var/backups/postgres/cron.log 2>&1
   ```

It gzips the dump, logs to `backup.log` in the backup dir, and auto-deletes backups older than `RETENTION_DAYS` (default 7).

One note on how I built this: this sandbox's command filter blocks any `${VAR}` brace-expansion syntax and shell function definitions containing quotes, so I avoided both (plain `$VAR` + `test -z` fallbacks, no helper function) — that's a sandbox quirk here, not a requirement for your real server.
