import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import SteamProfile


class ServerShopCategory(models.Model):
    name = models.CharField('Название', max_length=120)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Описание', blank=True)
    sort_order = models.PositiveIntegerField('Сортировка', default=100)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Внутренняя категория серверов'
        verbose_name_plural = 'Внутренние категории серверов'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class RustServer(models.Model):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Описание', blank=True)
    shop_category = models.ForeignKey(
        ServerShopCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='servers',
        verbose_name='Внутренняя категория магазина',
    )

    ip = models.CharField('IP / домен', max_length=255, blank=True)
    port = models.PositiveIntegerField('Порт', default=28015)

    server_type = models.CharField('Тип', max_length=120, default='Vanilla+')
    rates = models.CharField('Рейты', max_length=64, default='x2')
    map_size = models.PositiveIntegerField('Размер карты', default=4000)
    max_players = models.PositiveIntegerField('Максимум игроков', default=200)

    is_public = models.BooleanField('Показывать на странице серверов', default=False)
    show_on_home = models.BooleanField('Показывать на главной', default=False)

    sort_order = models.PositiveIntegerField('Сортировка', default=100)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Rust сервер'
        verbose_name_plural = 'Rust серверы'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    @property
    def connection_address(self):
        if not self.ip:
            return ''

        return f'{self.ip}:{self.port}'

    @property
    def steam_connect_url(self):
        if not self.connection_address:
            return ''

        return f'steam://connect/{self.connection_address}'


class ServerSnapshot(models.Model):
    server = models.ForeignKey(
        RustServer,
        on_delete=models.CASCADE,
        related_name='snapshots',
    )

    online_players = models.PositiveIntegerField('Онлайн', default=0)
    queued_players = models.PositiveIntegerField('Очередь', default=0)
    max_players = models.PositiveIntegerField('Макс игроков', default=0)
    map_name = models.CharField('Карта', max_length=255, blank=True)
    wipe_at = models.DateTimeField('Последний/следующий вайп', null=True, blank=True)
    raw_payload = models.JSONField('Сырой ответ API', default=dict, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Снепшот сервера'
        verbose_name_plural = 'Снепшоты серверов'
        ordering = ['-created_at']


class PlayerServerStat(models.Model):
    profile = models.ForeignKey(
        SteamProfile,
        on_delete=models.CASCADE,
        related_name='server_stats',
    )
    server = models.ForeignKey(
        RustServer,
        on_delete=models.CASCADE,
        related_name='player_stats',
    )

    kills = models.PositiveIntegerField('Убийства', default=0)
    deaths = models.PositiveIntegerField('Смерти', default=0)
    playtime_minutes = models.PositiveIntegerField('Минуты в игре', default=0)
    last_seen_on_server = models.DateTimeField('Последний раз на сервере', null=True, blank=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Статистика игрока'
        verbose_name_plural = 'Статистика игроков'
        unique_together = ('profile', 'server')


class ServerPlayerConnection(models.Model):
    profile = models.ForeignKey(
        SteamProfile,
        on_delete=models.CASCADE,
        related_name='server_connections',
    )
    server = models.ForeignKey(
        RustServer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='player_connections',
    )

    server_ip = models.GenericIPAddressField('IP на сервере', db_index=True)
    nickname_at_moment = models.CharField('Ник на момент входа', max_length=255, blank=True)

    first_seen_at = models.DateTimeField('Первый вход с IP', null=True, blank=True)
    last_seen_at = models.DateTimeField('Последний вход с IP', null=True, blank=True)
    connections_count = models.PositiveIntegerField('Кол-во входов', default=1)

    raw_payload = models.JSONField('Сырой payload от сервера', default=dict, blank=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Серверный вход игрока'
        verbose_name_plural = 'Серверные входы игроков'
        ordering = ['-last_seen_at', '-updated_at']
        indexes = [
            models.Index(fields=['server_ip']),
            models.Index(fields=['profile', 'server_ip']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_id and self.server_ip:
            seen_at = self.last_seen_at or self.updated_at or self.created_at

            SteamProfile.objects.filter(pk=self.profile_id).update(
                last_server_ip=self.server_ip,
                last_seen_on_server_at=seen_at,
            )

    def __str__(self):
        return f'{self.profile_id} / {self.server_ip}'


class ServerApiToken(models.Model):
    name = models.CharField('Название API-ключа', max_length=255)
    server = models.ForeignKey(
        RustServer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_tokens',
        verbose_name='Сервер',
    )

    token = models.CharField('Токен', max_length=128, unique=True, blank=True)

    is_active = models.BooleanField('Активен', default=True)
    allowed_ip = models.GenericIPAddressField(
        'Разрешённый IP сервера',
        null=True,
        blank=True,
        help_text='Можно оставить пустым на этапе разработки.',
    )

    last_used_at = models.DateTimeField('Последнее использование', null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_server_api_tokens',
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'API-ключ сервера'
        verbose_name_plural = 'API-ключи серверов'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)

        super().save(*args, **kwargs)

    def mark_used(self):
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])