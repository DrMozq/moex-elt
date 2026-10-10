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