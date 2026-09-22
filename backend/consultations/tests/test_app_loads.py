from django.apps import apps


def test_consultations_app_is_installed():
    assert apps.is_installed("consultations")
