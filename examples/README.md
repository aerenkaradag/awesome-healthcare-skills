# Examples

This folder contains small, **synthetic** example datasets used to test and
demonstrate the healthcare AI skills in this repository.

> **All data here is 100% synthetic.** It was generated programmatically and
> contains no real patients, names, addresses, phone numbers, emails, medical
> record numbers, or any other real identifiers. It must **not** be treated as
> real clinical evidence, used for medical decisions, or interpreted as
> validated clinical fact. The files exist only for **software testing and
> workflow demonstration**.

## Files

| File | Skill it helps test | Purpose |
|------|--------------------|---------|
| `synthetic-fhir-bundle.json` | `fhir-to-ml-dataset-builder` | A compact FHIR R4 transaction `Bundle` with synthetic patients and clinical resources. |
| `diabetes-cohort.csv` | `ehr-care-gap-analyzer` | A tabular diabetes cohort with labs, dates, diagnoses, medications, and follow-up fields. |
| `validation-results.csv` | `medical-ai-validation-report-writer` | Synthetic model predictions, labels, probabilities, and subgroup fields. |
| `scripts/generate_examples.py` | (reproducibility) | Regenerates all three files deterministically. |

### 1. `synthetic-fhir-bundle.json`

A FHIR R4 `Bundle` (`type: transaction`) with 10 synthetic patients and a mix
of resources:

- `Patient` (fake placeholder names, synthetic IDs, birth dates, gender)
- `Condition` — Type 2 diabetes (SNOMED `44054006`), hypertension
  (`38341003`), chronic kidney disease (`709044004`), hyperlipidemia, diabetic
  neuropathy
- `Observation` — HbA1c (LOINC `4548-4`), eGFR (`33914-3`), LDL (`18262-6`),
  creatinine (`2160-0`), systolic/diastolic blood pressure (`8480-6` /
  `8462-4`)
- `MedicationRequest` — metformin, insulin glargine, lisinopril, atorvastatin
  (RxNorm coded)
- `Encounter` — ambulatory encounters with start/end periods
- `Procedure` — a screening procedure for some patients

Coding systems used: **SNOMED CT** for conditions, **LOINC** for observations,
**RxNorm** for medications. The bundle is structurally close to valid FHIR R4
and is easy to parse with standard JSON tooling.

### 2. `diabetes-cohort.csv`

30 synthetic diabetic patients. Columns include demographics, the most recent
HbA1c / eGFR / LDL values with their dates, blood pressure, comorbidity flags,
medication flags, and the dates of the last specialist/screening visits, plus
optional fields (`bmi`, `smoking_status`, `albumin_creatinine_ratio`,
`acr_date`, `num_er_visits_12m`, `num_hospitalizations_12m`).

The cohort is built with deliberate variation so that care-gap rules have
signal to find, for example:

- Patients with high HbA1c and stale follow-up dates.
- Patients with low eGFR and no nephrology visit on record.
- Patients with no recent eye exam date.
- Patients with high LDL and no statin flag.
- Some relatively well-managed patients.
- A few **missing values** (represented as empty cells) to exercise
  missing-data handling.

Dates are ISO 8601 (`YYYY-MM-DD`). Missing values are blank.

### 3. `validation-results.csv`

200 rows of synthetic model evaluation output for a binary classifier.

- `true_label` / `predicted_label`: `complication_within_24m` or
  `no_complication_within_24m`
- `predicted_probability`: `0.00`–`1.00`
- `split`: `validation` or `test` (the test set is treated as locked until
  final evaluation; no `train` rows are included since training data is not
  needed for an evaluation report)
- Subgroup fields: `age_group`, `sex`, `site`, `has_ckd`, `has_hypertension`

Predictions are deliberately **imperfect** and include subgroup variation
(e.g. noisier predictions at one site, higher event rate for CKD and older age
groups). This supports calculation of sensitivity, specificity, PPV, NPV,
confusion matrix, AUROC-style analysis, and subgroup performance.

## How to use these files with the skills

Simple end-to-end test workflow:

```text
1. Use synthetic-fhir-bundle.json with fhir-to-ml-dataset-builder.
2. Use diabetes-cohort.csv with ehr-care-gap-analyzer.
3. Use validation-results.csv with medical-ai-validation-report-writer.
```

### fhir-to-ml-dataset-builder

Point the skill at `synthetic-fhir-bundle.json`. Expected outputs are
patient-level ML features, for example:

- `ml_features.csv` with one row per patient (10 rows here)
- Lab features such as `latest_hba1c_value`, `latest_egfr_value`,
  `latest_ldl_value`
- Diagnosis flags such as `has_type2_diabetes`, `has_hypertension`, `has_ckd`
- Medication exposure flags such as `exposed_metformin`, `exposed_insulin`
- A `feature_dictionary.md` and a `missingness_report.csv`

No direct identifiers (names, raw FHIR IDs) should appear in the exported ML
table.

### ehr-care-gap-analyzer

Feed `diabetes-cohort.csv` to the analyzer with configurable thresholds and
lookback windows. Expected outputs are conservative, review-oriented signals,
for example:

- `care_gap_patient_flags.csv` — per-patient **possible** care-gap flags such
  as "HbA1c above configured threshold and no recent endocrinology follow-up"
  or "eGFR below threshold and no nephrology visit found in lookback window"
- `care_gap_population_summary.csv` — aggregate counts per category
- A Markdown report using cautious language (`possible care gap`,
  `requires clinician validation`)

The cohort intentionally contains patients that trigger glycemic-control,
nephropathy-follow-up, retinopathy-screening, and lipid-management signals, as
well as well-managed patients that should **not** be flagged.

### medical-ai-validation-report-writer

Feed `validation-results.csv` to the report writer. Expected outputs are
structured validation documentation, for example:

- `validation_report.md` with metrics computed from the rows (sensitivity,
  specificity, PPV, NPV, confusion matrix, subgroup tables)
- `metrics_summary.csv`
- A `data_leakage_checklist.md` and `clinical_claims_checklist.md`
- Explicit notes that external validation, confidence intervals, and
  calibration were **not provided** (marked as missing rather than fabricated)

## Regenerating the examples

The files are produced deterministically by the bundled script:

```bash
python scripts/generate_examples.py
```

Notes:

- A fixed random seed makes every run byte-for-byte identical.
- Standard library only is required to generate the files (pandas is optional
  and only used to *read* them in your own workflows).
- No internet access is required.
- **Synthea is not required.** [Synthea](https://github.com/synthetichealth/synthea)
  is an open-source synthetic patient generator (requires Java 11+). If you
  have a real Synthea FHIR R4 export, you may use it in place of the built-in
  bundle:

  ```bash
  python scripts/generate_examples.py --synthea-bundle path/to/synthea_bundle.json
  ```

  The CSV files are always generated locally so the care-gap and validation
  workflows stay fully self-contained.

## Disclaimer

These examples are for software testing and workflow demonstration only. They
do not constitute medical advice, clinical evidence, or validated clinical
fact. Any real-world use of these skills must follow applicable privacy and
compliance requirements (HIPAA, GDPR, KVKK, institutional governance, etc.) and
must involve appropriate clinical, statistical, and regulatory review.
