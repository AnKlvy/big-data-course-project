import os
import sqlite3
import pandas as pd
import numpy as np

# Параметры
num_records = 12_682_131
chunk_size = 100_000
db_path = "data/raw/heart_sounds.db"

# Создаём папку перед подключением
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Шаблоны
ages_pattern = np.arange(20, 71)
genders_pattern = np.array(['M', 'F'])
locations_pattern = np.array(['apex', 'mitral', 'tricuspid'])
heart_sounds_pattern = np.array(['normal', 'abnormal'])
murmurs_pattern = np.array(['no', 'yes'])
relevance_date = '2026-03-02'

conn = sqlite3.connect(db_path)

conn.execute("""
CREATE TABLE IF NOT EXISTS heart_sounds (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    patient_age INTEGER,
    patient_gender TEXT,
    recording_location TEXT,
    heart_sound_label TEXT,
    murmur_label TEXT,
    relevance_date TEXT
)
""")
conn.commit()

current_id = 1
rng = np.random.default_rng()

for start in range(0, num_records, chunk_size):
    end = min(start + chunk_size, num_records)
    size = end - start

    ids = np.arange(current_id, current_id + size)

    # Возраст — нормальное распределение
    ages = np.clip(
        rng.normal(loc=47, scale=18, size=size).astype(int),
        0,
        90
    )

    # Пол — 52% F, 48% M
    genders = rng.choice(
        ['M', 'F'],
        size=size,
        p=[0.48, 0.52]
    )

    # Вероятность abnormal растёт с возрастом
    # от 3% у детей до ~40% у пожилых
    abnormal_prob = np.clip(
        0.03 + (ages / 90) * 0.37,
        0.03,
        0.40
    )

    heart_labels = np.where(
        rng.random(size) < abnormal_prob,
        'abnormal',
        'normal'
    )

    # Murmur логически зависит от abnormal
    murmurs = np.where(
        heart_labels == 'abnormal',
        rng.choice(['yes', 'no'], size=size, p=[0.75, 0.25]),
        rng.choice(['yes', 'no'], size=size, p=[0.03, 0.97])
    )

    df_chunk = pd.DataFrame({
        "id": ids,
        "file_path": [f"data/audio_{i:07d}.wav" for i in ids],
        "patient_age": ages,
        "patient_gender": genders,
        "recording_location": rng.choice(locations_pattern, size=size),
        "heart_sound_label": heart_labels,
        "murmur_label": murmurs,
        "relevance_date": [relevance_date] * size
    })

    df_chunk.to_sql("heart_sounds", conn, if_exists="append", index=False)
    current_id += size

    print(f"Inserted {end} rows")

conn.close()

print("Done.")