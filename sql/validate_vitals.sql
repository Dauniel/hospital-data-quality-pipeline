-- Flag records with out-of-range vital signs.
-- Physiologically plausible ranges used for validation:
--   heart_rate_bpm     : 30  - 220
--   systolic_bp_mmhg   : 60  - 220
--   diastolic_bp_mmhg  : 30  - 140
--   temp_celsius       : 33  - 42
--   oxygen_sat_pct     : 50  - 100
--   weight_kg          : 3   - 250

SELECT
    patient_id,
    heart_rate_bpm,
    systolic_bp_mmhg,
    diastolic_bp_mmhg,
    temp_celsius,
    oxygen_sat_pct,
    weight_kg,
    CONCAT_WS(', ',
        CASE WHEN heart_rate_bpm    NOT BETWEEN 30  AND 220 THEN 'heart_rate'    END,
        CASE WHEN systolic_bp_mmhg  NOT BETWEEN 60  AND 220 THEN 'systolic_bp'   END,
        CASE WHEN diastolic_bp_mmhg NOT BETWEEN 30  AND 140 THEN 'diastolic_bp'  END,
        CASE WHEN temp_celsius      NOT BETWEEN 33  AND 42  THEN 'temperature'   END,
        CASE WHEN oxygen_sat_pct    NOT BETWEEN 50  AND 100 THEN 'oxygen_sat'    END,
        CASE WHEN weight_kg         NOT BETWEEN 3   AND 250 THEN 'weight'        END
    ) AS flagged_fields
FROM records
WHERE
    heart_rate_bpm    NOT BETWEEN 30  AND 220 OR
    systolic_bp_mmhg  NOT BETWEEN 60  AND 220 OR
    diastolic_bp_mmhg NOT BETWEEN 30  AND 140 OR
    temp_celsius      NOT BETWEEN 33  AND 42  OR
    oxygen_sat_pct    NOT BETWEEN 50  AND 100 OR
    weight_kg         NOT BETWEEN 3   AND 250
ORDER BY patient_id;
