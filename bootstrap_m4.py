"""
Barrister_AI
M4 Bootstrap Script

Runs and validates the TF-IDF Legal Precedent Search Engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ml.tfidf_search import LegalPrecedentSearchEngine


PROJECT_ROOT = Path(__file__).resolve().parent

DATASET_PATH = (
    PROJECT_ROOT
    / "knowledge_base"
    / "generated"
    / "legal_cases.json"
)

REPORT_DIRECTORY = PROJECT_ROOT / "reports"
REPORT_PATH = REPORT_DIRECTORY / "m4_search_validation.json"


TEST_QUERIES = [
    {
        "name": "Cheque Bounce Search",
        "query": (
            "Cheque issued by accused was dishonoured "
            "because of insufficient funds"
        ),
        "expected_terms": [
            "cheque",
            "dishonour",
            "insufficient",
        ],
    },
    {
        "name": "Consumer Search",
        "query": (
            "Consumer purchased a defective product "
            "and seller refused replacement or refund"
        ),
        "expected_terms": [
            "consumer",
            "defective",
            "refund",
        ],
    },
    {
        "name": "Cyber Crime Search",
        "query": (
            "Victim lost money through phishing email "
            "and fraudulent online bank transaction"
        ),
        "expected_terms": [
            "cyber",
            "phishing",
            "fraud",
        ],
    },
    {
        "name": "Motor Accident Search",
        "query": (
            "Road accident caused by negligent driving "
            "resulted in bodily injury and compensation claim"
        ),
        "expected_terms": [
            "accident",
            "negligent",
            "compensation",
        ],
    },
    {
        "name": "Murder Search",
        "query": (
            "Accused intentionally caused death using "
            "a deadly weapon"
        ),
        "expected_terms": [
            "murder",
            "death",
            "weapon",
        ],
    },
]


def get_case_value(
    case: dict[str, Any],
    possible_fields: tuple[str, ...],
    default: str = "Not available",
) -> str:
    """
    Return the first usable value found among possible field names.
    """

    for field in possible_fields:
        value = case.get(field)

        if value is None:
            continue

        if isinstance(value, list):
            return ", ".join(str(item) for item in value)

        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)

        text = str(value).strip()

        if text:
            return text

    return default


def print_result(result: dict[str, Any]) -> None:
    """
    Print one ranked legal precedent.
    """

    case = result["case"]

    case_id = get_case_value(
        case,
        (
            "case_id",
            "id",
            "case_number",
            "case_no",
        ),
    )

    domain = get_case_value(
        case,
        (
            "domain",
            "category",
            "case_type",
            "legal_domain",
        ),
    )

    title = get_case_value(
        case,
        (
            "title",
            "case_title",
            "case_name",
            "name",
        ),
    )

    facts = get_case_value(
        case,
        (
            "facts",
            "case_facts",
            "summary",
            "description",
        ),
    )

    if len(facts) > 220:
        facts = facts[:217] + "..."

    print("-" * 70)
    print(f"Rank                 : {result['rank']}")
    print(f"Similarity Score     : {result['similarity_score']}")
    print(f"Similarity Percentage: {result['similarity_percentage']}%")
    print(f"Case ID              : {case_id}")
    print(f"Domain               : {domain}")
    print(f"Title                : {title}")
    print(f"Facts                : {facts}")


def run_validation(
    engine: LegalPrecedentSearchEngine,
) -> list[dict[str, Any]]:
    """
    Run predefined legal search queries and store their results.
    """

    validation_results: list[dict[str, Any]] = []

    print("\nRunning M4 Validation Queries...\n")

    for test_number, test in enumerate(TEST_QUERIES, start=1):
        query = test["query"]

        results = engine.search(
            query=query,
            top_k=3,
            minimum_score=0.0,
        )

        top_result = results[0] if results else None

        validation_record = {
            "test_number": test_number,
            "test_name": test["name"],
            "query": query,
            "expected_terms": test["expected_terms"],
            "results_returned": len(results),
            "top_similarity_score": (
                top_result["similarity_score"]
                if top_result
                else 0.0
            ),
            "top_similarity_percentage": (
                top_result["similarity_percentage"]
                if top_result
                else 0.0
            ),
            "top_case": (
                top_result["case"]
                if top_result
                else None
            ),
            "passed": bool(
                top_result
                and top_result["similarity_score"] > 0
            ),
        }

        validation_results.append(validation_record)

        status = (
            "PASSED"
            if validation_record["passed"]
            else "FAILED"
        )

        print(
            f"{test_number}. {test['name']}: {status}"
        )
        print(f"   Query: {query}")
        print(
            "   Top Similarity: "
            f"{validation_record['top_similarity_percentage']}%"
        )

        if top_result:
            domain = get_case_value(
                top_result["case"],
                (
                    "domain",
                    "category",
                    "case_type",
                    "legal_domain",
                ),
            )

            print(f"   Top Domain: {domain}")

        print()

    return validation_results


def save_validation_report(
    statistics: dict[str, Any],
    validation_results: list[dict[str, Any]],
) -> None:
    """
    Save M4 validation output as JSON.
    """

    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    tests_passed = sum(
        1
        for result in validation_results
        if result["passed"]
    )

    report = {
        "module": "M4 - TF-IDF Legal Precedent Search",
        "status": (
            "PASSED"
            if tests_passed == len(validation_results)
            else "FAILED"
        ),
        "statistics": statistics,
        "validation_summary": {
            "total_tests": len(validation_results),
            "tests_passed": tests_passed,
            "tests_failed": (
                len(validation_results) - tests_passed
            ),
        },
        "validation_results": validation_results,
    }

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )


def interactive_search(
    engine: LegalPrecedentSearchEngine,
) -> None:
    """
    Allow the user to enter legal queries from the terminal.
    """

    print("\n" + "=" * 70)
    print("BARRISTER_AI - INTERACTIVE PRECEDENT SEARCH")
    print("=" * 70)

    print(
        "\nEnter a legal problem to search for precedents."
    )
    print("Type 'exit' to close the search engine.\n")

    while True:
        query = input("Legal Query: ").strip()

        if query.lower() in {"exit", "quit", "q"}:
            print("\nSearch session closed.")
            break

        if not query:
            print("Please enter a non-empty query.\n")
            continue

        try:
            results = engine.search(
                query=query,
                top_k=5,
                minimum_score=0.0,
            )
        except ValueError as exc:
            print(f"Search error: {exc}\n")
            continue

        print(
            f"\nTop {len(results)} relevant precedents "
            f"for: \"{query}\"\n"
        )

        for result in results:
            print_result(result)

        print("-" * 70)
        print()


def main() -> None:
    """
    Execute M4 indexing, validation and interactive search.
    """

    print("=" * 70)
    print("BARRISTER_AI - M4 TF-IDF PRECEDENT SEARCH")
    print("=" * 70)

    print(f"\nDataset: {DATASET_PATH}")

    try:
        engine = LegalPrecedentSearchEngine(
            dataset_path=DATASET_PATH,
            max_features=5000,
            ngram_range=(1, 2),
        )

        print("\nLoading legal cases...")
        engine.initialize()

        statistics = engine.get_statistics()

        print(
            f"✓ Cases Loaded       : "
            f"{statistics['cases_indexed']}"
        )
        print(
            f"✓ Documents Indexed  : "
            f"{statistics['documents_created']}"
        )
        print(
            f"✓ Vocabulary Size    : "
            f"{statistics['vocabulary_size']}"
        )
        print(
            f"✓ TF-IDF Matrix      : "
            f"{statistics['matrix_rows']} x "
            f"{statistics['matrix_columns']}"
        )

        validation_results = run_validation(engine)

        save_validation_report(
            statistics=statistics,
            validation_results=validation_results,
        )

        tests_passed = sum(
            1
            for result in validation_results
            if result["passed"]
        )

        print("=" * 70)
        print("BARRISTER_AI - M4 VALIDATION SUMMARY")
        print("=" * 70)
        print(
            f"Tests Passed : "
            f"{tests_passed}/{len(validation_results)}"
        )
        print(f"Report       : {REPORT_PATH}")

        if tests_passed == len(validation_results):
            print("\n✅ M4 VALIDATION PASSED")
        else:
            print("\n⚠ M4 VALIDATION REQUIRES REVIEW")

        interactive_search(engine)

    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print("\n❌ M4 INITIALIZATION FAILED")
        print(f"Reason: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()