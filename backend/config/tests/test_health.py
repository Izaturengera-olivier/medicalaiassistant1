from django.urls import reverse
from rest_framework.test import APIClient


def test_health_endpoint_is_public():
    client = APIClient()
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.data["status"] == "ok"
    assert response.data["phase"] == 1
