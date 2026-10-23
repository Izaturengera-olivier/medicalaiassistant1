"""Move the starter corpus out of Python literals and into the database.

Before this, the sources and documents the AI could cite lived only inside
KnowledgeService, so nothing an admin approved in the Sources screen was ever
searchable.
"""

from django.db import migrations


def seed_knowledge_base(apps, schema_editor):
    from knowledge.seed_data import BASE_DOCUMENTS as DEFAULT_DOCUMENTS
    from knowledge.seed_data import DEFAULT_SOURCES

    MedicalKnowledgeSource = apps.get_model("knowledge", "MedicalKnowledgeSource")
    KnowledgeDocument = apps.get_model("knowledge", "KnowledgeDocument")

    for seed in DEFAULT_SOURCES:
        key = seed["id"]
        # An install may already hold the source under a name-derived key, so
        # match on the key first and only then adopt the seed key.
        source = (
            MedicalKnowledgeSource.objects.filter(source_key=key).first()
            or MedicalKnowledgeSource.objects.filter(name=seed["name"]).first()
        )
        if source is None:
            source = MedicalKnowledgeSource.objects.create(
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

    for seed in DEFAULT_DOCUMENTS:
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


def unseed_knowledge_base(apps, schema_editor):
    """Leave rows in place: retiring approved clinical guidance is a human call."""


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0002_medicalknowledgesource_source_key_knowledgedocument'),
    ]

    operations = [
        migrations.RunPython(seed_knowledge_base, unseed_knowledge_base),
    ]
