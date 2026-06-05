# FHIR to ML Dataset Builder

## Description

This skill guides an AI coding agent to inspect FHIR healthcare data exports and generate ML-ready tabular datasets for data engineering, clinical analytics, and healthcare AI experimentation. It focuses on safely transforming de-identified or synthetic FHIR resources into structured patient-level and feature-level tables that can be reviewed by data scientists, healthcare AI builders, and clinical analytics teams.

This skill does **not** diagnose, predict disease, recommend treatment, provide medical advice, or validate clinical correctness. It prepares data for downstream machine learning workflows while encouraging privacy-preserving handling of healthcare data. Users are responsible for HIPAA, GDPR, KVKK, institutional review, contractual obligations, and all other applicable local compliance requirements.

## When to use

Use this skill when the user needs help preparing FHIR data for machine learning or analytics, including:

- Convert FHIR JSON bundles into patient-level ML tables.
- Extract lab features from `Observation` resources.
- Create diagnosis features from `Condition` resources.
- Create medication features from `MedicationRequest` resources.
- Build longitudinal EHR features from dated clinical events.
- Create missingness reports and feature dictionaries.
- Prepare de-identified datasets for healthcare ML experiments.
- Normalize resource-level data into cohort, feature, and quality-report outputs.
- Create reproducible scripts that transform synthetic or de-identified FHIR exports into CSV or Parquet files.

## When not to use

Do not use this skill for:

- Direct clinical decision-making, diagnosis, triage, treatment selection, or patient-specific medical recommendations.
- Identifiable patient data unless the execution environment, storage, access controls, audit logging, and data handling processes are compliant for that data.
- Replacing clinical data governance, privacy review, security review, IRB/ethics review, or institutional data access approval.
- Inferring diagnoses from incomplete, ambiguous, or poorly mapped data.
- Claiming that derived features are clinically valid without review by qualified domain experts.
- Uploading real patient data to external services, model providers, or public systems.

## Supported FHIR resources

The agent should inspect and support the following FHIR resource types at minimum, while allowing extension to other resources when present:

- `Patient`
- `Observation`
- `Condition`
- `Encounter`
- `MedicationRequest`
- `Procedure`
- `DiagnosticReport`
- `ImagingStudy`
- `DocumentReference`

For each resource, tolerate common FHIR version and vendor differences. Prefer explicit mappings and documented assumptions over silent inference.

## Expected input

Inputs may include one or more of the following:

- FHIR `Bundle` JSON files.
- NDJSON FHIR exports, commonly one resource per line.
- A folder of individual FHIR resource JSON files.
- Synthetic FHIR data.
- De-identified FHIR data that is permitted for the current environment.
- A target label definition, if available.
- A feature extraction window, if relevant, such as an index date, lookback period, prediction horizon, or cohort entry criteria.
- Optional code-system mappings for local lab codes, diagnosis codes, medication names, procedures, or encounter classes.

If a target label is provided, keep target-label construction separate from feature extraction to reduce data leakage risk.

## Expected output

The implementation should generate clearly named outputs such as:

- `patients.csv`
- `observations_features.csv`
- `conditions_features.csv`
- `medications_features.csv`
- `encounters_features.csv`
- `ml_features.csv` or `features.parquet`
- `feature_dictionary.md`
- `data_quality_report.md`
- `missingness_report.csv`
- `cohort_summary.md`

Outputs should avoid direct identifiers. Export only the columns needed for analysis and keep any re-identification or linkage keys local, access-controlled, and separate from ML feature tables.

## Core workflow

Follow this workflow when implementing a FHIR-to-ML dataset transformation:

1. **Inspect files and detect FHIR resource types**
   - Discover input files using `pathlib`.
   - Detect JSON Bundle files, NDJSON files, and standalone resource JSON files.
   - Count resources by `resourceType` before transformation.

2. **Validate basic FHIR structure**
   - Check that each resource has a `resourceType`.
   - For Bundles, check `entry[].resource` objects.
   - Record malformed resources in a data-quality report instead of failing silently.
   - Emit clear errors for unreadable JSON, unsupported file formats, or missing required fields.

3. **Build a patient index**
   - Identify patients from `Patient` resources and references such as `subject.reference`, `patient.reference`, or `beneficiary.reference` where applicable.
   - Create a privacy-preserving `patient_key` for analysis outputs.
   - Do not export names, full addresses, phone numbers, medical record numbers, or raw patient identifiers.

4. **Normalize timestamps**
   - Parse dates from common FHIR fields such as `effectiveDateTime`, `effectivePeriod`, `issued`, `onsetDateTime`, `recordedDate`, `authoredOn`, `performedDateTime`, `period`, and `date`.
   - Normalize timestamps to a consistent timezone or date representation.
   - Preserve enough date precision for analysis while respecting privacy and compliance requirements.
   - Flag missing or unreliable timestamps.

