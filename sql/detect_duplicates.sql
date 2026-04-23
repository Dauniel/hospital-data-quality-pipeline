-- Identify duplicate patient_id rows.
-- Returns one row per duplicated patient_id with the duplicate count.

SELECT
    patient_id,
    COUNT(*)            AS occurrence_count,
    MIN(admission_date) AS earliest_admission,
    MAX(admission_date) AS latest_admission
FROM records
GROUP BY patient_id
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;
