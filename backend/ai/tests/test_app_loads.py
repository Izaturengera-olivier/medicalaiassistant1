from django.apps import apps


def test_ai_app_is_installed():
    assert apps.is_installed("ai")
