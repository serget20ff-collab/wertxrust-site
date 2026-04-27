from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class SteamProfile(models.Model):
    steam_id = models.CharField('Steam ID64', max_length=32, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='steam_profile')
    nickname = models.CharField('Ник Steam', max_length=255, blank=True)
    profile_url = models.URLField('Профиль Steam', blank=True)
    avatar_small = models.URLField('Аватар маленький', blank=True)
    avatar_medium = models.URLField('Аватар средний', blank=True)
    avatar_full = models.URLField('Аватар полный', blank=True)
    real_name = models.CharField('Реальное имя Steam', max_length=255, blank=True)
    country_code = models.CharField('Страна', max_length=8, blank=True)
    persona_state = models.IntegerField('Steam статус', default=0)
    first_seen_at = models.DateTimeField('Первый вход', auto_now_add=True)
    last_seen_at = models.DateTimeField('Последний вход', null=True, blank=True)
    last_known_ip = models.GenericIPAddressField('Последний IP', null=True, blank=True)
    last_user_agent = models.TextField('Последний User-Agent', blank=True)
    is_project_staff = models.BooleanField('Сотрудник проекта', default=False)
    is_banned_on_site = models.BooleanField('Бан на сайте', default=False)
    ban_reason = models.TextField('Причина бана', blank=True)
    notes = models.TextField('Внутренние заметки', blank=True)
    class Meta:
        verbose_name='Steam профиль'; verbose_name_plural='Steam профили'; ordering=['-last_seen_at','-first_seen_at']
    def __str__(self): return f'{self.nickname or "Unknown"} ({self.steam_id})'
    def touch_login(self, ip=None, user_agent=''):
        self.last_seen_at=timezone.now()
        if ip: self.last_known_ip=ip
        if user_agent: self.last_user_agent=user_agent[:2000]
        self.save(update_fields=['last_seen_at','last_known_ip','last_user_agent'])

class SteamLoginEvent(models.Model):
    profile=models.ForeignKey(SteamProfile,on_delete=models.CASCADE,related_name='login_events',null=True,blank=True)
    steam_id=models.CharField('Steam ID64',max_length=32,blank=True,db_index=True)
    ip_address=models.GenericIPAddressField('IP',null=True,blank=True)
    user_agent=models.TextField('User-Agent',blank=True)
    success=models.BooleanField('Успешно',default=False)
    reason=models.CharField('Причина/статус',max_length=255,blank=True)
    created_at=models.DateTimeField('Дата',auto_now_add=True)
    class Meta:
        verbose_name='Вход Steam'; verbose_name_plural='История входов Steam'; ordering=['-created_at']
    def __str__(self): return f'{self.steam_id or "unknown"} / {self.created_at:%Y-%m-%d %H:%M}'

class PlayerAdminNote(models.Model):
    profile=models.ForeignKey(SteamProfile,on_delete=models.CASCADE,related_name='admin_notes')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    title=models.CharField('Заголовок',max_length=255)
    body=models.TextField('Текст')
    created_at=models.DateTimeField('Создано',auto_now_add=True)
    class Meta:
        verbose_name='Заметка по игроку'; verbose_name_plural='Заметки по игрокам'; ordering=['-created_at']
    def __str__(self): return self.title
