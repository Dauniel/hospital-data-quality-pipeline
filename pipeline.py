"""
Hospital Data Quality Pipeline

Usage:
    python pipeline.py [--generate] [--input PATH] [--output PATH]

Flags:
    --generate      Generate synthetic raw data before running (default: False)
    --input PATH    Path to raw CSV (default: data/hospital_records_raw.csv)
    --output PATH   Directory for clean output (default: output/clean)
"""

import argparse
import os
import sys

from pyspark.sql import SparkSession

sys.path.insert(0, os.path.dirname(__file__))
from src import generate_data, profiler, cleaner


def build_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("HospitalDataQualityPipeline")
        .master("local[*]")
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .getOrCreate()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Hospital Data Quality Pipeline")
    parser.add_argument("--generate", action="store_true",
                        help="Generate synthetic raw data first")
    parser.add_argument("--input",  default="data/hospital_records_raw.csv")
    parser.add_argument("--output", default="output/clean")
    args = parser.parse_args()

    if args.generate:
        print("Generating synthetic hospital records...")
        df_raw = generate_data.generate()
        os.makedirs("data", exist_ok=True)
        df_raw.to_csv(args.input, index=False)
        print(f"  Wrote {len(df_raw):,} rows -> {args.input}")

    spark = build_spark()
    spark.sparkContext.setLogLevel("ERROR")

    print(f"\nReading {args.input} ...")
    df = spark.read.csv(args.input, header=True, inferSchema=True)

    profiler.profile(spark, df)

    df_clean = cleaner.clean(spark, df)

    os.makedirs(args.output, exist_ok=True)
    df_clean.coalesce(1).write.mode("overwrite").option("header", True).csv(args.output)
    print(f"\nClean data written -> {args.output}/")

    spark.stop()


if __name__ == "__main__":
    main()
