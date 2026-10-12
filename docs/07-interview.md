# Portfolio walkthrough and interview preparation

## Truthful CV bullets

- Built an authenticated Python URLhaus collector with conservative URL normalization, revisioned SQLite storage and a persistent delivery outbox for Splunk HEC.
- Validated six synthetic DNS/proxy correlation cases in Splunk, distinguishing exact URL matches, hostname associations and nonmatches; documented controlled expiry and retry-recovery tests.
- Configured local HEC certificate verification, loopback-only Splunk access and systemd automation; verified collection and searchable ingestion after an EC2 reboot.

Do not claim comprehensive feed coverage, prevented attacks, real compromise detection, exactly-once delivery, production scale or performance measurements.

## Questions and concise model answers

**Why SQLite before Splunk?** Indicator and immutable outbox payload commit together; pending work survives delivery failure/restart. SQLite stores state; Python retries.

**Does HEC success prove searchability?** No. It proves acceptance observed by the client. I separately searched event IDs; indexer ACK is not enabled.

**Can stable IDs prevent all duplicates?** No. Lost responses can cause retries after acceptance. The same ID supports result deduplication, while each revision has its own ID.

**Why not lowercase the full URL?** Paths and query values may be case-sensitive. Original URLs are retained, and only scheme/authority are lowercased.

**Why distinguish exact URL from hostname matches?** A full URL identifies a resource; a hostname may host benign content. DNS alone also does not establish a connection. Both need investigation.

**What happens after expiry?** Current correlation excludes expired latest revisions. Retained history remains available subject to retention. Historic as-of-time correlation is future work.

**Why loopback plus SSH?** All clients are local/tunneled. Loopback adds a barrier against accidental network exposure, especially because Free has no Web login.

**What would you improve first?** Coverage, empty-lookup handling, explicit failure signaling/post-delivery health and verified exports/restore; then production identity, availability and load testing.

## Demonstration order

1. Operational question and architecture.
2. Normalization, atomic storage and stable revisions.
3. Pending → retry recovery → searchable proof.
4. Six synthetic classifications and expiry simulation.
5. Investigation dashboard and reboot recovery.
6. Coverage/delivery/history/licensing limits.

This is a preparation guide. A live mock interview has not yet been completed.
