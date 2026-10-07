"""Pluggable medical retrieval interface. Implementations land in Phase 7."""

import re
from abc import ABC, abstractmethod
from typing import Any, Sequence, List, Dict
from datetime import datetime

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = frozenset({
    "the", "and", "for", "with", "have", "has", "had", "was", "were", "are", "been",
    "this", "that", "these", "those", "there", "from", "since", "about", "into",
    "when", "what", "where", "which", "whether", "would", "could", "should", "does",
    "did", "your", "her", "him", "his", "she", "they", "them", "their", "our", "you",
    "its", "not", "but", "also", "too", "very", "much", "many", "more", "most",
    "some", "any", "all", "each", "other", "than", "then", "just", "only", "like",
    "get", "got", "day", "days", "week", "weeks", "month", "months", "year", "years",
    "hour", "hours", "today", "yesterday", "feel", "feels", "feeling", "felt",
    "pain",
})


def _tokenize(text: str) -> List[str]:
    """Split text into meaningful lowercase tokens for keyword scoring."""
    return [
        token
        for token in _TOKEN_RE.findall((text or "").lower())
        if len(token) > 2 and token not in _STOPWORDS
    ]


class MedicalRetriever(ABC):
    """Abstract base class for medical knowledge retrieval systems."""
    
    @abstractmethod
    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]:
        """Search for relevant medical documents based on query."""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, source_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
        """Retrieve specific documents by their IDs."""
        raise NotImplementedError

    @abstractmethod
    def rank(self, query: str, documents: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        """Rank documents by relevance to the query."""
        raise NotImplementedError

    @abstractmethod
    def get_sources(self) -> Sequence[dict[str, Any]]:
        """Get list of available medical knowledge sources."""
        raise NotImplementedError

    @abstractmethod
    def add_document(self, document: Dict[str, Any]) -> str:
        """Add a new document to the knowledge base."""
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


class DocumentChunker:
    """Service for chunking documents for vector storage and retrieval."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Keep overlap words for context
                overlap_words = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else []
                current_chunk = overlap_words
                current_size = sum(len(w) + 1 for w in current_chunk)
            
            current_chunk.append(word)
            current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk a document into smaller pieces with metadata.
        
        Args:
            document: Document with 'content' field
            
        Returns:
            List of chunk dictionaries with metadata
        """
        content = document.get("content", "")
        chunks = self.chunk_text(content)
        
        chunked_docs = []
        for i, chunk_text in enumerate(chunks):
            chunked_docs.append({
                "id": f"{document.get('id', 'doc')}_{i}",
                "document_id": document.get("id"),
                "chunk_index": i,
                "content": chunk_text,
                "metadata": {
                    "source_id": document.get("source_id"),
                    "title": document.get("title"),
                    "url": document.get("url"),
                    "publication_date": document.get("publication_date"),
                    "chunk_count": len(chunks)
                }
            })
        
        return chunked_docs


class MockMedicalRetriever(MedicalRetriever):
    """Mock implementation of medical retriever for development/testing."""

    def __init__(self):
        self.documents = []
        self.sources = []

    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]:
        """Mock search - returns documents ranked by token overlap with the query."""
        tokens = _tokenize(query)

        scored_docs = []
        for doc in self.documents:
            score = self._score_document(tokens, doc)
            if score > 0:
                scored_docs.append({**doc, "relevance_score": score})

        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_docs[:limit]

    def retrieve(self, source_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
        """Mock retrieve - returns documents by ID."""
        return [doc for doc in self.documents if doc.get("id") in source_ids]

    def rank(self, query: str, documents: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        """Mock rank - re-scores documents by token overlap with the query."""
        tokens = _tokenize(query)

        for doc in documents:
            doc["relevance_score"] = self._score_document(tokens, doc)

        return sorted(documents, key=lambda x: x["relevance_score"], reverse=True)

    @staticmethod
    def _score_document(tokens: Sequence[str], document: Dict[str, Any]) -> int:
        """Score a document by token overlap, weighting title matches higher."""
        title_tokens = set(_tokenize(document.get("title") or ""))
        content_tokens = set(_tokenize(document.get("content") or ""))

        score = 0
        for token in tokens:
            if token in title_tokens:
                score += 2
            elif token in content_tokens:
                score += 1
        return score

    def get_sources(self) -> Sequence[dict[str, Any]]:
        """Mock get sources - returns predefined sources."""
        return self.sources

    def add_document(self, document: Dict[str, Any]) -> str:
        """Mock add document - stores in memory."""
        doc_id = document.get("id", f"doc_{len(self.documents)}")
        document["id"] = doc_id
        document["added_at"] = datetime.now().isoformat()
        self.documents.append(document)
        return doc_id

    def add_source(self, source: Dict[str, Any]) -> str:
        """Mock add source - stores in memory."""
        source_id = source.get("id", f"source_{len(self.sources)}")
        source["id"] = source_id
        self.sources.append(source)
        return source_id


class VectorSearchRetriever(MedicalRetriever):
    """
    Vector-based medical retriever using semantic search.
    This would be implemented with actual vector database (pgvector, Qdrant, etc.)
    """

    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.embedding_model = embedding_model
        self.chunker = DocumentChunker()
        # This would connect to actual vector database
        self.vector_db = None  # To be implemented

    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]:
        """Semantic search using vector embeddings."""
        # This would:
        # 1. Generate embedding for query
        # 2. Search vector database for similar documents
        # 3. Return top-k results
        raise NotImplementedError("Vector search requires vector database configuration")

    def retrieve(self, source_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
        """Retrieve documents by their IDs from vector database."""
        raise NotImplementedError("Vector search requires vector database configuration")

    def rank(self, query: str, documents: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        """Rank documents using semantic similarity."""
        # This would:
        # 1. Generate embedding for query
        # 2. Calculate similarity with document embeddings
        # 3. Return ranked results
        raise NotImplementedError("Vector search requires vector database configuration")

    def get_sources(self) -> Sequence[dict[str, Any]]:
        """Get configured medical knowledge sources."""
        # This would query the database for approved sources
        raise NotImplementedError("Vector search requires vector database configuration")

    def add_document(self, document: Dict[str, Any]) -> str:
        """Add document to vector database with chunking."""
        # This would:
        # 1. Chunk the document
        # 2. Generate embeddings for chunks
        # 3. Store in vector database
        raise NotImplementedError("Vector search requires vector database configuration")
