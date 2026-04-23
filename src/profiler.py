"""
Profiles a hospital records DataFrame using PySpark SQL.
Reports: row count, null rates, duplicate counts, value distributions.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F


def profile(spark: SparkSession, df: DataFrame) -> None:
    df.createOrReplaceTempView("records")

    total = df.count()
    print(f"\n{'='*60}")
    print(f"DATASET PROFILE")
    print(f"{'='*60}")
    print(f"Total rows : {total:,}")
    print(f"Columns    : {len(df.columns)}")

    # null rates
    print(f"\n--- Null Rates ---")
    null_exprs = [F.sum(F.col(c).isNull().cast("int")).alias(c) for c in df.columns]
    null_counts = df.select(null_exprs).collect()[0].asDict()
    for col, cnt in null_counts.items():
        if cnt > 0:
            print(f"  {col:<30} {cnt:>6,}  ({cnt/total*100:.1f}%)")

    # duplicate patient_ids
    dup_count = spark.sql("""
        SELECT COUNT(*) - COUNT(DISTINCT patient_id) AS duplicate_rows
        FROM records
    """).collect()[0]["duplicate_rows"]
    print(f"\n--- Duplicates ---")
    print(f"  Duplicate patient_id rows : {dup_count:,}")

    # ICD-10 validity (letter + 2 digits, optional decimal extension)
    invalid_icd = spark.sql("""
        SELECT COUNT(*) AS cnt
        FROM records
        WHERE icd10_code IS NOT NULL
          AND icd10_code NOT RLIKE '^[A-Z][0-9]{2}(\\\\.[0-9A-Z]{1,4})?$'
    """).collect()[0]["cnt"]
    print(f"\n--- ICD-10 Codes ---")
    print(f"  Invalid ICD-10 codes : {invalid_icd:,}")

    # vitals out-of-range
    out_of_range = spark.sql("""
        SELECT
            SUM(CASE WHEN heart_rate_bpm    NOT BETWEEN 30  AND 220  THEN 1 ELSE 0 END) AS bad_heart_rate,
            SUM(CASE WHEN systolic_bp_mmhg  NOT BETWEEN 60  AND 220  THEN 1 ELSE 0 END) AS bad_systolic,
            SUM(CASE WHEN diastolic_bp_mmhg NOT BETWEEN 30  AND 140  THEN 1 ELSE 0 END) AS bad_diastolic,
            SUM(CASE WHEN temp_celsius      NOT BETWEEN 33  AND 42   THEN 1 ELSE 0 END) AS bad_temp,
            SUM(CASE WHEN oxygen_sat_pct    NOT BETWEEN 50  AND 100  THEN 1 ELSE 0 END) AS bad_oxygen,
            SUM(CASE WHEN weight_kg         NOT BETWEEN 3   AND 250  THEN 1 ELSE 0 END) AS bad_weight
        FROM records
        WHERE heart_rate_bpm IS NOT NULL
    """).collect()[0].asDict()
    print(f"\n--- Out-of-Range Vitals ---")
    for field, cnt in out_of_range.items():
        if cnt and cnt > 0:
            print(f"  {field:<30} {cnt:>6,}")

    # admission date distribution
    print(f"\n--- Admission Year Distribution ---")
    spark.sql("""
        SELECT YEAR(admission_date) AS year, COUNT(*) AS cnt
        FROM records
        GROUP BY year ORDER BY year
    """).show(truncate=False)
