from django.db import migrations, models
from django.utils import timezone
from django.utils.text import slugify


def fill_legal_documents(apps, schema_editor):
    LegalDocument = apps.get_model('core', 'LegalDocument')

    used_slugs = set()

    for index, doc in enumerate(LegalDocument.objects.all().order_by('pk'), start=1):
        old_doc_type = getattr(doc, 'doc_type', '') or ''
        old_title = getattr(doc, 'title', '') or ''
        old_content = getattr(doc, 'content', '') or ''
        old_text = getattr(doc, 'text', '') or ''

        name = old_title or old_doc_type or f'Документ {index}'
        title = old_title or name
        text = old_text or old_content or ''

        base_slug_source = old_doc_type or name or f'document-{index}'
        base_slug = slugify(base_slug_source, allow_unicode=False) or f'document-{index}'

        slug = base_slug
        counter = 2

        while slug in used_slugs:
            slug = f'{base_slug}-{counter}'
            counter += 1

        used_slugs.add(slug)

        doc.name = name
        doc.slug = slug
        doc.title = title
        doc.text = text
        doc.is_published = True
        doc.created_at = timezone.now()
        doc.updated_at = timezone.now()
        doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SiteSetting',
        ),

        migrations.AddField(
            model_name='legaldocument',
            name='name',
            field=models.CharField(
                default='Документ',
                help_text='Название документа в списке. Например: Пользовательское соглашение.',
                max_length=255,
                verbose_name='Название',
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name='legaldocument',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=255,
                verbose_name='Slug / адрес',
            ),
        ),

        migrations.AddField(
            model_name='legaldocument',
            name='text',
            field=models.TextField(
                blank=True,
                verbose_name='Текст документа',
            ),
        ),

        migrations.AddField(
            model_name='legaldocument',
            name='is_published',
            field=models.BooleanField(
                default=True,
                verbose_name='Опубликован',
            ),
        ),

        migrations.AddField(
            model_name='legaldocument',
            name='created_at',
            field=models.DateTimeField(
                default=timezone.now,
                verbose_name='Создано',
            ),
        ),

        migrations.AddField(
            model_name='legaldocument',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='Обновлено',
            ),
        ),

        migrations.RunPython(fill_legal_documents, migrations.RunPython.noop),

        migrations.RemoveField(
            model_name='legaldocument',
            name='doc_type',
        ),

        migrations.AlterField(
            model_name='legaldocument',
            name='slug',
            field=models.SlugField(
                help_text='Адрес документа на сайте. Например: user-agreement.',
                max_length=255,
                unique=True,
                verbose_name='Slug / адрес',
            ),
        ),

        migrations.AlterModelOptions(
            name='legaldocument',
            options={
                'ordering': ['name'],
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документы',
            },
        ),
    ]