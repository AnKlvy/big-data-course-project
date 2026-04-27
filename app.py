import os
import streamlit as st
from pyspark.sql import functions as F
from spark_app.spark_session import get_spark_session

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