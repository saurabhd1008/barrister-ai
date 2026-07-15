"""
Barrister_AI
M4: TF-IDF Legal Precedent Search Engine

This module:
1. Loads legal cases from JSON.
2. Combines important textual fields.
3. Converts legal text into TF-IDF vectors.
4. Converts a user query into a TF-IDF vector.
5. Uses cosine similarity to rank precedents.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LegalPrecedentSearchEngine:
    """
    TF-IDF-based search engine for retrieving relevant legal precedents.
    """

    DEFAULT_TEXT_FIELDS = (
        "title",
        "case_title",
        "case_name",
        "facts",
        "case_facts",
        "summary",
        "description",
        "legal_issue",
        "issue",
        "judgment",
        "decision",
        "reasoning",
        "keywords",
        "acts",
        "sections",
        "domain",
        "category",
    )

    def __init__(
        self,
        dataset_path: str | Path,
        max_features: int = 5000,
        ngram_range: tuple[int, int] = (1, 2),
    ) -> None:
        """
        Initialize the search engine.

        Args:
            dataset_path:
                Path to legal_cases.json.

            max_features:
                Maximum number of TF-IDF vocabulary features.

            ngram_range:
                (1, 2) means the vectorizer learns:
                - individual words: "cheque"
                - two-word phrases: "cheque bounce"
        """

        self.dataset_path = Path(dataset_path)
        self.max_features = max_features
        self.ngram_range = ngram_range

        self.cases: list[dict[str, Any]] = []
        self.documents: list[str] = []

        self.vectorizer: TfidfVectorizer | None = None
        self.case_matrix = None

    def load_cases(self) -> list[dict[str, Any]]:
        """
        Load legal cases from the JSON dataset.

        Supports:
        - A direct JSON list
        - A dictionary containing a list under keys such as:
          cases, legal_cases, data, records
        """

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path.resolve()}"
            )

        try:
            with self.dataset_path.open("r", encoding="utf-8") as file:
                raw_data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Dataset contains invalid JSON: {self.dataset_path}"
            ) from exc

        if isinstance(raw_data, list):
            cases = raw_data

        elif isinstance(raw_data, dict):
            cases = self._extract_case_list(raw_data)

        else:
            raise ValueError(
                "Unsupported JSON structure. "
                "The dataset must contain a list or dictionary."
            )

        valid_cases = [case for case in cases if isinstance(case, dict)]

        if not valid_cases:
            raise ValueError("No valid legal case records were found.")

        self.cases = valid_cases
        return self.cases

    @staticmethod
    def _extract_case_list(raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract a list of cases from a dictionary-based JSON structure.
        """

        common_keys = (
            "cases",
            "legal_cases",
            "data",
            "records",
            "documents",
        )

        for key in common_keys:
            value = raw_data.get(key)

            if isinstance(value, list):
                return value

        # Fallback: locate the first list containing dictionaries.
        for value in raw_data.values():
            if (
                isinstance(value, list)
                and value
                and isinstance(value[0], dict)
            ):
                return value

        raise ValueError(
            "Could not locate a legal-case list inside the JSON file."
        )

    def build_documents(self) -> list[str]:
        """
        Convert each legal case into one searchable text document.

        The method combines important case fields such as:
        title, facts, issue, judgment, domain and keywords.
        """

        if not self.cases:
            raise RuntimeError(
                "Cases have not been loaded. Call load_cases() first."
            )

        self.documents = [
            self._case_to_searchable_text(case)
            for case in self.cases
        ]

        if not any(document.strip() for document in self.documents):
            raise ValueError(
                "The legal cases do not contain searchable text."
            )

        return self.documents

    def _case_to_searchable_text(self, case: dict[str, Any]) -> str:
        """
        Combine available legal fields into one normalized document.
        """

        text_parts: list[str] = []

        # First, prioritize known legal-text fields.
        for field in self.DEFAULT_TEXT_FIELDS:
            if field in case:
                normalized_value = self._normalize_value(case[field])

                if normalized_value:
                    text_parts.append(normalized_value)

        # Fallback for unexpected schemas:
        # add other string/list values not already captured.
        if not text_parts:
            for value in case.values():
                normalized_value = self._normalize_value(value)

                if normalized_value:
                    text_parts.append(normalized_value)

        return " ".join(text_parts).strip()

    @staticmethod
    def _normalize_value(value: Any) -> str:
        """
        Convert strings, lists and simple dictionaries into searchable text.
        """

        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, (int, float, bool)):
            return str(value)

        if isinstance(value, list):
            return " ".join(
                LegalPrecedentSearchEngine._normalize_value(item)
                for item in value
                if item is not None
            ).strip()

        if isinstance(value, dict):
            return " ".join(
                LegalPrecedentSearchEngine._normalize_value(item)
                for item in value.values()
                if item is not None
            ).strip()

        return ""

    def fit(self) -> None:
        """
        Train the TF-IDF vectorizer on the legal case documents.
        """

        if not self.documents:
            raise RuntimeError(
                "Documents have not been built. "
                "Call build_documents() first."
            )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            sublinear_tf=True,
        )

        self.case_matrix = self.vectorizer.fit_transform(
            self.documents
        )

        if self.case_matrix.shape[1] == 0:
            raise ValueError(
                "TF-IDF vocabulary is empty. "
                "Check whether the cases contain valid text."
            )

    def initialize(self) -> None:
        """
        Run the complete indexing pipeline.
        """

        self.load_cases()
        self.build_documents()
        self.fit()

    def search(
        self,
        query: str,
        top_k: int = 5,
        minimum_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Search for legal precedents relevant to a natural-language query.

        Args:
            query:
                Legal problem or search sentence.

            top_k:
                Maximum number of results returned.

            minimum_score:
                Exclude results below this cosine-similarity score.

        Returns:
            A ranked list of matching legal cases.
        """

        if self.vectorizer is None or self.case_matrix is None:
            raise RuntimeError(
                "Search engine is not initialized. "
                "Call initialize() first."
            )

        cleaned_query = query.strip()

        if not cleaned_query:
            raise ValueError("Search query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_vector = self.vectorizer.transform([cleaned_query])

        similarity_scores = cosine_similarity(
            query_vector,
            self.case_matrix,
        ).flatten()

        ranked_indices = np.argsort(similarity_scores)[::-1]

        results: list[dict[str, Any]] = []

        for index in ranked_indices:
            score = float(similarity_scores[index])

            if score < minimum_score:
                continue

            case = self.cases[int(index)]

            result = {
                "rank": len(results) + 1,
                "similarity_score": round(score, 4),
                "similarity_percentage": round(score * 100, 2),
                "case": case,
            }

            results.append(result)

            if len(results) >= min(top_k, len(self.cases)):
                break

        return results

    def get_statistics(self) -> dict[str, Any]:
        """
        Return index and TF-IDF model statistics.
        """

        if self.vectorizer is None or self.case_matrix is None:
            raise RuntimeError(
                "Search engine is not initialized."
            )

        return {
            "cases_indexed": len(self.cases),
            "documents_created": len(self.documents),
            "vocabulary_size": len(
                self.vectorizer.get_feature_names_out()
            ),
            "matrix_rows": self.case_matrix.shape[0],
            "matrix_columns": self.case_matrix.shape[1],
            "ngram_range": self.ngram_range,
        }