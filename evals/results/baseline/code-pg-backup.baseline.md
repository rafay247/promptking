That permission got denied in this sandbox — not a problem, you can chmod it yourself once you copy it over. Here's the finished script:

```bash
#!/usr/bin/env bash
set -uo pipefail

PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-mydb}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${PGDATABASE}_${TIMESTAMP}.sql.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"

mkdir -p "${BACKUP_DIR}"

NOW=$(date +%Y-%m-%dT%H:%M:%S)
echo "${NOW} Starting backup of database ${PGDATABASE}" >> "${LOG_FILE}"

if pg_dump -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" | gzip > "${BACKUP_FILE}"; then
    NOW=$(date +%Y-%m-%dT%H:%M:%S)
    echo "${NOW} Backup succeeded: ${BACKUP_FILE}" >> "${LOG_FILE}"
else
    NOW=$(date +%Y-%m-%dT%H:%M:%S)
    echo "${NOW} Backup FAILED" >> "${LOG_FILE}"
    rm -f "${BACKUP_FILE}"
    exit 1
fi

RETENTION_ARG="+${RETENTION_DAYS}"
find "${BACKUP_DIR}" -name "${PGDATABASE}_*.sql.gz" -mtime "${RETENTION_ARG}" -delete

NOW=$(date +%Y-%m-%dT%H:%M:%S)
echo "${NOW} Pruned backups older than ${RETENTION_DAYS} days" >> "${LOG_FILE}"
echo "${NOW} Backup job complete" >> "${LOG_FILE}"
```

It's saved at `/tmp/claude-1000/-tmp-tmp18sv9i0r/aef3d59a-6ebb-491a-9ca3-c4aafe2a1df3/scratchpad/backup_postgres.sh` in this sandbox, but that path is session-temporary — copy the content above into the actual location on your server.

**To use it:**
1. Save it somewhere like `/usr/local/bin/backup_postgres.sh`, then `chmod +x` it.
2. Set your DB credentials — either export `PGDATABASE`, `PGUSER`, etc. before calling it, or edit the defaults at the top. For the password, put it in `~/.pgpass` (format `host:port:database:user:password`, chmod 600) rather than hardcoding it — `pg_dump` picks it up automatically.
3. Add it to root's (or your DB user's) crontab to run nightly, e.g. at 2:00 AM:
   ```
   0 2 * * * /usr/local/bin/backup_postgres.sh
   ```
   Edit via `crontab -e`.

It dumps the DB, gzips it with a timestamped filename, logs each run to `backup.log` in the same directory, and deletes backups older than `RETENTION_DAYS` (default 7).
