# Skill Design Principles for Healthcare AI Agents

This guide describes how to design healthcare AI agent skills that are practical, bounded, and reviewable. It is intended for contributors writing or revising `SKILL.md` files in this repository.

Healthcare AI skills should help builders complete structured research, prototyping, data engineering, validation, and workflow support tasks. They should not create the impression that an agent can make independent clinical decisions.

## 1. What makes a good healthcare AI skill

A good healthcare AI skill is:

- **Specific**: It names the workflow it supports and the data it expects.
- **Bounded**: It states what the skill must not be used for.
- **Data-aware**: It tells the agent to inspect schemas, missingness, coding systems, units, and provenance.
- **Review-oriented**: It frames outputs as drafts, audit findings, quality checks, or review signals.
- **Reproducible**: It encourages deterministic steps, fixtures, logs, and documented assumptions.
- **Conservative with claims**: It avoids clinical conclusions that the data and workflow cannot support.
- **Useful to builders**: It gives enough detail for an agent to produce code, reports, tables, or checklists that a human can review.

A weak skill usually has broad promises, vague inputs, missing safety boundaries, and no testable output contract.

## 2. Scope and intended use

Every skill should clearly define its intended use. In healthcare AI, the difference between research support and clinical use must be visible.

Include statements such as:

- This skill supports research, prototyping, validation support, data engineering, or workflow assistance.
- This skill is not a medical device, diagnostic system, treatment system, or substitute for professional judgment.
- Outputs require review by qualified humans before use in clinical, operational, legal, or regulatory settings.

### Good vs bad wording

Bad:

> Diagnose diabetic nephropathy from lab values.

Good:

> Flag records with possible nephropathy-related care gap signals for human review.

Bad:

> Determine whether the model is safe for hospital deployment.

Good:

> Summarize available validation results, limitations, subgroup findings, and unresolved review questions for qualified stakeholders.

## 3. Input and output contracts

A skill should tell the agent what inputs to inspect and what outputs to produce. Do not assume that healthcare data is clean or standardized.

A useful input contract may include:

- Supported formats, such as CSV, JSON, FHIR bundles, DICOM metadata, image folders, Parquet, SQL exports, or metric tables.
- Required fields and optional fields.
- Acceptable substitutes for common local column names.
- Expected date formats, coding systems, units, and join keys.
- Privacy expectations, such as de-identified or synthetic input data.

A useful output contract may include:

- A structured report.
- A machine-readable CSV, JSON, or Markdown summary.
- A column mapping table.
- A missingness and data quality summary.
- A list of review flags with severity labels that do not imply diagnosis.
- A limitations section.
- A reproducibility section with commands, scripts, assumptions, and versions.

Bad:

> Read the patient file and find problems.

Good:

> Inspect the provided de-identified tables, identify patient keys and date columns, map available fields to documented concepts, report missing fields, and produce a care gap summary for human review.

## 4. Safety boundaries

Safety boundaries should be explicit and repeated when the workflow touches clinical concepts, health data, patient-level records, or model performance.

A skill should prohibit use for:

- Autonomous diagnosis, triage, treatment, monitoring, or patient management.
- Medication recommendations to patients.
- Denial of care, services, insurance, benefits, or coverage.
- Claims of clinical validation, deployment readiness, regulatory clearance, or guaranteed outcomes.
- Processing identifiable health data outside approved environments.

Bad:

> Tell the patient what medication to take.

Good:

> Identify missing medication fields and summarize data quality issues.

Bad:

> Rank patients by who needs treatment first.

Good:

> Group de-identified records by transparent review signals so qualified staff can decide whether further review is appropriate.

## 5. Data privacy assumptions

Skills should assume that public examples, tests, and fixtures use synthetic or de-identified data. Contributors should not include PHI, patient images, direct identifiers, clinical notes from real patients, or institution-sensitive exports.

A skill should instruct the agent to:

- Detect columns that may contain direct identifiers or sensitive free text.
- Avoid printing raw patient identifiers in reports.
- Hash, suppress, or aggregate identifiers when needed.
- Keep patient-level outputs local and controlled.
- Warn when data appears identifiable or when the environment is not appropriate for PHI.

