SELECT count(*) AS missing_securities
FROM (
    SELECT boardid, secid FROM core.daily_quotes
    WHERE trade_date = (SELECT max(trade_date) FROM core.daily_quotes)
    EXCEPT
    SELECT boardid, secid FROM core.securities
) AS missing
HAVING count(*) > 5;