from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny


class PublicSchemaView(SpectacularAPIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []


class PublicSwaggerView(SpectacularSwaggerView):
    permission_classes = [AllowAny]
    authentication_classes: list = []


urlpatterns = [
    path("", PublicSchemaView.as_view(), name="schema"),
    path("docs/", PublicSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
