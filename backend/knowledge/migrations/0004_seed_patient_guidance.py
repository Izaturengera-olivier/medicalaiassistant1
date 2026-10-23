"""Add patient guidance documents verified against published WHO fact sheets.

These cover the complaints patients actually ask about (TB, HIV, cholera, measles,
pneumonia, anaemia, depression, stroke, meningitis, sickle-cell disease, rabies,
burns, epilepsy, kidney disease, maternal danger signs, COPD, preterm birth).
Each passage restates what the cited page says and omits dosages, per AI_SAFETY.md.
"""

from django.db import migrations


def seed_patient_guidance(apps, schema_editor):
    from knowledge.seed_data import PATIENT_GUIDANCE_DOCUMENTS

    MedicalKnowledgeSource = apps.get_model("knowledge", "MedicalKnowledgeSource")
    KnowledgeDocument = apps.get_model("knowledge", "KnowledgeDocument")

    for seed in PATIENT_GUIDANCE_DOCUMENTS:
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
        ('knowledge', '0003_seed_knowledge_base'),
    ]

    operations = [
        migrations.RunPython(seed_patient_guidance, migrations.RunPython.noop),
    ]
