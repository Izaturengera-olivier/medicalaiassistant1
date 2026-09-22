from django.apps import apps


def test_pharmacists_app_is_installed():
    assert apps.is_installed("pharmacists")
