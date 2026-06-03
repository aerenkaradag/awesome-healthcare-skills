# Medical AI Validation Report Writer

## Description

This skill guides an AI agent to create structured medical AI validation reports from model metrics, datasets, intended use statements, evaluation designs, confusion matrices, calibration results, subgroup analyses, and error analyses. It is designed for health AI researchers, startup teams, data scientists, clinical collaborators, hospital innovation groups, and internal model governance teams that need clear documentation of how a medical AI model was evaluated.

This is a **report-writing and validation-structure skill**. It helps organize evidence, metrics, limitations, validation methodology, and open questions. It does **not** certify, approve, regulate, or clinically validate a medical AI model. It does **not** provide legal, regulatory, clinical, safety, reimbursement, or market authorization advice. Any report created with this skill should be reviewed by appropriate clinicians, statisticians, regulatory experts, privacy/security experts, and institutional stakeholders before being used for high-stakes decisions.

## When to use

Use this skill when the user wants to:

- Summarize model evaluation results.
- Write a clinical validation-style report.
- Compare internal and external validation performance.
- Document dataset characteristics.
- Report sensitivity, specificity, AUROC, AUPRC, PPV, NPV, F1-score, calibration, and related metrics.
- Write subgroup analysis sections.
- Document limitations and failure modes.
- Prepare investor, hospital, research, publication-support, diligence, or internal validation documentation.
- Convert CSV or JSON evaluation outputs into markdown tables, checklists, and structured report files.
- Audit an existing validation report for missing evidence, unclear denominators, overclaims, or insufficient limitations.
- Create documentation that is useful for both imaging models and EHR/tabular AI models.

## When not to use

Do not use this skill:

- As regulatory approval, certification, clearance, authorization, conformity assessment, or legal advice.
- To claim clinical safety, effectiveness, or readiness for deployment without appropriate evidence.
- To invent validation results, sample sizes, confidence intervals, benchmarks, subgroup metrics, or external validation findings.
- To hide, minimize, or obscure limitations, failure modes, missing evidence, domain shift risks, or uncertainty.
- As a replacement for clinical review, statistical review, regulatory/legal review, IRB/ethics review, privacy/security review, or institutional governance.
- To produce patient-specific diagnosis, treatment, triage, or clinical management recommendations.
- To convert exploratory retrospective results into unsupported prospective clinical claims.

## Expected inputs

The agent should request, parse, or clearly mark as missing the following inputs where relevant:

- Model name and version.
- Intended use statement.
- Intended users and deployment context.
- Model type, input modality, output type, and decision threshold.
- Dataset description.
- Data source names or categories, such as hospitals, registries, imaging archives, EHR tables, devices, or vendors.
- Data sources and collection period.
- Inclusion and exclusion criteria.
- Ground truth definition and reference standard.
- Labeling workflow, adjudication procedure, labeler qualifications, and inter-rater agreement, if available.
- Train/validation/test split description.
- Internal validation data and denominators.
- External validation data, if available.
- Confusion matrix.
- ROC and PR metrics.
- Sensitivity and specificity.
- PPV and NPV.
- Calibration metrics, such as calibration curve, calibration slope/intercept, expected calibration error, or Brier score.
- Confidence intervals or bootstrap results, if available.
- Subgroup metrics.
- Error examples, representative false positives, representative false negatives, and difficult cases.
- Baseline comparator or standard workflow, if available.
- Known limitations.
- Known failure modes.
- Risk controls and human oversight model.

## Expected outputs

When generating files, save outputs in a report folder such as `validation_report_output/` unless the user specifies another path. Useful outputs include:

- `validation_report.md`
- `executive_summary.md`
- `metrics_summary.csv`
- `subgroup_analysis.md`
- `limitations.md`
- `risk_and_failure_modes.md`
- `data_leakage_checklist.md`
- `clinical_claims_checklist.md`

The main report should be concise enough for stakeholders to read while preserving enough methodological detail for technical, clinical, and statistical review. Supporting files should make assumptions, missing evidence, and limitations easy to find.

## Report structure

Generate a report using the following structure. If a section cannot be completed from the available evidence, include it with `Missing`, `Not provided`, or `Not evaluated` rather than fabricating content.

1. **Executive summary**
   - Model name/version, intended use, evaluation dataset, headline metrics, external validation status, major limitations, and recommended next review steps.
