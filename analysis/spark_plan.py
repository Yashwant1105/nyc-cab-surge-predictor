# analysis/spark_plan.py
"""
Spark Physical Plan generation module for NYC Cab Surge Predictor.
"""

from pathlib import Path
from pyspark.sql import SparkSession
from pipeline.cab_surge_pipeline import build_training_dataframe


def capture_formatted_plan(df) -> str:
    """
    Capture formatted physical plan string directly without logging pollution.
    """
    try:
        jvm = df._sc._jvm
        return jvm.PythonSQLUtils.explainString(df._jdf.queryExecution(), "formatted")
    except Exception:
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            df.explain("formatted")
        return buf.getvalue()


def generate_cab_surge_plan(
    output_path: str | Path,
    fixture_dir: str | Path | None = None,
    spark: SparkSession | None = None,
) -> Path:
    """
    Build the cab-surge training DataFrame and save its formatted
    Spark physical execution plan to `output_path`.

    :param output_path: Destination path for the physical plan text file
    :param fixture_dir: Directory containing fixtures (default: data/fixtures)
    :param spark: Optional active SparkSession. If None, creates a local SparkSession and closes it cleanly.
    :return: Resolved Path to the generated plan file
    """
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    owns_spark = False
    if spark is None:
        spark = (
            SparkSession.builder
            .appName("NYC-Cab-Surge-SparkLens")
            .master("local[1]")
            .config("spark.ui.enabled", "false")
            .config("spark.driver.host", "localhost")
            .config("spark.sql.adaptive.enabled", "true")
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("ERROR")
        owns_spark = True

    try:
        training_df = build_training_dataframe(spark, fixture_dir=fixture_dir)
        plan_str = capture_formatted_plan(training_df)
        out_file.write_text(plan_str, encoding="utf-8")
        return out_file
    finally:
        if owns_spark:
            spark.stop()

