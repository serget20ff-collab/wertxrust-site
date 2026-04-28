from django.db import models
class RuleSection(models.Model):
    SECTION_TYPES=[('server','Сервер'),('discord','Discord'),('shop','Магазин'),('legal','Юридическое')]
    title=models.CharField('Название',max_length=255); section_type=models.CharField('Тип',max_length=32,choices=SECTION_TYPES,default='server'); description=models.TextField('Описание',blank=True); sort_order=models.PositiveIntegerField('Сортировка',default=100); is_public=models.BooleanField('Показывать',default=True)
    class Meta: verbose_name='Раздел правил'; verbose_name_plural='Разделы правил'; ordering=['sort_order','title']
    def __str__(self): return self.title
class RuleItem(models.Model):
    section=models.ForeignKey(RuleSection,on_delete=models.CASCADE,related_name='items'); code=models.CharField('Номер/код',max_length=32,blank=True); title=models.CharField('Заголовок',max_length=255); body=models.TextField('Текст правила'); note=models.TextField('Примечание',blank=True); punishment=models.CharField('Наказание',max_length=255,blank=True); sort_order=models.PositiveIntegerField('Сортировка',default=100); is_public=models.BooleanField('Показывать',default=True)
    class Meta: verbose_name='Правило'; verbose_name_plural='Правила'; ordering=['section__sort_order','sort_order','id']
    def __str__(self): return f'{self.code} {self.title}'.strip()
