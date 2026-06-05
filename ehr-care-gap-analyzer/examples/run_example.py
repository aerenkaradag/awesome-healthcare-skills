#!/usr/bin/env python3
"""Run a conservative care-gap demo on synthetic diabetes EHR rows."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "output"
DIRECT_IDENTIFIER_COLUMNS = {"name", "phone", "address", "national_id", "mrn", "medical_record_number", "email"}


def load_config(path: Path) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.replace(".", "", 1).isdigit():
            config[key.strip()] = float(value) if "." in value else int(value)
        else:
            config[key.strip()] = value
    return config


def parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def days_since(value: str, reference_date: date) -> int | None:
    parsed = parse_date(value)
    return (reference_date - parsed).days if parsed else None


def to_float(value: str) -> float | None:
    return float(value) if value else None


def is_recent(value: str, reference_date: date, lookback_days: int) -> bool:
    elapsed = days_since(value, reference_date)
    return elapsed is not None and elapsed <= lookback_days


def audit_row(row: dict[str, str], config: dict[str, Any]) -> dict[str, Any]:
    reference_date = date.fromisoformat(str(config["reference_date"]))
    followup_days = int(config["followup_lookback_days"])
    eye_exam_days = int(config["eye_exam_lookback_days"])
    flags: list[str] = []
    evidence: list[str] = []

    hba1c = to_float(row.get("last_hba1c", ""))
    if hba1c is None:
        flags.append("missing_recent_monitoring_data")
        evidence.append("HbA1c value missing in provided export")
    elif hba1c > float(config["hba1c_review_threshold"]) and not is_recent(
        row.get("last_endocrinology_visit_date", ""), reference_date, followup_days
    ):
        flags.append("possible_glycemic_control_followup_gap")
        evidence.append("HbA1c above configured threshold and no recent endocrinology visit found")

    egfr = to_float(row.get("egfr", ""))
    if egfr is not None and egfr < float(config["egfr_review_threshold"]) and not is_recent(
        row.get("last_nephrology_visit_date", ""), reference_date, followup_days
    ):
        flags.append("possible_nephropathy_followup_gap")
        evidence.append("eGFR below configured threshold and no recent nephrology visit found")

    if not is_recent(row.get("last_eye_exam_date", ""), reference_date, eye_exam_days):
        flags.append("possible_retinopathy_screening_gap")
        evidence.append("No recent eye exam date found in configured lookback window")

    ldl = to_float(row.get("ldl", ""))
    if ldl is not None and ldl > float(config["ldl_review_threshold"]) and row.get("on_statin") != "1":
        flags.append("possible_lipid_management_review_signal")
        evidence.append("LDL above configured threshold and no statin flag in provided export")

    return {
        "patient_id": row["patient_id"],
        "flag_count": len(flags),
        "review_flags": ";".join(flags) or "none",
        "evidence": "; ".join(evidence) or "No configured review signal in available synthetic fields",
    }


def write_markdown_report(path: Path, flags: list[dict[str, Any]], config: dict[str, Any]) -> None:
    flagged = [row for row in flags if row["review_flags"] != "none"]
    lines = [
        "# Synthetic Care Gap Report",
        "",
        "This report uses synthetic data only. Flags are possible review signals, not diagnoses or care instructions.",
        "",
        "## Configuration",
        "",
        f"- Reference date: {config['reference_date']}",
        f"- Follow-up lookback days: {config['followup_lookback_days']}",
        f"- Eye exam lookback days: {config['eye_exam_lookback_days']}",
        "",
        "## Summary",
        "",
        f"- Synthetic patients reviewed: {len(flags)}",
        f"- Patients with at least one possible review signal: {len(flagged)}",
        "",
        "## Limitations",
        "",
        "- Absence of a record does not prove absence of care.",
        "- Thresholds are demonstration values and require local clinical governance review.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    config = load_config(HERE / "config.yaml")
    rows = list(csv.DictReader((HERE / "synthetic_diabetes_ehr.csv").open(encoding="utf-8")))
    direct_identifiers = DIRECT_IDENTIFIER_COLUMNS.intersection(rows[0].keys() if rows else [])
    if direct_identifiers:
        raise ValueError(f"Synthetic output would include direct identifier columns: {sorted(direct_identifiers)}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    flags = [audit_row(row, config) for row in rows]
    with (OUTPUT_DIR / "care_gap_patient_flags.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["patient_id", "flag_count", "review_flags", "evidence"])
        writer.writeheader()
        writer.writerows(flags)

    summary_rows = []
    for flag_name in sorted({flag for row in flags for flag in row["review_flags"].split(";") if flag != "none"}):
        summary_rows.append({"review_flag": flag_name, "patient_count": sum(flag_name in row["review_flags"].split(";") for row in flags)})
    with (OUTPUT_DIR / "care_gap_population_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["review_flag", "patient_count"])
        writer.writeheader()
        writer.writerows(summary_rows)

    write_markdown_report(OUTPUT_DIR / "care_gap_report.md", flags, config)
    print(f"Wrote synthetic care-gap outputs to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
