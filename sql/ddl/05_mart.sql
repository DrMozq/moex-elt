CREATE TABLE IF NOT EXISTS mart.daily_returns (
    boardid             TEXT            NOT NULL,
    secid               TEXT            NOT NULL,
    trade_date          DATE            NOT NULL,
    shortname           TEXT            NOT NULL,
    security_class      TEXT,
    listlevel           SMALLINT,
    price               NUMERIC,
    prev_trade_date     DATE,
    prev_price          NUMERIC,
    daily_return_pct    NUMERIC,
    value               NUMERIC         NOT NULL,
    built_at            TIMESTAMPTZ     NOT NULL DEFAULT now(),
    PRIMARY KEY (boardid, secid, trade_date)
);