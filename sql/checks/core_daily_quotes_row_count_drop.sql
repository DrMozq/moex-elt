WITH daily AS (
    SELECT trade_date, count(*) AS row_count
    FROM core.daily_quotes
    GROUP BY trade_date
),
compared AS (
    SELECT
        trade_date,
        row_count,
        LAG(row_count) OVER (ORDER BY trade_date) AS prev_row_count
    FROM daily
)
SELECT trade_date, row_count, prev_row_count
FROM compared
WHERE row_count < prev_row_count * 0.9
    AND trade_date > (SELECT max(trade_date) FROM core.daily_quotes) - 14;
