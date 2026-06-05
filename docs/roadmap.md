# Roadmap

This roadmap describes intent and direction, not commitments or timelines. Priorities may change based on community input and contributions. New skills should follow `docs/skill-design-principles.md` and the safety expectations in `CONTRIBUTING.md`.

## Near-term

- **Healthcare AI evaluator**: a skill to structure evaluation plans and summarize results for healthcare AI models, with explicit metrics, denominators, and review gaps.
- **FHIR data quality auditor**: a skill to inspect FHIR exports for missingness, coding-system inconsistencies, unit problems, and timeline issues before feature building.
- **Synthetic healthcare dataset generator**: tooling to generate larger synthetic, de-identified fixtures for testing skills across modalities and edge cases.
- **Clinical AI product reviewer**: a skill to audit product claims, intended-use statements, and documentation for overclaims and missing evidence.
- **More example fixtures**: additional synthetic datasets and end-to-end demonstrations for each skill.

## Later

- **More FHIR profiles**: broader resource coverage and support for additional implementation guides and local profiles.
- **More imaging dataset audit examples**: synthetic imaging fixtures covering patient-level leakage, duplicates, and domain shift.
- **Optional evaluation scripts**: reusable, dependency-light scripts that demonstrate metric computation and leakage checks on synthetic data.
- **Community-contributed skills**: skills proposed and maintained by the community that fit the bounded, review-oriented design.

## Out of scope

The following remain out of scope for this project:

- Clinical decision support, diagnosis, treatment, or medication recommendations.
- Claims of clinical validation, regulatory clearance, or deployment readiness.
- Processing of real patient data or PHI in this repository.
