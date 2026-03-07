import os
from pyspark.sql import SparkSession

def get_spark_session() -> SparkSession:
    # Берём корень проекта
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    jar_path = os.path.join(project_root, "jars", "sqlite-jdbc-3.42.0.0.jar")

    spark = SparkSession.builder \
        .appName("HeartSounds") \
        .config("spark.jars", jar_path) \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
    return spark