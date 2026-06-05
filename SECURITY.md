# Security and Privacy Policy

This repository contains documentation and agent-readable skills for healthcare AI development. It does not host a deployed service. The most important risks here are privacy of health data, accidental disclosure of secrets, and unsafe use of the skills. Please read this policy before contributing or reporting an issue.

## Do not submit real patient data

Do not submit real patient data to this repository in any form, including issues, pull requests, commits, examples, fixtures, tests, screenshots, or discussions.

All data in this repository must be synthetic or fully de-identified.

## Do not submit protected health information (PHI)

Do not include PHI or directly identifying information, including but not limited to:

- Real names, initials tied to real people, or signatures.
- Dates of birth or other identifying dates tied to a real person.
- Addresses, phone numbers, or email addresses.
- Medical record numbers, accession numbers, insurance identifiers, or national identifiers.
- Real patient images, DICOM files, or scans.
- Real free-text clinical notes.

If you are unsure whether something is identifiable, do not submit it.

## Do not include secrets

Do not commit secrets or credentials, including:

- API keys, tokens, or passwords.
- Connection strings or database credentials.
- Private keys or certificates.
- Internal hostnames, endpoints, or institution-specific configuration that should remain private.

If a secret is committed by accident, treat it as compromised, rotate it, and report the exposure so history can be addressed.

## Scope and intended use

These skills support research, prototyping, data engineering, validation support, and workflow assistance. They are not clinical tools.

- This repository is not for clinical emergencies.
- This repository is not for patient-specific medical advice, diagnosis, or treatment.
- These skills do not provide medical advice and are not clinically validated.
- Outputs require review by qualified humans before any clinical, operational, legal, or regulatory use.

If you are dealing with a medical emergency, contact your local emergency services or appropriate care provider. This repository cannot help with urgent or patient-specific clinical situations.

## How to report a privacy or safety issue

If you discover real patient data, PHI, a committed secret, or another privacy or safety concern in this repository:

1. Do not open a public issue that repeats or links to the sensitive content.
2. Report it privately to the maintainers using GitHub's private vulnerability reporting for this repository, or by contacting a maintainer directly.
3. Include the file path or location and a short description of the concern, without copying the sensitive data into the report.

We will review reports promptly, remove or remediate exposed content, and address repository history where needed. We will respect the privacy of anyone who reports a concern.

## Responsible use reminder

Users are responsible for complying with applicable laws and policies for any data they process, including HIPAA, GDPR, KVKK, data-use agreements, and institutional governance. Confirm that your environment, permissions, and data flow are appropriate before using any skill with identifiable health data.
