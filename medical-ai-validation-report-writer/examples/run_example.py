#!/usr/bin/env python3
"""Generate a demo medical AI validation report from sample metrics.

This example intentionally uses synthetic data and demonstrates conservative
reporting, missing-evidence warnings, a data leakage checklist, and a clinical
claims checklist.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "output"


def fmt(value: Any) -> str:
    """Format values for report display without inventing missing evidence."""
    if value is None:
        return "Missing"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def fmt_ci(metrics: dict[str, Any], metric_name: str) -> str:
    ci = metrics.get("confidence_intervals", {}).get(metric_name)
    if not ci:
        return "Not provided"
    return f"{ci[0]:.3f}–{ci[1]:.3f}"


def load_confusion_matrix(path: Path) -> dict[tuple[str, str], int]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"actual", "predicted", "count"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Confusion matrix missing required columns: {sorted(missing)}")
        return {
            (row["actual"].strip().lower(), row["predicted"].strip().lower()): int(row["count"])
            for row in reader
        }


def metric_table(metrics: dict[str, Any]) -> str:
    rows = [
        ("Sensitivity / recall", "sensitivity"),
        ("Specificity", "specificity"),
        ("Precision / PPV", "ppv"),
        ("NPV", "npv"),
        ("AUROC", "auroc"),
        ("AUPRC", "auprc"),
        ("F1-score", "f1_score"),
        ("Accuracy (interpret with prevalence context)", "accuracy"),
        ("Brier score", "brier_score"),
    ]
    lines = ["| Metric | Value | Confidence interval |", "|---|---:|---|"]
    for label, key in rows:
        lines.append(f"| {label} | {fmt(metrics.get(key))} | {fmt_ci(metrics, key)} |")
    return "\n".join(lines)


def subgroup_table(subgroups: list[dict[str, Any]]) -> str:
    if not subgroups:
        return "Subgroup metrics were not provided."
    lines = ["| Subgroup | N | Sensitivity | Specificity |", "|---|---:|---:|---:|"]
    for row in subgroups:
        lines.append(
            f"| {row.get('name', 'Unnamed subgroup')} | {fmt(row.get('n'))} | "
            f"{fmt(row.get('sensitivity'))} | {fmt(row.get('specificity'))} |"
        )
    return "\n".join(lines)


def checklist(title: str, items: list[tuple[str, str]]) -> str:
    lines = [f"## {title}", "", "| Item | Status |", "|---|---|"]
    for item, status in items:
        lines.append(f"| {item} | {status} |")
    return "\n".join(lines)


def build_report(metrics_path: Path, confusion_path: Path) -> str:
    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    cm = load_confusion_matrix(confusion_path)
    dataset = data.get("dataset", {})
    evaluation = data.get("evaluation", {})
    metrics = data.get("metrics", {})

    tp = cm.get(("positive", "positive"), 0)
    fn = cm.get(("positive", "negative"), 0)
    fp = cm.get(("negative", "positive"), 0)
    tn = cm.get(("negative", "negative"), 0)

    warnings = []
    if not data.get("external_validation"):
        warnings.append("No external validation dataset was provided; generalizability remains uncertain.")
    if not data.get("baseline_comparison"):
        warnings.append("No baseline or standard-workflow comparison was provided.")
    if not metrics.get("confidence_intervals"):
        warnings.append("Confidence intervals were not provided for the reported metrics.")

    leakage_items = [
        ("Patient-level split confirmed", "Reported; verify source split file"),
        ("Duplicate image leakage checked", "Not assessed in sample"),
        ("Same patient across train/test checked", "Reported as patient-level split"),
        ("Same encounter/study across train/test checked", "Not assessed in sample"),
        ("Preprocessing fitted only on training data", "Not assessed in sample"),
        ("Label leakage through metadata assessed", "Not assessed in sample"),
        ("Temporal leakage assessed", "Not applicable / not assessed for imaging sample"),
        ("Device/site leakage assessed", "Concern: single synthetic site only"),
        ("Augmented images across splits checked", "Not assessed in sample"),
    ]
    claims_items = [
        ("Model identifies referable diabetic retinopathy in this synthetic test set", "Partially supported"),
        ("Model is clinically proven", "Unsupported"),
        ("Model is ready for autonomous diagnosis", "Unsupported; requires regulatory/legal review"),
        ("Performance generalizes to other hospitals and cameras", "Requires external validation"),
        ("Prospective workflow benefit", "Requires prospective validation"),
    ]

    warning_text = "\n".join(f"- {warning}" for warning in warnings) or "- No warnings generated."
    limitations = "\n".join(f"- {item}" for item in data.get("limitations", [])) or "- Not provided."
    failure_modes = "\n".join(f"- {item}" for item in data.get("known_failure_modes", [])) or "- Not provided."

    return f"""# Medical AI Validation Report

