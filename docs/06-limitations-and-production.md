# Implementation limits and production differences

## Actual limits

- Latest 3 URLs every 30 minutes: incomplete source coverage, missed records and no comprehensive refresh of historical provider records.
- Local 24-hour TTL: freshness policy, not a benignness verdict; provider status retained separately.
- At-least-once HEC delivery: ambiguous responses can duplicate indexed events. Stable IDs support SPL deduplication; no indexer ACK integration.
- Up to 1,000 pending rows selected per delivery run, three attempts per event. An early failure pauses later delivery; large backlogs can exceed the 180-second service timeout.
- Handled collection/delivery failures may exit 0; fatal storage/secret errors can bypass normal health reporting. A running collection record may remain unfinished after a fatal failure.
- Health is a before-delivery snapshot; no post-delivery live queue metric or complete error-branch testing.
- Conservative ASCII URL handling: no IDNA or complete percent-encoding/default-port equivalence normalization. It can miss equivalent URLs rather than modifying meaningful suffixes.
- Fixture seed assumptions: an unexpired domain, case-changeable path and variants absent from the snapshot. No empty-seed fallback. Saved fixture replay is stable; separate new runs are not deterministic.
- Empty/all-expired CSV behavior remains unverified; hostname matches have bounded lookup fan-out. Multiple records sharing one URL need an explicit aggregate policy beyond the original unique seed validation.
- History survives only within retention/capacity. Accepted payloads and run records are not pruned; disk grows. Full retention/restore policy and historical temporal correlation are incomplete.
- Splunk Free lacks user authentication/alerting. Loopback fits local clients, not remote production collectors. CLI hostname validation and certificate renewal monitoring remain separate gaps.
- All components share one host/failure domain. No throughput, high availability or production deployment claim.
- Original Splunk exports and clean rebuild remain outstanding. Reconstructed SPL is labeled as such; original code was not modified by packaging.

## Production direction — not deployed

| Need | Production change |
|---|---|
| Source coverage | Supported bulk/delta mechanism, checkpoints, provider update/removal tracking and coverage measurement |
| Durable distributed delivery | Broker/outbox, independent consumers, backpressure, deduplication and acknowledgment reconciliation |
| Availability | Separate failure domains, verified backup/restore and capacity planning |
| Access security | Organization identity/roles, private routing and managed TLS |
| Detection quality | Real telemetry normalization, source confidence, allowlists, match specificity and historic validity |
| Monitoring | Post-delivery queue depth, failure rate, last success, certificate expiry and meaningful failure exits |
| Lifecycle | Storage budgets, revision retention, expiry/reappearance policies and auditable cleanup |
| Testing | Representative replay/load, outages, ambiguous-response and restore tests, measured SLOs |

No extra servers, paid APIs or AI subscription were added. AI summaries remain an optional, unimplemented extension requiring a budget check and comparison to the non-AI workflow.
