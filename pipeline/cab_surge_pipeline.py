# pipeline/cab_surge_pipeline.py
"""
Reusable PySpark Feature Engineering & Training Pipeline for NYC Cab Surge Predictor.

Reproduces the transformations from `cab_surge_pred_final.ipynb`:
1. Clean taxi trips & extract datetime fields (pickup_hour, pickup_day, pickup_date).
2. Aggregate trip counts by (pickup_date, pickup_hour).
3. Extract daily weather features (precipitation, rain_flag).
4. Join weather on pickup_date.
5. Extract event dates from film permits and join event_flag.
6. Compute calendar features: is_weekend and peak_hour.
7. Build composite surge_label.
8. Assemble feature vector and apply StandardScaler.
"""

from pathlib import Path
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler, StandardScaler


def build_training_dataframe(
    spark: SparkSession,
    fixture_dir: str | Path | None = None,
    threshold: int = 1,
) -> DataFrame:
    """
    Build the cab-surge training DataFrame following the exact notebook transformations.

    :param spark: An active SparkSession
    :param fixture_dir: Directory containing nyc_cab_sample.csv, nyc_weather_sample.json, nyc_events_sample.csv.
                        If None, defaults to `data/fixtures` in the repository.
    :param threshold: Surge threshold for trip count comparison (default: 1 for small sample fixtures)
    :return: DataFrame ready for ML training with 'features' and 'surge_label' columns
    """
    if fixture_dir is None:
        repo_root = Path(__file__).resolve().parent.parent
        fixture_dir = repo_root / "data" / "fixtures"
    else:
        fixture_dir = Path(fixture_dir)

    taxi_file = fixture_dir / "nyc_cab_sample.csv"
    weather_file = fixture_dir / "nyc_weather_sample.json"
    events_file = fixture_dir / "nyc_events_sample.csv"

    # 1. Read & filter raw taxi trips
    taxi_df = spark.read.csv(str(taxi_file), header=True, inferSchema=True)
    df = taxi_df.select(
        "tpep_pickup_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "PULocationID",
    ).filter(
        (F.col("passenger_count") > 0)
        & (F.col("trip_distance") > 0)
        & (F.col("fare_amount") > 0)
    )

    # 2. Extract temporal columns
    df = df.withColumn("pickup_hour", F.hour("tpep_pickup_datetime")) \
           .withColumn("pickup_day", F.dayofweek("tpep_pickup_datetime")) \
           .withColumn("pickup_month", F.month("tpep_pickup_datetime")) \
           .withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))

    # 3. Demand aggregation (count trips per date and hour)
    demand_df = df.groupBy("pickup_date", "pickup_hour") \
                  .count() \
                  .withColumnRenamed("count", "trip_count")

    # 4. Weather extraction & processing
    weather_df = spark.read.json(str(weather_file))
    weather_flat = weather_df.select(
        F.explode(
            F.arrays_zip(
                F.col("daily.time"),
                F.col("daily.temperature_2m_max"),
                F.col("daily.precipitation_sum"),
            )
        ).alias("data")
    ).select(
        F.to_date(F.col("data.time")).alias("pickup_date"),
        F.col("data.temperature_2m_max").alias("temperature"),
        F.col("data.precipitation_sum").alias("precipitation"),
    ).withColumn(
        "rain_flag",
        F.when(F.col("precipitation") > 0, 1).otherwise(0),
    )

    # 5. Join weather with demand
    final_df = demand_df.join(weather_flat, on="pickup_date", how="left")

    # 6. Events extraction & processing
    events_df = spark.read.csv(str(events_file), header=True, inferSchema=True)
    events_df = events_df.withColumn("event_date", F.to_date("startdatetime"))
    event_dates = events_df.select("event_date").distinct().withColumn("event_flag", F.lit(1))

    final_df = final_df.join(
        event_dates,
        final_df.pickup_date == event_dates.event_date,
        "left",
    ).fillna({"event_flag": 0}).drop("event_date")

    # 7. Calendar features: is_weekend and peak_hour
    final_df = final_df.withColumn(
        "is_weekend",
        F.when(F.dayofweek("pickup_date").isin([1, 7]), 1).otherwise(0),
    ).withColumn(
        "peak_hour",
        F.when(F.col("pickup_hour").isin([8, 9, 17, 18, 19]), 1).otherwise(0),
    )

    # 8. Clean nulls
    final_df = final_df.fillna({
        "pickup_hour": 0,
        "trip_count": 0,
        "rain_flag": 0,
        "event_flag": 0,
        "is_weekend": 0,
        "peak_hour": 0,
    })

    # 9. Surge label (Composite surge definition from notebook)
    final_df = final_df.withColumn(
        "surge_label",
        (
            (F.col("trip_count") > threshold)
            & (
                (F.col("rain_flag") == 1)
                | (F.col("event_flag") == 1)
                | (F.col("peak_hour") == 1)
            )
        ).cast("int"),
    )

    # 10. ML Feature Vectorization & Scaling
    assembler = VectorAssembler(
        inputCols=["pickup_hour", "trip_count", "rain_flag", "event_flag", "is_weekend", "peak_hour"],
        outputCol="features_raw",
    )
    scaler = StandardScaler(
        inputCol="features_raw",
        outputCol="features",
        withMean=True,
        withStd=True,
    )

    assembled_df = assembler.transform(final_df)
    scaler_model = scaler.fit(assembled_df)
    training_df = scaler_model.transform(assembled_df)

    return training_df