2. **Model overview**
   - Model architecture or family, input data, output, threshold, version, training freeze date if available, and model card link if available.
3. **Intended use and intended users**
   - Population, clinical setting, intended users, supported workflow step, and explicit out-of-scope uses.
4. **Clinical context**
   - Clinical problem, target condition or endpoint, current workflow, why the task matters, and how model output would be reviewed by humans.
5. **Dataset description**
   - Cohort size, case/control counts, prevalence, modalities, source types, row/image/encounter/patient counts, missingness, and relevant data characteristics.
6. **Data sources and collection period**
   - Sites, hospitals, devices, EHR systems, vendors, countries/regions, and collection dates where permitted.
7. **Inclusion and exclusion criteria**
   - Cohort definition, excluded records, exclusion rationale, and potential selection bias.
8. **Ground truth / reference standard**
   - Label source, reference standard, adjudication process, label timing, uncertainty, and whether labels reflect clinical outcomes, expert review, billing codes, tests, pathology, imaging reads, or proxy labels.
9. **Model version and evaluation setup**
   - Model version, threshold, software environment, preprocessing, split method, patient-level separation, and frozen evaluation protocol.
10. **Primary endpoint**
    - Primary metric and endpoint definition, denominator, decision threshold, and success criterion if prespecified.
11. **Secondary endpoints**
    - Additional metrics, calibration, subgroup endpoints, operational metrics, or comparison endpoints.
12. **Performance metrics**
    - Present sensitivity, specificity, AUROC, AUPRC, PPV, NPV, F1-score, accuracy with caution, confidence intervals, denominators, and thresholds.
13. **Confusion matrix interpretation**
    - Summarize true positives, false positives, true negatives, and false negatives with denominators and clinical implications of errors.
14. **Subgroup analysis**
    - Report subgroup denominators, metrics, confidence intervals if available, missing subgroup data, and whether subgroup differences are statistically or clinically meaningful.
15. **Calibration analysis**
    - Report calibration curve, Brier score, calibration slope/intercept, expected calibration error, and whether probabilities are suitable for decision support.
16. **Error analysis**
    - Summarize false positives, false negatives, ambiguous cases, common failure modes, data quality issues, and example case themes without exposing PHI.
17. **Data leakage and bias checks**
    - Document split checks, duplicate checks, preprocessing leakage checks, metadata leakage risks, temporal leakage risks, and bias concerns.
18. **External validation, if available**
    - Describe external cohort, source, time period, population differences, performance metrics, and domain shift observations. If unavailable, state this explicitly.
19. **Comparison with baseline or standard workflow, if available**
    - Compare against clinicians, rules, prior models, standard screening workflow, or operational baseline only when evidence is provided.
20. **Limitations**
    - Clearly identify retrospective design, missing prospective validation, small sample sizes, class imbalance, lack of external data, missing subgroups, label noise, and generalizability concerns.
21. **Risk management considerations**
    - Describe possible harms, mitigations, monitoring needs, escalation paths, human review points, and post-deployment performance monitoring.
22. **Human oversight requirements**
    - State what humans must review, which decisions remain clinician-controlled, how uncertainty is communicated, and when model output should not be used.
23. **Conclusion**
    - Conservative summary of measured performance, readiness gaps, required reviews, and next validation steps.
24. **Appendix: metric definitions**
    - Define all reported metrics in plain language and, where useful, include formulas.
25. **Appendix: reproducibility details**
    - Include code version, data version, random seeds, environment, scripts, packages, evaluation date, and report generation date.

## Metric guidance

Report metrics with denominators, thresholds, and confidence intervals whenever available. If confidence intervals are not provided, state that uncertainty intervals were not available.

