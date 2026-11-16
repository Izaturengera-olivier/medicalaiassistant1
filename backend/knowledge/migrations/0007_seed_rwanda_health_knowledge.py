"""Seed Rwanda public health sources and guidance documents (doc_40 to doc_48).

Adds Rwanda Biomedical Centre (RBC) and Rwanda Social Security Board (CBHI)
sources, along with national guidelines for emergency care, navigating care in
unfamiliar areas, malaria protocols, maternal/child health, TB/HIV, epidemic
protocols, pharmacy/FDA regulations, immunization, and insurance referrals.
"""

from django.db import migrations


def seed_rwanda_health_knowledge(apps, schema_editor):
    from knowledge.seed_data import DEFAULT_SOURCES, PATIENT_GUIDANCE_DOCUMENTS

    MedicalKnowledgeSource = apps.get_model("knowledge", "MedicalKnowledgeSource")
    KnowledgeDocument = apps.get_model("knowledge", "KnowledgeDocument")

    # 1. Ensure all sources exist
    for seed in DEFAULT_SOURCES:
        key = seed["id"]
        source = (
            MedicalKnowledgeSource.objects.filter(source_key=key).first()
            or MedicalKnowledgeSource.objects.filter(name=seed["name"]).first()
        )
        if source is None:
            MedicalKnowledgeSource.objects.create(
                source_key=key,
                name=seed["name"],
                url=seed["url"],
                source_type=seed["source_type"],
                approval_status=seed["approval_status"],
                notes=seed.get("description", ""),
            )
        elif source.source_key != key and not MedicalKnowledgeSource.objects.filter(source_key=key).exists():
            source.source_key = key
            source.save(update_fields=["source_key"])

    # 2. Seed documents doc_40 through doc_48
    target_ids = {f"doc_{n}" for n in range(40, 49)}
    for seed in PATIENT_GUIDANCE_DOCUMENTS:
        if seed["id"] not in target_ids:
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
        ('knowledge', '0006_seed_facility_guidance_document'),
    ]

    operations = [
        migrations.RunPython(seed_rwanda_health_knowledge, migrations.RunPython.noop),
    ]
