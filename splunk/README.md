# Splunk integration and dashboard recreation

SPL files reconstruct documented searches. They are **not an export** of the original Splunk app. Exact original dashboard XML, metadata, savedsearches and transforms exports remain outstanding.

## Lookup and report

1. Search & Reporting → run `searches/refresh-active-lookup.spl`. It replaces `ti_active_urls.csv` in the project app.
2. Settings → Lookups → Lookup definitions → create `ti_active_urls` using that CSV; enable case-sensitive matching. Share the file and definition globally.
3. Save refresh search as **TI - Refresh active URL lookup**, app `search`, run as Owner, all-time range, cron `*/5 * * * *`, globally shared. After Free migration verify effective owner `admin`.
4. Confirm scheduler success and CSV refresh age. A saved schedule is not proof of execution. Empty/all-expired lookup behavior is still unverified.

## Dashboard recreation

Create a Classic dashboard **Threat Intelligence Lab**, globally shared, with these table panels:

| Panel | Search |
|---|---|
| Collector Health — Before Delivery Snapshot | `collector-health.spl` |
| Synthetic Activity — IOC Correlation | `correlation-six-cases.spl` |
| Exact URL Matches — Investigation Context | `exact-investigation-context.spl` |
| Active IOC Lookup — Freshness | `lookup-freshness.spl` |

Replace the example captured run ID with your new fixture ID. Configure the display timezone to UTC to match the evidence; `strftime` itself uses the configured search timezone. Old fixtures may stop matching after expiry. The exact-context search reconstructs shown fields/results and must be checked during recreation; it is not independently redeployed/exported XML.

## Free transition finding

HEC token authorization, search and dashboard remained operational under Free. The scheduled refresh initially failed because its pre-Free named owner was orphaned. UI permission/reassignment required unavailable Auth functionality. The exact saved-search metadata owner was backed up and changed to valid `admin` while Splunk was stopped; a later scheduled run succeeded.

Do not perform broad metadata substitution. Back up and export the exact report section before an ownership repair. This host's observed fix is not a universal migration script. No email/page alert, enterprise user roles or AI Assistant entitlement is claimed.
