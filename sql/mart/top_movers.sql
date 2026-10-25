TRUNCATE mart.top_movers;


INSERT INTO mart.top_movers (
    period, direction, rank,
    boardid, secid, shortname,
    start_date, end_date,
    start_price, end_price, return_pct
)
WITH periods AS (
    SELECT p.period, p.days,
           (SELECT max(trade_date) FROM mart.daily_returns) AS end_date
    FROM (VALUES ('1W', 7), ('1M', 30), ('3M', 90)) AS p(period, days)
),
bounds AS (
    SELECT period, end_date,
           (SELECT max(trade_date) FROM mart.daily_returns
            WHERE trade_date <= end_date - days) AS start_date
    FROM periods
),
returns AS (
    SELECT
        b.period, b.start_date, b.end_date,
        e.boardid, e.secid, e.shortname,
        s.price AS start_price,
        e.price AS end_price,
        (e.price / NULLIF(s.price, 0) - 1) * 100 AS return_pct
    FROM bounds b
        JOIN mart.daily_returns e ON e.trade_date = b.end_date
        JOIN mart.daily_returns s
            ON s.trade_date = b.start_date AND s.boardid = e.boardid AND s.secid = e.secid
    WHERE e.listlevel = 1
      AND e.security_class IN ('common_share', 'preferred_share', 'depositary_receipt')
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY period ORDER BY return_pct DESC, secid) AS gain_rank,
           ROW_NUMBER() OVER (PARTITION BY period ORDER BY return_pct ASC,  secid) AS loss_rank
    FROM returns
    WHERE return_pct IS NOT NULL
)
SELECT period, 'gain', gain_rank,
       boardid, secid, shortname,
       start_date, end_date,
       start_price, end_price, round(return_pct, 4) as return_pct
FROM ranked
WHERE gain_rank <= 10 AND return_pct > 0

UNION ALL

SELECT period, 'loss', loss_rank,
       boardid, secid, shortname,
       start_date, end_date,
       start_price, end_price, round(return_pct, 4) as return_pct
FROM ranked
WHERE loss_rank <= 10 AND return_pct < 0;