- **Sensitivity / recall**: proportion of true positive cases correctly identified. Emphasize clinical consequences of false negatives.
- **Specificity**: proportion of true negative cases correctly identified. Emphasize consequences of false positives and unnecessary follow-up.
- **Precision / PPV**: proportion of positive model predictions that are true positives. Interpret in relation to disease prevalence and deployment population.
- **NPV**: proportion of negative model predictions that are true negatives. Interpret in relation to prevalence and intended triage use.
- **AUROC**: threshold-independent discrimination across sensitivity/specificity tradeoffs. Note that AUROC can look strong even when positive-class performance is limited in imbalanced datasets.
- **AUPRC**: precision-recall performance, often especially informative for rare outcomes or imbalanced datasets.
- **F1-score**: harmonic mean of precision and recall. Use when balancing false positives and false negatives is meaningful, but do not treat it as a complete clinical utility measure.
- **Accuracy, with caution**: report only with class balance/prevalence context. Medical AI reports should not rely on accuracy alone, especially with imbalanced datasets.
- **Confidence intervals**: include method, such as bootstrap, Wilson, exact binomial, or DeLong, if available.
- **Calibration curve / Brier score**: report if probability outputs are used. Poor calibration may limit use for risk stratification even when discrimination is acceptable.
- **Decision threshold selection**: state the selected threshold, how it was chosen, whether it was prespecified, and the operating point tradeoff.

Avoid presenting any single metric as proof of clinical safety. Explain metric tradeoffs in the context of the intended use.

## Safety and honesty rules

The agent must follow these rules in every report:

- Never fabricate metrics, sample sizes, confidence intervals, p-values, external validation results, subgroup results, or comparator results.
- If metrics are missing, ask for them or mark them as missing.
- Report uncertainty clearly and avoid false precision.
- Highlight small sample sizes and unstable estimates.
- Highlight class imbalance and prevalence differences.
- Highlight absence of external validation.
- Highlight domain shift risk across sites, devices, populations, EHR systems, imaging protocols, clinical workflows, geography, language, or time.
- Separate measured performance from aspirational claims, roadmap claims, marketing language, and intended future use.
- Avoid saying `clinically proven`, `validated for clinical use`, `safe`, `approved`, `certified`, `regulatory-ready`, or equivalent unless the supplied evidence and expert review explicitly support that wording.
- Prefer conservative phrases such as `retrospective evaluation suggests`, `measured in this dataset`, `requires prospective validation`, and `requires clinical and statistical review`.
- Do not expose PHI in examples, reports, or generated artifacts.

## Data leakage checklist

Include a data leakage checklist in the report or as `data_leakage_checklist.md`. Mark each item as `Pass`, `Concern`, `Not assessed`, or `Not applicable`, and include evidence or notes.

- Patient-level split confirmed.
- Duplicate image, waveform, note, row, specimen, or encounter leakage checked.
- Same patient does not appear across train/validation/test splits.
- Same encounter, admission, study, imaging exam, accession, or episode does not appear across splits.
- Preprocessing, imputation, normalization, feature selection, dimensionality reduction, and calibration were not fitted on the full dataset before splitting.
- Label leakage through metadata was assessed, such as scanner ID, site code, timestamp, billing code, order text, acquisition protocol, downstream treatment, or report fields.
- Temporal leakage was assessed, including future labs, future diagnoses, future medications, future notes, post-outcome features, and retrospective labels visible at prediction time.
- Device/site leakage was assessed, including site-specific case mix, scanner/vendor effects, acquisition protocol differences, or EHR-system artifacts.
- Augmented images or transformed duplicates were not split across train/validation/test sets.
- Near-duplicate records, copied notes, repeated measurements, and templated text were checked where relevant.
- The test set remained locked until final evaluation.

## Subgroup analysis guidance

Subgroup sections should include denominators, prevalence, missingness, metrics, confidence intervals if available, and a cautious interpretation. If subgroup metrics are not available, explicitly state that subgroup performance was not evaluated.

Consider subgroup analyses by:

- Age groups.
- Sex.
- Race/ethnicity, language, socioeconomic proxy, or geography when ethically appropriate, legally permissible, and available.
- Site/hospital.
- Department, clinic, region, or data source.
- Device type, scanner vendor, sensor, imaging protocol, EHR vendor, or acquisition setting.
- Disease severity.
- Image quality, note quality, missingness burden, or data completeness.
- Comorbidities.
- Missingness groups.
- Data source groups.
- Time period, especially pre/post workflow changes or pre/post model training period.

Do not overinterpret subgroup differences from small samples. Flag subgroup gaps that require additional data or expert review.

## Clinical claims risk audit

When reviewing a report, investor deck, manuscript draft, or marketing statement, classify each clinical or operational claim into one of the following categories:

