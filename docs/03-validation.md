# Validation and evidence record

| Step | Test type | Verified result | Screenshot |
|---|---|---|---|
| TLS verification | Live local HTTPS | Trusted certificate and IP validation: Verification OK | 01 |
| TI11 | Identical import | 3 inserts; second import 3 duplicates; revision 1 retained | 02 |
| TI16 | Controlled temporary DB | Update reaches revision 2; both distinct payloads retained | 03 |
| TI14 | Controlled unavailable endpoint | Local port 1 substituted for HEC; pending, 3 attempts, ConnectionError | 04 |
| TI15 | Live recovery | Same event accepted on cumulative attempt 4, error cleared, searchable | 05–06 |
| TI24 | Mocked HTTP and temp DB | 10 tests pass; API 401/429/invalid JSON/timeout; HEC 429/503 persistence and recovery | 07 |
| TI48 | Synthetic indexed events | 6 expected classifications PASS: 1 exact, 3 hostname, 2 nonmatches | 08 |
| TI49 | Search-only expiry simulation | Found expiry fields overridden to now minus 60s; all 6 no_match; original CSV/SQLite unchanged | 09 |
| TI70 | Live dashboard | Health success, six PASS rows, exact context, fresh lookup with 35 rows | 10 |
| TI61 | License | Free group visible, no violations in that snapshot | 11 |
| TI75 | Actual reboot | Boot 19:01:14 UTC; both units enabled/active; listeners loopback | 12 |
| TI76 | Automatic post-reboot run | 19:02:28 UTC: fetched 3, rejected 0, updated 3, accepted 4; queue 67 accepted and no pending group | 13 |
| TI77 | Splunk search | 3 IOC + 1 health rows from 19:02–19:03 UTC, one copy each | 14 |

Screenshot numbers map to [the evidence catalog](../screenshots/README.md). Counts are observations at capture time, not fixed expectations for every later feed response. No malicious connection, malware execution, compromise, throughput or real-attack detection accuracy is claimed.

## Re-run the original suite

**Ubuntu, repo root, virtual environment active:**

```bash
set -o pipefail
PYTHONPATH=src python -m unittest discover -s tests -v
```

Ten unittest methods are included. HEC cooldown tests exercise 429 and 503 as subcases, close/reopen SQLite, confirm no request during cooldown, and confirm acceptance after its deadline. HTTP is mocked; no external feed requests are made by the test suite. Original EC2 outputs are under `docs/evidence/`.

During package review, the same 10 methods also passed locally on Python 3.12 with the recorded dependency versions. That is an offline portability check, not an additional EC2 end-to-end run. Its exact output is recorded separately.

## Outstanding validation

- All-expired/empty active CSV handling: `create_empty=true` can create a zero-length lookup. Current searches check expiry but empty-file behavior is not proven.
- No-data/stale-feed/error health branches: not all have controlled tests. A real stale lookup was observed after the Free transition, before ownership repair.
- Acceptance followed by lost response: explained as at-least-once risk, not preserved as a completed test.
- Port-1 failure is simulated unavailability, not a delivery run while Splunk itself was stopped.
- Historical as-of-time correlation and reappearance after expiry are not implemented/tested.
- Original Splunk dashboard/config exports, consistent database backup and restore remain unverified.
- Overnight stopped-state, current credit balance and final AWS cleanup remain unverified.
- Clean rebuild and a live mock interview remain outstanding.

Ad hoc duplicate/update checks have screenshots but were not supplied as additional automated test files. These gaps are not part of the passed-results table.
