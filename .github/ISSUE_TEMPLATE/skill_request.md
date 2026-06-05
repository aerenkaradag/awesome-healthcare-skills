---
name: Skill request
about: Propose a new healthcare AI skill
title: "[Skill] "
labels: skill-request
---

Please read `CONTRIBUTING.md` and `docs/skill-design-principles.md` before proposing a skill.

## What workflow should the skill support

Describe the bounded task the skill helps an AI coding agent perform.

## What inputs are expected

Formats and fields, for example CSV, FHIR bundles, image folders, or metric tables.

## What outputs are expected

Named, reviewable artifacts, for example reports, tables, checklists, or summaries.

## What safety boundaries are needed

What the skill must not do, and which review steps are required. Avoid diagnosis, treatment, and medication recommendations except as explicit "do not do this" boundaries.

## Can synthetic examples be provided

Can you contribute small synthetic or de-identified fixtures to test the skill? If yes, describe them.

## Reminder

Do not include real patient data or PHI in this issue. See `SECURITY.md`.
