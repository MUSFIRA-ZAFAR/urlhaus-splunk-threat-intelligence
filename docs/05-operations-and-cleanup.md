# Operations, troubleshooting and cost control

## Read-only checks — Ubuntu

```bash
systemctl is-enabled Splunkd.service ti-collector.timer
systemctl is-active Splunkd.service ti-collector.timer
systemctl list-timers ti-collector.timer --no-pager
sudo journalctl -u ti-collector.service -b --no-pager -n 40
sudo ss -lntp | grep -E ':(8000|8088|8089)\b'
```

Health snapshots are before-delivery, not real-time queue state. Check the SQLite outbox and cooldowns for current state without printing secret files. Rotating application logs are configured at 1 MiB with three backups; actual rollover was not tested. Individual delivery error prints reach the journal, but do not all use the rotating logger.

| Symptom | Focused check | Action |
|---|---|---|
| Pending / ConnectionError | HEC listener, service and endpoint | Restore availability; retain pending work and honor cooldown |
| SSLError | Trust file, expiry and SAN | Correct trust/certificate, never disable verification |
| API 401 | Private Auth-Key and current access | Fix credentials; honor stored cooldown |
| API 429 / HEC 503 | Retry-After and persistent deadline | Wait for allowed retry; do not repeatedly hammer the endpoint |
| HEC success, no search result | Response code, event ID, target index and time | Acceptance is not proof of indexing |
| Stale report after Free | Scheduler logs and effective owner | Repair exact orphaned owner under valid admin, then confirm success |
| Service says success, collection failed | Journal, collection_runs and outbox | Some handled failures exit 0; service status alone is insufficient |
| Old fixture no longer matches | TTL, lookup freshness and fixture seed | Expired intelligence is excluded; regenerate only as a new labeled run |
| Tunnel fails after Stop/start | Current public DNS and SSH /32 rule | Update connection details and reopen tunnel |

## Export before terminating — still outstanding

1. Preserve repo, screenshots, runtime fixture/snapshot and original dashboard XML/report/lookup exports on Windows.
2. Stop the collector timer and confirm no collection is running. Use SQLite's backup API for consistent database copies. Do not copy only the main file while omitting a live WAL. Include the synthetic database separately if needed.
3. Export indexed Splunk evidence if needed; a configuration-only backup does not contain index data.
4. Keep secrets/private Splunk backups outside Git. The earlier full Splunk `etc` backup contains sensitive configuration and was not restore-tested.
5. Check archive integrity, row counts and restoration from an isolated copy before deleting cloud storage.

Example indicator backup **from the repo root**, after confirming the collector is inactive:

```bash
sudo systemctl stop ti-collector.timer
PYTHONPATH=src .venv/bin/python - <<'PY'
import json, sqlite3, os
from pathlib import Path
from storage import open_database
os.umask(0o077)
cfg=json.loads(Path('config/lab.json').read_text())
folder=Path.home()/'.local/state/ti-lab/backups'
folder.mkdir(parents=True,exist_ok=True,mode=0o700)
destination=folder/'indicators-export.sqlite3'
if destination.exists():
    raise SystemExit('Backup exists: choose another filename')
source=open_database(cfg['database_file'])
target=sqlite3.connect(destination)
source.backup(target)
print('integrity:',target.execute('PRAGMA integrity_check').fetchone()[0])
target.close();source.close()
PY
```

This backup example has not been executed on EC2 in the preserved evidence. Restart the timer if continuing the lab after backup.

## Overnight stop and final cleanup

**AWS Console:** EC2 → Instances → select the project instance → Instance state → Stop instance → normal Stop. Preserve a screenshot of **Stopped**. The overnight stop instruction was issued, but its final state was not evidenced.

Stopping compute preserves EBS and continuing storage charges. Review associated Elastic IPs if any; this lab used an auto-assigned public address. Before restarting, recheck credits/Free Plan expiry, current public DNS and SSH source IP. No old balance is treated as current.

After verified exports, terminate only the project instance when no longer needed. Verify its delete-on-termination EBS is removed and review leftover project volumes/snapshots/IPs. Check billing/credits again. Do not delete unrelated older resources without identifying their purpose and obtaining scope authorization. No successful cleanup or zero final bill is claimed.
