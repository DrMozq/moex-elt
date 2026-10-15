INSERT INTO core.daily_quotes (
    boardid, secid, trade_date, shortname,
    open, high, low, close, waprice, legalcloseprice,
    volume, value, numtrades, currencyid
)
SELECT
    boardid,
    secid,
    tradedate::date,
    shortname,
    open::numeric,
    high::numeric,
    low::numeric,
    close::numeric,
    waprice::numeric,
    legalcloseprice::numeric,
    volume::bigint,
    value::numeric,
    numtrades::int,
    currencyid
FROM stg.history
ON CONFLICT (boardid, secid, trade_date) DO UPDATE SET
    shortname       = excluded.shortname,
    open            = excluded.open,
    high            = excluded.high,
    low             = excluded.low,
    close           = excluded.close,
    waprice         = excluded.waprice,
    legalcloseprice = excluded.legalcloseprice,
    volume          = excluded.volume,
    value           = excluded.value,
    numtrades       = excluded.numtrades,
    currencyid      = excluded.currencyid,
    updated_at      = now();