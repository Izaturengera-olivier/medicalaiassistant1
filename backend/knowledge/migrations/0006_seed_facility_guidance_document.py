"""Seed the approved document that says where care actually happens in Rwanda.

Until this, nothing in the corpus answered "which hospital", so a question about
facilities could only produce disease guidance.
"""

from django.db import migrations


def seed_facility_guidance(apps, schema_editor):
    from knowledge.seed_data import PATIENT_GUIDANCE_DOCUMENTS

    MedicalKnowledgeSource = apps.get_model("knowledge", "MedicalKnowledgeSource")
    KnowledgeDocument = apps.get_model("knowledge", "KnowledgeDocument")

    for seed in PATIENT_GUIDANCE_DOCUMENTS:
        if seed["id"] != "doc_39":
            continue
        source = MedicalKnowledgeSource.objects.filter(source_key=seed["source_id"]).first()
        if source is None:
            continue
        KnowledgeDocument.objects.update_or_create(
            document_key=seed["id"],
            defaults={
                "source": source,
                "title": seed["title"],
                "content": seed["content"],
                "url": seed.get("url", ""),
                "is_active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('knowledge', '0005_healthfacility'),
    ]

    operations = [
        migrations.RunPython(seed_facility_guidance, migrations.RunPython.noop),
    ]
