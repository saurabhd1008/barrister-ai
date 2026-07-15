"""Barrister_AI M5.5 Step 2.

Generate balanced positive, same-domain hard-negative and
cross-domain negative legal precedent pairs.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "generated"
    / "legal_cases_hardened.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ml"
    / "generated"
    / "hardened_precedent_pairs.json"
)

RANDOM_SEED = 42
POSITIVES_PER_SOURCE = 4
HARD_NEGATIVES_PER_SOURCE = 2
CROSS_NEGATIVES_PER_SOURCE = 2


def load_cases(file_path: Path) -> list[dict[str, Any]]:
    """Load and validate hardened legal cases."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Hardened dataset not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError("Expected a non-empty JSON list.")

    required_fields = {
        "case_id",
        "source_case_id",
        "language_variant",
        "domain",
    }

    for index, case in enumerate(cases):
        missing = required_fields - case.keys()

        if missing:
            raise ValueError(
                f"Case {index} is missing: {sorted(missing)}"
            )

    return cases


def group_cases(
    cases: list[dict[str, Any]],
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
]:
    """Group cases by source identifier and legal domain."""
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for case in cases:
        by_source[case["source_case_id"]].append(case)
        by_domain[case["domain"]].append(case)

    return dict(by_source), dict(by_domain)


def make_pair(
    query: dict[str, Any],
    candidate: dict[str, Any],
    label: int,
    pair_type: str,
) -> dict[str, Any]:
    """Create one labelled legal pair."""
    return {
        "query_case_id": query["case_id"],
        "candidate_case_id": candidate["case_id"],
        "query_source_id": query["source_case_id"],
        "candidate_source_id": candidate["source_case_id"],
        "query_domain": query["domain"],
        "candidate_domain": candidate["domain"],
        "label": label,
        "pair_type": pair_type,
    }


def generate_pairs(
    cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate balanced and challenging training pairs."""
    rng = random.Random(RANDOM_SEED)
    by_source, by_domain = group_cases(cases)
    all_cases = list(cases)

    pairs: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()

    for source_id, source_cases in by_source.items():
        query = rng.choice(source_cases)

        positive_candidates = [
            case
            for case in source_cases
            if case["case_id"] != query["case_id"]
        ]

        same_domain_candidates = [
            case
            for case in by_domain[query["domain"]]
            if case["source_case_id"] != source_id
        ]

        cross_domain_candidates = [
            case
            for case in all_cases
            if case["domain"] != query["domain"]
        ]

        selections = [
            (
                rng.sample(
                    positive_candidates,
                    min(POSITIVES_PER_SOURCE, len(positive_candidates)),
                ),
                1,
                "positive_variant",
            ),
            (
                rng.sample(
                    same_domain_candidates,
                    min(
                        HARD_NEGATIVES_PER_SOURCE,
                        len(same_domain_candidates),
                    ),
                ),
                0,
                "hard_negative_same_domain",
            ),
            (
                rng.sample(
                    cross_domain_candidates,
                    min(
                        CROSS_NEGATIVES_PER_SOURCE,
                        len(cross_domain_candidates),
                    ),
                ),
                0,
                "negative_cross_domain",
            ),
        ]

        for candidates, label, pair_type in selections:
            for candidate in candidates:
                pair_key = (
                    query["case_id"],
                    candidate["case_id"],
                )

                if pair_key in seen_pairs:
                    continue

                seen_pairs.add(pair_key)

                pairs.append(
                    make_pair(
                        query,
                        candidate,
                        label,
                        pair_type,
                    )
                )

    rng.shuffle(pairs)
    return pairs


def validate_pairs(pairs: list[dict[str, Any]]) -> None:
    """Validate labels and pair construction."""
    positives = [pair for pair in pairs if pair["label"] == 1]
    negatives = [pair for pair in pairs if pair["label"] == 0]

    if not positives or not negatives:
        raise ValueError("Both classes must be present.")

    for pair in positives:
        if (
            pair["query_source_id"]
            != pair["candidate_source_id"]
        ):
            raise ValueError("Invalid positive pair detected.")

    for pair in negatives:
        if (
            pair["query_source_id"]
            == pair["candidate_source_id"]
        ):
            raise ValueError("Invalid negative pair detected.")


def main() -> None:
    """Run M5.5 Step 2."""
    cases = load_cases(INPUT_FILE)
    pairs = generate_pairs(cases)
    validate_pairs(pairs)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            pairs,
            file,
            indent=2,
            ensure_ascii=False,
        )

    positive_count = sum(
        pair["label"] == 1 for pair in pairs
    )
    negative_count = len(pairs) - positive_count

    hard_negative_count = sum(
        pair["pair_type"] == "hard_negative_same_domain"
        for pair in pairs
    )

    print("=" * 60)
    print("BARRISTER_AI - M5.5 STEP 2")
    print("=" * 60)
    print(f"Hardened cases loaded : {len(cases)}")
    print(f"Training pairs        : {len(pairs)}")
    print(f"Positive pairs        : {positive_count}")
    print(f"Negative pairs        : {negative_count}")
    print(f"Same-domain negatives : {hard_negative_count}")
    print(f"Output file           : {OUTPUT_FILE}")
    print("=" * 60)

    if positive_count != negative_count:
        raise ValueError(
            "Expected an equal number of positive and negative pairs."
        )

    print("✅ M5.5 Step 2 validation passed")


if __name__ == "__main__":
    main()