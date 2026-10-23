from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.permissions import IsAdminUser, IsAdminUserOrReadOnly
from .models import KnowledgeDocument, MedicalKnowledgeSource
from .serializers import (
    KnowledgeDocumentSerializer,
    MedicalKnowledgeSourceSerializer,
    KnowledgeSearchRequestSerializer,
    KnowledgeSearchResponseSerializer
)
from .services import KnowledgeService, RetrievalService, ensure_seed_data


class MedicalKnowledgeSourceViewSet(viewsets.ModelViewSet):
    """Full CRUD viewset for MedicalKnowledgeSource (Admin full access, safe methods for authenticated users)."""

    queryset = MedicalKnowledgeSource.objects.all()
    serializer_class = MedicalKnowledgeSourceSerializer
    permission_classes = [IsAdminUserOrReadOnly]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_sources(request):
    """
    List all medical knowledge sources.
    """
    try:
        sources = MedicalKnowledgeSource.objects.all()
        if not sources.exists():
            # Seed the approved starter corpus into the DB if empty
            ensure_seed_data()
            sources = MedicalKnowledgeSource.objects.all()

        if request.user.role != "ADMIN":
            sources = sources.filter(approval_status="approved")

        serializer = MedicalKnowledgeSourceSerializer(sources, many=True)
        return Response({
            "sources": serializer.data,
            "total": sources.count()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def add_source(request):
    """
    Add a new medical knowledge source (admin only).
    """
    serializer = MedicalKnowledgeSourceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    source = serializer.save()
    return Response({
        "message": _("Source added successfully"),
        "source": MedicalKnowledgeSourceSerializer(source).data
    }, status=status.HTTP_201_CREATED)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_source(request, pk):
    """Update source details or approval status (admin only)."""
    try:
        source = MedicalKnowledgeSource.objects.get(pk=pk)
    except MedicalKnowledgeSource.DoesNotExist:
        return Response({"error": _("Source not found")}, status=status.HTTP_404_NOT_FOUND)

    serializer = MedicalKnowledgeSourceSerializer(source, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if "approval_status" in request.data:
        source.last_verified_date = timezone.now().date()

    source = serializer.save()
    return Response(MedicalKnowledgeSourceSerializer(source).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_source(request, pk):
    """Delete a medical knowledge source (admin only)."""
    try:
        source = MedicalKnowledgeSource.objects.get(pk=pk)
        source.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except MedicalKnowledgeSource.DoesNotExist:
        return Response({"error": _("Source not found")}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def sync_knowledge_base(request):
    """Report what retrieval can currently search.

    Retrieval reads the approved corpus straight from the database, so there is
    no separate index to rebuild; this endpoint tells the admin how much material
    is live and re-seeds the corpus if the tables are still empty.
    """
    if not MedicalKnowledgeSource.objects.exists():
        ensure_seed_data()

    sources = MedicalKnowledgeSource.objects.values_list("approval_status", flat=True)
    approved_count = sum(1 for status in sources if status == "approved")
    document_count = KnowledgeDocument.objects.filter(
        is_active=True, source__approval_status="approved"
    ).count()
    return Response({
        "message": _(
            "Retrieval is live: %(documents)d approved documents across %(sources)d approved sources."
        ) % {"documents": document_count, "sources": approved_count},
        "approved_sources_synced": approved_count,
        "approved_documents_synced": document_count,
        "timestamp": timezone.now().isoformat()
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """List the guidance documents retrieval can search, with their source."""
    source_id = request.query_params.get("source")
    documents = KnowledgeDocument.objects.select_related("source")
    if source_id:
        documents = documents.filter(source_id=source_id)
    return Response({
        "documents": KnowledgeDocumentSerializer(documents, many=True).data,
        "total": documents.count(),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def add_document(request):
    """Add guidance text from an approved source (admin only)."""
    serializer = KnowledgeDocumentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    document = serializer.save()
    return Response({
        "message": _("Document added to the knowledge base"),
        "document": KnowledgeDocumentSerializer(document).data,
    }, status=status.HTTP_201_CREATED)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_document(request, pk):
    """Correct or retire a knowledge document (admin only)."""
    try:
        document = KnowledgeDocument.objects.get(pk=pk)
    except KnowledgeDocument.DoesNotExist:
        return Response({"error": _("Document not found")}, status=status.HTTP_404_NOT_FOUND)

    serializer = KnowledgeDocumentSerializer(document, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(KnowledgeDocumentSerializer(serializer.save()).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_document(request, pk):
    """Delete a knowledge document (admin only)."""
    deleted, _count = KnowledgeDocument.objects.filter(pk=pk).delete()
    if not deleted:
        return Response({"error": _("Document not found")}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)


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
        sources_used = list(set([e["source_name"] for e in evidence]))
        
        return Response({
            "query": query,
            "results": evidence,
            "total_results": len(evidence),
            "sources_used": sources_used
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

