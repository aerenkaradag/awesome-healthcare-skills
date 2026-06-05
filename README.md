# Awesome Healthcare AI Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Validate](https://github.com/aerenkaradag/awesome-healthcare-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/aerenkaradag/awesome-healthcare-skills/actions/workflows/validate.yml)
[![Latest release](https://img.shields.io/github/v/release/aerenkaradag/awesome-healthcare-skills?display_name=tag&sort=semver)](https://github.com/aerenkaradag/awesome-healthcare-skills/releases)

Awesome Healthcare AI Skills is a collection of open-source AI agent skills for healthcare AI development. The repository focuses on practical workflows around EHR data, FHIR, care gap analysis, medical AI validation, medical imaging dataset quality, and evidence or citation checking.

These skills are intended for research, prototyping, data engineering, validation support, and workflow assistance. They are not medical devices, clinical decision systems, or substitutes for professional medical judgment.

## Who this is for

This repository is for people who build with healthcare data and want bounded, reviewable workflows:

- Healthcare AI engineers and clinical data scientists.
- Healthtech startup teams and hospital innovation groups.
- Researchers preparing datasets, validation documentation, or evidence reviews.
- Anyone using an AI coding agent who wants explicit safety boundaries built into the workflow.

It is not for clinicians seeking patient-specific guidance, and it is not for clinical emergencies. See [Safety boundaries](#safety-boundaries).

## v0.1.0 scope

This is the first open-source release. The current scope is intentionally small:

- Five healthcare AI skills, each with a `SKILL.md`.
- Two documentation guides under `docs/`.
- Synthetic example data and scripts under `examples/`.
- Community files for licensing, contribution, conduct, and security.

Out of scope for v0.1.0: hosted services, packaged libraries, clinical validation, and any claim of regulatory clearance or deployment readiness. See [Roadmap](#roadmap) for what may come next.

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
| [`fhir-to-ml-dataset-builder`](./fhir-to-ml-dataset-builder/SKILL.md) | Convert FHIR or FHIR-derived resources into structured, ML-ready tables with documented mappings. | Synthetic FHIR bundles, data engineering prototypes, cohort feature extraction, reproducible dataset preparation. | Use de-identified or synthetic data by default. Confirm cohort definitions, code systems, units, dates, and leakage controls before using outputs. |
| [`ehr-care-gap-analyzer`](./ehr-care-gap-analyzer/SKILL.md) | Inspect EHR-derived tables for possible care gap signals and missing follow-up documentation. | Quality improvement prototypes, population health analytics, diabetes cohort review workflows, operational summaries. | Flags are review signals, not diagnoses or care instructions. Do not use for autonomous triage, treatment, denial of services, or patient-specific clinical decisions. |
| [`medical-ai-validation-report-writer`](./medical-ai-validation-report-writer/SKILL.md) | Turn model metrics, cohorts, evaluation notes, and limitations into a structured validation report. | Research validation summaries, internal model review, prototype evaluation documentation, metric interpretation support. | Does not establish clinical validity, regulatory clearance, or deployment readiness. Reports require statistical, clinical, legal, and governance review. |
| [`medical-imaging-dataset-auditor`](./medical-imaging-dataset-auditor/SKILL.md) | Audit imaging datasets for split integrity, duplicates, metadata leakage, class balance, and dataset documentation gaps. | Medical imaging dataset preparation, train/validation/test split review, external validation planning, leakage investigation. | Does not diagnose images or validate clinical performance. Patient-level separation, metadata privacy, label quality, and acquisition bias require human review. |
| [`health-ai-evidence-citation-checker`](./health-ai-evidence-citation-checker/SKILL.md) | Review healthcare AI answers for unsupported medical claims, citation quality, uncertainty language, and escalation boundaries. | Draft answer review, evidence hygiene checks, high-risk claim review, citation coverage for medical content. | Citation checks do not guarantee correctness. High-risk clinical, regulatory, or legal claims need qualified professional review. |

## Recommended first workflows

Start with one of these three skills if you are new to the repository:

1. **[`fhir-to-ml-dataset-builder`](./fhir-to-ml-dataset-builder/SKILL.md)**
   Use this when you have synthetic FHIR bundles or FHIR-derived tables and want a documented path toward ML-ready features.

2. **[`medical-ai-validation-report-writer`](./medical-ai-validation-report-writer/SKILL.md)**
   Use this when you already have evaluation results and need a structured report that separates metrics, assumptions, limitations, and review needs.

3. **[`ehr-care-gap-analyzer`](./ehr-care-gap-analyzer/SKILL.md)**
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
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── docs/
│   ├── healthcare-ai-best-practices.md
│   └── skill-design-principles.md
├── examples/
│   └── README.md
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

## Documentation

Two guides explain how these skills are designed and how to use them safely:

- [`docs/skill-design-principles.md`](./docs/skill-design-principles.md): how to design bounded, reviewable healthcare AI skills, with good and weak wording examples.
- [`docs/healthcare-ai-best-practices.md`](./docs/healthcare-ai-best-practices.md): practical guidance on data handling, FHIR and EHR quality, ML dataset preparation, validation, imaging dataset quality, evidence and citations, and deployment boundaries.

Synthetic example data and a generator script are documented in [`examples/README.md`](./examples/README.md).

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

Before opening a pull request, read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the required skill structure and PR checklist, and confirm that examples do not contain PHI or institution-sensitive data. Participation is governed by the [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md). Privacy and safety issues should follow [`SECURITY.md`](./SECURITY.md).

## Roadmap

Near-term candidates include a healthcare AI evaluator, a FHIR data quality auditor, a synthetic healthcare dataset generator, a clinical AI product reviewer, and more example fixtures. See [`docs/roadmap.md`](./docs/roadmap.md) for the full near-term and later plans.

This roadmap describes intent, not commitments or timelines.

## License

MIT License unless otherwise specified. See [`LICENSE`](./LICENSE).

## Releases and changelog

Notable changes are tracked in [`CHANGELOG.md`](./CHANGELOG.md). Release notes are under [`docs/releases/`](./docs/releases/), starting with [`v0.1.0`](./docs/releases/v0.1.0.md).

## Maintainer note

Maintained by contributors interested in safer, more practical healthcare AI workflows.
