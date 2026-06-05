#!/usr/bin/env python3
"""Validate the synthetic example files for the healthcare AI skills.

This script performs lightweight, dependency-free checks on the three example
data files so they stay safe and usable for testing the priority skills:

  - synthetic-fhir-bundle.json : fhir-to-ml-dataset-builder
  - diabetes-cohort.csv        : ehr-care-gap-analyzer
  - validation-results.csv     : medical-ai-validation-report-writer

Checks performed:
  - CSV files load and parse.
  - JSON file loads and parses.
  - Required columns exist in each CSV.
  - The FHIR bundle is a Bundle and contains the expected resource types.
  - No obvious PHI fields are present (email, phone, address, name, ...).
  - Date-like values are ISO-like (YYYY-MM-DD or full ISO datetimes).
  - Row counts are within the expected ranges.

Usage:
  python validate_examples.py            # validate files in ../ (examples/)
  python validate_examples.py --dir PATH # validate files in a custom dir

Exit status:
  0 if all checks pass, non-zero if any check fails.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Expectations
# --------------------------------------------------------------------------- #
COHORT_REQUIRED_COLUMNS = [
    "patient_id", "age", "sex", "diabetes_type", "diabetes_duration_years",
    "last_hba1c", "last_hba1c_date", "egfr", "egfr_date", "ldl", "ldl_date",
    "systolic_bp", "diastolic_bp", "has_hypertension", "has_ckd", "has_cvd",
    "has_neuropathy", "on_metformin", "on_insulin", "on_ace_arb", "on_statin",
    "last_eye_exam_date", "last_nephrology_visit_date",
    "last_cardiology_visit_date", "last_foot_exam_date",
    "last_primary_care_visit_date", "bmi", "smoking_status",
    "albumin_creatinine_ratio", "acr_date", "num_er_visits_12m",
    "num_hospitalizations_12m",
]

VALIDATION_REQUIRED_COLUMNS = [
    "patient_id", "split", "true_label", "predicted_label",
    "predicted_probability", "age_group", "sex", "site", "has_ckd",
    "has_hypertension",
]

VALIDATION_LABELS = {"complication_within_24m", "no_complication_within_24m"}

EXPECTED_FHIR_RESOURCE_TYPES = {
    "Patient", "Encounter", "Condition", "Observation", "MedicationRequest",
}

COHORT_ROW_RANGE = (20, 50)
VALIDATION_ROW_RANGE = (100, 300)
FHIR_PATIENT_RANGE = (5, 15)

# Column names / keys that would suggest direct identifiers (PHI).
PHI_TOKENS = [
    "email", "e_mail", "e-mail", "phone", "telecom", "fax", "address",
    "street", "city", "zip", "postal", "first_name", "last_name", "fullname",
    "full_name", "given_name", "family_name", "patient_name", "ssn",
    "national_id", "mrn", "medical_record_number", "date_of_birth", "dob",
    "birth_name", "maiden_name",
]

# Columns whose names end in *_date (or are exactly "date"-like) and should
# hold ISO-like values when present.
DATE_COLUMN_SUFFIXES = ("_date",)

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$"
)

# An '@' anywhere indicates an email-like value.
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
# A North-American-style phone number with separators or parentheses, e.g.
# "(555) 123-4567", "555-123-4567", "+1 555 123 4567". Deliberately requires
# phone-style grouping so it does NOT match plain ISO dates (YYYY-MM-DD) or
# simple integers.
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?"      # optional country code
    r"(?:\(\d{3}\)|\d{3})[\s.-]"          # area code, then a separator
    r"\d{3}[\s.-]\d{4}(?!\d)"             # 3-4 split local number
)


class ValidationError(Exception):
    """Raised when a validation check fails."""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _is_iso_like(value: str) -> bool:
    return bool(ISO_DATE_RE.match(value) or ISO_DATETIME_RE.match(value))


def _looks_like_phi_key(key: str) -> bool:
    norm = key.strip().lower()
    return any(tok in norm for tok in PHI_TOKENS)


def _read_csv(path: Path) -> tuple[list[str], list[dict]]:
    if not path.exists():
        raise ValidationError(f"missing file: {path.name}")
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not fieldnames:
        raise ValidationError(f"{path.name}: no header row found")
    return fieldnames, rows


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #
def check_cohort(path: Path, problems: list[str]) -> None:
    name = path.name
    try:
        fieldnames, rows = _read_csv(path)
    except ValidationError as exc:
        problems.append(str(exc))
        return

    # Required columns.
    missing = [c for c in COHORT_REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        problems.append(f"{name}: missing required columns: {missing}")

    # PHI-like column names.
    phi_cols = [c for c in fieldnames if _looks_like_phi_key(c)]
    if phi_cols:
        problems.append(f"{name}: PHI-like column names present: {phi_cols}")

    # Row count range.
    lo, hi = COHORT_ROW_RANGE
    if not (lo <= len(rows) <= hi):
        problems.append(
            f"{name}: row count {len(rows)} outside expected range {lo}-{hi}")

    # Date columns must be ISO-like when not empty.
    date_cols = [c for c in fieldnames
                 if c.endswith(DATE_COLUMN_SUFFIXES)]
    for idx, row in enumerate(rows, start=2):  # header is line 1
        for col in date_cols:
            val = (row.get(col) or "").strip()
            if val and not _is_iso_like(val):
                problems.append(
                    f"{name}: line {idx}: column '{col}' value "
                    f"'{val}' is not ISO-like")
        # PHI value scan across the whole row.
        _scan_row_values_for_phi(name, idx, row, problems)


def check_validation(path: Path, problems: list[str]) -> None:
    name = path.name
    try:
        fieldnames, rows = _read_csv(path)
    except ValidationError as exc:
        problems.append(str(exc))
        return

    missing = [c for c in VALIDATION_REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        problems.append(f"{name}: missing required columns: {missing}")

    phi_cols = [c for c in fieldnames if _looks_like_phi_key(c)]
    if phi_cols:
        problems.append(f"{name}: PHI-like column names present: {phi_cols}")

    lo, hi = VALIDATION_ROW_RANGE
    if not (lo <= len(rows) <= hi):
        problems.append(
            f"{name}: row count {len(rows)} outside expected range {lo}-{hi}")

    # Label vocabulary and probability range checks (only if columns exist).
    has_labels = {"true_label", "predicted_label"} <= set(fieldnames)
    has_prob = "predicted_probability" in fieldnames
    for idx, row in enumerate(rows, start=2):
        if has_labels:
            for col in ("true_label", "predicted_label"):
                val = (row.get(col) or "").strip()
                if val and val not in VALIDATION_LABELS:
                    problems.append(
                        f"{name}: line {idx}: column '{col}' has unexpected "
                        f"label '{val}'")
        if has_prob:
            raw = (row.get("predicted_probability") or "").strip()
            if raw:
                try:
                    p = float(raw)
                except ValueError:
                    problems.append(
                        f"{name}: line {idx}: predicted_probability "
                        f"'{raw}' is not numeric")
                else:
                    if not (0.0 <= p <= 1.0):
                        problems.append(
                            f"{name}: line {idx}: predicted_probability "
                            f"{p} outside [0, 1]")
        _scan_row_values_for_phi(name, idx, row, problems)


def check_fhir_bundle(path: Path, problems: list[str]) -> None:
    name = path.name
    if not path.exists():
        problems.append(f"missing file: {name}")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        problems.append(f"{name}: invalid JSON: {exc}")
        return

    if not isinstance(data, dict) or data.get("resourceType") != "Bundle":
        problems.append(f"{name}: not a FHIR Bundle (resourceType != 'Bundle')")
        return

    entries = data.get("entry")
    if not isinstance(entries, list) or not entries:
        problems.append(f"{name}: Bundle has no 'entry' list")
        return

    present_types: set[str] = set()
    patient_count = 0
    for entry in entries:
        resource = (entry or {}).get("resource", {})
        rtype = resource.get("resourceType")
        if rtype:
            present_types.add(rtype)
        if rtype == "Patient":
            patient_count += 1
            # No name / contact identifiers should be present.
            for phi_key in ("name", "telecom", "address"):
                if resource.get(phi_key):
                    problems.append(
                        f"{name}: Patient '{resource.get('id')}' contains "
                        f"PHI field '{phi_key}'")

    missing_types = EXPECTED_FHIR_RESOURCE_TYPES - present_types
    if missing_types:
        problems.append(
            f"{name}: missing expected resource types: "
            f"{sorted(missing_types)}")

    lo, hi = FHIR_PATIENT_RANGE
    if not (lo <= patient_count <= hi):
        problems.append(
            f"{name}: patient count {patient_count} outside expected "
            f"range {lo}-{hi}")

    # Scan the full serialized bundle for accidental PHI values.
    raw = path.read_text(encoding="utf-8")
    if EMAIL_RE.search(raw):
        problems.append(f"{name}: an email-like value was found in the bundle")


def _scan_row_values_for_phi(name: str, idx: int, row: dict,
                             problems: list[str]) -> None:
    for col, val in row.items():
        if val is None:
            continue
        text = str(val)
        if EMAIL_RE.search(text):
            problems.append(
                f"{name}: line {idx}: column '{col}' contains an "
                f"email-like value")
        if PHONE_RE.search(text):
            problems.append(
                f"{name}: line {idx}: column '{col}' contains a "
                f"phone-like value")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--dir", default=None,
        help="Directory containing the example files (default: the examples/ "
             "folder, i.e. the parent of this scripts/ directory).")
    args = parser.parse_args()

    base = (Path(args.dir) if args.dir
            else Path(__file__).resolve().parent.parent)

    cohort_path = base / "diabetes-cohort.csv"
    validation_path = base / "validation-results.csv"
    bundle_path = base / "synthetic-fhir-bundle.json"

    problems: list[str] = []
    check_cohort(cohort_path, problems)
    check_validation(validation_path, problems)
    check_fhir_bundle(bundle_path, problems)

    if problems:
        print("Validation FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        print(f"\n{len(problems)} problem(s) found.")
        return 1

    print("Validation PASSED. All example files are present, well-formed, "
          "contain required columns/resource types, use ISO-like dates, show "
          "no obvious PHI, and have row counts in the expected ranges.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
