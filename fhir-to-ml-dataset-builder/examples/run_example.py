#!/usr/bin/env python3
"""Create a small ML-ready table from the synthetic FHIR sample bundle."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "output"
REFERENCE_DATE = "2024-06-01"

OBSERVATION_FEATURES = {
    "4548-4": "latest_hba1c_value",
    "33914-3": "latest_egfr_value",
    "18262-6": "latest_ldl_value",
}
CONDITION_FEATURES = {
    "44054006": "has_type2_diabetes",
    "38341003": "has_hypertension",
    "709044004": "has_ckd",
}


def patient_key(raw_id: str) -> str:
    return hashlib.sha256(f"sample-local-salt:{raw_id}".encode("utf-8")).hexdigest()[:16]


def iter_resources(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry["resource"] for entry in bundle.get("entry", []) if isinstance(entry.get("resource"), dict)]


def subject_id(resource: dict[str, Any]) -> str:
    reference = resource.get("subject", {}).get("reference", "")
    return reference.removeprefix("Patient/")


def first_code(resource: dict[str, Any]) -> str:
    codings = resource.get("code", {}).get("coding", [])
    return codings[0].get("code", "") if codings else ""


def build_features(bundle_path: Path) -> list[dict[str, Any]]:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    resources = iter_resources(bundle)
    patients = [resource for resource in resources if resource.get("resourceType") == "Patient"]

    rows: dict[str, dict[str, Any]] = {}
    for patient in patients:
        raw_id = patient.get("id", "")
        rows[raw_id] = {
            "patient_key": patient_key(raw_id),
            "administrative_gender": patient.get("gender", "Missing"),
            "birth_year": patient.get("birthDate", "Missing")[:4],
            "latest_hba1c_value": "",
            "latest_egfr_value": "",
            "latest_ldl_value": "",
            "has_type2_diabetes": 0,
            "has_hypertension": 0,
            "has_ckd": 0,
        }

    latest_observation_dates: dict[tuple[str, str], str] = {}
    for resource in resources:
        resource_type = resource.get("resourceType")
        patient_id = subject_id(resource)
        if patient_id not in rows:
            continue
        code = first_code(resource)
        if resource_type == "Observation" and code in OBSERVATION_FEATURES:
            feature = OBSERVATION_FEATURES[code]
            effective_date = resource.get("effectiveDateTime", "")
            key = (patient_id, feature)
            if effective_date >= latest_observation_dates.get(key, ""):
                rows[patient_id][feature] = resource.get("valueQuantity", {}).get("value", "")
                latest_observation_dates[key] = effective_date
        elif resource_type == "Condition" and code in CONDITION_FEATURES:
            rows[patient_id][CONDITION_FEATURES[code]] = 1

    return list(rows.values())


def write_outputs(rows: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    fieldnames = [
        "patient_key",
        "administrative_gender",
        "birth_year",
        "latest_hba1c_value",
        "latest_egfr_value",
        "latest_ldl_value",
        "has_type2_diabetes",
        "has_hypertension",
        "has_ckd",
    ]
    with (OUTPUT_DIR / "ml_features.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with (OUTPUT_DIR / "missingness_report.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["feature", "missing_count", "missing_percent"])
        writer.writeheader()
        for feature in fieldnames:
            missing = sum(1 for row in rows if row.get(feature) in {"", "Missing", None})
            writer.writerow(
                {
                    "feature": feature,
                    "missing_count": missing,
                    "missing_percent": round(missing / len(rows) * 100, 2) if rows else 0,
                }
            )

    dictionary_lines = [
        "# Feature Dictionary",
        "",
        f"Generated on: {REFERENCE_DATE}",
        "",
        "| Feature | Source | Logic |",
        "|---|---|---|",
        "| patient_key | Patient.id | Local salted hash; raw FHIR IDs are not exported. |",
        "| administrative_gender | Patient.gender | Included for synthetic demonstration only. |",
        "| birth_year | Patient.birthDate | Year only; full birth date is not exported. |",
        "| latest_hba1c_value | Observation LOINC 4548-4 | Latest numeric value by effectiveDateTime. |",
        "| latest_egfr_value | Observation LOINC 33914-3 | Latest numeric value by effectiveDateTime. |",
        "| latest_ldl_value | Observation LOINC 18262-6 | Latest numeric value by effectiveDateTime. |",
        "| has_type2_diabetes | Condition SNOMED 44054006 | Flag from explicit code match. |",
        "| has_hypertension | Condition SNOMED 38341003 | Flag from explicit code match. |",
        "| has_ckd | Condition SNOMED 709044004 | Flag from explicit code match. |",
    ]
    (OUTPUT_DIR / "feature_dictionary.md").write_text("\n".join(dictionary_lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_features(HERE / "sample_bundle.json")
    write_outputs(rows)
    print(f"Wrote {len(rows)} patient rows to {OUTPUT_DIR / 'ml_features.csv'}")


if __name__ == "__main__":
    main()
