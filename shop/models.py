from decimal import Decimal

from django.db import models
from django.utils import timezone

from accounts.models import SteamProfile
from servers.models import RustServer, ServerShopCategory


class ProductCategory(models.Model):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Описание', blank=True)
    icon = models.CharField('Иконка / emoji', max_length=32, blank=True)

    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Категория магазина'
        verbose_name_plural = 'Категории магазина'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_PRIVILEGE = 'privilege'
    PRODUCT_KIT = 'kit'
    PRODUCT_RESOURCE = 'resource'
    PRODUCT_WEAPON = 'weapon'
    PRODUCT_COMPONENT = 'component'
    PRODUCT_COSMETIC = 'cosmetic'
    PRODUCT_SERVICE = 'service'

    PRODUCT_TYPES = [
        (PRODUCT_PRIVILEGE, 'Привилегия'),
        (PRODUCT_KIT, 'Кит'),
        (PRODUCT_RESOURCE, 'Ресурс'),
        (PRODUCT_WEAPON, 'Оружие'),
        (PRODUCT_COMPONENT, 'Компонент'),
        (PRODUCT_COSMETIC, 'Косметика'),
        (PRODUCT_SERVICE, 'Услуга'),
    ]

    SERVER_SCOPE_ALL = 'all'
    SERVER_SCOPE_SELECTED = 'selected'

    SERVER_SCOPE_CHOICES = [
        (SERVER_SCOPE_ALL, 'Все серверы'),
        (SERVER_SCOPE_SELECTED, 'Выбранные серверы'),
    ]

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Категория',
    )

    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Slug', unique=True)

    product_type = models.CharField(
        'Тип товара',
        max_length=32,
        choices=PRODUCT_TYPES,
        default=PRODUCT_PRIVILEGE,
        db_index=True,
    )

    short_description = models.CharField('Короткое описание', max_length=255, blank=True)
    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Основное красивое описание товара. Можно писать обычным текстом.',
    )

    detail_lines = models.TextField(
        'Список возможностей / условий',
        blank=True,
        help_text='Каждый пункт с новой строки. Например: Доступ к /kit vip',
    )

    how_to_get = models.TextField(
        'Как получить',
        blank=True,
        help_text='Например: после покупки войди на сервер и используй команду /kit.',
    )

    image = models.ImageField('Изображение', upload_to='shop/products/', blank=True)

    display_amount = models.CharField(
        'Количество / объём',
        max_length=120,
        blank=True,
        help_text='Для ресурса, оружия, компонента или косметики. Например: x1000, 1 шт., набор.',
    )

    price_rub = models.DecimalField('Текущая цена, ₽', max_digits=10, decimal_places=0)
    old_price_rub = models.DecimalField(
        'Старая цена, ₽',
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
    )

    duration_days = models.PositiveIntegerField(
        'Длительность действия, дней',
        default=30,
        help_text='Для привилегий/услуг. Например, VIP на 30 дней.',
    )

    promo_duration_days = models.PositiveIntegerField(
        'Длительность акции, дней',
        default=0,
        help_text='Если указать число больше 0, акция считается от даты создания товара.',
    )

    is_active = models.BooleanField('Активен', default=True)
    is_featured = models.BooleanField('Показывать на главной', default=False)
    server_scope = models.CharField(
        'Доступность по серверам',
        max_length=16,
        choices=SERVER_SCOPE_CHOICES,
        default=SERVER_SCOPE_ALL,
    )
    servers = models.ManyToManyField(
        RustServer,
        blank=True,
        related_name='products',
        verbose_name='Доступные серверы',
    )
    server_categories = models.ManyToManyField(
        ServerShopCategory,
        blank=True,
        related_name='products',
        verbose_name='Внутренние категории серверов',
        help_text='Товар будет доступен на серверах из выбранных внутренних категорий.',
    )

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def has_discount(self):
        return bool(self.old_price_rub and self.old_price_rub > self.price_rub)

    @property
    def discount_percent(self):
        if not self.has_discount:
            return 0

        discount = (self.old_price_rub - self.price_rub) / self.old_price_rub * Decimal('100')
        return int(discount.quantize(Decimal('1')))

    @property
    def detail_list(self):
        return [line.strip() for line in self.detail_lines.splitlines() if line.strip()]

    @property
    def is_kit(self):
        return self.product_type == self.PRODUCT_KIT

    @property
    def is_privilege(self):
        return self.product_type == self.PRODUCT_PRIVILEGE

    @property
    def is_simple_item(self):
        return self.product_type in [
            self.PRODUCT_RESOURCE,
            self.PRODUCT_WEAPON,
            self.PRODUCT_COMPONENT,
            self.PRODUCT_COSMETIC,
        ]

    @property
    def is_service(self):
        return self.product_type == self.PRODUCT_SERVICE

    @property
    def promo_ends_at(self):
        if not self.promo_duration_days:
            return None

        return self.created_at + timezone.timedelta(days=self.promo_duration_days)

    @property
    def promo_days_left(self):
        promo_ends_at = self.promo_ends_at

        if not promo_ends_at:
            return None

        now = timezone.now()

        if promo_ends_at <= now:
            return 0

        delta = promo_ends_at - now
        return max(0, delta.days)

    @property
    def is_promo_ending_soon(self):
        days_left = self.promo_days_left

        if days_left is None:
            return False

        return 0 <= days_left <= 10

    def is_available_for_server(self, server):
        if self.server_scope == self.SERVER_SCOPE_ALL:
            return True

        if not server:
            return False

        if self.servers.filter(pk=server.pk).exists():
            return True

        if server.shop_category_id:
            return self.server_categories.filter(pk=server.shop_category_id).exists()

        return False

    def available_servers(self):
        if self.server_scope == self.SERVER_SCOPE_ALL:
            return RustServer.objects.filter(is_public=True).order_by('sort_order', 'name')

        selected_ids = self.servers.filter(is_public=True).values_list('pk', flat=True)
        category_ids = self.server_categories.filter(is_active=True).values_list('pk', flat=True)

        return (
            RustServer.objects
            .filter(is_public=True)
            .filter(models.Q(pk__in=selected_ids) | models.Q(shop_category_id__in=category_ids))
            .distinct()
            .order_by('sort_order', 'name')
        )


class ProductContentItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='content_items',
    )

    name = models.CharField('Название предмета', max_length=255)
    amount = models.PositiveIntegerField('Количество', default=1)
    image = models.ImageField('Иконка предмета', upload_to='shop/items/', blank=True)

    class Meta:
        verbose_name = 'Состав кита'
        verbose_name_plural = 'Состав китов'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} x{self.amount}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('granting', 'Ожидает выдачи'),
        ('completed', 'Выполнен'),
        ('failed', 'Ошибка выдачи'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возврат'),
    ]

    profile = models.ForeignKey(
        SteamProfile,
        on_delete=models.PROTECT,
        related_name='orders',
    )

    status = models.CharField('Статус', max_length=32, choices=STATUS_CHOICES, default='draft')
    selected_server = models.ForeignKey(
        RustServer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Сервер покупки',
    )
    total_rub = models.DecimalField('Сумма, ₽', max_digits=10, decimal_places=0, default=0)
    delivery_error = models.TextField('Ошибка выдачи', blank=True)

    customer_email = models.EmailField('Email покупателя', blank=True)
    comment = models.TextField('Комментарий', blank=True)

    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} / {self.profile_id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField('Количество', default=1)
    price_rub = models.DecimalField('Цена на момент покупки', max_digits=10, decimal_places=0)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'


class PaymentTransaction(models.Model):
    PROVIDERS = [
        ('yookassa', 'ЮKassa'),
        ('manual', 'Вручную'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')

    provider = models.CharField('Провайдер', max_length=32, choices=PROVIDERS, default='yookassa')
    provider_payment_id = models.CharField('ID платежа у провайдера', max_length=255, blank=True, db_index=True)
    status = models.CharField('Статус платежа', max_length=64, blank=True)
    amount_rub = models.DecimalField('Сумма, ₽', max_digits=10, decimal_places=0, default=0)
    raw_payload = models.JSONField('Сырой payload', default=dict, blank=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Платежная транзакция'
        verbose_name_plural = 'Платежные транзакции'
        ordering = ['-created_at']


class Entitlement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает выдачи'),
        ('sent', 'Отправлено на сервер'),
        ('active', 'Активно'),
        ('failed', 'Ошибка выдачи'),
        ('refunded', 'Возвращено'),
        ('expired', 'Истекло'),
        ('revoked', 'Отозвано'),
    ]

    profile = models.ForeignKey(
        SteamProfile,
        on_delete=models.CASCADE,
        related_name='entitlements',
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    server = models.ForeignKey(
        RustServer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entitlements',
        verbose_name='Сервер',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entitlements',
    )

    status = models.CharField('Статус', max_length=32, choices=STATUS_CHOICES, default='active')
    starts_at = models.DateTimeField('Начало')
    expires_at = models.DateTimeField('Окончание', null=True, blank=True)

    server_payload = models.JSONField('Данные для выдачи серверному агенту', default=dict, blank=True)
    delivery_error = models.TextField('Ошибка выдачи', blank=True)
    delivered_at = models.DateTimeField('Выдано', null=True, blank=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Выданное право/покупка'
        verbose_name_plural = 'Выданные права/покупки'
        ordering = ['-created_at']
