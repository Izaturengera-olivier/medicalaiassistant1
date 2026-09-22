"""HTTP endpoints for knowledge. Implemented in later phases."""

from rest_framework import status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from .serializers import (
    MedicalKnowledgeSourceSerializer,
    KnowledgeSearchRequestSerializer,
    KnowledgeSearchResponseSerializer
)
from .services import KnowledgeService, RetrievalService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_sources(request):
    """
    List all medical knowledge sources.
    """
    try:
        knowledge_service = KnowledgeService()
        sources = knowledge_service.get_approved_sources()
        
        return Response({
            "sources": sources,
            "total": len(sources)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def add_source(request):
    """
    Add a new medical knowledge source (admin only).
    """
    serializer = MedicalKnowledgeSourceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        knowledge_service = KnowledgeService()
        source_id = knowledge_service.add_source(serializer.validated_data)
        
        return Response({
            "message": _("Source added successfully"),
            "source_id": source_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_knowledge(request):
    """
    Search medical knowledge base.
    """
    serializer = KnowledgeSearchRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        query = serializer.validated_data["query"]
        limit = serializer.validated_data["limit"]
        filter_approved = serializer.validated_data["filter_approved"]
        
        retrieval_service = RetrievalService()
        
        evidence = retrieval_service.retrieve_evidence(
            query=query,
            max_results=limit,
            apply_filter=filter_approved
        )
        
        # Extract sources used
        sources_used = list(set([e["source_name"] for e in evidence]))
        
        return Response({
            "query": query,
            "results": evidence,
            "total_results": len(evidence),
            "sources_used": sources_used
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_source_reliability(request, source_id: str):
    """
    Check the reliability of a specific source.
    """
    try:
        retrieval_service = RetrievalService()
        reliability_info = retrieval_service.check_source_reliability(source_id)
        
        return Response(reliability_info, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
