from django.apps import apps


def test_medical_app_is_installed():
    assert apps.is_installed("medical")
