from django.db import models
class SiteSetting(models.Model):
    key=models.SlugField('Ключ',max_length=120,unique=True); value=models.TextField('Значение',blank=True); description=models.CharField('Описание',max_length=255,blank=True)
    class Meta: verbose_name='Настройка сайта'; verbose_name_plural='Настройки сайта'; ordering=['key']
    def __str__(self): return self.key
class LegalDocument(models.Model):
    DOCUMENT_TYPES=[('offer','Оферта'),('privacy','Политика конфиденциальности'),('refund','Возвраты'),('terms','Пользовательское соглашение')]
    doc_type=models.CharField('Тип',max_length=32,choices=DOCUMENT_TYPES,unique=True); title=models.CharField('Заголовок',max_length=255); body=models.TextField('Текст'); updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta: verbose_name='Юридический документ'; verbose_name_plural='Юридические документы'
    def __str__(self): return self.title