5. **Extract demographic features**
   - Create minimal demographic features only when permitted, such as age at index date, birth year bucket, administrative gender, or deceased indicator.
   - Avoid exporting direct identifiers or granular geography unless explicitly approved and compliant.

6. **Extract lab and observation features**
   - Parse `Observation.code`, coding systems, display names, values, units, reference ranges, status, and dates.
   - Prefer standardized code mappings such as LOINC when available.
   - Generate features such as latest value, count, min, max, mean, abnormal flag, and time since last measurement.
   - Treat non-numeric observations separately from numeric lab values.

7. **Extract diagnosis features**
   - Parse `Condition.code`, coding systems, clinical status, verification status, onset date, recorded date, and subject.
   - Create diagnosis flags by configured code lists, code prefixes, or documented groupings.
   - Do not infer new diagnoses from incomplete data.

8. **Extract medication exposure features**
   - Parse `MedicationRequest.medicationCodeableConcept`, medication references, authored date, status, intent, dosage, and subject.
   - Create medication exposure flags, counts, recency features, or therapeutic-class features only when mappings are explicit or documented.

9. **Extract encounter, procedure, diagnostic, imaging, and document features**
   - Use `Encounter` for encounter count, class, type, period, length of stay, and recency.
   - Use `Procedure` for procedure flags and counts.
   - Use `DiagnosticReport`, `ImagingStudy`, and `DocumentReference` for availability, counts, dates, and metadata-derived features where appropriate.
   - Do not parse free-text clinical notes unless the user confirms data governance and privacy controls are appropriate.

10. **Aggregate longitudinal values using clinically meaningful windows**
    - Use documented windows such as 30, 90, or 365 days before an index date.
    - Avoid mixing pre-index and post-index data unless explicitly intended.
    - Consider data leakage risk whenever target labels, outcomes, or future events are present.

11. **Generate a missingness report**
    - Report missing counts and percentages for each feature.
    - Include patient counts, feature completeness, and unavailable resource types.

12. **Generate a feature dictionary**
    - For every exported feature, document name, source resource, source field, transformation logic, unit, time window, missing-value handling, and known limitations.

13. **Export ML-ready table**
    - Produce one row per patient unless the user explicitly requests another grain.
    - Use stable column names and deterministic transformations.
    - Prefer CSV for simple examples and Parquet for larger datasets when `pyarrow` is available.

14. **Document assumptions and limitations**
    - Write assumptions, code mappings, excluded resources, malformed records, time-window logic, target-label logic, privacy decisions, and data-quality issues into the generated reports.

## Feature engineering guidance

Use transparent, reproducible features with documented source logic. Examples include:

- `latest_<lab>_value`: latest numeric lab value before the index date.
- `<lab>_min_30d`, `<lab>_max_90d`, `<lab>_mean_365d`: min, max, or mean lab values over 30-, 90-, or 365-day lookback windows.
- `<lab>_count_365d`: number of available measurements in a window.
- `<lab>_days_since_last`: time since the latest measurement before the index date.
- `<lab>_abnormal_latest`: abnormal-value flag when FHIR reference ranges or interpretation codes exist.
- `has_<condition_group>`: diagnosis flag based on explicit `Condition` code mappings.
- `<condition_group>_first_seen_days`: days from first documented condition to index date.
- `exposed_<medication_group>`: medication exposure flag based on explicit `MedicationRequest` mappings.
- `<medication_group>_request_count_365d`: medication request count in a lookback window.
- `encounter_count_30d`, `encounter_count_365d`: encounter utilization counts.
- `inpatient_encounter_count_365d`: encounter count by class when encounter class is reliable.
- Trend features, such as slope or change over time, only when timestamps, units, and repeated measurements are reliable.

Avoid feature names that encode target labels or future events. Separate cohort selection, feature extraction, and target construction into distinct steps.

## Safety and privacy rules

Follow these rules for every implementation:

- Prefer synthetic or de-identified data.
- Treat all healthcare data as sensitive unless proven otherwise.
- Never print PHI in logs, exceptions, screenshots, notebooks, generated reports, or console output.
- Do not expose names, full addresses, raw IDs, phone numbers, emails, MRNs, insurance identifiers, precise facility-linked identifiers, or other direct identifiers in exported ML tables.
- Hash or remove patient identifiers when exporting. If hashing is used, use a local salt or key that is not committed to source control.
- Keep linkage keys local, access-controlled, and separate from feature outputs when linkage is necessary.
- Warn the user if direct identifiers appear to be present in the input or requested output.
- Do not upload real patient data to external services, public repositories, telemetry systems, hosted notebooks, or model APIs unless the user explicitly confirms that the environment and data flow are compliant.
- Minimize exported columns and avoid unnecessary sensitive fields.
- Remind users that they are responsible for HIPAA, GDPR, KVKK, data processing agreements, institutional policies, and local legal or regulatory requirements.

