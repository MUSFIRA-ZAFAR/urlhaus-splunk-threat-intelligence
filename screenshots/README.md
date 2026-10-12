# Evidence screenshots

Selected from supplied screenshots. Crops remove surrounding UI only, without generating or changing evidence pixels. Query/output context is preserved. Originals are unchanged and not duplicated in this package. Token screens, repetitive clicks and AWS billing/personal-information screens are omitted.

| File | Step | Evidence |
|---|---|---|
| [01-hec-tls-verification.png](01-hec-tls-verification.png) | TLS | Certificate trust and IP validation returned Verification: OK. |
| [02-duplicate-import.png](02-duplicate-import.png) | TI11 | Identical reimport: three inserts, three duplicates, revision 1 retained. |
| [03-revision-history.png](03-revision-history.png) | TI16 | Controlled temporary DB update: revision 2, both payloads retained. |
| [04-delivery-pending.png](04-delivery-pending.png) | TI14 | Intentionally unreachable local port 1; pending after three attempts. |
| [05-delivery-recovered.png](05-delivery-recovered.png) | TI15 | Same test event accepted on attempt 4, error cleared. |
| [06-recovery-searchable.png](06-recovery-searchable.png) | TI15 | Recovered synthetic event searchable in ti_health. |
| [07-unit-tests.png](07-unit-tests.png) | TI24 | Ten original tests PASS; external HTTP failures mocked. |
| [08-correlation-six-cases.png](08-correlation-six-cases.png) | TI48 | Six synthetic cases, all expected classifications PASS. |
| [09-simulated-expiry.png](09-simulated-expiry.png) | TI49 | Search-only SIMULATED_EXPIRY: all six no_match, PASS. |
| [10-investigation-dashboard.png](10-investigation-dashboard.png) | TI70 | Four-panel dashboard: health, correlation, exact context and fresh lookup. |
| [11-free-license.png](11-free-license.png) | TI61 | Free license group visible; displayed date is not represented as actual expiry. |
| [12-reboot-services.png](12-reboot-services.png) | TI75 | New boot, enabled/active services and loopback ports. |
| [13-post-reboot-collector.png](13-post-reboot-collector.png) | TI76 | Automatic collection: 3 updated, 4 accepted; no pending group. |
| [14-post-reboot-search.png](14-post-reboot-search.png) | TI77 | Four post-reboot indexed events, copies=1 per event ID. |

`provenance.json` records original/output SHA-256 and crop rectangles. Captures show source-time state, not current live state. Browser addresses are absent from some original screenshots and therefore not proven by those images. Malicious URL text is retained as intelligence context; never follow those destinations.
