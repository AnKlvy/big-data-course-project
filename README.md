# Heart Sounds Analytics Project

Проект реализует ETL-пайплайн: выгрузка данных из SQLite, трансформация через PySpark, сохранение в Parquet, визуализация дашборда через Streamlit.

## Требования

| Способ запуска | Что нужно |
|---|---|
| Docker Compose | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| Локально | Python 3.10+, Java JDK 17+ |

Устанавливать Hadoop или Spark отдельно **не нужно** — всё включено в `pyspark`.

> На Windows при локальном запуске `winutils.exe` и `hadoop.dll` скачиваются автоматически.

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

### Вариант 1 — Docker Compose (рекомендуется)

Требуется только [Docker Desktop](https://www.docker.com/products/docker-desktop/).
Java, Python и все зависимости устанавливаются внутри контейнера автоматически.

**1. Собрать образ** (SQLite JDBC JAR скачивается при сборке):

```bash
docker-compose build
```

**2. Запустить ETL-пайплайн** (генерация БД + Spark-трансформация, ~12.7 млн записей):

```bash
docker-compose run --rm etl
```

**3. Запустить дашборд:**

```bash
docker-compose up dashboard
```

Открыть в браузере: [http://localhost:8501](http://localhost:8501)

Данные сохраняются в именованном Docker volume `app_data` и доступны обоим сервисам.

---

### Вариант 2 — Локальный запуск

#### Установка

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

#### Запуск

**Шаг 1 — ETL (извлечение, трансформация, загрузка в Parquet):**

```bash
python main.py
```

При первом запуске автоматически:
- скачивается `sqlite-jdbc-3.42.0.0.jar` в папку `jars/`
- генерируется база данных `data/raw/heart_sounds.db` (если отсутствует)
- на Windows скачиваются `winutils.exe` и `hadoop.dll` в `jars/hadoop/bin/`
- результат сохраняется в `data/processed/parquet/`

**Шаг 2 — Дашборд:**

```bash
streamlit run app.py
```

Открыть в браузере: [http://localhost:8501](http://localhost:8501)

## Структура проекта

```
big-data-course-project/
├── Dockerfile          # образ: Python 3.11 + Java 17 + зависимости
├── docker-compose.yml  # сервисы: etl, dashboard
├── .dockerignore
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
