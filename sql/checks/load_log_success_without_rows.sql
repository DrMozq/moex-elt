SELECT DISTINCT l.as_of_date
FROM meta.load_log l
WHERE l.dataset = 'history'
  AND l.status = 'success'
  AND extract(isodow FROM l.as_of_date) < 6
  AND NOT EXISTS (
      SELECT 1 FROM core.daily_quotes q WHERE q.trade_date = l.as_of_date
  );