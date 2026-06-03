# EHR Care Gap Analyzer

## Description

This skill guides an AI coding agent to inspect de-identified, anonymized, or synthetic EHR exports and produce conservative care gap summaries for clinical review, quality improvement, and hospital operational planning. It is especially useful for chronic disease populations such as diabetes, where clinical operations teams may need to identify possible overlooked follow-up opportunities, abnormal lab patterns that merit review, and population-level monitoring gaps.

This is an operational and analytical skill, not a diagnostic medical device. It should identify **possible care gaps**, **review-worthy signals**, and **data patterns requiring clinician validation**. It must not diagnose patients, prescribe treatment, replace clinician judgment, deny services, or claim guaranteed clinical or financial outcomes.

The skill should support AId Core-style healthcare analytics expertise while remaining generic, transparent, and community-usable. Do not reveal, recreate, imply, or expose proprietary DiaRisk scoring logic or any other proprietary risk scoring method. Prefer simple, transparent, configurable rules that can be reviewed by local clinical experts.

## When to use

Use this skill when the user wants an AI coding agent to help with healthcare analytics workflows such as:

- Analyze de-identified diabetes patient data.
- Detect missing follow-up signals.
- Identify abnormal labs without documented specialist follow-up.
- Summarize population-level care gaps.
- Generate a hospital operations report.
- Prepare a demo using synthetic or anonymized data.
- Prioritize patients for human clinical review.
- Produce quality-improvement outputs that separate patient-level review flags from aggregate operational summaries.

## When not to use

Do not use this skill for:

- Autonomous diagnosis, triage, or clinical decision-making.
- Treatment decisions without clinician review.
- Identifiable patient data in non-compliant environments.
- Denying care, insurance, coverage, services, or benefits.
- Making billing, revenue, reimbursement, cost-saving, or financial outcome guarantees.
- Claiming that a clinician, department, or institution missed care based only on an EHR export.
- Creating black-box or proprietary risk scores.
- Exposing proprietary DiaRisk logic, weights, thresholds, feature interactions, or scoring internals.

## Supported input formats

The agent may support one or more of the following input formats:

- CSV files.
- XLSX spreadsheets.
- Parquet files.
- FHIR-derived tables.
- SQL exports.
- Synthetic EHR demo data.

When multiple files are provided, inspect table names, column names, join keys, and date fields before assuming a patient-level schema. If the input is FHIR-derived, map source tables such as observations, conditions, encounters, medications, procedures, and referrals into transparent patient-level concepts.

## Suggested input columns

Available columns may vary by institution and export format. The agent should inspect the actual schema and map local columns to standard concepts where possible. Useful columns may include:

- `patient_id` or `anonymized_id`
- `age`
- `sex`
- `diagnosis_codes`
- `diagnosis_names`
- `HbA1c`
- `eGFR`
- `creatinine`
- `LDL`
- `HDL`
- `triglycerides`
- `blood_pressure_systolic`
- `blood_pressure_diastolic`
- `BMI`
- `medications`
- `last_eye_exam_date`
- `last_nephrology_visit_date`
- `last_cardiology_visit_date`
- `last_endocrinology_visit_date`
- `last_lab_date`
- `encounter_dates`
- `procedure_codes`
- `referral_history`

Treat these columns as examples, not requirements. Add warnings for missing important fields, but do not fail merely because optional columns are unavailable.

## Care gap categories

The agent should create transparent, review-oriented categories such as:

- **Poor glycemic control review signal**: data suggests elevated glycemic markers that may merit clinician review.
- **Possible nephropathy follow-up gap**: kidney-related lab patterns are present and recent nephrology follow-up is not found in the available data.
- **Possible retinopathy screening gap**: diabetes-related cohort membership is present and recent eye screening documentation is not found.
- **Cardiovascular risk management gap**: lipid, blood pressure, diagnosis, or medication patterns suggest review may be useful.
- **Hypertension management review signal**: blood pressure values in the export exceed configured review thresholds.
- **Lipid management review signal**: lipid values exceed configured review thresholds or follow-up documentation is not found.
- **Medication follow-up gap**: medication patterns, abnormal labs, or missing encounters suggest a medication review may be useful.
- **Missing recent monitoring data**: expected labs or encounters are not found within the configured lookback period.
- **Multi-comorbidity high-review-priority signal**: multiple non-proprietary, transparent flags are present and may warrant prioritized human review.

Always frame categories as possible gaps or review signals. Do not state that a patient has a disease, that a clinician missed care, or that a referral is mandatory.

## Core workflow

When implementing or using this skill, the agent should:

1. **Inspect available columns**
   - Load the provided tables.
   - Identify patient keys, date columns, lab columns, diagnosis columns, medication columns, visit columns, procedure columns, and referral fields.
   - Detect possible PHI-like columns and prevent them from appearing in outputs.

