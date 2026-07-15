"""Barrister_AI M5.5 Step 1.

Create deterministic legal-language variants from the existing
synthetic cases without modifying the original M3 dataset.
"""

from __future__ import annotations

import copy
import json
import random
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "generated"
    / "legal_cases.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "generated"
    / "legal_cases_hardened.json"
)

VARIANTS_PER_CASE = 5
RANDOM_SEED = 42

PROTECTED_FIELDS = {
    "case_id",
    "id",
    "case_number",
    "domain",
    "label",
    "outcome",
}

LANGUAGE_VARIANTS = {
    "cheque dishonoured": [
        "cheque returned unpaid",
        "payment instrument was dishonoured",
        "bank declined the cheque",
    ],
    "insufficient funds": [
        "inadequate account balance",
        "insufficient balance",
        "lack of available funds",
    ],
    "consumer complaint": [
        "consumer grievance",
        "complaint before the consumer forum",
        "consumer dispute",
    ],
    "defective product": [
        "faulty goods",
        "product suffering from defects",
        "substandard merchandise",
    ],
    "online transaction": [
        "digital transaction",
        "internet-based payment",
        "electronic financial transaction",
    ],
    "cyber crime": [
        "digital offence",
        "computer-related offence",
        "online criminal activity",
    ],
    "motor accident": [
        "road traffic accident",
        "vehicular collision",
        "motor vehicle incident",
    ],
    "compensation": [
        "monetary relief",
        "financial compensation",
        "damages",
    ],
    "murder": [
        "homicide",
        "fatal criminal act",
        "unlawful killing",
    ],
    "accused": [
        "defendant",
        "person charged",
        "alleged offender",
    ],
    "evidence": [
        "evidentiary material",
        "proof placed before the court",
        "supporting material",
    ],
    "court": [
        "judicial forum",
        "trial court",
        "competent court",
    ],
}

NEUTRAL_SENTENCES = [
    "The dispute required examination of the available record.",
    "The court assessed the facts and applicable legal principles.",
    "The parties relied on documentary and oral material.",
    "The matter involved interpretation of the relevant law.",
    "The decision depended on the circumstances of the case.",
]


def load_cases(file_path: Path) -> list[dict[str, Any]]:
    """Load and validate the original legal cases."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Original dataset not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "Expected a non-empty JSON list of cases."
        )

    return cases


def get_case_id(case: dict[str, Any], index: int) -> str:
    """Return the original case identifier."""
    for field in ("case_id", "id", "case_number"):
        if case.get(field):
            return str(case[field])

    return f"CASE{index + 1:04d}"


def replace_legal_language(
    text: str,
    rng: random.Random,
) -> tuple[str, bool]:
    """Replace legal expressions with alternative wording."""
    changed = False
    updated_text = text

    phrases = list(LANGUAGE_VARIANTS.items())
    rng.shuffle(phrases)

    for phrase, alternatives in phrases:
        if re.search(
            re.escape(phrase),
            updated_text,
            flags=re.IGNORECASE,
        ):
            replacement = rng.choice(alternatives)

            updated_text = re.sub(
                re.escape(phrase),
                replacement,
                updated_text,
                count=1,
                flags=re.IGNORECASE,
            )

            changed = True

    return updated_text, changed


def transform_value(
    value: Any,
    rng: random.Random,
) -> tuple[Any, bool]:
    """Recursively transform textual case content."""
    if isinstance(value, str):
        return replace_legal_language(value, rng)

    if isinstance(value, list):
        transformed_items = []
        changed = False

        for item in value:
            transformed, item_changed = transform_value(item, rng)
            transformed_items.append(transformed)
            changed = changed or item_changed

        return transformed_items, changed

    if isinstance(value, dict):
        transformed_dict = {}
        changed = False

        for key, item in value.items():
            transformed, item_changed = transform_value(item, rng)
            transformed_dict[key] = transformed
            changed = changed or item_changed

        return transformed_dict, changed

    return value, False


def create_variant(
    case: dict[str, Any],
    original_id: str,
    variant_number: int,
    rng: random.Random,
) -> dict[str, Any]:
    """Create one language-varied copy of a legal case."""
    variant = copy.deepcopy(case)
    changed = False

    for field, value in list(variant.items()):
        if field in PROTECTED_FIELDS:
            continue

        transformed, field_changed = transform_value(value, rng)
        variant[field] = transformed
        changed = changed or field_changed

    if not changed:
        for field, value in variant.items():
            if field not in PROTECTED_FIELDS and isinstance(value, str):
                variant[field] = (
                    f"{value} {rng.choice(NEUTRAL_SENTENCES)}"
                )
                break

    variant["case_id"] = (
        f"{original_id}_V{variant_number}"
    )
    variant["source_case_id"] = original_id
    variant["language_variant"] = variant_number

    return variant


def generate_hardened_dataset(
    cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create originals plus language-varied cases."""
    rng = random.Random(RANDOM_SEED)
    hardened_cases: list[dict[str, Any]] = []

    for index, case in enumerate(cases):
        original_id = get_case_id(case, index)

        original = copy.deepcopy(case)
        original["case_id"] = original_id
        original["source_case_id"] = original_id
        original["language_variant"] = 0
        hardened_cases.append(original)

        for variant_number in range(
            1,
            VARIANTS_PER_CASE + 1,
        ):
            hardened_cases.append(
                create_variant(
                    case,
                    original_id,
                    variant_number,
                    rng,
                )
            )

    return hardened_cases


def main() -> None:
    """Run M5.5 Step 1."""
    cases = load_cases(INPUT_FILE)
    hardened_cases = generate_hardened_dataset(cases)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            hardened_cases,
            file,
            indent=2,
            ensure_ascii=False,
        )

    unique_ids = {
        case["case_id"]
        for case in hardened_cases
    }

    if len(unique_ids) != len(hardened_cases):
        raise ValueError("Duplicate case IDs detected.")

    expected_total = len(cases) * (
        VARIANTS_PER_CASE + 1
    )

    if len(hardened_cases) != expected_total:
        raise ValueError(
            "Unexpected hardened dataset size."
        )

    print("=" * 60)
    print("BARRISTER_AI - M5.5 STEP 1")
    print("=" * 60)
    print(f"Original cases       : {len(cases)}")
    print(f"Variants per case    : {VARIANTS_PER_CASE}")
    print(f"Total hardened cases : {len(hardened_cases)}")
    print(f"Unique case IDs      : {len(unique_ids)}")
    print(f"Output file          : {OUTPUT_FILE}")
    print("=" * 60)
    print("✅ M5.5 Step 1 validation passed")


if __name__ == "__main__":
    main()