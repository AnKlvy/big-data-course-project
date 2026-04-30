import json
import os
import joblib
import pandas as pd
import streamlit as st
from pyspark.sql import functions as F
from spark_app.spark_session import get_spark_session
from spark_app.ml import METRICS_PATH, SKLEARN_MODEL_PATH

DATA_PATH = "data/processed/parquet/"

st.set_page_config(page_title="Heart Sounds Dashboard", layout="wide")
st.title("Heart Sounds Analytics Dashboard")

if not os.path.exists(DATA_PATH) or len(os.listdir(DATA_PATH)) == 0:
    st.warning("Данные отсутствуют. Сначала выполните ETL.")
    st.stop()

# Инициализация SparkSession с индикатором загрузки
with st.spinner("Загрузка данных..."):
    spark = get_spark_session()

    df_spark = spark.read.parquet(DATA_PATH)

    # KPI на Spark
    total_records = df_spark.count()
    abnormal_pct = df_spark.agg(F.avg("is_abnormal").alias("abnormal_pct")).collect()[0]["abnormal_pct"] * 100
    avg_age = df_spark.agg(F.avg("patient_age").alias("avg_age")).collect()[0]["avg_age"]

    # Распределение по возрастным группам
    age_dist = df_spark.groupBy("age_group").count().toPandas()

    # Аномальные случаи по возрастным группам
    abnormal_by_group = df_spark.groupBy("age_group").agg(F.avg("is_abnormal").alias("abnormal_pct")).toPandas()

    # Распределение по полу
    gender_dist = df_spark.groupBy("patient_gender").count().toPandas()

st.success("Данные загружены!")

# KPI
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", total_records)
col2.metric("Abnormal %", round(abnormal_pct, 2))
col3.metric("Average Age", round(avg_age, 1))

st.divider()

# Age distribution
st.subheader("Patients by Age Group")
st.bar_chart(age_dist.set_index("age_group")["count"])

# Abnormal by age group
st.subheader("Abnormal Cases by Age Group")
st.bar_chart(abnormal_by_group.set_index("age_group")["abnormal_pct"])

# Gender distribution
st.subheader("Gender Distribution")
st.bar_chart(gender_dist.set_index("patient_gender")["count"])

st.divider()

# ML Metrics
st.subheader("ML Model — RandomForest (PySpark MLlib)")
if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        ml_metrics = json.load(f)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Accuracy",  ml_metrics["accuracy"])
    m2.metric("F1",        ml_metrics["f1"])
    m3.metric("Precision", ml_metrics["precision"])
    m4.metric("Recall",    ml_metrics["recall"])
    m5.metric("AUC-ROC",   ml_metrics["auc_roc"])
else:
    st.info("ML-метрики отсутствуют. Запустите ETL-пайплайн (python main.py).")

st.divider()

# Предсказание для нового пациента
st.subheader("Предсказание для нового пациента")
st.caption("Введите данные пациента — модель определит, норма или аномалия.")

with st.form("prediction_form"):
    col_a, col_b = st.columns(2)

    age = col_a.slider("Возраст пациента", min_value=0, max_value=90, value=47)

    gender_option = col_b.selectbox("Пол", ["Мужской (M)", "Женский (F)"])

    location_option = st.selectbox("Место записи сердечного звука", [
        "Верхушка сердца (apex)",
        "Митральная область (mitral)",
        "Трёхстворчатый клапан (tricuspid)",
    ])

    murmur_option = st.selectbox("Сердечный шум", [
        "Шум отсутствует",
        "Физиологический шум (вариант нормы)",
        "Мягкий шум (Grade I–II)",
        "Умеренный шум (Grade III–IV)",
        "Интенсивный шум (Grade V–VI)",
    ])

    submitted = st.form_submit_button("Получить предсказание", use_container_width=True)

if submitted:
    if not os.path.exists(SKLEARN_MODEL_PATH):
        st.warning("Модель не найдена. Запустите python main.py.")
    else:
        gender = "M" if "M" in gender_option else "F"

        location_map = {
            "Верхушка сердца (apex)":           "apex",
            "Митральная область (mitral)":       "mitral",
            "Трёхстворчатый клапан (tricuspid)": "tricuspid",
        }
        murmur_map = {
            "Шум отсутствует":                     "no",
            "Физиологический шум (вариант нормы)": "no",
            "Мягкий шум (Grade I–II)":             "yes",
            "Умеренный шум (Grade III–IV)":        "yes",
            "Интенсивный шум (Grade V–VI)":        "yes",
        }

        artifacts = joblib.load(SKLEARN_MODEL_PATH)
        sk_model    = artifacts["model"]
        le_gender   = artifacts["le_gender"]
        le_location = artifacts["le_location"]
        le_murmur   = artifacts["le_murmur"]

        X = pd.DataFrame([{
            "patient_age":  age,
            "gender_enc":   le_gender.transform([gender])[0],
            "location_enc": le_location.transform([location_map[location_option]])[0],
            "murmur_enc":   le_murmur.transform([murmur_map[murmur_option]])[0],
        }])

        pred         = int(sk_model.predict(X)[0])
        prob_abnormal = float(sk_model.predict_proba(X)[0][1])

        if pred == 1:
            st.error(f"Аномалия сердечного звука — вероятность {prob_abnormal:.1%}")
        else:
            st.success(f"Норма — вероятность аномалии {prob_abnormal:.1%}")