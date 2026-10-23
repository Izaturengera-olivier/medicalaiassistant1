"""Service for managing the medical knowledge base and its approved sources.

The database is the source of truth: material an admin approves in the Sources
screen reaches the AI without a code change. The in-memory retriever is only a
read cache (and a development fallback while the knowledge tables are missing),
so scoring and approval filtering behave identically in both modes.
"""

import logging
from typing import Any, Dict, List, Optional

from django.db import DatabaseError, IntegrityError, OperationalError, ProgrammingError
from django.utils.text import slugify

from ..models import KnowledgeDocument, MedicalKnowledgeSource
from ..retrievers import MockMedicalRetriever
from ..seed_data import DEFAULT_DOCUMENTS, DEFAULT_SOURCES

logger = logging.getLogger(__name__)

# Reading the corpus fails with an Operational/Programming error when the
# knowledge tables do not exist yet (fresh checkout, migrations pending) and
# with a RuntimeError when database access is switched off, as pytest-django
# does for tests that are not marked django_db. Both mean "use the seed corpus".
_DB_UNAVAILABLE = (OperationalError, ProgrammingError, DatabaseError, RuntimeError)


def _source_key_of(seed: Dict[str, Any]) -> str:
    return seed.get("id") or seed["name"]


def ensure_seed_data() -> bool:
    """Write the starter corpus into the database.

    Idempotent and key-preserving: existing rows are matched by name or key and
    simply gain their retrieval key, so re-running it never duplicates sources.
    """
    try:
        for seed in DEFAULT_SOURCES:
            key = _source_key_of(seed)
            # Match on the key first, then the display name: an older install may
            # already hold the row under a name-derived key.
            source = (
                MedicalKnowledgeSource.objects.filter(source_key=key).first()
                or MedicalKnowledgeSource.objects.filter(name=seed["name"]).first()
            )
            if source is None:
                source = MedicalKnowledgeSource.objects.create(
                    source_key=key,
                    name=seed["name"],
                    url=seed["url"],
                    source_type=seed["source_type"],
                    approval_status=seed["approval_status"],
                    notes=seed.get("description", ""),
                )
            elif not source.source_key or source.source_key != key:
                if not MedicalKnowledgeSource.objects.filter(source_key=key).exists():
                    source.source_key = key
                    source.save(update_fields=["source_key"])

        for seed in DEFAULT_DOCUMENTS:
            source = MedicalKnowledgeSource.objects.filter(source_key=seed["source_id"]).first()
            if source is None:
                logger.warning("Skipping seed document %s: source %r is missing",
                               seed["id"], seed["source_id"])
                continue
            KnowledgeDocument.objects.update_or_create(
                document_key=seed["id"],
                defaults={
                    "source": source,
                    "title": seed["title"],
                    "content": seed["content"],
                    "url": seed.get("url", ""),
                },
            )
    except _DB_UNAVAILABLE:
        # Migrations have not been applied yet (fresh checkout, running tests).
        logger.info("Knowledge tables unavailable; leaving the seeded corpus in memory.")
        return False
    return True


