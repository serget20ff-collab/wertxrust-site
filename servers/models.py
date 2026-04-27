from django.db import models
from accounts.models import SteamProfile
class RustServer(models.Model):
    name=models.CharField('Название',max_length=255); slug=models.SlugField('Slug',unique=True); description=models.TextField('Описание',blank=True)
    ip=models.CharField('IP / домен',max_length=255,blank=True); port=models.PositiveIntegerField('Порт',default=28015); connect_command=models.CharField('Команда подключения',max_length=255,blank=True)
    server_type=models.CharField('Тип',max_length=120,default='Vanilla+'); rates=models.CharField('Рейты',max_length=64,default='x2'); map_size=models.PositiveIntegerField('Размер карты',default=4000); max_players=models.PositiveIntegerField('Максимум игроков',default=200)
    wipe_schedule=models.CharField('Расписание вайпов',max_length=255,blank=True); battlemetrics_id=models.CharField('BattleMetrics ID',max_length=64,blank=True); is_public=models.BooleanField('Показывать на сайте',default=True); sort_order=models.PositiveIntegerField('Сортировка',default=100)
    created_at=models.DateTimeField('Создано',auto_now_add=True); updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta: verbose_name='Rust сервер'; verbose_name_plural='Rust серверы'; ordering=['sort_order','name']
    def __str__(self): return self.name
class ServerSnapshot(models.Model):
    server=models.ForeignKey(RustServer,on_delete=models.CASCADE,related_name='snapshots'); online_players=models.PositiveIntegerField('Онлайн',default=0); queued_players=models.PositiveIntegerField('Очередь',default=0); max_players=models.PositiveIntegerField('Макс игроков',default=0); map_name=models.CharField('Карта',max_length=255,blank=True); wipe_at=models.DateTimeField('Последний/следующий вайп',null=True,blank=True); raw_payload=models.JSONField('Сырой ответ API',default=dict,blank=True); created_at=models.DateTimeField('Создано',auto_now_add=True)
    class Meta: verbose_name='Снепшот сервера'; verbose_name_plural='Снепшоты серверов'; ordering=['-created_at']
class PlayerServerStat(models.Model):
    profile=models.ForeignKey(SteamProfile,on_delete=models.CASCADE,related_name='server_stats'); server=models.ForeignKey(RustServer,on_delete=models.CASCADE,related_name='player_stats'); kills=models.PositiveIntegerField('Убийства',default=0); deaths=models.PositiveIntegerField('Смерти',default=0); playtime_minutes=models.PositiveIntegerField('Минуты в игре',default=0); last_seen_on_server=models.DateTimeField('Последний раз на сервере',null=True,blank=True); updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta: verbose_name='Статистика игрока'; verbose_name_plural='Статистика игроков'; unique_together=('profile','server')
