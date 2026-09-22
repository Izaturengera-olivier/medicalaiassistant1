"""Pluggable medical retrieval interface. Implementations land in Phase 7."""

from abc import ABC, abstractmethod
from typing import Any, Sequence


class MedicalRetriever(ABC):
    @abstractmethod
    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, source_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def rank(self, query: str, documents: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_sources(self) -> Sequence[dict[str, Any]]:
        raise NotImplementedError


class ApprovedSourceFilter:
    """Rejects evidence that is not on the admin-managed allow-list."""

    def __init__(self, allowed_source_ids: Sequence[str]):
        self.allowed_source_ids = set(allowed_source_ids)

    def filter(self, documents: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            document
            for document in documents
            if document.get("source_id") in self.allowed_source_ids
        ]


class MockMedicalRetriever(MedicalRetriever):
    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]:
        return []

    def retrieve(self, source_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
        return []

    def rank(self, query: str, documents: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        return list(documents)

    def get_sources(self) -> Sequence[dict[str, Any]]:
        return []
