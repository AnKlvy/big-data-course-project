from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when


def transform(df: DataFrame) -> DataFrame:

    df = df.filter(
        (col("patient_age") >= 0) &
        (col("patient_age") <= 120)
    )

    df = df.withColumn(
        "is_abnormal",
        when(col("heart_sound_label") == "abnormal", 1).otherwise(0)
    )

    df = df.withColumn(
        "age_group",
        when(col("patient_age") < 18, "child")
        .when(col("patient_age") < 35, "young")
        .when(col("patient_age") < 50, "adult")
        .when(col("patient_age") < 65, "senior")
        .otherwise("elder")
    )

    return df