# Medical Imaging Dataset Auditor

## Description

This skill guides an AI coding agent to inspect medical imaging datasets for dataset quality problems and machine-learning risk before or after model training. It is especially useful for fundus photography, OCT, FFA, radiology, dermatology, histopathology, endoscopy, generic image-folder datasets, and DICOM exports.

Use this skill to audit datasets for leakage, imbalance, metadata problems, domain shift, split errors, duplicate or near-duplicate images, inconsistent preprocessing, and documentation gaps. The output should help students, researchers, startups, medical AI teams, and clinical collaborators identify dataset problems before training, publication, external validation, or clinical validation planning.

This is a **dataset quality and ML risk audit skill**. It does **not** diagnose patient images, validate clinical performance, certify clinical safety, approve a model for deployment, or replace clinical annotation review. It helps detect problems in the data and evaluation setup that can make model results unreliable, inflated, non-reproducible, or poorly documented.

## When to use

Use this skill when the user wants to:

- Audit a medical imaging dataset before training a medical imaging model.
- Review dataset quality before publishing results.
- Check data quality before clinical validation or prospective evaluation planning.
- Combine multiple datasets from different studies, hospitals, devices, scanners, cameras, or vendors.
- Create, review, or repair train/validation/test splits.
- Investigate suspiciously high model performance.
- Prepare external validation data and document external validation risks.
- Verify that patient-level, study-level, visit-level, eye-level, or scanner/site-level dependencies are handled appropriately.
- Generate dataset documentation, a data card, or a reproducible audit report.

## When not to use

Do not use this skill:

- To diagnose patient images or make patient-specific clinical decisions.
- As a substitute for clinical annotation review, adjudication, or expert relabeling.
- To assume labels are correct without expert review.
- To validate clinical performance, safety, efficacy, generalizability, or readiness for deployment.
- To justify clinical use without formal clinical, statistical, regulatory, privacy, and governance review.
- With patient-identifiable images, DICOM files, metadata, screenshots, or reports in unsafe or uncontrolled environments.
- To upload real patient data to external systems unless the user explicitly confirms that the environment, data flow, permissions, and privacy controls are appropriate.

## Supported dataset types

This skill can be adapted to:

- Fundus photography datasets.
- OCT datasets, including B-scan and volume-level datasets.
- FFA datasets.
- Radiology images, including X-ray, CT, MRI, ultrasound, and other DICOM-based modalities.
- Dermatology images.
- Histopathology images, including tiles and whole-slide-derived image folders.
- Endoscopy images.
- Generic DICOM datasets.
- Generic PNG, JPG, TIFF, or image-folder datasets.
- Multi-site, multi-device, multi-scanner, and multi-study medical imaging exports.

## Supported input formats

The agent should support or gracefully document missing support for:

- Folder-per-class image datasets, such as `normal/`, `disease/`, or `urgent/` folders.
- Train/validation/test split folders, such as `train/`, `val/`, and `test/`.
- CSV metadata files containing image paths, labels, patient IDs, study IDs, device fields, site fields, timestamps, or split assignments.
- DICOM folders.
- Image files including PNG, JPG, JPEG, TIFF, and TIF.
- Multi-site dataset exports.
- Dataset manifests in CSV, JSON, JSONL, or plain-text path-list form.
- Mixed datasets where labels are stored in folders, metadata tables, or both.

## Core audit workflow

When using this skill, the agent should follow this workflow:

1. **Clarify scope and data safety**
   - Ask for the dataset root path, metadata file path, output directory, expected labels, and intended split strategy if missing.
   - Remind the user not to expose patient-identifiable data in unsafe environments.
   - Prefer synthetic, de-identified, or local-only processing.

2. **Inspect dataset structure**
   - List top-level folders and infer whether the dataset is split-first, class-first, DICOM-first, or manifest-driven.
   - Detect common split names such as `train`, `training`, `val`, `valid`, `validation`, `test`, `holdout`, and `external`.
   - Detect class folders when present.

3. **Count images per class and split**
   - Produce counts by split, class, file extension, and metadata label.
   - Compare folder-derived labels with CSV-derived labels when both exist.
   - Flag empty classes, tiny classes, and unexplained label names.

4. **Detect patient identifiers or metadata leakage**
   - Review metadata column names and file names for direct identifiers, patient IDs, labels, outcome terms, dates, site names, device names, or other leakage-prone fields.
   - Do not print raw patient identifiers in reports; hash or summarize identifiers when possible.

5. **Check train/validation/test split integrity**
   - Confirm every image appears in exactly one split unless the user intentionally configured overlap.
   - Detect identical file paths, identical basenames, duplicate hashes, and metadata IDs appearing across splits.
   - Identify split folders that mix train, validation, test, external, or holdout data.

