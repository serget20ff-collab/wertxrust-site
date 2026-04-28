from django.db import migrations


PRIVACY_TEXT = (
    'Сайт использует файлы cookie для авторизации через Steam, работы личного '
    'кабинета, безопасности, обработки платежей и аналитики. Данные используются '
    'только для работы проекта WertxRust и связи с пользователем по вопросам '
    'аккаунта, покупок и поддержки.'
)


def ensure_privacy_document(apps, schema_editor):
    LegalDocument = apps.get_model('core', 'LegalDocument')

    LegalDocument.objects.update_or_create(
        slug='privacy',
        defaults={
            'name': 'Политика конфиденциальности',
            'title': 'Политика конфиденциальности',
            'text': PRIVACY_TEXT,
            'body': PRIVACY_TEXT,
            'is_published': True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_seed_privacy_document'),
    ]

    operations = [
        migrations.RunPython(ensure_privacy_document, migrations.RunPython.noop),
    ]
