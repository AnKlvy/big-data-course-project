from pyspark.sql import DataFrame, SparkSession


def extract_from_sqlite(spark: SparkSession, db_path: str) -> DataFrame:
    jdbc_url = f"jdbc:sqlite:{db_path}"

    df = (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "heart_sounds")
        .option("driver", "org.sqlite.JDBC")
        .load()
    )

    return df