6. **Check patient-level separation**
   - Prefer patient-level splits over image-level splits for most medical imaging tasks.
   - Check patient, study, encounter, visit, accession, eye, volume, or scanner/session identifiers when available.
   - Flag the same patient, visit, study, or OCT volume appearing across train and test.

7. **Check duplicates and near-duplicates**
   - Compute exact file hashes incrementally.
   - Use perceptual hashing if available.
   - Compare same filename across splits.
   - Compare same patient/study IDs, dimensions, timestamps, and near-identical metadata.
   - Warn that near-duplicate detection may be approximate and should be reviewed manually.

8. **Check class imbalance**
   - Report class counts and percentages per split.
   - Flag severe imbalance, missing classes in validation/test, and prevalence differences between train and test.
   - Recommend stratification, resampling, additional data collection, or metric choices such as AUPRC where appropriate.

9. **Check image dimensions and formats**
   - Summarize dimensions, color mode, channels, bit depth when available, and file extensions.
   - Flag inconsistent dimensions, grayscale/RGB mismatches, unsupported formats, and unusually small or large images.

10. **Check corrupted files**
    - Open images lazily and verify them without loading the entire dataset into memory.
    - Record unreadable, truncated, zero-byte, unsupported, or malformed files.
    - For DICOM, use `pydicom` when available and record parse failures without exposing sensitive tags.

11. **Check label taxonomy**
    - Document label names, label source, class definitions, hierarchy, mutually-exclusive versus multi-label assumptions, severity scales, and mapping decisions.
    - Flag inconsistent synonyms, merged labels, ambiguous labels, and dataset-to-dataset taxonomy conflicts.

12. **Check site/device/domain distribution**
    - Summarize site, hospital, scanner, camera, device model, manufacturer, acquisition protocol, and modality distribution when metadata is available.
    - Flag device/site groups that appear only in one split or only in external validation.

13. **Check acquisition date leakage**
    - Review acquisition dates, visit dates, study dates, upload dates, and split creation dates.
    - Flag splits that are separated by time in a way that may be intentional temporal validation or unintended leakage.
    - Watch for future outcome dates or post-label information included as features.

14. **Check preprocessing consistency**
    - Document resizing, normalization, cropping, windowing, denoising, color conversion, augmentation, registration, segmentation masks, and feature extraction.
    - Check whether preprocessing statistics, scalers, PCA, stain normalization, histogram matching, or imputation were fitted on all data instead of training data only.

15. **Generate audit report**
    - Produce markdown and CSV outputs with issue severity, evidence, affected splits/classes, and recommended fixes.
    - Clearly separate observed facts from assumptions and recommendations.

16. **Recommend fixes**
    - Recommend patient-level or group-level re-splitting, duplicate removal, metadata cleaning, label taxonomy reconciliation, stratification, external validation design, or additional documentation.
    - Do not make clinical claims or assert that the dataset is clinically valid.

## Leakage risks to check

The agent should explicitly check and report these leakage risks where relevant:

- Same patient in train and test.
- Same patient in train and validation when validation is used for model selection.
- Same image duplicated across splits.
- Same image saved with different filenames across splits.
- Augmented copies across splits.
- Laterality leakage, especially when left/right images from the same patient are split independently.
- Visit-level leakage where multiple visits from the same patient appear in different splits.
- Study-level, accession-level, series-level, OCT-volume-level, tile-level, or scanner-session leakage.
- Device, scanner, camera, protocol, or site leakage that allows the model to learn source-specific shortcuts.
- File names containing label information, split information, patient identifiers, outcome names, severity classes, or acquisition metadata.
- Metadata columns containing target labels, future outcomes, adjudication results, or post-test clinical actions.
- Preprocessing, normalization, feature selection, stain normalization, imputation, or dimensionality reduction fitted on all data instead of training data only.
- Test set used during model selection, threshold tuning, architecture selection, augmentation tuning, prompt tuning, or repeated leaderboard-style iteration.
- Public dataset duplicates across training data and external validation data.
- Multiple crops, tiles, frames, slices, or B-scans from the same source image, volume, video, whole slide, or study split across train and test.

## Medical imaging-specific checks

The agent should include medical imaging-specific checks such as:

