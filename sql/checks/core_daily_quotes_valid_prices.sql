SELECT boardid, secid, trade_date, low, high, legalcloseprice
FROM core.daily_quotes
WHERE legalcloseprice <= 0 OR low > high;
