"""
Cleans hospital patient records using PySpark SQL.

Steps:
  1. Remove duplicate patient_id rows (keep most recent admission)
  2. Flag and drop records with invalid ICD-10 codes
  3. Flag and drop records with out-of-range vital signs
  4. Standardize date formats and column types
  5. Report counts at each stage
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import Window


VITALS_RANGES = {
    "heart_rate_bpm":    (30,  220),
    "systolic_bp_mmhg":  (60,  220),
    "diastolic_bp_mmhg": (30,  140),
    "temp_celsius":      (33,  42),
    "oxygen_sat_pct":    (50,  100),
    "weight_kg":         (3,   250),
}

ICD10_PATTERN = r'^[A-Z][0-9]{2}(\.[0-9A-Z]{1,4})?$'


def _log(label: str, before: int, after: int) -> None:
    removed = before - after
    print(f"  [{label}] {before:,} -> {after:,}  (removed {removed:,})")


def remove_duplicates(spark: SparkSession, df: DataFrame) -> DataFrame:
    df.createOrReplaceTempView("raw")
    deduped = spark.sql("""
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY patient_id
                       ORDER BY admission_date DESC
                   ) AS rn
            FROM raw
        )
        WHERE rn = 1
    """).drop("rn")
    return deduped


def remove_invalid_icd10(df: DataFrame) -> DataFrame:
    return df.filter(
        F.col("icd10_code").isNotNull() &
        F.col("icd10_code").rlike(ICD10_PATTERN)
    )


def remove_bad_vitals(df: DataFrame) -> DataFrame:
    condition = F.lit(True)
    for col, (lo, hi) in VITALS_RANGES.items():
        condition = condition & (
            F.col(col).isNull() |
            F.col(col).between(lo, hi)
        )
    return df.filter(condition)


def standardize(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("dob",            F.to_date("dob"))
        .withColumn("admission_date", F.to_date("admission_date"))
        .withColumn("discharge_date", F.to_date("discharge_date"))
        .withColumn("length_of_stay_days",
                    F.datediff(F.col("discharge_date"), F.col("admission_date")))
        .withColumn("icd10_code",     F.upper(F.trim(F.col("icd10_code"))))
        .withColumn("first_name",     F.initcap(F.trim(F.col("first_name"))))
        .withColumn("last_name",      F.initcap(F.trim(F.col("last_name"))))
    )


def clean(spark: SparkSession, df: DataFrame) -> DataFrame:
    print("\n--- Cleaning Pipeline ---")
    n0 = df.count()
    print(f"  [start]     {n0:,} rows")

    df = remove_duplicates(spark, df)
    _log("dedup", n0, df.count())
    n1 = df.count()

    df = remove_invalid_icd10(df)
    _log("icd10", n1, df.count())
    n2 = df.count()

    df = remove_bad_vitals(df)
    _log("vitals", n2, df.count())
    n3 = df.count()

    df = standardize(df)
    print(f"  [standardize] dates cast, length_of_stay_days added, strings trimmed")
    print(f"  [done]      {n3:,} clean rows")

    return df