- Patient-level split is preferred over image-level split unless the task and independence assumptions justify otherwise.
- Study-level, series-level, video-level, volume-level, or whole-slide-level splitting may be required depending on the modality.
- Eye-level and patient-level dependencies are important for ophthalmology datasets.
- Left/right eye correlation can inflate performance if each eye is split independently.
- Multiple visits per patient can create temporal or visit-level leakage.
- Device model, scanner type, vendor, acquisition protocol, and site differences can create domain shift.
- Image quality differences can correlate with labels, sites, or devices.
- Resolution differences can encode scanner, camera, site, or dataset identity.
- Grayscale versus RGB consistency should be checked and documented.
- DICOM tags should be reviewed when relevant, while avoiding exposure of direct identifiers.
- Scanner/site stratification should be considered for train/validation/test and external validation design.
- Tile, frame, slice, B-scan, crop, and patch-level datasets must preserve source-level grouping.

## Ophthalmology-specific guidance

For fundus, OCT, and FFA datasets, the agent should pay special attention to:

- Device variation across fundus cameras, OCT scanners, FFA systems, image fields, acquisition protocols, and vendors.
- The same patient may contribute both eyes and multiple visits.
- Left and right eyes are correlated but may have different disease status, severity, or image quality.
- OCT datasets may include volumes, B-scans, en face images, segmentation maps, and derived thickness maps; splitting at the B-scan level can leak volume-level information.
- FFA sequences may contain multiple frames from the same angiography study; frame-level splitting can leak study-level information.
- Disease severity labels may vary across datasets, graders, grading protocols, referral pathways, and clinical definitions.
- Referral, urgent, non-urgent, referable, non-referable, and screening labels should be documented carefully because they may encode workflow, triage policy, or local practice rather than only pathology.
- External validation should consider device, site, acquisition protocol, population, referral pathway, and disease prevalence differences.
- Image quality labels, macula-centered versus disc-centered fields, laterality, dilation status, and field of view may be important confounders.

## Expected outputs

When generating files, save outputs in a user-specified audit directory or a default directory such as `dataset_audit_output/`. Useful outputs include:

- `dataset_audit_report.md` — executive summary, issue table, dataset structure, key risks, assumptions, and recommended fixes.
- `class_distribution.csv` — counts and percentages by split, class, and label source.
- `split_integrity_report.csv` — patient, study, file, and split overlap findings.
- `duplicate_candidates.csv` — exact hash duplicates, same-filename duplicates, and approximate duplicate candidates when available.
- `metadata_leakage_report.md` — suspicious metadata columns, file-name leakage, direct identifier concerns, and target-leakage risks.
- `domain_shift_summary.md` — site, device, scanner, camera, modality, protocol, date, and resolution distribution summaries.
- `recommended_split_strategy.md` — patient/group-level splitting plan and stratification recommendations.
- `data_card.md` — concise dataset documentation, intended ML use, labels, sources, limitations, and known risks.

## Code-generation instructions

When writing audit code, the agent should:

- Use Python.
- Use `pathlib.Path` for filesystem paths.
- Use `pandas` for metadata tables, summaries, and CSV outputs.
- Use PIL/Pillow or OpenCV for image inspection.
- Optionally use `pydicom` for DICOM parsing and DICOM tag review.
- Optionally use image hashing, such as exact cryptographic hashes and perceptual hashes, for duplicate detection.
- Avoid reading all images into memory at once.
- Work on large datasets incrementally with generators, chunked CSV reading, streaming file hashing, and progress summaries.
- Avoid logging raw PHI, direct identifiers, raw DICOM tags with identifiers, or patient-level file paths when reports will be shared externally.
- Use clear, deterministic output filenames.
- Generate clear markdown and CSV outputs.
- Include command-line arguments for dataset root, metadata file, output directory, split column, label column, patient ID column, study ID column, device column, site column, and date column when practical.
- Keep code modular with functions such as `discover_images`, `load_metadata`, `inspect_images`, `compute_file_hashes`, `audit_splits`, `audit_patient_overlap`, `audit_class_distribution`, `audit_metadata_leakage`, `audit_domain_shift`, `write_markdown_report`, and `write_csv_reports`.
- Mark unknown or unavailable evidence as `Missing`, `Not provided`, or `Not evaluated` instead of fabricating results.

## Duplicate detection guidance

The agent should use multiple duplicate signals where feasible:

- Exact file hash, such as SHA-256, to find byte-identical files.
- Perceptual hash, if an image hashing package is available, to find visually similar images.
- Same filename or basename across splits.
- Same patient IDs, study IDs, accession IDs, visit IDs, eye IDs, OCT volume IDs, slide IDs, video IDs, frame IDs, or scanner session IDs.
- Same dimensions, modality, acquisition date/time, device model, and near-identical metadata.
- Same public dataset identifiers or image IDs across internal training data and external validation data.

Warn users that duplicate and near-duplicate detection may be approximate. Exact hashes can miss resized, recompressed, cropped, color-converted, augmented, or otherwise transformed copies. Perceptual hashes can produce false positives and false negatives, especially across modalities and preprocessing pipelines. Candidate duplicates should be manually reviewed before deletion.