## Code-generation instructions

When writing code for this skill, the coding agent should:

- Prefer Python for extraction scripts and examples.
- Use `pandas` for tabular transformations and `pyarrow` for Parquet output when useful.
- Use `pathlib.Path` for filesystem paths.
- Write modular functions such as `load_fhir_resources`, `build_patient_index`, `extract_observation_features`, `extract_condition_features`, `extract_medication_features`, `build_missingness_report`, and `write_feature_dictionary`.
- Add schema checks for required FHIR fields and expected output columns.
- Add clear error messages for malformed JSON, missing resource types, empty cohorts, unsupported resources, and invalid date windows.
- Avoid hardcoding local paths; use command-line arguments, configuration files, or paths relative to the script location.
- Include small sample data or synthetic test data when possible.
- Add a `README.md` or example usage if helpful.
- Keep code deterministic and reproducible.
- Avoid logging raw resource payloads or direct identifiers.
- Prefer explicit code mappings supplied by the user over guessed clinical groupings.

## Test instructions

If the repository does not already contain a minimal fixture, create:

```text
fhir-to-ml-dataset-builder/examples/sample_bundle.json
```

The fixture should be synthetic and small. It should contain at least:

- One or more `Patient` resources without real identifiers.
- Numeric `Observation` resources, such as synthetic HbA1c, eGFR, or LDL values.
- `Condition` resources with explicit codes suitable for diagnosis-flag extraction.

Then create a simple test or example script:

```text
fhir-to-ml-dataset-builder/examples/run_example.py
```

The script should:

- Load `sample_bundle.json`.
- Extract at least `Patient`, `Observation`, and `Condition` features.
- Generate an ML-ready CSV, such as `examples/output/ml_features.csv`.
- Generate a feature dictionary, such as `examples/output/feature_dictionary.md`.
- Verify that the output has one row per patient.
- Verify that no direct PHI fields are exported.
- Print only aggregate status messages, never raw patient records.

Suggested checks include:

- Patient row count equals the number of distinct synthetic patients.
- Exported columns exclude `name`, `address`, `telecom`, `phone`, `email`, `mrn`, `identifier`, and raw FHIR `id` values.
- Expected columns such as `patient_key`, observation-derived features, and condition flags are present.
- Missingness report generation succeeds for all output features.

## Example user prompts

Users might invoke this skill with prompts such as:

- "Convert these FHIR bundles into a patient-level ML dataset."
- "Extract HbA1c, eGFR, LDL, diagnosis flags, and medication exposure features."
- "Create a missingness report and feature dictionary for this FHIR export."
- "Build a diabetes cohort table from these synthetic FHIR resources."
- "Generate Parquet features from NDJSON FHIR exports with a 365-day lookback window."
- "Inspect this folder of FHIR resources and summarize which ML features can be safely extracted."

## Limitations

- FHIR implementations vary across vendors, versions, countries, and export tools.
- Local code systems may need explicit mapping before features are meaningful.
- Resource completeness can vary by workflow, organization, and data source.
- Clinical interpretation requires domain expert review.
- This skill prepares data but does not validate clinical correctness.
- Missing data may reflect care patterns, data access limitations, or documentation practices rather than true absence of disease, medication use, or measurement.
- Free-text resources may contain PHI and require separate governance and privacy controls.
- Feature engineering choices can introduce bias or data leakage if index dates, outcome windows, and lookback windows are not carefully defined.

## Output quality checklist

Before considering the transformation complete, verify:

- [ ] One row per patient is produced for patient-level ML outputs.
- [ ] No direct identifiers are exported.
- [ ] Feature names are clear, stable, and machine-readable.
- [ ] Time windows are documented.
- [ ] Missingness is reported.
- [ ] Assumptions are documented.
- [ ] Data leakage risk is considered.
- [ ] Target label construction is separated from feature extraction.
- [ ] Code mappings and local terminology assumptions are documented.
- [ ] Data-quality issues and malformed resources are summarized.
- [ ] Outputs are reproducible from the provided inputs and configuration.

## Self-review for the implementation agent

After writing or modifying this skill, perform a quick self-review:

- Is the skill useful without exposing proprietary IP or product-specific claims?
- Is it safe for healthcare data and explicit about privacy-preserving handling?
- Is it specific enough for an agent to execute on FHIR files?
- Does it include practical test guidance and example fixture expectations?
- Does it avoid claims about diagnosing, predicting disease, treating patients, or providing medical advice?
- Does it remind users that they are responsible for HIPAA, GDPR, KVKK, and local compliance?
