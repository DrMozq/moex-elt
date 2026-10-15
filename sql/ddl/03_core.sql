CREATE TABLE IF NOT EXISTS core.daily_quotes (
    boardid             TEXT            NOT NULL,
    secid               TEXT            NOT NULL,
    trade_date          DATE            NOT NULL,
    shortname           TEXT            NOT NULL,
    open                NUMERIC,
    high                NUMERIC,
    low                 NUMERIC,
    close               NUMERIC,
    waprice             NUMERIC,
    legalcloseprice     NUMERIC,
    volume              BIGINT          NOT NULL,
    value               NUMERIC         NOT NULL,
    numtrades           INT             NOT NULL,
    currencyid          TEXT            NOT NULL,
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    PRIMARY KEY (boardid, secid, trade_date)
);