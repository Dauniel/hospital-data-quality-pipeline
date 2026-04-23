# Hospital Data Quality Pipeline

A SQL and PySpark pipeline that profiles and cleans 51K+ synthetic hospital patient records. Detects duplicates, invalid ICD-10 codes, and out-of-range vital signs, then standardizes and outputs clean data.

## Features

- **Data generation** — synthetic 51K hospital records with seeded duplicates, invalid ICD-10 codes, bad vitals, and missing values
- **Profiling** — null rates, duplicate counts, ICD-10 validity summary, vitals distribution
- **Cleaning** — deduplication via SQL window functions, ICD-10 regex validation, physiological range checks on six vital signs
- **Standardization** — date casting, length-of-stay computation, string normalization
- **Output** — cleaned records written as CSV

## Stack

- Python 3.12
- PySpark 3.5.4 (local mode)
- Java 11 (Amazon Corretto)

## Project Structure

```
hospital-data-quality-pipeline/
├── pipeline.py          # entry point
├── src/
│   ├── generate_data.py # synthetic data generation
│   ├── profiler.py      # data profiling with Spark SQL
│   └── cleaner.py       # cleaning logic
├── sql/
│   ├── detect_duplicates.sql
│   ├── validate_icd10.sql
│   └── validate_vitals.sql
├── data/                # raw input (git-ignored)
└── output/              # clean output (git-ignored)
```

## Setup

```bash
pip install -r requirements.txt
```

> Requires Java 11+. PySpark 3.5.x is capped at Java 11 compatibility.

## Usage

Generate synthetic data and run the full pipeline:

```bash
python pipeline.py --generate
```

Run on an existing CSV:

```bash
python pipeline.py --input path/to/records.csv --output output/clean
```

## Data Quality Checks

| Check | Method |
|---|---|
| Duplicate patient records | SQL `ROW_NUMBER()` window, keep latest admission |
| Invalid ICD-10 codes | Regex `^[A-Z][0-9]{2}(\.[0-9A-Z]{1,4})?$` |
| Out-of-range heart rate | 30–220 bpm |
| Out-of-range systolic BP | 60–220 mmHg |
| Out-of-range diastolic BP | 30–140 mmHg |
| Out-of-range temperature | 33–42 °C |
| Out-of-range oxygen saturation | 50–100% |
| Out-of-range weight | 3–250 kg |

## Sample Output

```
========================================================
DATASET PROFILE
========================================================
Total rows : 51,800
Columns    : 11

--- Null Rates ---
  icd10_code                        92  (0.2%)
  heart_rate_bpm                    78  (0.2%)
  ...

--- Duplicates ---
  Duplicate patient_id rows :  800

--- ICD-10 Codes ---
  Invalid ICD-10 codes :  600

--- Cleaning Pipeline ---
  [start]     51,800 rows
  [dedup]     51,800 -> 51,000  (removed 800)
  [icd10]     51,000 -> 50,316  (removed 684)
  [vitals]    50,316 -> 49,892  (removed 424)
  [standardize] dates cast, length_of_stay_days added, strings trimmed
  [done]      49,892 clean rows
```
