from django.apps import apps


def test_audit_app_is_installed():
    assert apps.is_installed("audit")