- **Supported by validation data**: directly backed by provided metrics, denominators, dataset description, and intended-use alignment.
- **Partially supported**: some evidence exists, but the claim is broader than the evaluation data, lacks external validation, has subgroup gaps, or needs more precise wording.
- **Unsupported**: not backed by supplied validation evidence or contradicts known limitations.
- **Requires prospective validation**: retrospective or offline evidence is insufficient for the stated deployment, workflow, outcome, or safety claim.
- **Requires regulatory/legal review**: claim may imply approval, medical device status, clinical safety/effectiveness, reimbursement, compliance, or other regulated positioning.

Rewrite unsupported or overbroad claims into conservative, evidence-aligned language. Separate product aspirations from measured validation results.

## Code-generation and file-generation instructions

If input metrics are provided as CSV or JSON, the agent should:

1. Load metrics using a transparent, reproducible script.
2. Validate required fields, including model name/version, dataset name, split, denominators, core performance metrics, threshold, and confusion matrix values when available.
3. Generate markdown tables for metrics, confusion matrix, subgroup performance, calibration, limitations, leakage checks, and clinical claims checks.
4. Generate `validation_report.md` and any requested companion files.
5. Avoid fabricating missing values. Use `Missing`, `Not provided`, `Not evaluated`, or a placeholder with a clear warning.
6. Create placeholders for missing evidence, especially external validation, confidence intervals, calibration, subgroup metrics, and baseline comparisons.
7. Save outputs in a report folder.
8. Include warnings for missing external validation and missing high-impact evidence.
9. Keep PHI out of generated examples and reports.
10. Include reproducibility metadata, such as generation date, input file names, script version, and assumptions.

Generated scripts should be deterministic, readable, and dependency-light unless the user requests a specific stack.

## Example artifacts and test instructions

An implementation of this skill should include example files under `medical-ai-validation-report-writer/examples/`:

- `sample_metrics.json`
- `sample_confusion_matrix.csv`
- `run_example.py`

The example should:

- Load sample metrics.
- Load a sample confusion matrix.
- Generate `validation_report.md` in an output folder.
- Include warnings for missing external validation.
- Include a data leakage checklist.
- Include a clinical claims checklist.
- Demonstrate missing-evidence placeholders instead of fabricated values.
- Be runnable with standard Python where possible.

## Example user prompts

Users may ask:

- "Turn these model results into a medical AI validation report."
- "Write a validation report for a diabetic retinopathy classifier using these metrics."
- "Create an executive summary for hospital stakeholders."
- "Audit this validation report for overclaims and missing evidence."
- "Generate a data leakage checklist for this medical imaging model."
- "Compare internal and external validation performance for this sepsis prediction model."
- "Summarize subgroup performance and identify validation gaps."

## Limitations

This skill has important limitations:

- It does not replace clinical validation.
- It does not provide regulatory approval, certification, clearance, or legal advice.
- Statistical review may be required, especially for confidence intervals, subgroup comparisons, sample size adequacy, calibration, and multiplicity.
- Prospective validation may be necessary before real-world clinical use.
- Performance may not generalize across sites, devices, populations, time periods, data vendors, care workflows, or documentation practices.
- Retrospective validation can miss workflow integration risks and unintended consequences.
- Report quality depends on the completeness and accuracy of user-provided evidence.

## Quality checklist

Before finalizing a report, verify that:

- Intended use is stated.
- Intended users and deployment context are stated.
- Dataset is described.
- Data sources and collection period are described or marked missing.
- Inclusion and exclusion criteria are documented.
- Ground truth / reference standard is defined.
- Model version and evaluation setup are documented.
- Metrics are reported with denominators.
- Decision threshold is documented.
- Confidence intervals are included if available or marked missing.
- External validation status is clear.
- Subgroup analysis is included or marked missing.
- Calibration analysis is included or marked missing when probabilities are used.
- Error analysis and representative failure modes are documented.
- Data leakage checks are included.
- Clinical claims are evidence-aligned.
- Limitations are explicit.
- No fabricated metrics or claims are present.
- Human oversight is described.
- Recommendations include clinician, statistician, and regulatory/legal expert review where appropriate.

## Final self-review for the agent

After writing or updating a validation report, review these questions:

- Does this help a healthcare AI team produce better validation documentation?
- Does it avoid regulatory, legal, and clinical overclaiming?
- Does it prevent fabricated metrics and make missing evidence visible?
- Is it useful for both imaging AI models and EHR/tabular AI models?
- Would a clinician, statistician, or regulatory expert be able to identify what was measured, what remains uncertain, and what requires further review?
