#!/usr/bin/env python3
"""Run a lightweight medical imaging dataset audit on a local dataset.

This example is intentionally simple and synthetic-data friendly. It demonstrates
core checks that a production audit can expand for larger datasets, DICOM tags,
near-duplicate image hashing, and modality-specific logic.
"""

from __future__ import annotations

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd
from PIL import Image, UnidentifiedImageError


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
SPLIT_NAMES = {"train", "training", "val", "valid", "validation", "test", "holdout", "external"}
LABEL_TERMS = {"normal", "referable", "urgent", "disease", "positive", "negative", "case", "control"}
IMAGE_COLUMNS = ["image_path", "absolute_path", "split_from_path", "label_from_path", "filename", "extension"]
INSPECTION_COLUMNS = [
    "image_path",
    "width",
    "height",
    "mode",
    "format",
    "file_size_bytes",
    "sha256",
    "is_corrupted",
    "error",
]
DUPLICATE_COLUMNS = ["duplicate_type", "sha256", "splits", "image_paths", "cross_split", "count"]
SPLIT_REPORT_COLUMNS = ["severity", "check", "identifier_hash", "splits", "count", "recommendation"]


def discover_images(dataset_root: Path) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    if not dataset_root.exists():
        return pd.DataFrame(columns=IMAGE_COLUMNS)
    for path in sorted(dataset_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        relative = path.relative_to(dataset_root)
        parts = relative.parts
        split = next((part for part in parts if part.lower() in SPLIT_NAMES), "unknown")
        label = "unknown"
        if split != "unknown":
            try:
                split_index = parts.index(split)
            except ValueError:
                split_index = -1
            if split_index >= 0 and len(parts) > split_index + 1:
                label = parts[split_index + 1]
        rows.append(
            {
                "image_path": relative.as_posix(),
                "absolute_path": str(path),
                "split_from_path": split,
                "label_from_path": label,
                "filename": path.name,
                "extension": path.suffix.lower(),
            }
        )
    return pd.DataFrame(rows, columns=IMAGE_COLUMNS)


def load_metadata(metadata_path: Path | None) -> pd.DataFrame:
    if metadata_path is None:
        return pd.DataFrame()
    return pd.read_csv(metadata_path)


def merge_metadata(images: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    if metadata.empty:
        merged = images.copy()
        merged["split"] = merged["split_from_path"]
        merged["label"] = merged["label_from_path"]
        return merged
    if "image_path" not in metadata.columns:
        raise ValueError("Metadata CSV must contain an image_path column for this example audit.")
    merged = images.merge(metadata, on="image_path", how="left", suffixes=("", "_metadata"))
    merged["split"] = merged.get("split", merged["split_from_path"]).fillna(merged["split_from_path"])
    merged["label"] = merged.get("label", merged["label_from_path"]).fillna(merged["label_from_path"])
    return merged


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_images(rows: pd.DataFrame) -> pd.DataFrame:
    inspected: list[dict[str, object]] = []
    if rows.empty:
        return pd.DataFrame(columns=INSPECTION_COLUMNS)
    for row in rows.to_dict("records"):
        path = Path(row["absolute_path"])
        record = {
            "image_path": row["image_path"],
            "width": None,
            "height": None,
            "mode": None,
            "format": None,
            "file_size_bytes": path.stat().st_size if path.exists() else None,
            "sha256": None,
            "is_corrupted": False,
            "error": "",
        }
        try:
            record["sha256"] = sha256_file(path)
            with Image.open(path) as image:
                record["width"], record["height"] = image.size
                record["mode"] = image.mode
                record["format"] = image.format
                image.verify()
        except (OSError, UnidentifiedImageError, ValueError) as exc:
            record["is_corrupted"] = True
            record["error"] = type(exc).__name__
        inspected.append(record)
    return pd.DataFrame(inspected, columns=INSPECTION_COLUMNS)


def class_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["split", "label", "count", "percent_within_split"])
    counts = df.groupby(["split", "label"], dropna=False).size().reset_index(name="count")
    totals = counts.groupby("split")["count"].transform("sum")
    counts["percent_within_split"] = (counts["count"] / totals * 100).round(2)
    return counts.sort_values(["split", "label"])


def duplicate_candidates(df: pd.DataFrame) -> pd.DataFrame:
    candidates: list[dict[str, object]] = []
    for sha, group in df.dropna(subset=["sha256"]).groupby("sha256"):
        if len(group) <= 1:
            continue
        splits = sorted(group["split"].dropna().unique())
        candidates.append(
            {
                "duplicate_type": "exact_sha256",
                "sha256": sha,
                "splits": ";".join(splits),
                "image_paths": ";".join(group["image_path"].astype(str)),
                "cross_split": len(splits) > 1,
                "count": len(group),
            }
        )
    for filename, group in df.groupby("filename"):
        if len(group) <= 1:
            continue
        splits = sorted(group["split"].dropna().unique())
        candidates.append(
            {
                "duplicate_type": "same_filename",
                "sha256": "",
                "splits": ";".join(splits),
                "image_paths": ";".join(group["image_path"].astype(str)),
                "cross_split": len(splits) > 1,
                "count": len(group),
            }
        )
    return pd.DataFrame(candidates, columns=DUPLICATE_COLUMNS)


def split_integrity(df: pd.DataFrame) -> pd.DataFrame:
    findings: list[dict[str, object]] = []
    for column in ["patient_id", "study_id", "visit_id", "volume_id"]:
        if column not in df.columns:
            continue
        for identifier, group in df.dropna(subset=[column]).groupby(column):
            splits = sorted(group["split"].dropna().unique())
            if len(splits) > 1:
                findings.append(
                    {
                        "severity": "Critical" if "test" in splits and "train" in splits else "High",
                        "check": f"{column}_across_splits",
                        "identifier_hash": hashlib.sha256(str(identifier).encode()).hexdigest()[:12],
                        "splits": ";".join(splits),
                        "count": len(group),
                        "recommendation": f"Keep each {column} in only one split or document why overlap is intended.",
                    }
                )
    return pd.DataFrame(findings, columns=SPLIT_REPORT_COLUMNS)


def metadata_leakage_findings(df: pd.DataFrame) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    suspicious_columns = []
    for column in df.columns:
        lower = column.lower()
        if any(term in lower for term in ["label", "target", "outcome", "diagnosis", "severity", "urgent"]):
            suspicious_columns.append(column)
        if any(term in lower for term in ["patient", "mrn", "name", "dob", "address", "phone", "email"]):
            findings.append(
                {
                    "severity": "Medium",
                    "issue": f"Potential identifier-like metadata column: `{column}`",
                    "recommendation": "Keep linkage keys local, avoid printing raw identifiers, and hash or remove direct identifiers in shared outputs.",
                }
            )
    if suspicious_columns:
        findings.append(
            {
                "severity": "High",
                "issue": "Metadata contains label/target-like columns: " + ", ".join(f"`{col}`" for col in suspicious_columns),
                "recommendation": "Ensure target labels are not included as model inputs or preprocessing features.",
            }
        )
    filename_hits = [path for path in df["image_path"].astype(str) if any(term in path.lower() for term in LABEL_TERMS)]
    if filename_hits:
        findings.append(
            {
                "severity": "High",
                "issue": f"{len(filename_hits)} filenames or paths contain label-like terms.",
                "recommendation": "Ensure models never receive filenames or path-derived labels as input features.",
            }
        )
    return findings


def markdown_table(df: pd.DataFrame) -> str:
    """Render a small DataFrame as a markdown table without optional tabulate dependency."""
    if df.empty:
        return "_No rows._"
    display = df.fillna("").astype(str)
    headers = list(display.columns)
    separator = ["---"] * len(headers)
    rows = [headers, separator, *display.values.tolist()]
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def write_markdown(path: Path, title: str, lines: Iterable[str]) -> None:
    path.write_text("\n".join([f"# {title}", "", *lines, ""]), encoding="utf-8")


def audit(dataset_root: Path, metadata_path: Path | None, output_dir: Path) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    images = discover_images(dataset_root)
    metadata = load_metadata(metadata_path)
    df = merge_metadata(images, metadata)
    inspection = inspect_images(df)
    df = df.merge(inspection, on="image_path", how="left")

    class_counts = class_distribution(df)
    class_counts.to_csv(output_dir / "class_distribution.csv", index=False)

    duplicates = duplicate_candidates(df)
    duplicates.to_csv(output_dir / "duplicate_candidates.csv", index=False)

    split_report = split_integrity(df)
    split_report.to_csv(output_dir / "split_integrity_report.csv", index=False)

    leakage = metadata_leakage_findings(df)
    write_markdown(
        output_dir / "metadata_leakage_report.md",
        "Metadata Leakage Report",
        [
            *(f"- **{item['severity']}**: {item['issue']} Recommendation: {item['recommendation']}" for item in leakage),
            *( ["- **Informational**: No suspicious metadata fields were detected by this lightweight example."] if not leakage else []),
        ],
    )

    domain_lines: list[str] = []
    for column in ["device", "site", "laterality", "extension", "mode", "format"]:
        if column in df.columns:
            summary = df.groupby(["split", column], dropna=False).size().reset_index(name="count")
            domain_lines.extend([f"## {column}", "", markdown_table(summary), ""])
    write_markdown(output_dir / "domain_shift_summary.md", "Domain Shift Summary", domain_lines)

    recommendations = [
        "- Use patient-level or group-level splitting for training, validation, and testing.",
        "- Remove or quarantine exact duplicate images across train/test before model evaluation.",
        "- Review class imbalance and ensure validation/test sets contain clinically meaningful denominators.",
        "- Document device, site, laterality, acquisition date, and preprocessing differences.",
        "- Do not treat this audit as clinical validation or proof of model safety.",
    ]
    write_markdown(output_dir / "recommended_split_strategy.md", "Recommended Split Strategy", recommendations)

    data_card_lines = [
        "## Dataset summary",
        f"- Dataset root: `{dataset_root}`",
        f"- Image count: {len(df)}",
        f"- Metadata file: `{metadata_path}`" if metadata_path else "- Metadata file: Not provided",
        "",
        "## Known risks",
        "- Review duplicate, split integrity, metadata leakage, and domain shift reports before training.",
        "- This synthetic example does not assess clinical label correctness.",
    ]
    write_markdown(output_dir / "data_card.md", "Data Card", data_card_lines)

    issues: list[tuple[str, str]] = []
    if not split_report.empty:
        issues.append(("Critical", f"{len(split_report)} identifier overlap finding(s) across splits."))
    if not duplicates.empty and duplicates["cross_split"].any():
        issues.append(("Critical", "Exact duplicate candidate(s) found across splits."))
    if df["is_corrupted"].fillna(False).any():
        issues.append(("High", "Corrupted or unreadable image file(s) found."))
    for _, row in class_counts.iterrows():
        if row["count"] <= 1:
            issues.append(("High", f"Very small class count for split={row['split']} label={row['label']}: {row['count']} image(s)."))

    report_lines = [
        "## Executive summary",
        f"- Images audited: {len(df)}",
        f"- Critical/High issue count: {sum(1 for severity, _ in issues if severity in {'Critical', 'High'})}",
        "- This is a dataset quality and ML risk audit, not clinical validation.",
        "",
        "## Issues",
        *(f"- **{severity}**: {message}" for severity, message in issues),
        *( ["- **Informational**: No critical or high issues were detected by this lightweight example."] if not issues else []),
        "",
        "## Image dimensions and formats",
        markdown_table(df[["image_path", "split", "label", "width", "height", "mode", "format", "is_corrupted"]]),
        "",
        "## Generated files",
        "- `class_distribution.csv`",
        "- `split_integrity_report.csv`",
        "- `duplicate_candidates.csv`",
        "- `metadata_leakage_report.md`",
        "- `domain_shift_summary.md`",
        "- `recommended_split_strategy.md`",
        "- `data_card.md`",
    ]
    write_markdown(output_dir / "dataset_audit_report.md", "Dataset Audit Report", report_lines)
    return {"images": len(df), "issues": len(issues), "duplicates": len(duplicates), "split_findings": len(split_report)}


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parent / "synthetic_dataset"
    parser = argparse.ArgumentParser(description="Run a lightweight medical imaging dataset audit.")
    parser.add_argument("--dataset-root", type=Path, default=default_root, help="Dataset root to audit.")
    parser.add_argument("--metadata", type=Path, default=None, help="Optional metadata CSV path.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "audit_output",
        help="Directory where audit reports should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = args.metadata
    if metadata is None:
        candidate = args.dataset_root / "metadata.csv"
        metadata = candidate if candidate.exists() else None
    summary = audit(args.dataset_root, metadata, args.output_dir)
    print(f"Audit output directory: {args.output_dir}")
    print(
        "Summary: "
        f"images={summary['images']}, issues={summary['issues']}, "
        f"duplicate_candidates={summary['duplicates']}, split_findings={summary['split_findings']}"
    )


if __name__ == "__main__":
    main()
