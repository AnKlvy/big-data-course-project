FROM python:3.11-slim-bookworm

# Install Java 17 (required by PySpark/Spark)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

WORKDIR /app

# Install Python dependencies (separate layer for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SQLite JDBC driver so the container is self-contained
RUN mkdir -p jars && \
    python -c "\
import urllib.request; \
print('Downloading SQLite JDBC driver...'); \
urllib.request.urlretrieve( \
    'https://gitlab.com/university-projects5735812/the-frog/-/raw/main/libs/sqlite-jdbc-3.42.0.0.jar?ref_type=heads&inline=false', \
    'jars/sqlite-jdbc-3.42.0.0.jar' \
); \
print('sqlite-jdbc-3.42.0.0.jar downloaded.')"

# Copy source code (data/ and jars/ are excluded via .dockerignore)
COPY . .

EXPOSE 8501
