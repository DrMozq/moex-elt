TRUNCATE mart.market_daily;

INSERT INTO mart.market_daily (
    boardid, trade_date, securities_count, traded_count,
    advancers, decliners, unchanged, total_value,
    avg_return_pct, median_return_pct
)
SELECT
    boardid,
    trade_date,
    count(*)                                                    AS securities_count,
    count(*) FILTER (WHERE value > 0)                           AS traded_count,
    count(*) FILTER (WHERE value > 0 AND daily_return_pct > 0)  AS advancers,
    count(*) FILTER (WHERE value > 0 AND daily_return_pct < 0)  AS decliners,
    count(*) FILTER (WHERE value > 0 AND daily_return_pct = 0)  AS unchanged,
    sum(value)                                                  AS total_value,
    round(avg(daily_return_pct) FILTER (WHERE value > 0), 4)    AS avg_return_pct,
    round(
        (percentile_cont(0.5) WITHIN GROUP (ORDER BY daily_return_pct)
            FILTER (WHERE value > 0))::numeric, 4
    )                                                           AS median_return_pct
FROM mart.daily_returns
WHERE security_class IN ('common_share', 'preferred_share', 'depositary_receipt')
GROUP BY boardid, trade_date;