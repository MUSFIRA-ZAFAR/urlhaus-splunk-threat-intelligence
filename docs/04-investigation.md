# Analyst investigation workflow

| Result | Meaning | Further evidence needed in a real SOC |
|---|---|---|
| Exact URL | Proxy record matches an active normalized URL IOC | Proxy disposition, user/device/process, transfer and execution evidence |
| Hostname-only | Host associated with an active URL IOC | Full URL, DNS answer, shared-hosting context and actual connection evidence |
| No match | No active match under these rules | Other sources, expired history and telemetry completeness |

The six recorded events are synthetic and assigned to `synthetic-device-01`. They do not demonstrate an infected endpoint. The matched hostname was a shared hosting provider: an IOC for one hosted path does not label the entire provider malicious.

## Triage sequence

1. Verify the synthetic flag, activity type, event time, device and match specificity.
2. Inspect original provider URL, source record ID, status, collection time, revision and TTL; check feed and lookup freshness.
3. In real logs, pivot to proxy action/status/bytes, DNS answers, user identity, endpoint process lineage and file/hash events. Those telemetry sources are not integrated in this lab.
4. Assess benign explanations and surrounding activity. DNS resolution alone is weaker evidence than a full proxy URL.
5. Document confidence, missing evidence and recommended next action. Automatic isolation is not implemented.

## Expired intelligence

Expiry removes an IOC from current active correlation, not from retained historical outbox payloads or indexed history. Expired does not mean proven benign. History exists only as long as capacity, retention and exports preserve it.

For a past event, choose the latest revision collected **at or before that event time**, then test that revision's expiry. Today's latest revision is not automatically the right historic context. Provider date_added and collector collection time are distinct: a local collection/TTL window cannot establish the complete maliciousness timeline.

Historic intelligence was viewed in the lab, but an as-of-time temporal correlation and reappearance-after-expiry scenario were not implemented/tested. Search-only expiry testing proves exclusion from current matching, not full historical investigation.

Never browse the reported malicious URL for this lab. Use retained metadata and authorized telemetry; malicious destination strings in screenshots are evidence data.
