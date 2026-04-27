import os
import sys
import urllib.request
import subprocess

from spark_app.spark_session import get_spark_session
from spark_app.extract import extract_from_sqlite
from spark_app.transform import transform
from spark_app.load import load_to_parquet

RAW_DB_PATH = "data/raw/heart_sounds.db"
OUTPUT_PATH = "data/processed/parquet/"

JAR_PATH = "jars/sqlite-jdbc-3.42.0.0.jar"
JAR_URL = "https://gitlab.com/university-projects5735812/the-frog/-/raw/main/libs/sqlite-jdbc-3.42.0.0.jar?ref_type=heads&inline=false"


def ensure_sqlite_jar():
    if not os.path.exists(JAR_PATH):
        os.makedirs("jars", exist_ok=True)
        urllib.request.urlretrieve(JAR_URL, JAR_PATH)


def ensure_raw_db():
    if not os.path.exists(RAW_DB_PATH):
        print(f"{RAW_DB_PATH} не найден, запускаю dataset.py...")
        subprocess.run([sys.executable, "dataset.py"], check=True)


def initialize_spark():
    spark = get_spark_session()

    df = extract_from_sqlite(spark, RAW_DB_PATH)
    df = transform(df)
    load_to_parquet(df, OUTPUT_PATH)

    spark.stop()


def run_with_spark_submit():
    subprocess.run(
        [
            ".venv\\Scripts\\spark-submit.cmd",
            "--jars",
            JAR_PATH,
            sys.argv[0],
            "--spark-run",
        ],
        check=True,
    )


def main():
    ensure_sqlite_jar()
    ensure_raw_db()

    # if "--spark-run" not in sys.argv:
    #     run_with_spark_submit()
    #     return

    initialize_spark()


if __name__ == "__main__":
    main()