2. **Map columns to standard concepts**
   - Create explicit column mapping logic for common aliases and local names.
   - Document every mapping in the report.
   - Avoid silent assumptions when mappings are ambiguous.

3. **Detect missing required or useful fields**
   - Identify which concepts are unavailable.
   - Add warnings for missing columns that limit specific care gap checks.
   - Continue processing checks that can be performed safely with available data.

4. **Create a data quality summary**
   - Report row counts, patient counts, missingness, duplicate patient keys, date parsing issues, invalid numeric values, and out-of-range values.
   - Describe which care gap categories were enabled or disabled because of schema limitations.

5. **Apply transparent rule-based care gap checks**
   - Use simple, non-proprietary rules.
   - Make thresholds and lookback windows configurable in YAML or JSON.
   - Require clinical expert review of thresholds before operational use.

6. **Create patient-level review flags**
   - Generate one row per anonymized patient or patient-period, depending on the input design.
   - Include only anonymized linkage keys and review flags needed for local clinical workflow.
   - Include brief, auditable evidence strings such as `HbA1c value above configured threshold` or `no eye exam date found in lookback window`.

7. **Create department-level summaries**
   - Summarize counts and rates by department, clinic, service line, facility, or cohort if those fields are available and non-identifying.
   - Avoid ranking clinicians or implying fault.

8. **Create a population-level summary**
   - Summarize denominator definitions, enabled rules, flag counts, overlap between categories, and data quality limitations.
   - Distinguish between missing documentation and confirmed absence of care.

9. **Generate a conservative report**
   - Use cautious wording: `review-worthy`, `possible care gap`, `requires clinician validation`, `data suggests`, and `not a diagnosis`.
   - Avoid overclaiming, guaranteed outcomes, or clinical directives.

10. **Clearly separate data patterns from clinical conclusions**
    - State what the dataset shows.
    - State what cannot be concluded from the dataset.
    - Recommend clinician and operational review rather than autonomous action.

## Rule-based signal examples

The following are non-proprietary example checks. They are not universal medical rules. Thresholds, lookback windows, denominator definitions, and specialist-follow-up definitions must be configurable and reviewed by local clinical experts before use.

- HbA1c is above a configured review threshold and no recent endocrinology follow-up is found in the available data.
- eGFR is below a configured review threshold and no recent nephrology follow-up is found in the available data.
- A diabetes diagnosis or diabetes cohort flag is present and no recent eye screening date is found in the configured lookback window.
- LDL is above a configured review threshold and cardiovascular risk follow-up documentation is missing or outdated.
- Repeated abnormal values are found across multiple lab dates and no recent encounter is documented.
- A known diabetes population member has no recent HbA1c measurement in the configured monitoring window.
- Blood pressure values exceed configured review thresholds and no recent follow-up encounter is found.
- Multiple independent review signals are present, creating a higher-priority queue item for human clinical review.

Do not convert these checks into claims such as `patient has uncontrolled diabetes`, `doctor missed referral`, or `must refer to specialist`. Use language like `data suggests a possible follow-up gap for clinician validation`.

## Output files

Expected outputs should be clearly named and safe for operational review:

- `care_gap_patient_flags.csv`
- `care_gap_population_summary.csv`
- `department_review_summary.csv`
- `data_quality_report.md`
- `care_gap_report.md`
- `assumptions_and_limitations.md`

Patient-level outputs should use only anonymized linkage keys. Aggregate outputs should avoid small-cell disclosures where applicable and should follow institutional privacy rules.

## Report style

Reports should be useful to:

- Hospital managers.
- Clinical operations teams.
- Quality improvement teams.
- Data science teams.

Use conservative, transparent language such as:

- `review-worthy`
- `possible care gap`
- `requires clinician validation`
- `data suggests`
- `not a diagnosis`
- `available records do not show`
- `documentation not found in the provided export`

Avoid language such as:

- `patient has disease`
- `doctor missed`
- `guaranteed revenue`
- `must refer`
- `automatic diagnosis`
- `confirmed non-adherence`
- `clinician failure`
- `guaranteed clinical improvement`

## Privacy and compliance

The agent must treat healthcare data conservatively:

- Use de-identified, anonymized, or synthetic data whenever possible.
- Do not export names, phone numbers, addresses, national IDs, medical record numbers, MRNs, emails, exact street addresses, or other direct identifiers.
- Keep patient linkage local, access-controlled, and separate from reports when possible.
- Avoid uploading patient-level data to external systems, public services, or non-compliant model providers.
- Follow HIPAA, GDPR, KVKK, institutional governance rules, data-use agreements, IRB or ethics requirements, and local privacy and security policies.
- Redact or block PHI-like columns from generated CSV, Markdown, logs, test snapshots, and notebook outputs.
- Warn users if requested operations appear to involve identifiable patient data or non-compliant data movement.

