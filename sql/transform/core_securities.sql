INSERT INTO core.securities (
    boardid, secid, shortname, secname, latname,
    isin, regnumber, sectype, security_class,
    listlevel, lotsize, facevalue, faceunit, currencyid,
    decimals, minstep, issuesize, status, last_seen_date
)
SELECT
    boardid,
    secid,
    shortname,
    secname,
    latname,
    isin,
    regnumber,
    sectype,
    CASE sectype
        WHEN '1' THEN 'common_share'
        WHEN '2' THEN 'preferred_share'
        WHEN 'D' THEN 'depositary_receipt'
        WHEN 'J' THEN 'fund'
        WHEN '9' THEN 'fund'
        WHEN 'A' THEN 'fund'
        WHEN 'B' THEN 'fund'
        ELSE 'other'
    END AS security_class,
    listlevel::smallint,
    lotsize::int,
    facevalue::numeric,
    faceunit,
    currencyid,
    decimals::smallint,
    minstep::numeric,
    issuesize::bigint,
    status,
    substring(source_file FROM '(\d{4}-\d{2}-\d{2})\.jsonl$')::date AS last_seen_date
FROM stg.securities
ON CONFLICT (boardid, secid) DO UPDATE SET
    shortname      = excluded.shortname,
    secname        = excluded.secname,
    latname        = excluded.latname,
    isin           = excluded.isin,
    regnumber      = excluded.regnumber,
    sectype        = excluded.sectype,
    security_class = excluded.security_class,
    listlevel      = excluded.listlevel,
    lotsize        = excluded.lotsize,
    facevalue      = excluded.facevalue,
    faceunit       = excluded.faceunit,
    currencyid     = excluded.currencyid,
    decimals       = excluded.decimals,
    minstep        = excluded.minstep,
    issuesize      = excluded.issuesize,
    status         = excluded.status,
    last_seen_date = excluded.last_seen_date,
    updated_at     = now();