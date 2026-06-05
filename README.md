# Awesome Healthcare AI Skills

Awesome Healthcare AI Skills is a collection of open-source AI agent skills for healthcare AI development. The repository focuses on practical workflows around EHR data, FHIR, care gap analysis, medical AI validation, medical imaging dataset quality, and evidence or citation checking.

These skills are intended for research, prototyping, data engineering, validation support, and workflow assistance. They are not medical devices, clinical decision systems, or substitutes for professional medical judgment.

## Why this exists

Many AI agent skills are written for general software tasks. Healthcare AI work has additional constraints that should be explicit in the workflow itself:

- Health data requires careful privacy handling, schema inspection, and provenance tracking.
- FHIR and EHR exports are heterogeneous, incomplete, and often institution-specific.
- Validation work needs clear assumptions, test data, metrics, cohort definitions, and subgroup checks.
- Medical claims require discipline, citations, uncertainty language, and human review.
- Safety boundaries should be visible to both the agent and the person using it.

This repository packages repeatable healthcare AI workflows as agent-readable skills. Each skill is designed to help an AI coding agent follow a bounded process, ask better questions about data and outputs, and avoid overstating what the workflow can support.

## Available skills

| Skill | Purpose | Best used for | Risk and safety notes |
| --- | --- | --- | --- |
| `fhir-to-ml-dataset-builder` | Convert FHIR or FHIR-derived resources into structured, ML-ready tables with documented mappings. | Synthetic FHIR bundles, data engineering prototypes, cohort feature extraction, reproducible dataset preparation. | Use de-identified or synthetic data by default. Confirm cohort definitions, code systems, units, dates, and leakage controls before using outputs. |
| `ehr-care-gap-analyzer` | Inspect EHR-derived tables for possible care gap signals and missing follow-up documentation. | Quality improvement prototypes, population health analytics, diabetes cohort review workflows, operational summaries. | Flags are review signals, not diagnoses or care instructions. Do not use for autonomous triage, treatment, denial of services, or patient-specific clinical decisions. |
| `medical-ai-validation-report-writer` | Turn model metrics, cohorts, evaluation notes, and limitations into a structured validation report. | Research validation summaries, internal model review, prototype evaluation documentation, metric interpretation support. | Does not establish clinical validity, regulatory clearance, or deployment readiness. Reports require statistical, clinical, legal, and governance review. |
| `medical-imaging-dataset-auditor` | Audit imaging datasets for split integrity, duplicates, metadata leakage, class balance, and dataset documentation gaps. | Medical imaging dataset preparation, train/validation/test split review, external validation planning, leakage investigation. | Does not diagnose images or validate clinical performance. Patient-level separation, metadata privacy, label quality, and acquisition bias require human review. |
| `health-ai-evidence-citation-checker` | Review healthcare AI answers for unsupported medical claims, citation quality, uncertainty language, and escalation boundaries. | Draft answer review, evidence hygiene checks, high-risk claim review, citation coverage for medical content. | Citation checks do not guarantee correctness. High-risk clinical, regulatory, or legal claims need qualified professional review. |

## Recommended first workflows

Start with one of these skills if you are new to the repository:

1. **`fhir-to-ml-dataset-builder`**
   Use this when you have synthetic FHIR bundles or FHIR-derived tables and want a documented path toward ML-ready features.

2. **`medical-ai-validation-report-writer`**
   Use this when you already have evaluation results and need a structured report that separates metrics, assumptions, limitations, and review needs.

3. **`ehr-care-gap-analyzer`**
   Use this when you want to inspect de-identified EHR-derived records for possible population-level care gap signals that require human review.

## Example use cases

- Convert synthetic FHIR bundles into ML-ready patient-level tables.
- Audit an EHR-derived diabetes cohort for possible care gap signals and missing follow-up documentation.
- Generate a validation report from model metrics, cohort definitions, subgroup results, and known limitations.
- Check whether a healthcare AI answer contains unsupported medical claims or weak citations.
- Audit a medical imaging dataset for leakage, duplicate images, patient overlap across splits, and split imbalance.

## Safety boundaries

These boundaries apply across the repository:

- These skills do not provide medical advice.
- These skills do not diagnose, treat, monitor, or manage patients.
- These skills are not clinical decision systems and should not be used as substitutes for professional judgment.
- Use de-identified or synthetic data unless you have proper legal, institutional, contractual, and technical authorization to process identifiable health data.
- Do not place PHI, patient images, direct identifiers, or sensitive free-text notes in public issues, examples, commits, or pull requests.
- Outputs should be reviewed by qualified humans before being used for research conclusions, operational decisions, clinical communication, or deployment planning.
- Regulatory, legal, reimbursement, safety, and clinical claims require professional review.
- The skills are not claimed to be clinically validated.

## Repository structure

```text
awesome-healthcare-skills/
├── README.md
├── docs/
│   ├── healthcare-ai-best-practices.md
│   └── skill-design-principles.md
├── fhir-to-ml-dataset-builder/
│   └── SKILL.md
├── ehr-care-gap-analyzer/
│   └── SKILL.md
├── medical-ai-validation-report-writer/
│   └── SKILL.md
├── medical-imaging-dataset-auditor/
│   └── SKILL.md
└── health-ai-evidence-citation-checker/
    └── SKILL.md
```

## How to use

Each skill folder contains a `SKILL.md` file. A `SKILL.md` is an agent-readable instruction document that describes when to use the skill, what inputs to expect, what outputs to produce, and which safety boundaries apply.

Python examples use the dependencies listed in `requirements.txt`. Install them in your local environment before running examples that use pandas or Pillow.

A typical tool-agnostic workflow is:

1. Choose the skill that matches the task.
2. Provide the AI coding agent with the relevant `SKILL.md` and the task context.
3. Use synthetic or de-identified fixtures when testing the workflow.
4. Ask the agent to inspect schemas, file layouts, assumptions, and missing fields before producing outputs.
5. Review generated code, reports, tables, and claims before sharing or using them.
6. Keep all patient-specific or institution-sensitive work inside approved environments.

The skills are designed to be adapted to different coding agents, notebooks, local scripts, and repository workflows. They are not tied to a single agent platform.

## Contributing

Contributions are welcome when they make the skills more practical, safer, or easier to reproduce. Good contributions should:

- Include clear safety boundaries and intended-use limits.
- Use synthetic, dummy, or de-identified data in examples and tests.
- Avoid unsupported clinical, legal, regulatory, or financial claims.
- Include examples, fixtures, or expected outputs where possible.
- Document assumptions, input contracts, and output formats.
- Prefer transparent logic over hidden scoring rules.
- Keep workflows practical and reproducible for healthcare AI engineers, clinical data scientists, healthtech startups, hospital innovation teams, and researchers.

Before opening a pull request, check that examples do not contain PHI or institution-sensitive data.

## License

MIT License unless otherwise specified. See `LICENSE`.

## Maintainer note

Maintained by contributors interested in safer, more practical healthcare AI workflows.
