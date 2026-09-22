from django.urls import path
from .views import list_sources, add_source, search_knowledge, check_source_reliability

urlpatterns = [
    path("sources/", list_sources, name="list_sources"),
    path("sources/add/", add_source, name="add_source"),
    path("search/", search_knowledge, name="search_knowledge"),
    path("sources/<str:source_id>/reliability/", check_source_reliability, name="check_source_reliability"),
]