## Code-generation instructions

When asked to implement tooling for this skill, the coding agent should:

- Use Python and pandas for data loading, cleaning, rule evaluation, and reporting.
- Make thresholds, lookback windows, enabled rules, denominator definitions, and output settings configurable in a YAML or JSON file.
- Create clear column mapping logic with aliases and documented fallbacks.
- Add warnings for missing columns and disabled checks.
- Avoid failing when optional columns are missing.
- Produce both patient-level and aggregate outputs.
- Add synthetic example data for demos and tests.
- Include simple tests for rule behavior, missing-column behavior, and PHI-output blocking.
- Use deterministic outputs when possible so examples and tests are reproducible.
- Keep proprietary scoring systems out of the implementation.

Recommended implementation components include:

- `load_inputs.py` or equivalent logic for CSV, XLSX, Parquet, and SQL-export tables.
- `column_mapping.py` for mapping local field names to standard concepts.
- `rules.py` for transparent configurable checks.
- `quality.py` for missingness, invalid values, duplicate keys, and date parsing summaries.
- `reports.py` for Markdown and CSV outputs.
- `privacy.py` for PHI-like column detection and export safeguards.

## Test instructions

When building an example implementation, create the following files:

- `ehr-care-gap-analyzer/examples/synthetic_diabetes_ehr.csv`
- `ehr-care-gap-analyzer/examples/config.yaml`
- `ehr-care-gap-analyzer/examples/run_example.py`

The example should:

- Load synthetic diabetes patient data.
- Apply configurable care gap rules.
- Generate patient-level flags.
- Generate aggregate summary.
- Generate a Markdown report.
- Confirm no PHI-like columns are exported.
- Demonstrate behavior when optional follow-up columns are missing.
- Print or save a concise data quality summary.

Suggested tests include:

- A synthetic patient with HbA1c above the configured threshold and no recent endocrinology follow-up receives a review flag.
- A synthetic patient with a recent eye exam does not receive a retinopathy-screening gap flag.
- Missing optional columns produce warnings rather than crashes.
- Outputs do not contain direct identifier columns such as `name`, `phone`, `address`, `national_id`, `mrn`, or `medical_record_number`.
- Aggregate summaries match the generated patient-level flags.

## Example user prompts

Users may ask:

- `Analyze this anonymized diabetes EHR export for possible care gaps.`
- `Find patients with abnormal labs and no documented specialist follow-up.`
- `Generate a hospital operations summary from these care gap flags.`
- `Create a conservative care gap report for clinical review.`
- `Build a synthetic demo showing diabetes monitoring gaps without using real patient data.`
- `Summarize the data quality limitations before interpreting care gap counts.`

## Limitations

The agent must clearly communicate limitations, including:

- EHR data may be incomplete, delayed, incorrectly coded, or fragmented across systems.
- Absence of a record does not prove absence of care.
- Rules require local clinical validation and governance approval before operational use.
- Coding systems, laboratory names, units, diagnosis conventions, and referral workflows vary by institution.
- Outputs are for review, quality improvement, and operational planning, not autonomous medical decisions.
- Abnormal values can reflect context not present in the export, such as acute illness, outside care, specialist plans, patient preferences, or measurement error.
- Population summaries can be biased by missing data, cohort definition choices, and documentation practices.
- The skill does not provide billing advice, reimbursement guarantees, or financial outcome guarantees.
- The skill does not expose or depend on proprietary DiaRisk scoring logic.

## Quality checklist

Before finishing an implementation or report, verify that:

- Transparent rules are documented.
- Thresholds and lookback windows are configurable.
- No PHI or direct identifiers appear in outputs.
- A data quality report is included.
- Patient-level and aggregate outputs are separated.
- Clinical disclaimers are included.
- No proprietary scoring logic is exposed.
- No diagnosis or treatment claims are made.
- Missing data and disabled checks are reported.
- Outputs use conservative language such as `possible care gap` and `requires clinician validation`.
- Small-cell and re-identification risks are considered for aggregate reporting.
- The report avoids commercial overclaims and does not promise clinical, operational, billing, or financial results.

## Commercial safety review guidance

Before presenting final outputs, review the work for commercial and clinical safety:

- Keep the skill generic and useful to the healthcare analytics community.
- Support AId Core-style domain expertise through careful workflow design, data quality checks, privacy safeguards, and conservative reporting.
- Do not reveal, approximate, or market proprietary DiaRisk internals.
- Do not suggest guaranteed revenue, guaranteed case discovery, guaranteed improved outcomes, or replacement of clinical staff.
- Emphasize doctor-in-the-loop review, hospital operations planning, quality improvement, and transparent analytics.
