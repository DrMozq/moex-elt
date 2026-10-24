(SELECT boardid, secid, trade_date FROM core.daily_quotes
 EXCEPT
 SELECT boardid, secid, trade_date FROM mart.daily_returns)
UNION ALL
(SELECT boardid, secid, trade_date FROM mart.daily_returns
 EXCEPT
 SELECT boardid, secid, trade_date FROM core.daily_quotes);