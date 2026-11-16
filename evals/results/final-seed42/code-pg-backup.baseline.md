Saved at `/tmp/claude-1000/-tmp-tmp6rt-ei29/b01a778c-28d8-46d9-b4e6-fceaa411f1c4/scratchpad/pg_backup.sh`. To use it on your actual server:

**1. Copy it to the server and set it up:**
```bash
sudo mkdir -p /opt/scripts
sudo cp pg_backup.sh /opt/scripts/
sudo chmod +x /opt/scripts/pg_backup.sh
```

**2. Configure credentials** — either export env vars before running, or (recommended) create a `~/.pgpass` file so the password isn't in plaintext env vars:
```
# ~/.pgpass (chmod 600)
localhost:5432:mydb:postgres:yourpassword
```
Then just set `PGHOST`, `PGUSER`, `PGDATABASE` as needed (drop `PGPASSWORD`).

**3. Schedule it nightly via cron** (e.g. 2 AM):
```bash
crontab -e
```
Add:
```
0 2 * * * PGDATABASE=mydb BACKUP_DIR=/var/backups/postgres /opt/scripts/pg_backup.sh >> /var/log/pg_backup.log 2>&1
```

**What it does:**
- Dumps the DB with `pg_dump`, gzips it, timestamps the filename
- Fails loudly (non-zero exit, logged) if `pg_dump` is missing or the dump fails, and cleans up partial files
- Deletes backups older than `RETENTION_DAYS` (default 7) so disk doesn't fill up

Want me to add off-site upload (S3/GCS) or restore instructions too?
