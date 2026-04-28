from django.db import migrations


def seed_privacy_document(apps, schema_editor):
    LegalDocument = apps.get_model('core', 'LegalDocument')

    LegalDocument.objects.get_or_create(
        slug='privacy',
        defaults={
            'name': 'Политика конфиденциальности',
            'title': 'Политика конфиденциальности',
            'text': (
                'Сайт использует файлы cookie для авторизации через Steam, '
                'работы личного кабинета, безопасности, обработки платежей и аналитики.'
            ),
            'body': (
                'Сайт использует файлы cookie для авторизации через Steam, '
                'работы личного кабинета, безопасности, обработки платежей и аналитики.'
            ),
            'is_published': True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_seed_help_categories'),
    ]

    operations = [
        migrations.RunPython(seed_privacy_document, migrations.RunPython.noop),
    ]
