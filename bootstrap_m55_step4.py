"""Barrister_AI M5.5 Step 4.

Train and evaluate a hardened precedent-relevance classifier
using pairwise textual similarity features.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent

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

REPORT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "m55_hardened_classifier_report.txt"
)

RANDOM_SEED = 42


def load_dataset(file_path: Path) -> list[dict[str, Any]]:
    """Load and validate a dataset split."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list) or not data:
        raise ValueError(
            f"Expected non-empty JSON list: {file_path}"
        )

    return data


def fit_vectorizer(
    train_data: list[dict[str, Any]],
) -> TfidfVectorizer:
    """Fit TF-IDF on training documents only."""
    documents: list[str] = []

    for record in train_data:
        documents.extend(
            [
                record["query_text"],
                record["candidate_text"],
            ]
        )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=5000,
    )

    vectorizer.fit(documents)
    return vectorizer


def word_overlap(
    query_text: str,
    candidate_text: str,
) -> float:
    """Calculate Jaccard-style shared vocabulary ratio."""
    query_words = set(query_text.lower().split())
    candidate_words = set(candidate_text.lower().split())

    union = query_words | candidate_words

    if not union:
        return 0.0

    return len(query_words & candidate_words) / len(union)


def create_features(
    dataset: list[dict[str, Any]],
    vectorizer: TfidfVectorizer,
) -> tuple[np.ndarray, np.ndarray]:
    """Create pairwise numerical features and labels."""
    query_texts = [
        record["query_text"]
        for record in dataset
    ]

    candidate_texts = [
        record["candidate_text"]
        for record in dataset
    ]

    query_vectors = vectorizer.transform(query_texts)
    candidate_vectors = vectorizer.transform(candidate_texts)

    cosine_scores = np.asarray(
        query_vectors.multiply(
            candidate_vectors
        ).sum(axis=1)
    ).ravel()

    overlap_scores = np.array(
        [
            word_overlap(query, candidate)
            for query, candidate in zip(
                query_texts,
                candidate_texts,
            )
        ],
        dtype=float,
    )

    length_differences = np.array(
        [
            abs(
                len(query.split())
                - len(candidate.split())
            )
            for query, candidate in zip(
                query_texts,
                candidate_texts,
            )
        ],
        dtype=float,
    )

    features = np.column_stack(
        [
            cosine_scores,
            overlap_scores,
            length_differences,
        ]
    )

    labels = np.array(
        [int(record["label"]) for record in dataset]
    )

    return features, labels


def build_report(
    y_true: np.ndarray,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    features: np.ndarray,
) -> str:
    """Build the model evaluation report."""
    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    positive_similarity = features[y_true == 1, 0]
    negative_similarity = features[y_true == 0, 0]

    return "\n".join(
        [
            "=" * 60,
            "BARRISTER_AI - M5.5 HARDENED CLASSIFIER",
            "=" * 60,
            f"Accuracy  : {accuracy_score(y_true, predictions):.4f}",
            f"Precision : {precision_score(y_true, predictions):.4f}",
            f"Recall    : {recall_score(y_true, predictions):.4f}",
            f"F1-score  : {f1_score(y_true, predictions):.4f}",
            f"ROC-AUC   : {roc_auc_score(y_true, probabilities):.4f}",
            "",
            "Average Cosine Similarity",
            f"Relevant     : {positive_similarity.mean():.4f}",
            f"Not relevant : {negative_similarity.mean():.4f}",
            "",
            "Confusion Matrix",
            f"True negatives  : {matrix[0, 0]}",
            f"False positives : {matrix[0, 1]}",
            f"False negatives : {matrix[1, 0]}",
            f"True positives  : {matrix[1, 1]}",
            "",
            "Classification Report",
            classification_report(
                y_true,
                predictions,
                target_names=[
                    "Not Relevant",
                    "Relevant",
                ],
                digits=4,
                zero_division=0,
            ),
        ]
    )


def main() -> None:
    """Train and evaluate the hardened classifier."""
    train_data = load_dataset(TRAIN_FILE)
    test_data = load_dataset(TEST_FILE)

    vectorizer = fit_vectorizer(train_data)

    x_train, y_train = create_features(
        train_data,
        vectorizer,
    )

    x_test, y_test = create_features(
        test_data,
        vectorizer,
    )

    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_SEED,
    )

    model.fit(x_train, y_train)

    predictions = model.predict(x_test_scaled)
    probabilities = model.predict_proba(
        x_test_scaled
    )[:, 1]

    report = build_report(
        y_test,
        predictions,
        probabilities,
        x_test,
    )

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_FILE.write_text(
        report,
        encoding="utf-8",
    )

    print(report)
    print(f"Report saved to: {REPORT_FILE}")
    print("=" * 60)
    print("✅ M5.5 Step 4 validation passed")


if __name__ == "__main__":
    main()