moex-elt/
├── app/
│   ├── __init__.py
│   ├── __main__.py точка входа: разбор аргументов командной строки
│   ├── config.py настройки из окружения (база, API, стартовая дата)
│   ├── log.py    настройка логирования
│   ├── errors.py иерархия исключений
│   ├── http.py  ApiClient: сессия, таймауты, повторы, 429
│   ├── moex.py всё что знает про API биржи: пути, пагинация, формат
│   ├── raw.py  запись и чтение сырых JSONL-файлов
│   ├── db.py   подключение, транзакции, COPY, запуск .sql-файлов
│   ├── state.py         журнал загрузок и watermark
│   └── pipeline.py      сборка шагов в один запуск
├── sql/
│   ├── ddl/             создание схем и таблиц
│   │   ├── 01_schemas.sql
│   │   ├── 02_stg.sql
│   │   ├── 03_core.sql
│   │   └── 04_meta.sql
│   ├── transform/       staging → core
│   ├── marts/           витрины
│   └── checks/          проверки качества
├── data/raw/            в Git не попадает
├── .env / .env.example
├── .gitignore
├── requirements.txt
└── README.md

{'BOARDID': 'TQBR', 'TRADEDATE': '2026-10-06', 'SHORTNAME': 'iАРТГЕН ао', 'SECID': 'ABIO', 'NUMTRADES': 648, 'VALUE': 2464024.08, 'OPEN': 44.6, 'LOW': 44.12, 'HIGH': 44.82, 'LEGALCLOSEPRICE': 44.44, 'WAPRICE': 44.38, 'CLOSE': 44.44, 'VOLUME': 55519, 'MARKETPRICE2': 44.38, 'MARKETPRICE3': 44.38, 'ADMITTEDQUOTE': None, 'MP2VALTRD': 1097132.54, 'MARKETPRICE3TRADESVALUE': 1097132.54, 'ADMITTEDVALUE': None, 'WAVAL': 0, 'TRADINGSESSION': 3, 'CURRENCYID': 'SUR', 'TRENDCLSPR': 0.05, 'TRADE_SESSION_DATE': '2026-10-06'}