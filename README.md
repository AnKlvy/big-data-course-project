# Heart Sounds Analytics Project

Проект реализует ETL-пайплайн: выгрузка данных из SQLite, трансформация через PySpark, сохранение в Parquet, визуализация дашборда через Streamlit.

## Требования

- Python 3.10+
- Java JDK 17+ (обязательно для PySpark)
- Устанавливать Hadoop или Spark отдельно **не нужно** — всё включено в `pyspark`

> На Windows `winutils.exe` и `hadoop.dll` скачиваются автоматически при первом запуске.

## Установка

1. Склонировать репозиторий:

```bash
git clone https://github.com/AnKlvy/big-data-course-project.git
cd big-data-course-project
```

2. Создать виртуальное окружение и активировать его:

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

3. Установить зависимости:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Запуск

### Шаг 1 — ETL (извлечение, трансформация, загрузка в Parquet)

```bash
python main.py
```

При первом запуске автоматически:
- скачивается `sqlite-jdbc-3.42.0.0.jar` в папку `jars/`
- генерируется база данных `data/raw/heart_sounds.db` (если отсутствует)
- на Windows скачиваются `winutils.exe` и `hadoop.dll` в `jars/hadoop/bin/`
- результат сохраняется в `data/processed/parquet/`

### Шаг 2 — Дашборд

```bash
streamlit run app.py
```

Открыть в браузере: [http://localhost:8501](http://localhost:8501)

## Структура проекта

```
big-data-course-project/
├── app.py              # Streamlit-дашборд
├── main.py             # ETL точка входа
├── dataset.py          # Генерация SQLite БД
├── requirements.txt
├── spark_app/
│   ├── spark_session.py  # Инициализация SparkSession (с winutils для Windows)
│   ├── extract.py        # Чтение из SQLite
│   ├── transform.py      # Трансформации данных
│   └── load.py           # Запись в Parquet
├── jars/
│   ├── sqlite-jdbc-3.42.0.0.jar  # скачивается автоматически
│   └── hadoop/bin/               # winutils.exe, hadoop.dll (только Windows, авто)
└── data/
    ├── raw/heart_sounds.db       # генерируется автоматически
    └── processed/parquet/        # результат ETL
```

## Известные предупреждения (не ошибки)

- `WARN NativeCodeLoader: Unable to load native-hadoop library` — безвредно, Spark использует встроенные Java-классы
- `WARN SparkEnv: Exception while deleting Spark temp dir` — безвредно, Windows не отпускает JAR-файл сразу после завершения
