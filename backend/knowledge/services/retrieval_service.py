"""Service for medical knowledge retrieval and evidence gathering."""

import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ..retrievers import MockMedicalRetriever, VectorSearchRetriever, ApprovedSourceFilter
from core.glossary import expand_query
from .knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving medical evidence from approved sources."""

    # Long enough for the model to ground an answer, short enough to keep the
    # prompt within a free-tier per-minute budget. Measured: every approved
    # KnowledgeDocument in the corpus is 241-995 characters, so 1600 never clips
    # an approved passage, while live web-search passages (which arrive up to 4000
    # characters) are bounded instead of flooding the prompt.
    EVIDENCE_CONTENT_CHARS = 1600

    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.approved_source_filter = ApprovedSourceFilter(
            self._get_approved_source_ids()
        )

    def _get_approved_source_ids(self) -> List[str]:
        """Get list of approved source IDs."""
        approved_sources = self.knowledge_service.get_approved_sources()
        return [source.get("id") for source in approved_sources]

    def retrieve_evidence(
        self,
        query: str,
        max_results: int = 8,
        apply_filter: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve medical evidence based on query.
        
        Args:
            query: Medical query
            max_results: Maximum number of results
            apply_filter: Whether to filter by approved sources only
            
        Returns:
            List of retrieved evidence with metadata
        """
        # Search the local approved corpus first, then optionally search approved
        # medical domains through the configured web-search provider.
        # Kinyarwanda questions are expanded with their English terms first: every
        # approved source publishes in English, so the raw question would match nothing.
        search_query = expand_query(query)
        documents = self.knowledge_service.search_knowledge(search_query, limit=max_results)
        documents.extend(self._search_web(search_query, max_results=max_results))

        # Apply approved source filter if requested
        if apply_filter:
            documents = self.approved_source_filter.filter(documents)

        # Rank results by relevance
        ranked_documents = self.knowledge_service.retriever.rank(search_query, documents)
        
        # Format as evidence
        evidence = []
        for doc in ranked_documents:
            evidence.append({
                "document_id": doc.get("id"),
                "title": doc.get("title"),
                "content": doc.get("content"),
                "source_id": doc.get("source_id"),
                "source_name": self._get_source_name(doc.get("source_id")),
                "source_type": self._get_source_type(doc.get("source_id")),
                "url": doc.get("url"),
                "relevance_score": doc.get("relevance_score", 0),
                "metadata": doc.get("metadata", {})
            })
        
        return evidence

    def _search_web(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Ask the live search providers, in configured order, for trusted pages.

        The first provider that returns usable results wins, so a Google quota or
        outage falls through to Tavily instead of quietly dropping the citations.
        Nothing is returned when no provider is configured, which keeps offline
        and test runs free of network calls.
        """
        configured_domains = getattr(settings, "WEB_SEARCH_ALLOWED_DOMAINS", [])
        allowed_domains = [host for host in map(self._normalise_host, configured_domains) if host]
        if not allowed_domains:
            logger.warning(
                "WEB_SEARCH_ALLOWED_DOMAINS is empty; live trusted search is disabled "
                "because every result would be unverified."
            )
            return []

        providers = [
            provider.strip().lower()
            for provider in str(getattr(settings, "WEB_SEARCH_PROVIDER", "")).split(",")
            if provider.strip()
        ]
        for provider in providers:
            if provider == "google":
                documents = self._search_google(query, max_results, allowed_domains)
            elif provider == "tavily":
                documents = self._search_tavily(query, max_results, allowed_domains)
            else:
                logger.warning(
                    "WEB_SEARCH_PROVIDER=%r is not supported; expected google or tavily.",
                    provider,
                )
                continue
            if documents:
                return documents
        return []

    @staticmethod
    def _normalise_host(value: Any) -> str:
        """Lower-case a host or configured domain, without its www. label."""
        host = str(value or "").strip().lower().rstrip(".")
        return host[4:] if host.startswith("www.") else host

    @classmethod
    def _url_is_trusted(cls, url: str, allowed_domains: List[str]) -> bool:
        """True only for the allow-listed publishers themselves and their subdomains.

        A substring test would accept "who.int.evil.example", so the comparison is
        made against the parsed hostname with a label boundary enforced.
        """
        hostname = cls._normalise_host(urlparse(url).hostname)
        return bool(hostname) and any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in allowed_domains
        )

    def _search_google(self, query: str, max_results: int,
                       allowed_domains: List[str]) -> List[Dict[str, Any]]:
        api_key = getattr(settings, "WEB_SEARCH_GOOGLE_API_KEY", "")
        engine_id = getattr(settings, "WEB_SEARCH_GOOGLE_ENGINE_ID", "")
        if not api_key or not engine_id:
            # Debug, not warning: an unset provider is the normal state until the
            # keys are pasted, and this runs on every question.
            logger.debug(
                "Google Programmable Search needs WEB_SEARCH_GOOGLE_API_KEY and "
                "WEB_SEARCH_GOOGLE_ENGINE_ID; trying the next provider."
            )
            return []

        # Google returns at most 10 results per request.
        params = {
            "key": api_key,
            "cx": engine_id,
            "q": query[:2000],
            "num": str(min(max_results, 10)),
        }
        try:
            response = requests.get(
                getattr(settings, "WEB_SEARCH_GOOGLE_URL",
                        "https://www.googleapis.com/customsearch/v1"),
                params=params,
                timeout=getattr(settings, "WEB_SEARCH_TIMEOUT", 10),
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError, TypeError) as exc:
            logger.warning("Google Programmable Search failed: %s", exc)
            return []

        documents = []
        for position, result in enumerate(payload.get("items") or [], 1):
            url = str(result.get("link") or "").strip()
            title = str(result.get("title") or "").strip()
            content = str(result.get("snippet") or "").strip()
            if not url or not title or not content:
                continue
            # The engine's own scope is an admin setting outside this app; the
            # allow-list is the part the assistant actually vouches for.
            if not self._url_is_trusted(url, allowed_domains):
                logger.info("Discarded off-list Google search result: %s", url)
                continue
            documents.append({
                "id": f"web:{url}",
                "title": title,
                "content": content[:4000],
                "source_id": "web_search",
                "url": url,
                "relevance_score": max(0.9 - 0.05 * (position - 1), 0.1),
                "metadata": {
                    "retrieval_method": "live_web_search",
                    "provider": "google",
                },
            })
        return documents

    def _search_tavily(self, query: str, max_results: int,
                       allowed_domains: List[str]) -> List[Dict[str, Any]]:
        api_key = getattr(settings, "WEB_SEARCH_API_KEY", "")
        if not api_key:
            logger.debug("Tavily web search needs WEB_SEARCH_API_KEY; skipped.")
            return []

        payload = {
            "api_key": api_key,
            "query": query[:2000],
            "search_depth": "advanced",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
            "include_domains": allowed_domains,
        }
        try:
            response = requests.post(
                getattr(settings, "WEB_SEARCH_URL", "https://api.tavily.com/search"),
                json=payload,
                timeout=getattr(settings, "WEB_SEARCH_TIMEOUT", 10),
            )
            response.raise_for_status()
            results = response.json().get("results", [])
        except (requests.RequestException, ValueError, TypeError) as exc:
            logger.warning("Tavily web search failed: %s", exc)
            return []

        documents = []
        for result in results:
            url = str(result.get("url") or "").strip()
            title = str(result.get("title") or "").strip()
            content = str(result.get("content") or "").strip()
            if not url or not title or not content:
                continue
            documents.append({
                "id": f"web:{url}",
                "title": title,
                "content": content[:4000],
                "source_id": "web_search",
                "url": url,
                "relevance_score": float(result.get("score") or 0),
                "metadata": {
                    "retrieval_method": "live_web_search",
                    "provider": "tavily",
                },
            })
        return documents

    def _get_source_name(self, source_id: str) -> str:
        """Get source name by ID."""
        source = self.knowledge_service.get_source_details(source_id)
        return source.get("name", "Unknown") if source else "Unknown"

    def _get_source_type(self, source_id: str) -> str:
        """Get source type (WHO/MOH/FDA/...) by ID."""
        source = self.knowledge_service.get_source_details(source_id)
        return source.get("source_type", "") if source else ""

    def extract_key_points(self, evidence: Dict[str, Any]) -> List[str]:
        """
        Extract key points from retrieved evidence.
        
        Args:
            evidence: Evidence document
            
        Returns:
            List of key points
        """
        content = evidence.get("content", "")
        
        # Simple extraction - would use NLP in production
        # Split by sentences and return first few as key points
        sentences = [s.strip() for s in content.split(".") if s.strip()]
        
        key_points = []
        for sentence in sentences[:3]:  # Take first 3 sentences
            if len(sentence) > 20:  # Filter out very short fragments
                key_points.append(sentence)
        
        return key_points

    def format_evidence_for_ai(
        self,
        evidence_list: List[Dict[str, Any]]
    ) -> str:
        """
        Format retrieved evidence for AI consumption.
        
        Args:
            evidence_list: List of retrieved evidence
            
        Returns:
            Formatted string for AI prompt
        """
        if not evidence_list:
            return "No relevant evidence found from approved sources."

        formatted = (
            "Retrieved evidence from approved medical sources. "
            "Cite each one by its number below, e.g. [1].\n\n"
        )

        for i, evidence in enumerate(evidence_list, 1):
            content = (evidence.get("content") or "").strip()
            formatted += f"[{i}] {evidence.get('source_name') or 'Unknown'} — {evidence.get('title') or ''}\n"
            formatted += f"URL: {evidence.get('url') or ''}\n"
            formatted += f"Content: {content[:self.EVIDENCE_CONTENT_CHARS]}\n\n"

        return formatted

    def check_source_reliability(self, source_id: str) -> Dict[str, Any]:
        """
        Check the reliability and trustworthiness of a source.
        
        Args:
            source_id: Source identifier
            
        Returns:
            Dictionary with reliability information
        """
        source = self.knowledge_service.get_source_details(source_id)
        
        if not source:
            return {
                "reliable": False,
                "reason": "Source not found"
            }
        
        reliability_score = 0.5  # Base score
        
        # Bonus points for certain source types
        source_type = source.get("source_type", "")
        if source_type in ["WHO", "MOH", "FDA"]:
            reliability_score += 0.3
        elif source_type in ["HOSPITAL", "GUIDELINE"]:
            reliability_score += 0.2
        
        # Check approval status
        if source.get("approval_status") == "approved":
            reliability_score += 0.2
        elif source.get("approval_status") == "rejected":
            reliability_score -= 0.5
        
        return {
            "reliable": reliability_score >= 0.7,
            "score": reliability_score,
            "source_type": source_type,
            "approval_status": source.get("approval_status"),
            "last_verified": source.get("last_verified_date")
        }

    def get_citation_format(self, evidence: Dict[str, Any]) -> str:
        """
        Generate citation format for evidence.
        
        Args:
            evidence: Evidence document
            
        Returns:
            Formatted citation string
        """
        return f"{evidence['source_name']}. {evidence['title']}. Retrieved from {evidence['url']}"

    def batch_retrieve(
        self,
        queries: List[str],
        max_results_per_query: int = 4
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve evidence for multiple queries.
        
        Args:
            queries: List of medical queries
            max_results_per_query: Max results per query
            
        Returns:
            Dictionary mapping queries to evidence lists
        """
        results = {}
        
        for query in queries:
            evidence = self.retrieve_evidence(query, max_results=max_results_per_query)
            results[query] = evidence
        
        return results