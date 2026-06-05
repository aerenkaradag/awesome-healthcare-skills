# Contributing

Thank you for your interest in improving this repository. Contributions are welcome when they make the skills more practical, safer, or easier to reproduce. This is a community-first, open-source project. Please read the guidance below before opening an issue or a pull request.

By contributing, you agree that your contributions will be licensed under the repository `LICENSE` (MIT) and that you will follow the `CODE_OF_CONDUCT.md`.

## Before you start

- Read `README.md` for the repository scope and safety boundaries.
- Read `docs/skill-design-principles.md` for how to design bounded healthcare AI skills.
- Read `docs/healthcare-ai-best-practices.md` for practical data, validation, and evidence guidance.
- Read `SECURITY.md` for privacy and data-handling rules.

## What we accept

Good contributions usually:

- Add a new, well-scoped healthcare AI skill.
- Improve an existing `SKILL.md` for clarity, safety, or reproducibility.
- Add synthetic fixtures or example scripts.
- Improve documentation.
- Fix errors, broken links, or inconsistent wording.

We are unlikely to accept contributions that add clinical decision logic, claim clinical validation, depend on proprietary scoring, or include real patient data.

## How to propose a new skill

1. Open an issue describing the workflow the skill supports, the intended users, and the data it expects.
2. Explain the safety boundaries and what the skill must not be used for.
3. Wait for brief feedback before investing significant effort, so scope and naming can be agreed early.
4. Submit a pull request that follows the required folder structure below.

A skill should support research, prototyping, data engineering, validation support, or workflow assistance. It should not present an AI agent as a clinical decision maker.

## Required structure for a skill folder

Each skill lives in its own top-level folder named with lowercase words separated by hyphens, for example `fhir-to-ml-dataset-builder`. The folder must contain a `SKILL.md`. An `examples/` subfolder with synthetic fixtures is recommended.

```text
your-skill-name/
  SKILL.md
  examples/        (recommended)
    run_example.py
    sample_input.*
```

Each `SKILL.md` must include the following sections, kept practical and readable:

- Purpose (what the skill does, in plain language).
- When to use.
- When not to use.
- Inputs (expected formats and fields).
- Outputs (named, reviewable artifacts).
- Workflow (ordered, bounded steps).
- Safety boundaries (explicit limits and privacy rules).
- Example prompts.
- Limitations.

Do not over-expand a `SKILL.md`. Prefer clear, bounded steps over long aspirational text.

## Safety expectations

Every skill and example must:

- Frame outputs as drafts, audits, summaries, checks, or review signals, not clinical decisions.
- Avoid wording such as "diagnose", "treat", or "recommend medication", except when explicitly framing them as actions the skill must not perform.
- Prefer wording such as "flag for review", "summarize", "audit", "prepare", "structure", and "check".
- State that outputs require review by qualified humans before any clinical, operational, legal, or regulatory use.
- Avoid claims of clinical validation, regulatory clearance, deployment readiness, or guaranteed outcomes.
- Keep final authority with qualified people and approved processes.

## Synthetic or de-identified examples only

All examples, fixtures, and tests must use synthetic or fully de-identified data.

- Do not submit real patient data, protected health information (PHI), or institution-sensitive exports.
- Do not include real names, dates of birth, addresses, phone numbers, emails, medical record numbers, accession numbers, or real free-text clinical notes.
- Do not include real patient images or DICOM files.
- Prefer programmatically generated, deterministic fixtures that are small enough to inspect.

If you are unsure whether data is safe to include, do not include it. Ask in an issue first.

## How to write good healthcare AI skill boundaries

Boundaries should be explicit and easy for both the agent and the reader to find.

- State the intended use and the population or data the skill targets.
- List concrete tasks the skill must not perform.
- Distinguish between research or prototyping support and clinical use.
- Tell the agent to inspect schemas, units, coding systems, missingness, and provenance before producing outputs.
- Require de-identified or synthetic data unless the user confirms an approved environment.
- Use conservative wording that separates observations from conclusions.

See `docs/skill-design-principles.md` for worked examples of good and weak wording.

## Pull request checklist

Before opening a pull request, confirm:

- [ ] The change matches the repository scope and safety boundaries.
- [ ] New or edited `SKILL.md` files include all required sections.
- [ ] Wording avoids diagnosis, treatment, and medication recommendations, except as explicit "do not do this" boundaries.
- [ ] Outputs are framed as review signals, summaries, audits, or structured drafts.
- [ ] Examples and fixtures use only synthetic or de-identified data.
- [ ] No PHI, secrets, credentials, or institution-sensitive data are included anywhere.
- [ ] No claims of clinical validation, regulatory clearance, or guaranteed outcomes.
- [ ] Markdown renders cleanly and links resolve.
- [ ] `CHANGELOG.md` is updated under the unreleased section when the change is user-facing.

## Reporting problems

For general bugs and documentation issues, open a GitHub issue. For privacy or safety concerns, follow `SECURITY.md`.
