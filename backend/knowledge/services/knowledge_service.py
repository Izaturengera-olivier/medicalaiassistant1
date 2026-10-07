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
            },
            {
                "id": "web_search",
                "name": "Approved medical web search",
                "url": "https://tavily.com",
                "source_type": "LITERATURE",
                "approval_status": "approved",
                "description": "Live results restricted to configured medical domains"
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
        """Seed the in-memory corpus used by the mock retriever.

        Placeholder for real source ingestion (crawl/ingest approved sources
        into the database). Content is generic public-health guidance only.
        """
        sample_documents = [
            {
                "id": "doc_1",
                "title": "Headache Management Guidelines",
                "content": "Headaches are common and usually not serious. Most headaches can be treated with rest, hydration, and over-the-counter pain relievers. Seek care urgently if a headache is sudden and severe, follows a head injury, or comes with fever and a stiff neck.",
                "source_id": "who",
                "url": "https://www.who.int/news-room/fact-sheets/detail/headache-disorders"
            },
            {
                "id": "doc_2", 
                "title": "Fever Treatment Recommendations",
                "content": "Fever is a common symptom of infection. For adults, rest and hydration are important. Over-the-counter fever reducers can help. Seek medical attention if fever exceeds 103°F (39.4°C), lasts more than 3 days, or comes with confusion, stiff neck, or difficulty breathing.",
                "source_id": "moh_rwanda",
                "url": "https://moh.gov.rw"
            },
            {
                "id": "doc_3",
                "title": "Cough and Cold Symptoms",
                "content": "Most coughs and colds resolve within 1-2 weeks without treatment. Rest, fluids, and over-the-counter medications can help relieve symptoms. Seek medical care if symptoms worsen, if you cough up blood, or if the cough persists beyond 2 weeks.",
                "source_id": "who",
                "url": "https://www.who.int"
            },
            {
                "id": "doc_4",
                "title": "Malaria Signs and When to Seek Care",
                "content": "Malaria is common in Rwanda. Fever with chills, sweating, headache, or body pain may be malaria and needs a test at a health facility the same day. Children under five and pregnant women should be seen urgently. Do not delay treatment when fever with chills occurs.",
                "source_id": "moh_rwanda",
                "url": "https://www.who.int/news-room/fact-sheets/detail/malaria"
            },
            {
                "id": "doc_5",
                "title": "Diarrhea and Dehydration",
                "content": "Most diarrhea improves with rest and fluids. Oral rehydration salts (ORS) replace lost water and salts; zinc is recommended for children. Seek care urgently if there is blood in the stool, no urine for many hours, sunken eyes, drowsiness, or persistent vomiting.",
                "source_id": "who",
                "url": "https://www.who.int/news-room/fact-sheets/detail/diarrhoeal-disease"
            },
            {
                "id": "doc_6",
                "title": "High Blood Pressure (Hypertension)",
                "content": "High blood pressure often has no symptoms, so it is found by measuring blood pressure. Reducing salt, staying active, and taking prescribed medicines help control it. Seek emergency care for chest pain, severe headache, blurred vision, or difficulty speaking.",
                "source_id": "who",
                "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension"
            },
            {
                "id": "doc_7",
                "title": "Diabetes: Common Signs and Danger Signs",
                "content": "Diabetes can cause thirst, frequent urination, tiredness, and blurred vision. Untreated high blood sugar can lead to confusion, drowsiness, or fruity-smelling breath, which need urgent medical attention. Regular check-ups and prescribed treatment are important.",
                "source_id": "who",
                "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes"
            },
            {
                "id": "doc_8",
                "title": "Asthma and Difficulty Breathing",
                "content": "Asthma causes wheezing, cough, and shortness of breath, and is managed with prescribed inhalers. Seek emergency care immediately if you cannot speak full sentences, your lips turn blue, or breathing becomes rapid and difficult despite using your inhaler.",
                "source_id": "who",
                "url": "https://www.who.int/news-room/fact-sheets/detail/asthma"
            },
            {
                "id": "doc_9",
                "title": "Skin Rash and Itching",
                "content": "Most rashes improve with gentle skin care and by avoiding scratching. Keep the area clean and dry. Seek care if a rash comes with fever, spreads quickly, blisters, or is accompanied by difficulty breathing or swelling of the face, which may be a severe reaction.",
                "source_id": "moh_rwanda",
                "url": "https://moh.gov.rw"
            },
            {
                "id": "doc_10",
                "title": "Danger Signs in Pregnancy",
                "content": "Pregnant women should go to a health facility immediately for bleeding from the vagina, severe headache, blurred vision, swelling of the face or hands, high fever, or reduced movement of the baby. These danger signs need urgent professional care.",
                "source_id": "moh_rwanda",
                "url": "https://moh.gov.rw"
            },
            {
                "id": "doc_11",
                "title": "Back Pain Assessment and Warning Signs",
                "content": "Back pain may come from muscle strain, joints, or the spine. Gentle movement and avoiding prolonged bed rest may help some uncomplicated pain. Seek urgent care for back pain with weakness or numbness in both legs, loss of bladder or bowel control, fever, or a major injury.",
                "source_id": "who",
                "url": "https://www.who.int/news-room/fact-sheets/detail/low-back-pain"
            },
            {
                "id": "doc_12",
                "title": "Abdominal Pain Assessment and Warning Signs",
                "content": "Abdominal pain, also called stomach pain, can have many causes, including digestive illness, infection, or problems involving abdominal organs. Seek urgent care for severe or worsening pain, a rigid abdomen, repeated vomiting, blood in vomit or stool, fainting, or pregnancy with severe pain or bleeding.",
                "source_id": "who",
                "url": "https://www.who.int/health-topics/food-safety"
            },
            {
                "id": "doc_13",
                "title": "Fatigue and Tiredness Assessment",
                "content": "Fatigue or unusual tiredness can be related to poor sleep, stress, infection, anemia, medication effects, or other health conditions. Seek urgent care for severe weakness with confusion, fainting, chest pain, difficulty breathing, or sudden one-sided weakness.",
                "source_id": "who",
                "url": "https://www.who.int/health-topics/anaemia"
            }
        ]
        
        for doc in sample_documents:
            try:
                self.add_document(doc)
            except:
                pass  # Document may already exist