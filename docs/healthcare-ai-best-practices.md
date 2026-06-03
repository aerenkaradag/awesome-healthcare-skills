# Healthcare AI Best Practices for Skill Users

This document gives practical guidance for builders using the skills in this repository. It is not legal, regulatory, or clinical advice. Use it to structure safer research, prototyping, data engineering, validation support, and workflow assistance.

## 1. Data handling

Use the least sensitive data that can support the task.

- Use synthetic or de-identified data for examples, tests, demos, public issues, and pull requests.
- Avoid PHI in public repositories, logs, prompts, screenshots, notebooks, and generated reports.
- Do not include patient names, addresses, phone numbers, dates of birth, medical record numbers, accession numbers, direct identifiers, or real free-text notes in repository fixtures.
- Document data assumptions, including source system, extraction date, inclusion criteria, exclusion criteria, de-identification status, and known limitations.
- Keep patient-level outputs in approved environments with appropriate access controls.
- Aggregate or suppress small counts when sharing summaries.
- Treat clinical notes, imaging metadata, and filenames as potentially sensitive.

Before using any skill with identifiable data, confirm that the environment, data flow, permissions, contracts, and institutional approvals support the planned use.

## 2. FHIR and EHR data quality

FHIR and EHR exports are often incomplete, local, and inconsistent. Inspect the data before building features, cohorts, or reports.

Key checks include:

- **Missingness**: Measure missing values by field, time period, site, encounter type, and patient subgroup where feasible.
- **Coding systems**: Document whether diagnoses, procedures, labs, medications, and observations use ICD, SNOMED CT, LOINC, RxNorm, CPT, local codes, or mixed coding systems.
- **Longitudinal consistency**: Check whether patient timelines are plausible, whether dates are in the expected order, and whether repeated measures are handled consistently.
- **Unit normalization**: Normalize lab and vital sign units before applying thresholds or deriving features. Record original units and conversion rules.
- **Encounter context**: Interpret observations in the context of inpatient, outpatient, emergency, telehealth, and lab-only encounters when available.
- **Join keys**: Confirm patient, encounter, observation, medication, and procedure identifiers before joining tables.
- **FHIR version and profile assumptions**: Record the FHIR version and any implementation guide or local profile assumptions if known.

Do not assume that missing documentation means care was not provided. It may mean the event occurred outside the available data, was recorded in another system, or was not mapped into the export.

## 3. ML dataset preparation

Dataset preparation should prevent leakage and preserve the meaning of labels and features.

Important practices include:

- **Patient-level splits**: Split by patient, not by row, image, encounter, or observation, unless there is a documented reason and leakage risk has been reviewed.
- **Temporal splits**: For prediction tasks, define feature windows and label windows so features occur before labels. Use time-based holdouts when they better match intended use.
- **Leakage prevention**: Remove or quarantine fields that directly encode the label, future events, post-outcome treatment, billing artifacts, filenames, or site-specific shortcuts.
- **Feature provenance**: Track each feature to its source table, code system, unit, date window, transformation, and missingness handling.
- **Label definition**: Define labels in operational terms, including source codes, time windows, adjudication process, exclusions, and known noise.
- **Cohort definition**: Record inclusion and exclusion criteria, index date logic, minimum history requirements, and follow-up requirements.
- **Imbalance and prevalence**: Report class prevalence by split and subgroup. Choose metrics that match the class distribution and intended evaluation question.
- **Reproducible splits**: Save split assignments, seeds, and split logic so results can be audited.

A high model score can be a sign of leakage, duplicated records, an easy proxy variable, or a narrow dataset. Investigate before interpreting performance.

## 4. Medical AI validation

Validation reports should be precise about what was tested, on which data, and with what limitations.

Include metrics that match the task:

- **Sensitivity and specificity**: Useful for thresholded classification. Report the threshold and rationale.
- **AUROC and AUPRC**: AUROC summarizes ranking performance across thresholds. AUPRC is often important for rare outcomes.
- **Calibration**: Check whether predicted probabilities match observed outcome frequencies. Include calibration plots or summary measures when available.
- **Subgroup analysis**: Evaluate performance by relevant demographic, site, device, time period, language, insurance, clinical subgroup, or acquisition subgroup when data and governance allow.
- **External validation**: Test on data from a different site, time period, device, or population when possible.
- **Dataset shift**: Compare development and validation datasets for differences in prevalence, missingness, coding, devices, sites, and workflows.
- **Confidence intervals**: Include uncertainty estimates where feasible, especially for small datasets or subgroup results.
- **Error analysis**: Review false positives and false negatives using de-identified or approved review processes.

Do not claim that a model is clinically validated, safe, effective, or deployment-ready based only on an internal metric table.

## 5. Medical imaging dataset quality

Medical imaging datasets have special leakage and bias risks. Audit both image files and metadata.

Key checks include:

