# scripts/generate_cab_plan.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("NYC_Cab_Surge_Plan") \
    .master("local[*]") \
    .getOrCreate()

# Create a sample NYC-style taxi dataset
# Replace this with your actual NYC taxi data later.
taxi = spark.createDataFrame(
    [
        (0, 12, 500, 0, 0, 1, 1),
        (1, 18, 1400, 1, 1, 0, 1),
        (2, 21, 3500, 1, 0, 1, 0),
        (3, 7, 600, 0, 0, 0, 0),
    ],
    ["ride_id", "pickup_hour", "trip_count", "rain_flag", "event_flag", "is_weekend", "peak_hour"]
)

weather = spark.createDataFrame(
    [
        (0, 0),
        (1, 1),
    ],
    ["ride_id", "weather_rain_flag"]
)

events = spark.createDataFrame(
    [
        (0, 0),
        (1, 1),
    ],
    ["ride_id", "event_flag"]
)

# Join-like feature engineering
df = taxi \
    .join(weather, on="ride_id", how="left") \
    .join(events, on="ride_id", how="left") \
    .withColumn("trip_count_log", F.log1p(F.col("trip_count"))) \
    .withColumn("rain_flag", F.col("weather_rain_flag")) \
    .withColumn("surge_label", F.when(F.col("trip_count") > 3000, 1).otherwise(0)) \
    .select(
        "pickup_hour",
        "trip_count",
        "rain_flag",
        "event_flag",
        "is_weekend",
        "peak_hour",
        "trip_count_log",
        "surge_label"
    )

# Approximate the same ML-enriched pipeline shape as your project
df = df.groupBy("pickup_hour", "rain_flag", "event_flag", "is_weekend", "peak_hour") \
    .agg(F.avg("trip_count").alias("avg_trip_count"),
         F.avg("surge_label").alias("surge_rate")) \
    .filter(F.col("avg_trip_count") > 100) \
    .orderBy("pickup_hour")

# IMPORTANT: SparkLens expects formatted physical plan text.
df.explain("formatted")

spark.stop()