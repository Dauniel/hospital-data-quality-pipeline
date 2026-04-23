"""
Generates synthetic hospital patient records with intentional data quality issues:
- duplicate records
- invalid ICD-10 codes
- out-of-range vital signs
- missing values
"""

import random
import string
import pandas as pd
from datetime import date, timedelta

SEED = 42
N_RECORDS = 51_000
N_DUPLICATES = 800
N_INVALID_ICD10 = 600
N_BAD_VITALS = 400
N_NULLS = 300

VALID_ICD10_PREFIXES = [
    "A00", "A01", "B15", "C34", "D50", "E11", "F32", "G35",
    "H26", "I21", "J18", "K35", "L40", "M54", "N18", "O80",
    "P07", "Q21", "R05", "S72", "T14", "Z00", "Z23", "Z51",
]

INVALID_ICD10_EXAMPLES = [
    "123", "XYZ", "A1", "99B", "ABCDE", "Z999999", "00A", "!23", "A0B", "11Z"
]

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
               "Linda", "William", "Barbara", "David", "Susan", "Richard", "Jessica",
               "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Lisa"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
              "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
              "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def random_icd10() -> str:
    prefix = random.choice(VALID_ICD10_PREFIXES)
    if random.random() < 0.5:
        return prefix
    suffix = f".{random.randint(0, 9)}{random.choice(string.ascii_uppercase)}"
    return prefix + suffix


def random_vitals(bad: bool = False) -> dict:
    if bad:
        return {
            "heart_rate_bpm": random.choice([random.randint(1, 20), random.randint(250, 400)]),
            "systolic_bp_mmhg": random.choice([random.randint(1, 30), random.randint(250, 350)]),
            "diastolic_bp_mmhg": random.choice([random.randint(1, 15), random.randint(150, 200)]),
            "temp_celsius": random.choice([round(random.uniform(20, 32), 1), round(random.uniform(43, 50), 1)]),
            "oxygen_sat_pct": random.choice([random.randint(1, 50), random.randint(101, 120)]),
            "weight_kg": random.choice([random.randint(1, 2), random.randint(300, 600)]),
        }
    return {
        "heart_rate_bpm": random.randint(45, 180),
        "systolic_bp_mmhg": random.randint(80, 190),
        "diastolic_bp_mmhg": random.randint(45, 120),
        "temp_celsius": round(random.uniform(35.5, 40.0), 1),
        "oxygen_sat_pct": random.randint(88, 100),
        "weight_kg": round(random.uniform(40, 160), 1),
    }


def generate(n: int = N_RECORDS) -> pd.DataFrame:
    random.seed(SEED)

    bad_vital_ids = set(random.sample(range(n), N_BAD_VITALS))
    invalid_icd_ids = set(random.sample(range(n), N_INVALID_ICD10))
    null_ids = set(random.sample(range(n), N_NULLS))

    records = []
    for i in range(n):
        dob = random_date(date(1930, 1, 1), date(2005, 12, 31))
        admission = random_date(date(2018, 1, 1), date(2024, 12, 31))
        discharge = admission + timedelta(days=random.randint(1, 30))

        icd10 = random.choice(INVALID_ICD10_EXAMPLES) if i in invalid_icd_ids else random_icd10()
        vitals = random_vitals(bad=(i in bad_vital_ids))

        record = {
            "patient_id": f"P{i+1:06d}",
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "dob": dob.isoformat(),
            "admission_date": admission.isoformat(),
            "discharge_date": discharge.isoformat(),
            "icd10_code": icd10,
            "primary_diagnosis": f"Diagnosis for {icd10}",
            **vitals,
        }

        if i in null_ids:
            field = random.choice(["icd10_code", "heart_rate_bpm", "systolic_bp_mmhg", "weight_kg"])
            record[field] = None

        records.append(record)

    df = pd.DataFrame(records)

    # inject duplicates (same patient_id, repeated rows)
    dup_indices = random.sample(range(n), N_DUPLICATES)
    dups = df.iloc[dup_indices].copy()
    df = pd.concat([df, dups], ignore_index=True)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = generate()
    out = "data/hospital_records_raw.csv"
    df.to_csv(out, index=False)
    print(f"Generated {len(df):,} records -> {out}")
    print(f"  Columns: {list(df.columns)}")
