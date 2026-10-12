# Setup and reproduction

These are reproduction instructions, not a claim that a clean rebuild was demonstrated. Original source/tests/config are preserved from the uploaded archive. Documentation and examples were assembled afterward.

## Cost and infrastructure

**AWS Console:** Billing and Cost Management → Free Tier and Credits. Verify the actual plan, remaining credits, plan expiry and credit expiry before restarting/provisioning. Do not upgrade to a Paid Plan. The demonstrated environment was one Ubuntu 26.04 LTS x86-64 EC2 server, 2 vCPU / 8 GiB and 30 GiB encrypted gp3. Recheck AWS availability/pricing and official Splunk OS support for a new build. Credit-funded EC2/EBS/IPv4 usage is not permanently free.

Security group: inbound SSH 22 only from the administrator's current public IP /32. Do not publicly expose Web 8000, HEC 8088 or management 8089.

## Python and database

**Ubuntu:** install Python/venv/Git through Ubuntu's package manager if absent. Place the repo at `/home/ubuntu/ti-urlhaus-lab` to match the included units; adapt user/path settings for other accounts.

```bash
cd /home/ubuntu/ti-urlhaus-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
python -m pip check
mkdir -p ~/.config/ti-lab ~/.local/state/ti-lab state
chmod 700 ~/.config/ti-lab ~/.local/state/ti-lab
```

The collector opens a database but does **not** initialize its schema. Before first collection:

```bash
PYTHONPATH=src python - <<'PY'
import json
from pathlib import Path
from storage import open_database
config=json.loads(Path('config/lab.json').read_text())
db=open_database(config['database_file'])
db.execute('PRAGMA journal_mode=WAL')
db.executescript(Path('config/schema.sql').read_text())
print('integrity:', db.execute('PRAGMA integrity_check').fetchone()[0])
db.close()
PY
```

`cooldowns` is created by the cooldown module on first use. The original requirements record the tested environment. If a pinned version becomes unavailable, select and verify a replacement explicitly.

## Splunk preparation

Install the official Linux x86-64 package, verify its official checksum and run it as the dedicated `splunk` OS account. Version 10.6.0.5 was demonstrated; its installer is not bundled.

Create indexes `ti_urlhaus`, `ti_health` and `ti_synthetic`. The collector HEC token permits the first two; the separate synthetic token permits only `ti_synthetic`. Enable HTTPS HEC on 8088. Indexer acknowledgment was disabled in the lab.

Generate/configure a local HEC certificate with SAN `DNS:localhost,IP:127.0.0.1` using current Splunk TLS instructions. The private combined PEM on the demonstrated host was `/opt/splunk/etc/auth/ti-lab/hec.pem`; its public certificate was copied to `~/.config/ti-lab/hec.crt` for collector trust. Private material is excluded from this repo.

The demonstrated settings were:

```ini
# /opt/splunk/etc/apps/ti_lab_tls/local/inputs.conf
[http]
serverCert = /opt/splunk/etc/auth/ti-lab/hec.pem
sslPassword =

# /opt/splunk/etc/apps/ti_lab_tls/local/web.conf
[settings]
server.socket_host = 127.0.0.1
mgmtHostPort = 127.0.0.1:8089
```

Set `SPLUNK_BINDIP = 127.0.0.1` in `/opt/splunk/etc/splunk-launch.conf`. Back up existing files and reconcile conflicting values rather than appending duplicates. Keep TLS private files restricted to the Splunk OS user.

**Windows PowerShell:** replace both placeholders with the actual values, then leave the tunnel open:

```powershell
ssh -i "C:\path\ti-splunk-key.pem" -N -L 127.0.0.1:18000:127.0.0.1:8000 -o ExitOnForwardFailure=yes ubuntu@CURRENT_PUBLIC_DNS
```

Open `http://127.0.0.1:18000`. Stop/start normally changes the auto-assigned public address, so check the Console before reconnecting.

## Private credentials and first collection

Obtain an Auth-Key through the official URLhaus access process; check current community-access and fair-use conditions. Keep credential values out of configuration/Git. Use a hidden prompt:

```bash
python - <<'PY'
import getpass, os
from pathlib import Path
os.umask(0o077)
folder=Path.home()/'.config/ti-lab'
folder.mkdir(mode=0o700,parents=True,exist_ok=True)
for name in ('urlhaus.key','hec.token','synthetic-hec.token'):
    value=getpass.getpass(f'{name}: ').strip()
    if not value:
        raise SystemExit('Empty credential: stopped')
    (folder/name).write_text(value+'\n')
    (folder/name).chmod(0o600)
PY
```

Review `config/lab.json` and place the trusted public certificate at its configured path.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python src/collector.py
```

Check the SQLite queue and then searchable events by ID. Exit status alone is insufficient: some handled failures currently exit 0.

## Automation

After a successful manual run and indexing verification:

```bash
sudo cp config/systemd/ti-collector.service /etc/systemd/system/
sudo cp config/systemd/ti-collector.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ti-collector.timer
```

Register Splunk with systemd using its documented stop-first procedure:

```bash
sudo -u splunk /opt/splunk/bin/splunk stop
sudo /opt/splunk/bin/splunk enable boot-start -systemd-managed 1 -user splunk -group splunk
sudo systemctl enable --now Splunkd.service
```

Build the lookup, report and dashboard using [Splunk instructions](../splunk/README.md). Free removes user authentication/alerting but supports scheduled searches for dashboard maintenance. Keep the report's effective owner valid (`admin` in this Free lab); do not rely on an orphaned pre-Free named user.

## Synthetic fixtures

Export the active lookup as CSV to `state/ti-active-snapshot.csv` with fields from the refresh search. It needs an unexpired domain seed with a usable case-sensitive path. The runtime snapshot is not bundled.

```bash
python src/generate_synthetic.py
python src/send_synthetic.py
```

Preserve `state/synthetic-events.json` for retries. Each new fixture has a random run ID; event IDs remain stable when replaying that saved fixture. Replace the captured run ID in the SPL with the new one. Generation refuses to overwrite existing fixtures. No real connection to IOC destinations occurs.

A clean installation, dashboard recreation and restore from this package remain to be verified; documentation does not close those evidence gaps.
