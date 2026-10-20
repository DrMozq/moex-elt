TRUNCATE mart.daily_returns;

INSERT INTO mart.daily_returns (
    boardid, secid, trade_date, shortname, security_class, listlevel,
    price, prev_trade_date, prev_price, daily_return_pct, value
)
WITH priced AS (
    SELECT
        boardid,
        secid,
        trade_date,
        shortname,
        legalcloseprice AS price,
        LAG(trade_date)      OVER w AS prev_trade_date,
        LAG(legalcloseprice) OVER w AS prev_price,
        value
    FROM core.daily_quotes
    WINDOW w AS (PARTITION BY boardid, secid ORDER BY trade_date)
)
SELECT
    p.boardid,
    p.secid,
    p.trade_date,
    COALESCE(s.shortname, p.shortname) AS shortname,
    s.security_class,
    s.listlevel,
    p.price,
    p.prev_trade_date,
    p.prev_price,
    round((p.price / NULLIF(p.prev_price, 0) - 1) * 100, 4) AS daily_return_pct,
    p.value
FROM priced p LEFT JOIN core.securities s
    ON s.boardid = p.boardid AND s.secid = p.secid;