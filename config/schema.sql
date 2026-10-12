CREATE TABLE IF NOT EXISTS indicators (
    ioc_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    indicator_type TEXT NOT NULL CHECK(indicator_type = 'url'),
    original_url TEXT NOT NULL,
    normalized_url TEXT NOT NULL,
    hostname TEXT NOT NULL,
    provider_date_added TEXT NOT NULL,
    provider_status TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    collected_at REAL NOT NULL,
    expires_at REAL NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    UNIQUE(source, source_record_id)
);

CREATE TABLE IF NOT EXISTS outbox (
    event_id TEXT PRIMARY KEY,
    ioc_id TEXT REFERENCES indicators(ioc_id),
    target_index TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'accepted')),
    attempts INTEGER NOT NULL DEFAULT 0,
    accepted_at REAL,
    last_error TEXT
);

CREATE INDEX IF NOT EXISTS outbox_pending
    ON outbox(status, created_at);

CREATE TABLE IF NOT EXISTS collection_runs (
    run_id TEXT PRIMARY KEY,
    started_at REAL NOT NULL,
    finished_at REAL,
    status TEXT NOT NULL,
    fetched INTEGER NOT NULL DEFAULT 0,
    rejected INTEGER NOT NULL DEFAULT 0,
    error TEXT
);