- **Patient-level split**: Ensure that the same patient does not appear across train, validation, test, or external sets. Also consider study, visit, eye, lesion, accession, scanner session, and volume identifiers.
- **Duplicate images**: Check exact duplicates, near-duplicates, repeated basenames, derived crops, augmented copies, and duplicated studies across splits.
- **Device and site bias**: Summarize scanner, camera, vendor, acquisition site, department, and protocol distribution by label and split.
- **Label noise**: Document label source, annotator type, adjudication process, label date, disease definitions, and known ambiguity.
- **Acquisition protocol differences**: Check image size, spacing, view, sequence, contrast, reconstruction kernel, compression, color mode, and preprocessing differences.
- **Metadata leakage**: Review filenames, folder names, DICOM tags, burned-in text, overlays, timestamps, and acquisition fields that may reveal labels or sites.
- **Corrupted files**: Identify unreadable, zero-byte, truncated, malformed, or unsupported files.

Strong imaging performance on a random image split may not generalize if patient, site, device, or study-level dependencies were not handled correctly.

## 6. Evidence and citation quality

Healthcare AI outputs should make it clear which statements are factual, which are recommendations, and which require human review.

Use these practices:

- **Separate facts from recommendations**: A factual statement about a guideline, study, or dataset is different from a recommendation for a patient or institution.
- **Cite high-risk claims**: Cite claims about diagnosis, treatment, prognosis, safety, effectiveness, contraindications, guidelines, and regulatory status.
- **Avoid overconfident medical language**: Prefer calibrated wording such as "may," "is associated with," "was observed in," and "requires review" when uncertainty exists.
- **Include uncertainty and escalation language**: State when evidence is incomplete, when a claim is outside scope, and when qualified clinical review is required.
- **Check source relevance**: Confirm that citations support the specific claim, population, intervention, comparator, outcome, and time frame.
- **Avoid citation padding**: Do not attach references that are only loosely related to the claim.
- **Keep recommendations bounded**: Do not turn general evidence into patient-specific advice unless the workflow is approved for that use and reviewed by qualified professionals.

A citation can support a factual statement without supporting a clinical recommendation in a new setting.

## 7. Deployment boundaries

Most repository workflows are intended for research, prototyping, validation support, and workflow assistance. Treat clinical deployment as a separate process.

Before any real-world use, address:

- **Research or prototype vs clinical use**: State whether the workflow is exploratory, retrospective, prospective, operational, or intended for clinical integration.
- **Human review**: Define who reviews outputs, how disagreements are handled, and what the system is not allowed to decide.
- **Audit logs**: Record input versions, model versions, prompts or configurations, code versions, outputs, reviewers, and decisions where appropriate.
- **Monitoring**: Monitor performance, missingness, data drift, workflow drift, calibration, subgroup performance, failures, and user feedback.
- **Local regulatory requirements**: Consult qualified legal, regulatory, compliance, privacy, and clinical experts for the jurisdiction and intended use.
- **Change management**: Document updates to data pipelines, prompts, models, thresholds, code, labels, and review workflows.
- **Incident response**: Define how errors, unsafe outputs, privacy issues, and user concerns are detected and handled.

Do not infer regulatory status, clinical validity, or safety from the presence of a skill, report, metric, or checklist.

## 8. Practical checklist

Use this checklist before sharing outputs, publishing examples, or using results in a project review.

### Data and privacy

- [ ] The data is synthetic, dummy, or de-identified, or the environment is approved for identifiable health data.
- [ ] Public files, prompts, logs, screenshots, and examples contain no PHI or institution-sensitive data.
- [ ] Data assumptions, source systems, extraction dates, and limitations are documented.
- [ ] Patient-level outputs are protected or aggregated as appropriate.

### FHIR, EHR, and cohort quality

- [ ] Required fields, optional fields, join keys, and date fields were inspected.
- [ ] Coding systems and local code mappings are documented.
- [ ] Units were normalized or unit limitations are clearly stated.
- [ ] Missingness and encounter context were reviewed.
- [ ] Cohort, feature, index date, and label definitions are explicit.

### ML and validation

- [ ] Train, validation, test, and external splits avoid patient-level leakage.
- [ ] Temporal leakage and future information were checked.
- [ ] Feature provenance is documented.
- [ ] Metrics include appropriate thresholded and ranking measures for the task.
- [ ] Calibration, subgroup performance, external validation, and dataset shift were considered.
- [ ] Limitations and unresolved review questions are included.

### Imaging datasets

- [ ] Patient, study, visit, eye, accession, or scanner-session overlap across splits was checked.
- [ ] Duplicate and near-duplicate images were assessed where feasible.
- [ ] Site, device, acquisition, and protocol distributions were reviewed.
- [ ] Label source and label quality limitations are documented.
- [ ] Metadata and filenames were checked for leakage and sensitive identifiers.

### Evidence and outputs

- [ ] High-risk medical claims are cited or removed.
- [ ] Facts, recommendations, assumptions, and limitations are separated.
- [ ] Overconfident language was replaced with bounded wording.
- [ ] Outputs state that qualified human review is required where appropriate.
- [ ] No output claims clinical validation, deployment readiness, regulatory clearance, or guaranteed outcomes unless formally supported and professionally reviewed.
