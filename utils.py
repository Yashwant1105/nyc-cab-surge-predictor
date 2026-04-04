from pyspark.sql import SparkSession
from pyspark.ml.classification import LogisticRegressionModel
import os

def load_model():
    # 🔥 Force disable native Hadoop
    os.environ["HADOOP_HOME"] = ""
    os.environ["hadoop.home.dir"] = ""

    spark = SparkSession.builder \
        .appName("SurgeApp") \
        .master("local[*]") \
        .config("spark.hadoop.io.native.lib.available", "false") \
        .config("spark.sql.warehouse.dir", "file:///tmp") \
        .getOrCreate()

    # 🔥 IMPORTANT: use absolute path
    model_path = os.path.abspath("model/surge_lr")

    model = LogisticRegressionModel.load(model_path)

    return spark, model