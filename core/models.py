from django.db import models


class LegalDocument(models.Model):
    name = models.CharField(
        'Название',
        max_length=255,
        help_text='Название документа в списке. Например: Пользовательское соглашение.',
    )

    slug = models.SlugField(
        'Slug / адрес',
        max_length=255,
        unique=True,
        help_text='Адрес документа на сайте. Например: user-agreement.',
    )

    title = models.CharField(
        'Заголовок',
        max_length=255,
        help_text='Заголовок внутри страницы документа.',
    )

    text = models.TextField(
        'Текст документа',
        blank=True,
        default='',
    )

    body = models.TextField(
        'Технический дубль текста',
        blank=True,
        default='',
        editable=False,
    )

    is_published = models.BooleanField(
        'Опубликован',
        default=True,
    )

    created_at = models.DateTimeField(
        'Создано',
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        'Обновлено',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.text = self.text or ''
        self.body = self.text
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HelpCategory(models.Model):
    title = models.CharField('Название', max_length=255)
    subtitle = models.CharField('Подпись', max_length=255, blank=True)
    icon = models.CharField(
        'Иконка',
        max_length=32,
        blank=True,
        help_text='Короткий текст или emoji. Например: ⚙, </>, $',
    )
    sort_order = models.PositiveIntegerField('Сортировка', default=100)
    is_public = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Категория помощи'
        verbose_name_plural = 'Категории помощи'
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title


class HelpItem(models.Model):
    category = models.ForeignKey(
        HelpCategory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Категория',
    )
    title = models.CharField('Вопрос / заголовок', max_length=255)
    body = models.TextField('Ответ / описание')
    sort_order = models.PositiveIntegerField('Сортировка', default=100)
    is_public = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Пункт помощи'
        verbose_name_plural = 'Пункты помощи'
        ordering = ['category__sort_order', 'sort_order', 'title']

    def __str__(self):
        return self.title