Do not write skills that encourage uploading real patient data to external systems unless the user has confirmed the required authorization, environment, data flow, and controls.

## 6. Clinical claim discipline

Healthcare AI skills must separate observations from conclusions. A skill can help identify missing data, possible review signals, or unsupported claims. It should not make final clinical judgments.

Use wording such as:

- possible signal
- may merit review
- documentation not found in the provided data
- available data suggests
- requires clinician validation
- outside the scope of this workflow

Avoid wording such as:

- the patient has
- the clinician missed
- the model proves
- safe for deployment
- clinically validated
- guaranteed reduction in risk

Bad:

> The patient has uncontrolled diabetes and needs urgent treatment.

Good:

> The record contains elevated HbA1c values in the provided data and no recent follow-up documentation was found. Flag for qualified clinical review.

Bad:

> The cited article proves the recommendation is correct.

Good:

> The citation appears relevant to the factual claim, but recommendation strength and applicability require human review.

## 7. Reproducibility

A healthcare AI skill should make it possible to repeat the workflow and understand how outputs were generated.

Include guidance to document:

- Input file names or dataset versions, without exposing sensitive paths if inappropriate.
- Schema mappings and code system assumptions.
- Inclusion and exclusion criteria.
- Feature definitions and label definitions.
- Date windows and lookback periods.
- Model metrics and confidence intervals when available.
- Random seeds and split strategies.
- Software versions, scripts, and commands.

Reproducibility is especially important when a workflow produces validation reports, cohort tables, or dataset audits.

## 8. Evaluation and testability

Skills should describe how a contributor or user can tell whether the workflow worked as expected.

Useful checks include:

- Unit tests for parsing and schema mapping.
- Fixture-based tests using synthetic data.
- Expected output snapshots for reports or summaries.
- Validation of required columns and graceful handling of missing optional fields.
- Leakage checks for patient overlap across ML splits.
- Consistency checks for units, dates, and coding systems.
- Manual review checkpoints for clinical, statistical, and privacy issues.

Bad:

> Generate a report and assume it is correct.

Good:

> Generate a report, include the source metrics used, list missing inputs, and add a checklist of items that require human review.

## 9. Examples and fixtures

Examples make skills easier to use and safer to test. They should be synthetic, small enough to inspect, and designed around common failure modes.

Good examples include:

- A synthetic FHIR bundle with missing units and mixed code systems.
- A de-identified-style diabetes cohort fixture with missing eye exam dates.
- A model metrics table with subgroup performance gaps.
- A fake imaging metadata CSV with duplicate patient IDs across splits.
- A sample answer with unsupported medical claims and incomplete citations.

Examples should not include:

- Real patient names, dates of birth, addresses, phone numbers, medical record numbers, accession numbers, or full clinical notes.
- Real patient images or DICOM files.
- Proprietary scoring logic or institution-specific confidential workflows.

## 10. Anti-patterns

Avoid these patterns when designing healthcare AI skills:

- **Unbounded clinical authority**: The skill tells the agent to diagnose, treat, triage, or make patient-specific recommendations.
- **Vague data requirements**: The skill does not say what files, columns, schemas, or outputs are expected.
- **Hidden scoring**: The skill asks for opaque risk scores without transparent definitions.
- **Overstated validation**: The skill claims that a report proves safety, efficacy, or deployment readiness.
- **Privacy leakage**: The skill prints identifiers, free-text notes, or raw image metadata in public outputs.
- **Metric-only evaluation**: The skill reports AUROC but ignores calibration, subgroup performance, external validation, and dataset shift.
- **Image-level splitting for patient tasks**: The skill allows the same patient, study, or visit to appear across train and test sets without warning.
- **Unsupported evidence claims**: The skill treats weak, old, or irrelevant citations as proof.
- **No human review**: The skill lacks review checkpoints for clinical, legal, statistical, and governance questions.

A strong healthcare AI skill should help an agent be useful while keeping the final authority with qualified people and approved processes.
