from django.apps import apps


def test_knowledge_app_is_installed():
    assert apps.is_installed("knowledge")
