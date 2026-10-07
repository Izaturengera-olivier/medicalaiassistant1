from django.urls import path
from .views import (
    list_sources,
    add_source,
    update_source,
    delete_source,
    sync_knowledge_base,
    search_knowledge,
    check_source_reliability,
)

urlpatterns = [
    path("sources/", list_sources, name="list_sources"),
    path("sources/add/", add_source, name="add_source"),
    path("sources/sync/", sync_knowledge_base, name="sync_knowledge_base"),
    path("sources/<int:pk>/", update_source, name="update_source"),
    path("sources/<int:pk>/delete/", delete_source, name="delete_source"),
    path("search/", search_knowledge, name="search_knowledge"),
    path("sources/<str:source_id>/reliability/", check_source_reliability, name="check_source_reliability"),
]

