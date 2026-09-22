from django.apps import apps


def test_doctors_app_is_installed():
    assert apps.is_installed("doctors")
