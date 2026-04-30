import json
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier as SklearnRF
from sklearn.preprocessing import LabelEncoder
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.sql import SparkSession

MODEL_PATH = "data/model/rf_model"
SKLEARN_MODEL_PATH = "data/model/sklearn_model.joblib"
METRICS_PATH = "data/model/metrics.json"


def _train_sklearn_model(df) -> None:
    """Обучает лёгкую sklearn-модель на 1% данных для инференса в дашборде."""
    print("Обучение sklearn-модели для дашборда (выборка 1%)...")
    pdf = (
        df.sample(0.01, seed=42)
        .select("patient_age", "patient_gender", "recording_location", "murmur_label", "is_abnormal")
        .toPandas()
    )

    le_gender   = LabelEncoder().fit(["F", "M"])
    le_location = LabelEncoder().fit(["apex", "mitral", "tricuspid"])
    le_murmur   = LabelEncoder().fit(["no", "yes"])

    X = pd.DataFrame({
        "patient_age":  pdf["patient_age"],
        "gender_enc":   le_gender.transform(pdf["patient_gender"]),
        "location_enc": le_location.transform(pdf["recording_location"]),
        "murmur_enc":   le_murmur.transform(pdf["murmur_label"]),
    })
    y = pdf["is_abnormal"]

    model = SklearnRF(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
    model.fit(X, y)

    joblib.dump({
        "model":       model,
        "le_gender":   le_gender,
        "le_location": le_location,
        "le_murmur":   le_murmur,
    }, SKLEARN_MODEL_PATH)
    print(f"sklearn-модель сохранена: {SKLEARN_MODEL_PATH}")


def train_and_evaluate(spark: SparkSession, parquet_path: str) -> dict:
    df = spark.read.parquet(parquet_path)

    # Кодирование категориальных признаков
    gender_indexer   = StringIndexer(inputCol="patient_gender",     outputCol="gender_idx")
    location_indexer = StringIndexer(inputCol="recording_location", outputCol="location_idx")
    murmur_indexer   = StringIndexer(inputCol="murmur_label",       outputCol="murmur_idx")

    assembler = VectorAssembler(
        inputCols=["patient_age", "gender_idx", "location_idx", "murmur_idx"],
        outputCol="features"
    )

    rf = RandomForestClassifier(
        labelCol="is_abnormal",
        featuresCol="features",
        numTrees=20,
        maxDepth=5,
        seed=42
    )

    pipeline = Pipeline(stages=[
        gender_indexer,
        location_indexer,
        murmur_indexer,
        assembler,
        rf,
    ])

    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

    print("Обучение Spark RandomForest на полном датасете...")
    model = pipeline.fit(train_df)

    predictions = model.transform(test_df)

    binary_eval = BinaryClassificationEvaluator(labelCol="is_abnormal", metricName="areaUnderROC")
    multi_eval  = MulticlassClassificationEvaluator(labelCol="is_abnormal", predictionCol="prediction")

    metrics = {
        "accuracy":  round(multi_eval.setMetricName("accuracy").evaluate(predictions),          4),
        "f1":        round(multi_eval.setMetricName("f1").evaluate(predictions),                 4),
        "precision": round(multi_eval.setMetricName("weightedPrecision").evaluate(predictions),  4),
        "recall":    round(multi_eval.setMetricName("weightedRecall").evaluate(predictions),     4),
        "auc_roc":   round(binary_eval.evaluate(predictions),                                    4),
    }

    print(f"Метрики: {metrics}")

    model.write().overwrite().save(MODEL_PATH)

    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Spark-модель сохранена: {MODEL_PATH}")
    print(f"Метрики сохранены: {METRICS_PATH}")

    # Лёгкая модель для инференса в дашборде (без Spark-воркеров)
    _train_sklearn_model(df)

    return metrics
