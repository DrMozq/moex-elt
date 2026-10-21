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

CREATE TABLE IF NOT EXISTS mart.market_daily (
    boardid             TEXT            NOT NULL,
    trade_date          DATE            NOT NULL,
    securities_count    INT             NOT NULL,
    traded_count        INT             NOT NULL,
    advancers           INT             NOT NULL,
    decliners           INT             NOT NULL,
    unchanged           INT             NOT NULL,
    total_value         NUMERIC         NOT NULL,
    avg_return_pct      NUMERIC,
    median_return_pct   NUMERIC,
    built_at            TIMESTAMPTZ     NOT NULL DEFAULT now(),
    PRIMARY KEY (boardid, trade_date)
);

CREATE TABLE IF NOT EXISTS mart.top_movers (
    period        TEXT         NOT NULL,
    direction     TEXT         NOT NULL,
    rank          SMALLINT     NOT NULL,
    boardid       TEXT         NOT NULL,
    secid         TEXT         NOT NULL,
    shortname     TEXT         NOT NULL,
    start_date    DATE         NOT NULL,
    end_date      DATE         NOT NULL,
    start_price   NUMERIC      NOT NULL,
    end_price     NUMERIC      NOT NULL,
    return_pct    NUMERIC      NOT NULL,
    built_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (period, direction, rank)
);
