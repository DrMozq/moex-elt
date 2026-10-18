CREATE TABLE IF NOT EXISTS meta.load_log (
    id              BIGINT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset         TEXT            NOT NULL,
    board           TEXT            NOT NULL,
    trade_date      DATE            NOT NULL,
    status          TEXT            NOT NULL CHECK (status IN ('success', 'failed')),
    rows_loaded     INT,
    error           TEXT,
    logged_at       TIMESTAMPTZ     NOT NULL DEFAULT now()
);