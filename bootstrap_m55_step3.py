"""Barrister_AI M5.5 Step 3.

Attach legal text to hardened pairs and create a leakage-safe
train/test split grouped by source case.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sklearn.model_selection import GroupShuffleSplit

PROJECT_ROOT = Path(__file__).resolve().parent

CASES_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "generated"
    / "legal_cases_hardened.json"
)

PAIRS_FILE = (
    PROJECT_ROOT
    / "ml"
    / "generated"
    / "hardened_precedent_pairs.json"
)

TRAIN_FILE = (
    PROJECT_ROOT
    / "ml"
    / "generated"
    / "hardened_precedent_train.json"
)

TEST_FILE = (
    PROJECT_ROOT
    / "ml"
    / "generated"
    / "hardened_precedent_test.json"
)

TEST_SIZE = 0.20
RANDOM_SEED = 42

TEXT_FIELDS = (
    "case_title",
    "title",
    "facts",
    "summary",
    "legal_issue",
    "issue",
    "legal_sections",
    "sections",
    "judgment",
    "decision",
    "reasoning",
)


def load_json(file_path: Path) -> list[dict[str, Any]]:
    """Load a non-empty JSON list."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list) or not data:
        raise ValueError(
            f"Expected non-empty JSON list: {file_path}"
        )

    return data


def normalise_value(value: Any) -> str:
    """Convert supported values into clean text."""
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(
            str(item).strip()
            for item in value
            if str(item).strip()
        )

    if isinstance(value, dict):
        return " ".join(
            f"{key} {item}"
            for key, item in value.items()
            if str(item).strip()
        )

    return str(value).strip()


def build_case_text(case: dict[str, Any]) -> str:
    """Combine legal fields into one text document."""
    parts: list[str] = []

    for field in TEXT_FIELDS:
        cleaned = normalise_value(case.get(field))

        if cleaned:
            parts.append(
                f"{field.replace('_', ' ')}: {cleaned}"
            )

    if not parts:
        excluded = {
            "case_id",
            "source_case_id",
            "language_variant",
            "domain",
            "label",
            "outcome",
        }

        for field, value in case.items():
            if field in excluded:
                continue

            cleaned = normalise_value(value)

            if cleaned:
                parts.append(
                    f"{field.replace('_', ' ')}: {cleaned}"
                )

    return " ".join(parts).strip()


def build_case_lookup(
    cases: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Index cases by unique case ID."""
    lookup: dict[str, dict[str, Any]] = {}

    for case in cases:
        case_id = str(case["case_id"])

        if case_id in lookup:
            raise ValueError(
                f"Duplicate case ID: {case_id}"
            )

        lookup[case_id] = case

    return lookup


def attach_text(
    pairs: list[dict[str, Any]],
    case_lookup: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach query and candidate text to all pairs."""
    records: list[dict[str, Any]] = []

    for index, pair in enumerate(pairs, start=1):
        query_id = pair["query_case_id"]
        candidate_id = pair["candidate_case_id"]

        if query_id not in case_lookup:
            raise KeyError(
                f"Unknown query case: {query_id}"
            )

        if candidate_id not in case_lookup:
            raise KeyError(
                f"Unknown candidate case: {candidate_id}"
            )

        query_text = build_case_text(
            case_lookup[query_id]
        )

        candidate_text = build_case_text(
            case_lookup[candidate_id]
        )

        if not query_text or not candidate_text:
            raise ValueError(
                f"Empty text detected in pair {index}"
            )

        records.append(
            {
                "pair_id": f"HPAIR{index:05d}",
                "query_case_id": query_id,
                "candidate_case_id": candidate_id,
                "query_source_id": pair["query_source_id"],
                "candidate_source_id": pair[
                    "candidate_source_id"
                ],
                "query_text": query_text,
                "candidate_text": candidate_text,
                "label": int(pair["label"]),
                "pair_type": pair["pair_type"],
            }
        )

    return records


def split_records(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split by query source case to avoid leakage."""
    groups = [
        record["query_source_id"]
        for record in records
    ]

    labels = [
        record["label"]
        for record in records
    ]

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
    )

    train_indices, test_indices = next(
        splitter.split(
            X=records,
            y=labels,
            groups=groups,
        )
    )

    train_data = [
        records[index]
        for index in train_indices
    ]

    test_data = [
        records[index]
        for index in test_indices
    ]

    return train_data, test_data


def validate_split(
    train_data: list[dict[str, Any]],
    test_data: list[dict[str, Any]],
) -> None:
    """Validate source separation and class presence."""
    train_sources = {
        record["query_source_id"]
        for record in train_data
    }

    test_sources = {
        record["query_source_id"]
        for record in test_data
    }

    overlap = train_sources & test_sources

    if overlap:
        raise ValueError(
            f"Source leakage detected: {sorted(overlap)}"
        )

    train_labels = {
        record["label"]
        for record in train_data
    }

    test_labels = {
        record["label"]
        for record in test_data
    }

    if train_labels != {0, 1}:
        raise ValueError(
            "Training split lacks one class."
        )

    if test_labels != {0, 1}:
        raise ValueError(
            "Testing split lacks one class."
        )


def save_json(
    data: list[dict[str, Any]],
    file_path: Path,
) -> None:
    """Save formatted JSON."""
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def print_summary(
    train_data: list[dict[str, Any]],
    test_data: list[dict[str, Any]],
) -> None:
    """Print split statistics."""
    train_positive = sum(
        item["label"] == 1
        for item in train_data
    )

    test_positive = sum(
        item["label"] == 1
        for item in test_data
    )

    print("=" * 60)
    print("BARRISTER_AI - M5.5 STEP 3")
    print("=" * 60)
    print(f"Training records     : {len(train_data)}")
    print(f"Testing records      : {len(test_data)}")
    print(
        f"Training labels      : "
        f"Relevant={train_positive}, "
        f"Non-relevant={len(train_data) - train_positive}"
    )
    print(
        f"Testing labels       : "
        f"Relevant={test_positive}, "
        f"Non-relevant={len(test_data) - test_positive}"
    )
    print("Query-source overlap : 0")
    print(f"Training file        : {TRAIN_FILE}")
    print(f"Testing file         : {TEST_FILE}")
    print("=" * 60)
    print("✅ M5.5 Step 3 validation passed")


def main() -> None:
    """Run M5.5 Step 3."""
    cases = load_json(CASES_FILE)
    pairs = load_json(PAIRS_FILE)

    case_lookup = build_case_lookup(cases)
    records = attach_text(pairs, case_lookup)

    train_data, test_data = split_records(records)

    validate_split(train_data, test_data)

    save_json(train_data, TRAIN_FILE)
    save_json(test_data, TEST_FILE)

    print_summary(train_data, test_data)


if __name__ == "__main__":
    main()