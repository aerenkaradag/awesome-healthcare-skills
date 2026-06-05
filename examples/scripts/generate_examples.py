#!/usr/bin/env python3
"""Generate synthetic, testable example files for the healthcare AI skills.

This script produces three deterministic example files plus this folder's
README workflow data. All output is SYNTHETIC. It contains no real patient
data, names, addresses, phone numbers, emails, or other direct identifiers.

Outputs (written to the parent ``examples/`` directory by default):
  - synthetic-fhir-bundle.json : FHIR R4 Bundle for fhir-to-ml-dataset-builder
  - diabetes-cohort.csv        : tabular cohort for ehr-care-gap-analyzer
  - validation-results.csv     : model eval rows for medical-ai-validation-report-writer

Design goals:
  - Deterministic: a fixed random seed makes every run byte-for-byte identical.
  - Dependency-light: standard library only (pandas is NOT required to GENERATE,
    though the outputs are trivially loadable by pandas).
  - No internet access required.
  - No Synthea installation required. Synthea support is optional (see
    ``--synthea-bundle`` below): if you have a real Synthea FHIR export you may
    merge/replace the synthetic bundle, but the default path is fully offline.

Synthea (optional):
  Synthea (https://github.com/synthetichealth/synthea) is an open-source
  synthetic patient generator. It requires Java 11+. If you have generated a
  Synthea FHIR R4 bundle, you can point this script at it with
  ``--synthea-bundle path/to/bundle.json`` to use it INSTEAD of the built-in
  synthetic bundle. The CSV files are always generated deterministically here
  so the care-gap and validation workflows remain self-contained.

Usage:
  python generate_examples.py                       # write all files
  python generate_examples.py --out ../             # custom output dir
  python generate_examples.py --synthea-bundle b.json
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
SEED = 20240101
RNG = random.Random(SEED)

# A fixed "today" so generated dates and ages are reproducible across runs.
REFERENCE_DATE = date(2024, 6, 1)

# --------------------------------------------------------------------------- #
# Coding systems (used in the FHIR bundle)
# --------------------------------------------------------------------------- #
SNOMED = "http://snomed.info/sct"
LOINC = "http://loinc.org"
RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"

CONDITION_CODES = {
    "type2_diabetes": ("44054006", "Type 2 diabetes mellitus"),
    "hypertension": ("38341003", "Hypertensive disorder, systemic arterial"),
    "ckd": ("709044004", "Chronic kidney disease"),
    "hyperlipidemia": ("55822004", "Hyperlipidemia"),
    "neuropathy": ("42345005", "Diabetic neuropathy"),
}

# LOINC codes for the observations we emit.
OBSERVATION_CODES = {
    "hba1c": ("4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood", "%"),
    "egfr": ("33914-3", "Glomerular filtration rate/1.73 sq M.predicted",
             "mL/min/1.73m2"),
    "ldl": ("18262-6", "LDL cholesterol in Serum or Plasma", "mg/dL"),
    "creatinine": ("2160-0", "Creatinine in Serum or Plasma", "mg/dL"),
    "systolic": ("8480-6", "Systolic blood pressure", "mmHg"),
    "diastolic": ("8462-4", "Diastolic blood pressure", "mmHg"),
}

# RxNorm codes for medications.
MEDICATION_CODES = {
    "metformin": ("860975", "Metformin hydrochloride 500 MG Oral Tablet"),
    "insulin_glargine": ("311041", "Insulin glargine 100 UNT/ML Injectable Solution"),
    "lisinopril": ("314076", "Lisinopril 10 MG Oral Tablet"),
    "atorvastatin": ("617312", "Atorvastatin 20 MG Oral Tablet"),
}

# Fake, clearly-synthetic given/family name pools (NOT real-person data; only
# used inside the FHIR Patient.name to keep the resource structurally valid).
FAKE_GIVEN = ["Synth", "Demo", "Test", "Sample", "Mock", "Example", "Fixture"]
FAKE_FAMILY = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot",
               "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike",
               "November", "Oscar"]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def iso(d: date) -> str:
    """ISO 8601 date string (YYYY-MM-DD)."""
    return d.isoformat()


def iso_dt(d: date, hour: int = 9) -> str:
    """ISO 8601 datetime with timezone for FHIR fields."""
    return f"{d.isoformat()}T{hour:02d}:00:00+00:00"


def days_ago(n: int) -> date:
    return REFERENCE_DATE - timedelta(days=n)


def round1(x: float) -> float:
    return round(x, 1)


# --------------------------------------------------------------------------- #
# FHIR bundle generation (fhir-to-ml-dataset-builder)
# --------------------------------------------------------------------------- #
def _codeable(system: str, code: str, display: str) -> dict:
    return {"coding": [{"system": system, "code": code, "display": display}],
            "text": display}


def _numeric_observation(obs_id, patient_id, key, value, eff_date):
    code, display, unit = OBSERVATION_CODES[key]
    return {
        "resource": {
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "category": [_codeable(
                "http://terminology.hl7.org/CodeSystem/observation-category",
                "laboratory", "Laboratory")],
            "code": _codeable(LOINC, code, display),
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": iso_dt(eff_date),
            "valueQuantity": {
                "value": value,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": unit,
            },
        }
    }


def _condition(cond_id, patient_id, key, onset_date):
    code, display = CONDITION_CODES[key]
    return {
        "resource": {
            "resourceType": "Condition",
            "id": cond_id,
            "clinicalStatus": _codeable(
                "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "active", "Active"),
            "verificationStatus": _codeable(
                "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "confirmed", "Confirmed"),
            "code": _codeable(SNOMED, code, display),
            "subject": {"reference": f"Patient/{patient_id}"},
            "onsetDateTime": iso_dt(onset_date),
            "recordedDate": iso(onset_date),
        }
    }


def _medication_request(med_id, patient_id, key, authored_date):
    code, display = MEDICATION_CODES[key]
    return {
        "resource": {
            "resourceType": "MedicationRequest",
            "id": med_id,
            "status": "active",
            "intent": "order",
            "medicationCodeableConcept": _codeable(RXNORM, code, display),
            "subject": {"reference": f"Patient/{patient_id}"},
            "authoredOn": iso(authored_date),
        }
    }


def _encounter(enc_id, patient_id, enc_date, enc_class="AMB",
               enc_class_display="ambulatory"):
    return {
        "resource": {
            "resourceType": "Encounter",
            "id": enc_id,
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": enc_class,
                "display": enc_class_display,
            },
            "type": [_codeable(SNOMED, "185349003",
                               "Encounter for check up")],
            "subject": {"reference": f"Patient/{patient_id}"},
            "period": {
                "start": iso_dt(enc_date, 9),
                "end": iso_dt(enc_date, 10),
            },
        }
    }


def _procedure(proc_id, patient_id, proc_date):
    return {
        "resource": {
            "resourceType": "Procedure",
            "id": proc_id,
            "status": "completed",
            "code": _codeable(SNOMED, "252779009",
                              "Single bright stimulus electroretinography"),
            "subject": {"reference": f"Patient/{patient_id}"},
            "performedDateTime": iso_dt(proc_date),
        }
    }


def build_fhir_bundle(n_patients: int = 10) -> dict:
    """Build a compact, structurally-valid FHIR R4 transaction bundle."""
    entries: list[dict] = []

    for i in range(1, n_patients + 1):
        pid = f"synthetic-patient-{i:03d}"
        sex = RNG.choice(["male", "female"])
        # Birth year => age between 38 and 82.
        age = RNG.randint(38, 82)
        birth_year = REFERENCE_DATE.year - age
        birth_date = date(birth_year, RNG.randint(1, 12), RNG.randint(1, 28))

        given = RNG.choice(FAKE_GIVEN)
        family = RNG.choice(FAKE_FAMILY)

        entries.append({
            "resource": {
                "resourceType": "Patient",
                "id": pid,
                "active": True,
                # Clearly-synthetic placeholder name; not a real person.
                "name": [{"use": "official", "family": family,
                          "given": [given]}],
                "gender": sex,
                "birthDate": iso(birth_date),
            }
        })

        # --- Conditions ------------------------------------------------------
        # Every patient has type 2 diabetes (diabetes-relevant cohort).
        onset = days_ago(RNG.randint(400, 4000))
        entries.append(_condition(f"cond-{i:03d}-dm2", pid, "type2_diabetes",
                                   onset))

        has_htn = RNG.random() < 0.65
        if has_htn:
            entries.append(_condition(f"cond-{i:03d}-htn", pid, "hypertension",
                                       days_ago(RNG.randint(300, 3000))))
        has_ckd = RNG.random() < 0.35
        if has_ckd:
            entries.append(_condition(f"cond-{i:03d}-ckd", pid, "ckd",
                                       days_ago(RNG.randint(200, 2000))))
        if RNG.random() < 0.4:
            entries.append(_condition(f"cond-{i:03d}-lipid", pid,
                                       "hyperlipidemia",
                                       days_ago(RNG.randint(200, 2500))))
        if RNG.random() < 0.25:
            entries.append(_condition(f"cond-{i:03d}-neuro", pid, "neuropathy",
                                       days_ago(RNG.randint(100, 1500))))

        # --- Observations ----------------------------------------------------
        hba1c_date = days_ago(RNG.randint(20, 500))
        hba1c = round1(RNG.uniform(5.8, 11.5))
        entries.append(_numeric_observation(f"obs-{i:03d}-hba1c", pid,
                                             "hba1c", hba1c, hba1c_date))

        egfr_date = days_ago(RNG.randint(20, 500))
        egfr = round1(RNG.uniform(22.0, 105.0) if has_ckd
                      else RNG.uniform(55.0, 110.0))
        entries.append(_numeric_observation(f"obs-{i:03d}-egfr", pid,
                                             "egfr", egfr, egfr_date))

        ldl_date = days_ago(RNG.randint(20, 600))
        ldl = round1(RNG.uniform(60.0, 190.0))
        entries.append(_numeric_observation(f"obs-{i:03d}-ldl", pid,
                                             "ldl", ldl, ldl_date))

        creat_date = egfr_date
        creatinine = round(0.9 + (90.0 - min(egfr, 90.0)) * 0.02, 2)
        entries.append(_numeric_observation(f"obs-{i:03d}-creat", pid,
                                             "creatinine", creatinine,
                                             creat_date))

        bp_date = days_ago(RNG.randint(10, 365))
        systolic = RNG.randint(118, 175) if has_htn else RNG.randint(110, 140)
        diastolic = RNG.randint(70, 100)
        entries.append(_numeric_observation(f"obs-{i:03d}-sbp", pid,
                                             "systolic", systolic, bp_date))
        entries.append(_numeric_observation(f"obs-{i:03d}-dbp", pid,
                                             "diastolic", diastolic, bp_date))

        # --- Medications -----------------------------------------------------
        if RNG.random() < 0.8:
            entries.append(_medication_request(f"med-{i:03d}-metformin", pid,
                                                "metformin",
                                                days_ago(RNG.randint(30, 700))))
        if hba1c > 9.0 or RNG.random() < 0.3:
            entries.append(_medication_request(f"med-{i:03d}-insulin", pid,
                                                "insulin_glargine",
                                                days_ago(RNG.randint(30, 500))))
        if has_htn or has_ckd:
            entries.append(_medication_request(f"med-{i:03d}-lisinopril", pid,
                                                "lisinopril",
                                                days_ago(RNG.randint(30, 600))))
        if ldl > 100 and RNG.random() < 0.7:
            entries.append(_medication_request(f"med-{i:03d}-atorvastatin", pid,
                                                "atorvastatin",
                                                days_ago(RNG.randint(30, 600))))

        # --- Encounters ------------------------------------------------------
        n_enc = RNG.randint(1, 3)
        for e in range(n_enc):
            entries.append(_encounter(f"enc-{i:03d}-{e}", pid,
                                       days_ago(RNG.randint(15, 700))))

        # --- Procedure (eye exam) for some patients --------------------------
        if RNG.random() < 0.5:
            entries.append(_procedure(f"proc-{i:03d}-eye", pid,
                                       days_ago(RNG.randint(60, 900))))

    return {
        "resourceType": "Bundle",
        "id": "synthetic-diabetes-bundle",
        "type": "transaction",
        "entry": entries,
    }


# --------------------------------------------------------------------------- #
# Diabetes cohort CSV (ehr-care-gap-analyzer)
# --------------------------------------------------------------------------- #
COHORT_COLUMNS = [
    "patient_id", "age", "sex", "diabetes_type", "diabetes_duration_years",
    "last_hba1c", "last_hba1c_date", "egfr", "egfr_date", "ldl", "ldl_date",
    "systolic_bp", "diastolic_bp", "has_hypertension", "has_ckd", "has_cvd",
    "has_neuropathy", "on_metformin", "on_insulin", "on_ace_arb", "on_statin",
    "last_eye_exam_date", "last_nephrology_visit_date",
    "last_cardiology_visit_date", "last_foot_exam_date",
    "last_primary_care_visit_date",
    # optional useful columns
    "bmi", "smoking_status", "albumin_creatinine_ratio", "acr_date",
    "num_er_visits_12m", "num_hospitalizations_12m",
]


def _maybe_date(d: date | None) -> str:
    return iso(d) if d is not None else ""


def build_cohort_rows(n: int = 30) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        pid = f"COHORT-{i:04d}"
        age = RNG.randint(34, 84)
        sex = RNG.choice(["M", "F"])
        dm_type = "type2" if RNG.random() < 0.9 else "type1"
        duration = RNG.randint(0, 28)

        # Build deliberate care-gap patterns so the analyzer has signal.
        # Pattern buckets cycle to guarantee coverage of each gap type.
        bucket = i % 6

        has_htn = RNG.random() < 0.6
        has_ckd = RNG.random() < 0.3
        has_cvd = RNG.random() < 0.25
        has_neuro = RNG.random() < 0.2

        # HbA1c
        if bucket == 0:  # poor control + stale follow-up
            hba1c = round1(RNG.uniform(9.5, 12.5))
            hba1c_date = days_ago(RNG.randint(400, 720))
        elif bucket == 5:  # well managed
            hba1c = round1(RNG.uniform(5.9, 6.8))
            hba1c_date = days_ago(RNG.randint(20, 120))
        else:
            hba1c = round1(RNG.uniform(6.5, 9.5))
            hba1c_date = days_ago(RNG.randint(30, 360))

        # eGFR / CKD
        if bucket == 1:  # low eGFR, no nephrology visit
            has_ckd = True
            egfr = round1(RNG.uniform(20.0, 44.0))
            egfr_date = days_ago(RNG.randint(40, 300))
            neph_date = None
        else:
            egfr = round1(RNG.uniform(45.0, 110.0))
            egfr_date = days_ago(RNG.randint(30, 400))
            neph_date = (days_ago(RNG.randint(30, 700))
                         if (has_ckd and RNG.random() < 0.7) else None)

        # LDL / statin
        if bucket == 3:  # high LDL, no statin
            ldl = round1(RNG.uniform(140.0, 210.0))
            on_statin = 0
        else:
            ldl = round1(RNG.uniform(55.0, 160.0))
            on_statin = 1 if (ldl > 100 and RNG.random() < 0.7) else 0
        ldl_date = days_ago(RNG.randint(30, 600))

        systolic = (RNG.randint(120, 178) if has_htn
                    else RNG.randint(108, 138))
        diastolic = RNG.randint(66, 102)

        on_metformin = 1 if RNG.random() < 0.8 else 0
        on_insulin = 1 if (hba1c > 9.0 or RNG.random() < 0.25) else 0
        on_ace_arb = 1 if ((has_htn or has_ckd) and RNG.random() < 0.75) else 0

        # Eye exam: bucket 2 has no recent eye exam.
        if bucket == 2:
            eye_date = (days_ago(RNG.randint(800, 1500))
                        if RNG.random() < 0.5 else None)
        else:
            eye_date = days_ago(RNG.randint(60, 500))

        foot_date = (days_ago(RNG.randint(60, 500))
                     if RNG.random() < 0.7 else None)
        cardio_date = (days_ago(RNG.randint(60, 800))
                       if (has_cvd and RNG.random() < 0.7) else None)
        pcp_date = days_ago(RNG.randint(20, 420))

        bmi = round1(RNG.uniform(22.0, 41.0))
        smoking = RNG.choice(["never", "former", "current", "never",
                              "former"])
        acr = round1(RNG.uniform(5.0, 350.0))
        acr_date = days_ago(RNG.randint(40, 500))
        er_visits = RNG.choice([0, 0, 0, 1, 1, 2, 3])
        hosp = RNG.choice([0, 0, 0, 0, 1, 1, 2])

        # Introduce a few missing values deterministically.
        if bucket == 4 and i % 12 == 4:
            # Simulate a patient with no recent labs at all.
            hba1c = None
            hba1c_date = None

        rows.append({
            "patient_id": pid,
            "age": age,
            "sex": sex,
            "diabetes_type": dm_type,
            "diabetes_duration_years": duration,
            "last_hba1c": "" if hba1c is None else hba1c,
            "last_hba1c_date": _maybe_date(hba1c_date),
            "egfr": egfr,
            "egfr_date": _maybe_date(egfr_date),
            "ldl": ldl,
            "ldl_date": _maybe_date(ldl_date),
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "has_hypertension": int(has_htn),
            "has_ckd": int(has_ckd),
            "has_cvd": int(has_cvd),
            "has_neuropathy": int(has_neuro),
            "on_metformin": on_metformin,
            "on_insulin": on_insulin,
            "on_ace_arb": on_ace_arb,
            "on_statin": on_statin,
            "last_eye_exam_date": _maybe_date(eye_date),
            "last_nephrology_visit_date": _maybe_date(neph_date),
            "last_cardiology_visit_date": _maybe_date(cardio_date),
            "last_foot_exam_date": _maybe_date(foot_date),
            "last_primary_care_visit_date": _maybe_date(pcp_date),
            "bmi": bmi,
            "smoking_status": smoking,
            "albumin_creatinine_ratio": acr,
            "acr_date": _maybe_date(acr_date),
            "num_er_visits_12m": er_visits,
            "num_hospitalizations_12m": hosp,
        })
    return rows


# --------------------------------------------------------------------------- #
# Validation results CSV (medical-ai-validation-report-writer)
# --------------------------------------------------------------------------- #
VALIDATION_COLUMNS = [
    "patient_id", "split", "true_label", "predicted_label",
    "predicted_probability", "age_group", "sex", "site", "has_ckd",
    "has_hypertension",
]

POS = "complication_within_24m"
NEG = "no_complication_within_24m"


def build_validation_rows(n: int = 200) -> list[dict]:
    rows = []
    age_groups = ["18-39", "40-59", "60-79", "80+"]
    sites = ["site_A", "site_B", "site_C"]

    for i in range(1, n + 1):
        pid = f"VAL-{i:04d}"
        # validation/test split only (test locked until final eval).
        split = "validation" if i % 3 != 0 else "test"
        age_group = RNG.choice(age_groups)
        sex = RNG.choice(["M", "F"])
        site = RNG.choice(sites)
        has_ckd = 1 if RNG.random() < 0.3 else 0
        has_htn = 1 if RNG.random() < 0.55 else 0

        # Base prevalence of positive ~ 30%, modulated by subgroup so that
        # subgroup performance differences are visible.
        base_p = 0.30
        if has_ckd:
            base_p += 0.18
        if age_group == "80+":
            base_p += 0.12
        if age_group == "18-39":
            base_p -= 0.12
        base_p = min(max(base_p, 0.05), 0.85)
        is_positive = RNG.random() < base_p
        true_label = POS if is_positive else NEG

        # Model probability: discriminative but imperfect; weaker at site_C
        # to create a domain-shift / subgroup signal.
        if is_positive:
            mean = 0.68
        else:
            mean = 0.32
        spread = 0.18
        if site == "site_C":
            spread = 0.27  # noisier predictions at one site
        prob = RNG.gauss(mean, spread)
        prob = min(max(prob, 0.01), 0.99)
        prob = round(prob, 3)

        predicted_label = POS if prob >= 0.5 else NEG

        rows.append({
            "patient_id": pid,
            "split": split,
            "true_label": true_label,
            "predicted_label": predicted_label,
            "predicted_probability": prob,
            "age_group": age_group,
            "sex": sex,
            "site": site,
            "has_ckd": has_ckd,
            "has_hypertension": has_htn,
        })
    return rows


# --------------------------------------------------------------------------- #
# Writers
# --------------------------------------------------------------------------- #
def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, obj: dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
        fh.write("\n")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--out", default=None,
        help="Output directory (default: the examples/ folder, i.e. the "
             "parent of this scripts/ directory).")
    parser.add_argument(
        "--synthea-bundle", default=None,
        help="Optional path to a real Synthea FHIR R4 bundle JSON to use "
             "INSTEAD of the built-in synthetic bundle.")
    parser.add_argument("--patients", type=int, default=10,
                        help="Number of FHIR patients (5-15).")
    parser.add_argument("--cohort-rows", type=int, default=30,
                        help="Number of diabetes cohort rows (20-50).")
    parser.add_argument("--validation-rows", type=int, default=200,
                        help="Number of validation result rows (100-300).")
    args = parser.parse_args()

    # Reset RNG so output is identical regardless of import-time usage.
    global RNG
    RNG = random.Random(SEED)

    out_dir = (Path(args.out) if args.out
               else Path(__file__).resolve().parent.parent)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. FHIR bundle ---------------------------------------------------------
    if args.synthea_bundle:
        bundle = json.loads(Path(args.synthea_bundle).read_text(encoding="utf-8"))
        print(f"Using Synthea bundle from {args.synthea_bundle}")
    else:
        n_patients = max(5, min(15, args.patients))
        bundle = build_fhir_bundle(n_patients)
    write_json(out_dir / "synthetic-fhir-bundle.json", bundle)

    # 2. Diabetes cohort -----------------------------------------------------
    cohort_rows = build_cohort_rows(max(20, min(50, args.cohort_rows)))
    write_csv(out_dir / "diabetes-cohort.csv", COHORT_COLUMNS, cohort_rows)

    # 3. Validation results --------------------------------------------------
    val_rows = build_validation_rows(max(100, min(300, args.validation_rows)))
    write_csv(out_dir / "validation-results.csv", VALIDATION_COLUMNS, val_rows)

    # Summary (aggregate only; no PHI / no patient-level detail).
    n_pos = sum(1 for r in val_rows if r["true_label"] == POS)
    print("Generated example files in:", out_dir)
    print(f"  synthetic-fhir-bundle.json : "
          f"{len(bundle['entry'])} resources")
    print(f"  diabetes-cohort.csv        : {len(cohort_rows)} patients")
    print(f"  validation-results.csv     : {len(val_rows)} rows "
          f"({n_pos} positives, {len(val_rows) - n_pos} negatives)")
    print("All data is SYNTHETIC. Do not treat as real clinical evidence.")


if __name__ == "__main__":
    main()