## Reporting style

Reports should classify issues by severity:

- **Critical** — issue can directly invalidate evaluation or create major leakage.
- **High** — issue can materially inflate or destabilize model performance.
- **Medium** — issue creates meaningful uncertainty or documentation gaps.
- **Low** — issue is worth fixing but unlikely to invalidate results alone.
- **Informational** — observation, assumption, or non-blocking documentation item.

Examples:

- **Critical:** Same patient appears across train and test.
- **Critical:** Exact duplicate image appears in both train and test.
- **High:** Severe class imbalance, missing minority class in validation/test, or large prevalence mismatch between train and test.
- **High:** Test set was used repeatedly for model selection or threshold tuning.
- **Medium:** Missing device metadata, missing site metadata, or incomplete acquisition date documentation.
- **Medium:** Label taxonomy differs across combined datasets without a documented mapping.
- **Low:** Inconsistent image dimensions that are handled by documented preprocessing.
- **Informational:** Dataset contains both grayscale and RGB images, with a documented conversion step.

Every issue should include evidence, affected data subset, likely impact, and recommended next action.

## Test instructions

When adding example code for this skill, create:

```text
medical-imaging-dataset-auditor/examples/create_synthetic_dataset.py
medical-imaging-dataset-auditor/examples/run_audit.py
```

The synthetic dataset script should:

- Create a small dummy image dataset using PNG or JPG files.
- Simulate `train`, `val`, and `test` folders.
- Include folder-per-class labels.
- Include one intentional duplicate across splits.
- Include class imbalance.
- Include a metadata CSV with `patient_id` and `device` columns.
- Include at least one additional domain field such as `site`, `laterality`, or `acquisition_date`.
- Avoid real patient data and clearly mark all data as synthetic.

The audit script should:

- Run on the synthetic dataset by default or accept command-line paths.
- Generate the expected markdown and CSV reports.
- Demonstrate class distribution checks, split overlap checks, exact duplicate detection, metadata leakage checks, and domain shift summaries.
- Print the output directory and a short issue summary.

## Example user prompts

Users may invoke this skill with prompts such as:

- "Audit this OCT dataset before training."
- "Check whether there is patient leakage between train and test."
- "Generate a class imbalance and duplicate report for this fundus dataset."
- "Review this medical imaging dataset for external validation risks."
- "Create a data card for this imaging dataset."
- "Audit this DICOM export for split leakage and device/site domain shift."
- "Check if my OCT B-scans are split by volume or accidentally mixed across train and test."

## Limitations

This skill has important limitations:

- It cannot confirm clinical label correctness without qualified experts and a documented review process.
- It cannot guarantee that all duplicates or near-duplicates are found.
- Metadata may be incomplete, inaccurate, missing, anonymized, or inconsistent across sites.
- Dataset audit does not prove model safety, effectiveness, fairness, clinical utility, regulatory readiness, or deployment readiness.
- Clinical validation, statistical review, bias assessment, privacy/security review, regulatory review, and institutional governance are still required for high-stakes use.
- Automated checks can miss subtle leakage, annotation artifacts, site-specific shortcuts, hidden preprocessing differences, and workflow-derived confounders.
- Recommendations should be reviewed by domain experts, clinical collaborators, statisticians, and data governance stakeholders.

## Quality checklist

Before considering an audit complete, verify that:

- [ ] Patient-level split checked.
- [ ] Study, visit, eye, volume, slide, frame, or series-level grouping checked when relevant.
- [ ] Duplicates checked.
- [ ] Class distribution reported.
- [ ] Metadata leakage reviewed.
- [ ] File-name leakage reviewed.
- [ ] Device/site distribution reviewed.
- [ ] Image quality, dimensions, formats, and color modes summarized.
- [ ] Corrupted or unreadable files checked.
- [ ] Label taxonomy documented.
- [ ] Acquisition date and temporal leakage risks reviewed.
- [ ] Preprocessing consistency reviewed.
- [ ] External validation risks documented.
- [ ] Recommended fixes included.
- [ ] Reports avoid clinical claims and do not expose patient-identifiable details.

## Final self-review for the agent

Before finalizing work that uses this skill, answer these questions:

- Is the audit useful for both ophthalmology and general medical imaging datasets?
- Does it reflect real-world leakage risks, including patient, visit, study, device/site, preprocessing, and public dataset overlap risks?
- Does it avoid diagnosing images, validating clinical performance, or making unsupported clinical claims?
- Does it include practical testing guidance with synthetic data and reproducible outputs?
- Are assumptions, missing evidence, limitations, and recommended fixes clearly separated from observed findings?
