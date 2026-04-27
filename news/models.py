from django.db import models
class NewsPost(models.Model):
    POST_TYPES=[('wipe','Вайп'),('update','Обновление'),('event','Ивент'),('sale','Акция'),('other','Другое')]
    title=models.CharField('Заголовок',max_length=255); slug=models.SlugField('Slug',unique=True); post_type=models.CharField('Тип',max_length=32,choices=POST_TYPES,default='other'); excerpt=models.CharField('Кратко',max_length=255,blank=True); body=models.TextField('Текст'); cover=models.ImageField('Обложка',upload_to='news/',blank=True); is_published=models.BooleanField('Опубликовано',default=False); published_at=models.DateTimeField('Дата публикации',null=True,blank=True); created_at=models.DateTimeField('Создано',auto_now_add=True); updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta: verbose_name='Новость'; verbose_name_plural='Новости'; ordering=['-published_at','-created_at']
    def __str__(self): return self.title