class KnowledgeService:
    """Service for managing medical knowledge sources and documents."""

    def __init__(self):
        self.retriever = MockMedicalRetriever()
        self.database_available = self._load_from_database()
        if not self.database_available:
            self._load_seed_corpus()

    # ------------------------------------------------------------------ corpus

    def _load_from_database(self) -> bool:
        """Populate the retriever from approved material stored in the database."""
        try:
            sources = list(MedicalKnowledgeSource.objects.order_by("pk"))
            documents = list(
                KnowledgeDocument.objects.filter(is_active=True).select_related("source").order_by("pk")
            )
        except _DB_UNAVAILABLE:
            return False

        for source in sources:
            self.retriever.add_source(self._source_to_dict(source))
        for document in documents:
            self.retriever.add_document(self._document_to_dict(document))
        return True

    def _load_seed_corpus(self) -> None:
        for seed in DEFAULT_SOURCES:
            self.retriever.add_source({
                "id": _source_key_of(seed),
                "name": seed["name"],
                "url": seed["url"],
                "source_type": seed["source_type"],
                "approval_status": seed["approval_status"],
                "description": seed.get("description", ""),
            })
        for seed in DEFAULT_DOCUMENTS:
            self.retriever.add_document(dict(seed))

    @staticmethod
    def _source_to_dict(source: MedicalKnowledgeSource) -> Dict[str, Any]:
        return {
            "id": source.source_key,
            "name": source.name,
            "url": source.url,
            "source_type": source.source_type,
            "approval_status": source.approval_status,
            "description": source.notes,
            "last_verified_date": source.last_verified_date,
        }

    @staticmethod
    def _document_to_dict(document: KnowledgeDocument) -> Dict[str, Any]:
        return {
            "id": document.document_key,
            "title": document.title,
            "content": document.content,
            "source_id": document.source.source_key,
            "url": document.url,
        }

    def refresh(self) -> None:
        """Re-read the corpus so approvals and edits take effect immediately."""
        self.retriever = MockMedicalRetriever()
        self.database_available = self._load_from_database()
        if not self.database_available:
            self._load_seed_corpus()

    # ----------------------------------------------------------------- sources

    def add_source(self, source_data: Dict[str, Any]) -> str:
        """
        Add a new medical knowledge source.

        Args:
            source_data: Source information (name, url, source_type, etc.)

        Returns:
            Source ID
        """
        source_key = source_data.get("id") or source_data["name"]
        if self.database_available:
            try:
                source, _created = MedicalKnowledgeSource.objects.get_or_create(
                    name=source_data["name"],
                    defaults={
                        "source_key": source_key,
                        "url": source_data.get("url", ""),
                        "source_type": source_data.get("source_type", "LITERATURE"),
                        "approval_status": source_data.get("approval_status", "pending"),
                        "notes": source_data.get("description", ""),
                    },
                )
                if not source.source_key:
                    source.source_key = source_key
                    source.save(update_fields=["source_key"])
                source_key = source.source_key
            except (DatabaseError, IntegrityError) as exc:
                logger.warning("Could not persist source %s: %s", source_key, exc)

        existing = {source.get("id") for source in self.retriever.get_sources()}
        if source_key not in existing:
            self.retriever.add_source({**source_data, "id": source_key})
        return source_key

    def get_approved_sources(self) -> List[Dict[str, Any]]:
        """
        Get list of approved medical knowledge sources.

        Returns:
            List of approved sources
        """
        all_sources = self.retriever.get_sources()
        return [source for source in all_sources if source.get("approval_status") == "approved"]

    def get_source_details(self, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific source.

        Args:
            source_id: Source identifier

        Returns:
            Source details or None if not found
        """
        for source in self.retriever.get_sources():
            if source.get("id") == source_id:
                return source
        return None

    def verify_source(self, source_id: str) -> bool:
        """
        Verify if a source is approved and trustworthy.

        Args:
            source_id: Source identifier

        Returns:
            True if source is approved
        """
        sources = self.get_approved_sources()
        return any(source.get("id") == source_id for source in sources)

    def update_source_status(self, source_id: str, status: str) -> bool:
        """
        Update the approval status of a source.

        Args:
            source_id: Source identifier
            status: New status (approved, rejected, deprecated)

        Returns:
            True if update successful
        """
        if self.database_available:
            try:
                updated = MedicalKnowledgeSource.objects.filter(source_key=source_id).update(
                    approval_status=status
                )
            except DatabaseError as exc:
                logger.warning("Could not update approval status for %s: %s", source_id, exc)
                return False
            if not updated:
                return False
            self.refresh()
            return True

        for source in self.retriever.get_sources():
            if source.get("id") == source_id:
                source["approval_status"] = status
                return True
        return False

    # --------------------------------------------------------------- documents

    def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add a medical document to the knowledge base.

        A document only earns a place in the corpus when it belongs to a known
        source, so unattributable text can never be retrieved as evidence.

        Args:
            document: Document with content, title, source_id, etc.

        Returns:
            Document ID
        """
        source_id = document.get("source_id")
        source_details = self.get_source_details(source_id) if source_id else None
        if source_details is None:
            logger.warning("Rejected document %r: unknown source %r", document.get("title"), source_id)
            return ""

        document_key = document.get("id") or f"{source_id}-{slugify(document.get('title', ''))[:60]}"
        if self.database_available:
            try:
                source_pk = MedicalKnowledgeSource.objects.filter(
                    source_key=source_id
                ).values_list("pk", flat=True).first()
                if source_pk is None:
                    return ""
                KnowledgeDocument.objects.update_or_create(
                    document_key=document_key,
                    defaults={
                        "source_id": source_pk,
                        "title": document.get("title", ""),
                        "content": document.get("content", ""),
                        "url": document.get("url", ""),
                        "is_active": True,
                    },
                )
            except (DatabaseError, IntegrityError) as exc:
                logger.warning("Could not persist document %s: %s", document_key, exc)
                return ""

        stored = next((doc for doc in self.retriever.documents if doc.get("id") == document_key), None)
        payload = {**document, "id": document_key}
        if stored is None:
            self.retriever.add_document(payload)
        else:
            stored.update(payload)
        return document_key

    def list_documents(self) -> List[Dict[str, Any]]:
        """Expose the corpus the retriever is currently searching."""
        return list(self.retriever.documents)

    # ----------------------------------------------------------------- search

    def search_knowledge(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Search medical knowledge base for relevant information.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of relevant documents with relevance scores
        """
        return list(self.retriever.search(query, limit=limit))
