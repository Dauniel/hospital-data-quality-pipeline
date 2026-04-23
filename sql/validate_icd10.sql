-- Flag records with invalid ICD-10 codes.
-- Valid format: one uppercase letter, two digits, optional decimal with 1-4 alphanumeric chars.
-- Example valid:   A00, B15.2, C34.1A
-- Example invalid: 123, XYZ, A1, ABCDE

SELECT
    patient_id,
    icd10_code,
    CASE
        WHEN icd10_code IS NULL                                                   THEN 'MISSING'
        WHEN icd10_code NOT RLIKE '^[A-Z][0-9]{2}(\\.[0-9A-Z]{1,4})?$'          THEN 'INVALID_FORMAT'
        ELSE                                                                            'VALID'
    END AS icd10_status
FROM records
WHERE icd10_code IS NULL
   OR icd10_code NOT RLIKE '^[A-Z][0-9]{2}(\\.[0-9A-Z]{1,4})?$'
ORDER BY icd10_status, patient_id;
