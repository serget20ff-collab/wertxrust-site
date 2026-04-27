from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class SteamProfile(models.Model):
    ROLE_PLAYER = 'player'
    ROLE_PAID_ADMIN = 'paid_admin'
    ROLE_SPONSOR = 'sponsor'
    ROLE_TRAINEE = 'trainee'
    ROLE_MODERATOR = 'moderator'
    ROLE_SENIOR_MODERATOR = 'senior_moderator'
    ROLE_ADMINISTRATOR = 'administrator'
    ROLE_SENIOR_ADMINISTRATOR = 'senior_administrator'
    ROLE_CURATOR = 'curator'
    ROLE_DEVELOPER = 'developer'

    PROJECT_ROLE_CHOICES = [
        (ROLE_PLAYER, 'Игрок'),
        (ROLE_PAID_ADMIN, 'Покупная админка'),
        (ROLE_SPONSOR, 'Спонсор'),
        (ROLE_TRAINEE, 'Стажёр'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_SENIOR_MODERATOR, 'Старший модератор'),
        (ROLE_ADMINISTRATOR, 'Администратор'),
        (ROLE_SENIOR_ADMINISTRATOR, 'Старший администратор'),
        (ROLE_CURATOR, 'Куратор'),
        (ROLE_DEVELOPER, 'Разработчик'),
    ]

    ROLE_LEVELS = {
        ROLE_PLAYER: 0,
        ROLE_PAID_ADMIN: 20,
        ROLE_SPONSOR: 25,
        ROLE_TRAINEE: 30,
        ROLE_MODERATOR: 40,
        ROLE_SENIOR_MODERATOR: 50,
        ROLE_ADMINISTRATOR: 60,
        ROLE_SENIOR_ADMINISTRATOR: 70,
        ROLE_CURATOR: 80,
        ROLE_DEVELOPER: 100,
    }

    STAFF_ROLE_ORDER = [
        ROLE_DEVELOPER,
        ROLE_CURATOR,
        ROLE_SENIOR_ADMINISTRATOR,
        ROLE_ADMINISTRATOR,
        ROLE_SENIOR_MODERATOR,
        ROLE_MODERATOR,
        ROLE_TRAINEE,
        ROLE_SPONSOR,
        ROLE_PAID_ADMIN,
    ]

    steam_id = models.CharField('Steam ID64', max_length=32, primary_key=True)

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='steam_profile',
    )

    nickname = models.CharField('Ник Steam', max_length=255, blank=True)
    profile_url = models.URLField('Профиль Steam', blank=True)
    avatar_small = models.URLField('Аватар маленький', blank=True)
    avatar_medium = models.URLField('Аватар средний', blank=True)
    avatar_full = models.URLField('Аватар полный', blank=True)

    real_name = models.CharField('Реальное имя Steam', max_length=255, blank=True)
    country_code = models.CharField('Страна', max_length=8, blank=True)
    persona_state = models.IntegerField('Steam статус', default=0)

    project_role = models.CharField(
        'Роль проекта',
        max_length=32,
        choices=PROJECT_ROLE_CHOICES,
        default=ROLE_PLAYER,
        db_index=True,
    )

    balance_rub = models.DecimalField(
        'Баланс, ₽',
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    first_seen_at = models.DateTimeField('Первый вход', auto_now_add=True)
    last_seen_at = models.DateTimeField('Последний вход на сайт', null=True, blank=True)

    last_known_ip = models.GenericIPAddressField(
        'Последний IP сайта',
        null=True,
        blank=True,
    )

    last_server_ip = models.GenericIPAddressField(
        'Последний IP сервера Rust',
        null=True,
        blank=True,
        db_index=True,
    )

    last_seen_on_server_at = models.DateTimeField(
        'Последний вход на Rust сервер',
        null=True,
        blank=True,
    )

    last_user_agent = models.TextField('Последний User-Agent', blank=True)

    is_project_staff = models.BooleanField('Сотрудник проекта', default=False)
    is_banned_on_site = models.BooleanField('Бан на сайте', default=False)
    ban_reason = models.TextField('Причина бана', blank=True)
    notes = models.TextField('Внутренние заметки', blank=True)

    class Meta:
        verbose_name = 'Steam профиль'
        verbose_name_plural = 'Steam профили'
        ordering = ['-last_seen_at', '-first_seen_at']

    def __str__(self):
        return f'{self.nickname or "Unknown"} ({self.steam_id})'

    @property
    def role_level(self):
        return self.ROLE_LEVELS.get(self.project_role, 0)

    @property
    def role_order_index(self):
        if self.project_role in self.STAFF_ROLE_ORDER:
            return self.STAFF_ROLE_ORDER.index(self.project_role)

        return 999

    @property
    def is_developer_role(self):
        return self.project_role == self.ROLE_DEVELOPER

    @property
    def is_curator_role(self):
        return self.project_role == self.ROLE_CURATOR

    @property
    def is_staff_member(self):
        return (
            self.is_project_staff
            or self.role_level >= self.ROLE_LEVELS[self.ROLE_PAID_ADMIN]
        )

    @property
    def can_access_panel(self):
        return self.is_staff_member and not self.is_banned_on_site

    def has_role_level(self, minimum_role):
        minimum_level = self.ROLE_LEVELS.get(minimum_role, 999)
        return self.role_level >= minimum_level

    def can_access_panel_section(self, section_key):
        if self.is_banned_on_site:
            return False

        if self.is_developer_role:
            return True

        section_minimum_roles = {
            'dashboard': self.ROLE_PAID_ADMIN,
            'player_check': self.ROLE_PAID_ADMIN,
            'discord_tools': self.ROLE_DEVELOPER,
	    'documents': self.ROLE_DEVELOPER,
            'reports': self.ROLE_TRAINEE,
            'moderation': self.ROLE_MODERATOR,

            'players': self.ROLE_MODERATOR,

            'servers': self.ROLE_ADMINISTRATOR,

            # Команда видна всем сотрудникам, но редактировать могут только куратор/разработчик.
            'staff': self.ROLE_PAID_ADMIN,

            # Настройки и серверные API — куратор и разработчик.
            'settings': self.ROLE_CURATOR,
            'developer': self.ROLE_CURATOR,

            # Магазин пока оставляем разработчику.
            'shop': self.ROLE_DEVELOPER,
        }

        minimum_role = section_minimum_roles.get(section_key)

        if not minimum_role:
            return False

        return self.has_role_level(minimum_role)

    def can_manage_staff(self):
        return self.project_role in [
            self.ROLE_CURATOR,
            self.ROLE_DEVELOPER,
        ]

    def can_manage_profile_role(self, target_profile, new_role):
        if not self.can_manage_staff():
            return False

        if self.is_developer_role:
            return True

        if self.is_curator_role:
            if target_profile.project_role == self.ROLE_DEVELOPER:
                return False

            if new_role == self.ROLE_DEVELOPER:
                return False

            return True

        return False

    def sync_django_permissions(self):
        if not self.user_id:
            return

        if self.project_role == self.ROLE_DEVELOPER:
            User.objects.filter(pk=self.user_id).update(
                is_staff=True,
                is_superuser=True,
            )
            return

        if self.project_role in [
            self.ROLE_CURATOR,
            self.ROLE_SENIOR_ADMINISTRATOR,
        ]:
            User.objects.filter(pk=self.user_id).update(
                is_staff=True,
                is_superuser=False,
            )
            return

        User.objects.filter(pk=self.user_id).update(
            is_staff=False,
            is_superuser=False,
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_django_permissions()

    def touch_login(self, ip=None, user_agent=''):
        self.last_seen_at = timezone.now()

        if ip:
            self.last_known_ip = ip

        if user_agent:
            self.last_user_agent = user_agent[:2000]

        self.save(
            update_fields=[
                'last_seen_at',
                'last_known_ip',
                'last_user_agent',
            ]
        )


class SteamLoginEvent(models.Model):
    profile = models.ForeignKey(
        SteamProfile,
        on_delete=models.CASCADE,
        related_name='login_events',
        null=True,
        blank=True,
    )

    steam_id = models.CharField('Steam ID64', max_length=32, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField('IP сайта', null=True, blank=True)
    user_agent = models.TextField('User-Agent', blank=True)
    success = models.BooleanField('Успешно', default=False)
    reason = models.CharField('Причина/статус', max_length=255, blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Вход Steam'
        verbose_name_plural = 'История входов Steam'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.steam_id or "unknown"} / {self.created_at:%Y-%m-%d %H:%M}'


class PlayerAdminNote(models.Model):
    profile = models.ForeignKey(
        SteamProfile,
        on_delete=models.CASCADE,
        related_name='admin_notes',
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    title = models.CharField('Заголовок', max_length=255)
    body = models.TextField('Текст')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Заметка по игроку'
        verbose_name_plural = 'Заметки по игрокам'
        ordering = ['-created_at']

    def __str__(self):
        return self.title