Generated on: {date.today().isoformat()}

## Executive summary

**Model:** {data.get('model_name', 'Missing')}  
**Version:** {data.get('model_version', 'Missing')}  
**Intended use:** {data.get('intended_use', 'Missing')}  
**Deployment context:** {data.get('deployment_context', 'Missing')}

This report summarizes retrospective example evaluation evidence. It does not provide clinical validation, regulatory approval, certification, or legal advice.

## Key warnings

{warning_text}

## Dataset description

- **Dataset:** {dataset.get('name', 'Missing')}
- **Description:** {dataset.get('description', 'Missing')}
- **Collection period:** {dataset.get('collection_period', 'Missing')}
- **Sources:** {', '.join(dataset.get('sources', [])) or 'Missing'}
- **Patients:** {fmt(dataset.get('n_patients'))}
- **Studies:** {fmt(dataset.get('n_studies'))}
- **Positive cases:** {fmt(dataset.get('positive_cases'))}
- **Negative cases:** {fmt(dataset.get('negative_cases'))}
- **Prevalence:** {fmt(dataset.get('prevalence'))}
- **Inclusion criteria:** {dataset.get('inclusion_criteria', 'Missing')}
- **Exclusion criteria:** {dataset.get('exclusion_criteria', 'Missing')}
- **Ground truth / reference standard:** {dataset.get('ground_truth', 'Missing')}

## Evaluation setup

- **Split:** {evaluation.get('split', 'Missing')}
- **Decision threshold:** {fmt(evaluation.get('threshold'))}
- **Primary endpoint:** {evaluation.get('primary_endpoint', 'Missing')}
- **Secondary endpoints:** {', '.join(evaluation.get('secondary_endpoints', [])) or 'Missing'}

## Performance metrics

{metric_table(metrics)}

Accuracy is shown with caution because it can be misleading when datasets are imbalanced.

## Confusion matrix interpretation

| Actual / Predicted | Positive | Negative |
|---|---:|---:|
| Positive | {tp} | {fn} |
| Negative | {fp} | {tn} |

- False negatives may represent missed cases that warrant clinical review in a screening workflow.
- False positives may create unnecessary follow-up workload and patient anxiety.

## Subgroup analysis

{subgroup_table(data.get('subgroups', []))}

Subgroup differences should be interpreted cautiously and reviewed by a statistician, especially when subgroup sample sizes are small.

## Calibration analysis

- **Brier score:** {fmt(metrics.get('brier_score'))}
- Calibration curve: Not provided in this sample.
- Calibration should be reviewed before using model probabilities for risk stratification.

## Error analysis and known failure modes

{failure_modes}

## External validation

External validation was not provided. The absence of external validation should be treated as a major generalizability limitation.

## Limitations

{limitations}

{checklist('Data leakage checklist', leakage_items)}

{checklist('Clinical claims checklist', claims_items)}

## Human oversight requirements

This example model output should be reviewed by qualified clinical users. The model should not be used for autonomous diagnosis, treatment, triage, or patient management based on this sample report.

## Conclusion

The supplied retrospective example metrics suggest measurable performance on the synthetic internal validation dataset, but the report identifies important missing evidence, including external validation, prospective workflow evaluation, full leakage assessment, and regulatory/legal review.
"""


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    report = build_report(HERE / "sample_metrics.json", HERE / "sample_confusion_matrix.csv")
    output_path = OUTPUT_DIR / "validation_report.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
