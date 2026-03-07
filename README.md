# Heart Sounds Analytics Project

Этот проект позволяет выгрузить данные из SQLite, преобразовать их с помощью Spark и отобразить дашборд через Streamlit.

## Требования

- Python 3.10+
- Java (для работы PySpark)
- Spark (необязательно локально, но желательно для больших данных)

## Установка

1. Склонировать репозиторий и перейти в папку проекта:

```bash
git clone https://github.com/AnKlvy/big-data-course-project.git
```
2. Создать виртуальное окружение и активировать его:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```
3. Установить зависимости:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```