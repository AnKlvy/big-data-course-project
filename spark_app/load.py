from pyspark.sql import DataFrame


def load_to_parquet(df: DataFrame, output_path: str) -> None:
    (
        df.write
        .mode("overwrite")
        .parquet(output_path)
    )