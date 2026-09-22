from django.apps import apps


def test_medications_app_is_installed():
    assert apps.is_installed("medications")
