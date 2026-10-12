# Engineering decisions

| Decision | Purpose | Implemented behavior |
|---|---|---|
| Official API | Structured, authenticated source | Exact recent/limit/3 endpoint; Auth-Key from private file |
| Original URL and raw metadata retained | Preserve investigative provenance | SQLite `original_url` and `metadata_json`; raw metadata in revision payload |
| Conservative normalization | Avoid altering case-sensitive resources | Lowercase scheme/authority; preserve path/query; remove fragment from matching value only |
| Stable identities | Separate revisions from retries | IOC SHA-256(`URLhaus:<source ID>`); event SHA-256(`<IOC ID>:<revision>`) |
| Transactional outbox | Indicator commit must include delivery work | `BEGIN IMMEDIATE` wraps indicator upsert and immutable payload insert |
| Pending state retained | Survive delivery failures | Stored payload, attempt count and last error |
| Persistent cooldowns | Restart must not bypass Retry-After | Per-scope deadline in SQLite; module creates table |
| Separate synthetic pipeline | Keep activity distinct from intelligence | Dedicated index/token/database and `synthetic=true` |
| Local-only Splunk | Restrict exposure with Free's unauthenticated Web | All three ports on loopback; administrator uses SSH tunnel |

## Delivery guarantees

`accepted` means the client observed HTTP 200 and HEC JSON code 0, then committed that result. It does not establish searchability or durable indexing. Indexer ACK was not enabled. Separate event-ID searches proved indexing for the observed runs.

If HEC accepts an event but the response is lost, SQLite remains pending. A retry sends the same event ID and can create duplicates in Splunk. `dedup event_id` suppresses duplicate correlation results; it does not erase duplicate indexed events. Each updated revision has its own ID and must remain historically distinguishable.

SQLite stores retry state; Python performs retries. The timer schedules Python. No database background worker independently sends events.

## Revisions, expiry and provider status

An identical record reimported with the same collection time is a duplicate. A later collection changes collection/expiry timestamps and creates another revision even if provider fields are unchanged. Revision detection is not provider-only.

The active lookup first selects the latest revision, then checks its 24-hour local TTL. Filtering before selecting could resurrect an older unexpired revision. Provider `online`, `offline` and `unknown` are retained but not used as the sole membership condition. Local expiry is not proof of benignness.

Splunk metadata also uses the field `source`. To recover the provider name, the refresh search extracts raw JSON `source` into `intel_source` with `spath`, separately from HEC metadata `source=urlhaus_collector`.

## Security and health

Secrets reside under `~/.config/ti-lab/` (700 directory, 600 files), outside Git. HEC certificate trust and IP validation were confirmed through OpenSSL, and Python uses the configured trust file. A CLI hostname-validation warning observed during administration is a separate setting; it is not fixed by Python HEC certificate verification.

Loopback prevents direct remote access but cannot defend against a compromised local account. Remote production collectors need restricted private-network HEC access.

Health snapshots are recorded before delivery. Newly collected work legitimately appears pending. These snapshots do not show the current post-delivery queue, and are supplemented by local SQLite checks and the journal.
