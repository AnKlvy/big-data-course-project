import os
import sys
import urllib.request
from pyspark.sql import SparkSession


def _ensure_winutils():
    """Download winutils.exe and hadoop.dll for Hadoop on Windows if not present."""
    if sys.platform != "win32":
        return None
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    hadoop_bin = os.path.join(project_root, "jars", "hadoop", "bin")
    os.makedirs(hadoop_bin, exist_ok=True)
    # PySpark 3.5.1 bundles Hadoop 3.3.4 jars
    base_url = "https://github.com/cdarlint/winutils/raw/master/hadoop-3.3.6/bin/"
    for filename in ("winutils.exe", "hadoop.dll"):
        dest = os.path.join(hadoop_bin, filename)
        if not os.path.exists(dest):
            print(f"Скачиваю {filename} для Hadoop...")
            urllib.request.urlretrieve(base_url + filename, dest)
            print(f"{filename} сохранён: {dest}")
    hadoop_home = os.path.join(project_root, "jars", "hadoop")
    os.environ["HADOOP_HOME"] = hadoop_home
    os.environ["hadoop.home.dir"] = hadoop_home
    # JAVA_TOOL_OPTIONS is read by the JVM at startup — must be set before getOrCreate()
    lib_opt = f"-Djava.library.path={hadoop_bin}"
    existing = os.environ.get("JAVA_TOOL_OPTIONS", "")
    if lib_opt not in existing:
        os.environ["JAVA_TOOL_OPTIONS"] = (existing + " " + lib_opt).strip()
    # Also add to PATH for Windows DLL search
    os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")
    return hadoop_bin


def get_spark_session() -> SparkSession:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    jar_path = os.path.join(project_root, "jars", "sqlite-jdbc-3.42.0.0.jar")

    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    _ensure_winutils()

    spark = SparkSession.builder \
        .appName("HeartSounds") \
        .config("spark.jars", jar_path) \
        .config("spark.driver.memory", "4g") \
        .config("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "2") \
        .getOrCreate()
    return spark
