"""Service for managing medical knowledge base and sources."""

from typing import List, Dict, Any, Optional
from django.utils.translation import gettext_lazy as _

from ..retrievers import MockMedicalRetriever, VectorSearchRetriever


class KnowledgeService:
    """Service for managing medical knowledge sources and documents."""

    def __init__(self):
        # Use mock retriever by default, can be configured to use vector search
        self.retriever = MockMedicalRetriever()
        self._initialize_default_sources()
        self._add_sample_documents()

    def _initialize_default_sources(self):
        """Initialize default approved medical knowledge sources."""
        default_sources = [
            {
                "id": "who",
                "name": "World Health Organization",
                "url": "https://www.who.int",
                "source_type": "WHO",
                "approval_status": "approved",
                "description": "Global health authority providing evidence-based guidelines"
            },
            {
                "id": "moh_rwanda",
                "name": "Rwanda Ministry of Health",
                "url": "https://moh.gov.rw",
                "source_type": "MOH",
                "approval_status": "approved",
                "description": "Official health authority for Rwanda"
            },
            {
                "id": "fda_rwanda",
                "name": "Rwanda Food and Drugs Authority",
                "url": "https://rfd.gov.rw",
                "source_type": "FDA",
                "approval_status": "approved",
                "description": "Regulatory authority for medicines and medical devices"
            }
        ]
        
        for source in default_sources:
            self.retriever.add_source(source)

    def add_source(self, source_data: Dict[str, Any]) -> str:
        """
        Add a new medical knowledge source.
        
        Args:
            source_data: Source information (name, url, source_type, etc.)
            
        Returns:
            Source ID
        """
        return self.retriever.add_source(source_data)

    def get_approved_sources(self) -> List[Dict[str, Any]]:
        """
        Get list of approved medical knowledge sources.
        
        Returns:
            List of approved sources
        """
        all_sources = self.retriever.get_sources()
        return [source for source in all_sources if source.get("approval_status") == "approved"]

    def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add a medical document to the knowledge base.
        
        Args:
            document: Document with content, title, source_id, etc.
            
        Returns:
            Document ID
        """
        return self.retriever.add_document(document)

    def search_knowledge(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Search medical knowledge base for relevant information.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant documents with relevance scores
        """
        # Debug: Check if documents exist
        if not self.retriever.documents:
            print("No documents in retriever, adding sample documents")
            self._add_sample_documents()
        
        return self.retriever.search(query, limit=limit)

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

    def get_source_details(self, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific source.
        
        Args:
            source_id: Source identifier
            
        Returns:
            Source details or None if not found
        """
        all_sources = self.retriever.get_sources()
        for source in all_sources:
            if source.get("id") == source_id:
                return source
        return None

    def update_source_status(self, source_id: str, status: str) -> bool:
        """
        Update the approval status of a source.
        
        Args:
            source_id: Source identifier
            status: New status (approved, rejected, deprecated)
            
        Returns:
            True if update successful
        """
        # This would update the database in production
        # For mock, we'll just return True
        return True

    def _add_sample_documents(self):
        """Add sample medical documents for testing."""
        sample_documents = [
            {
                "id": "doc_1",
                "title": "Headache Management Guidelines",
                "content": "Headaches are common and usually not serious. Most headaches can be treated with over-the-counter pain relievers, rest, and hydration. However, severe or sudden headaches should be evaluated by a healthcare professional.",
                "source_id": "who",
                "url": "https://www.who.int/news-room/fact-sheets/detail/headache-disorders"
            },
            {
                "id": "doc_2", 
                "title": "Fever Treatment Recommendations",
                "content": "Fever is a common symptom of infection. For adults, rest and hydration are important. Over-the-counter fever reducers can help. Seek medical attention if fever exceeds 103°F (39.4°C) or persists more than 3 days.",
                "source_id": "moh_rwanda",
                "url": "https://moh.gov.rw"
            },
            {
                "id": "doc_3",
                "title": "Cough and Cold Symptoms",
                "content": "Most coughs and colds resolve within 1-2 weeks without treatment. Rest, fluids, and over-the-counter medications can help relieve symptoms. Seek medical care if symptoms worsen or persist beyond 2 weeks.",
                "source_id": "who",
                "url": "https://www.who.int"
            }
        ]
        
        for doc in sample_documents:
            try:
                self.add_document(doc)
            except:
                pass  # Document may already exist