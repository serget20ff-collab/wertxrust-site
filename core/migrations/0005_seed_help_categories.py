from django.db import migrations


def seed_help_categories(apps, schema_editor):
    HelpCategory = apps.get_model('core', 'HelpCategory')

    categories = [
        ('Серверы', 'Список и статус серверов', '🎮', 10),
        ('Команды', 'Доступные игровые команды', '</>', 20),
        ('Проблемы с подключением', 'Ошибки и их решения', '≋', 30),
        ('Инвентарь', 'Описание предметов', '▣', 40),
        ('Магазин', 'Покупки и товары', '▾', 50),
        ('Услуги', 'Платные функции', '◆', 60),
        ('Блокировки после вайпа', 'Время разблокировки', '▣', 70),
    ]

    for title, subtitle, icon, sort_order in categories:
        HelpCategory.objects.get_or_create(
            title=title,
            defaults={
                'subtitle': subtitle,
                'icon': icon,
                'sort_order': sort_order,
                'is_public': True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_helpcategory_helpitem'),
    ]

    operations = [
        migrations.RunPython(seed_help_categories, migrations.RunPython.noop),
    ]
