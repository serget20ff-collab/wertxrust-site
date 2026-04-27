from django.db import models
from accounts.models import SteamProfile
class ProductCategory(models.Model):
    name=models.CharField('Название',max_length=255); slug=models.SlugField('Slug',unique=True); sort_order=models.PositiveIntegerField('Сортировка',default=100)
    class Meta: verbose_name='Категория магазина'; verbose_name_plural='Категории магазина'; ordering=['sort_order','name']
    def __str__(self): return self.name
class Product(models.Model):
    PRODUCT_TYPES=[('privilege','Привилегия'),('kit','Кит'),('cosmetic','Косметика'),('service','Услуга'),('other','Другое')]
    category=models.ForeignKey(ProductCategory,on_delete=models.SET_NULL,null=True,blank=True,related_name='products'); name=models.CharField('Название',max_length=255); slug=models.SlugField('Slug',unique=True); product_type=models.CharField('Тип',max_length=32,choices=PRODUCT_TYPES,default='privilege')
    short_description=models.CharField('Короткое описание',max_length=255,blank=True); description=models.TextField('Описание',blank=True); price_rub=models.DecimalField('Цена, ₽',max_digits=10,decimal_places=2); duration_days=models.PositiveIntegerField('Длительность, дней',default=30); image=models.ImageField('Изображение',upload_to='shop/',blank=True); is_active=models.BooleanField('Активен',default=True); is_featured=models.BooleanField('На главной',default=False); sort_order=models.PositiveIntegerField('Сортировка',default=100); created_at=models.DateTimeField('Создано',auto_now_add=True); updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta: verbose_name='Товар'; verbose_name_plural='Товары'; ordering=['sort_order','name']
    def __str__(self): return self.name
class Order(models.Model):
    STATUS_CHOICES=[('draft','Черновик'),('pending','Ожидает оплаты'),('paid','Оплачен'),('granting','Выдается'),('completed','Выполнен'),('cancelled','Отменен'),('refunded','Возврат')]
    profile=models.ForeignKey(SteamProfile,on_delete=models.PROTECT,related_name='orders'); status=models.CharField('Статус',max_length=32,choices=STATUS_CHOICES,default='draft'); total_rub=models.DecimalField('Сумма, ₽',max_digits=10,decimal_places=2,default=0); customer_email=models.EmailField('Email покупателя',blank=True); comment=models.TextField('Комментарий',blank=True); created_at=models.DateTimeField('Создан',auto_now_add=True); updated_at=models.DateTimeField('Обновлен',auto_now=True)
    class Meta: verbose_name='Заказ'; verbose_name_plural='Заказы'; ordering=['-created_at']
    def __str__(self): return f'Order #{self.pk} / {self.profile_id}'
class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items'); product=models.ForeignKey(Product,on_delete=models.PROTECT); quantity=models.PositiveIntegerField('Количество',default=1); price_rub=models.DecimalField('Цена на момент покупки',max_digits=10,decimal_places=2)
    class Meta: verbose_name='Позиция заказа'; verbose_name_plural='Позиции заказов'
class PaymentTransaction(models.Model):
    PROVIDERS=[('yookassa','ЮKassa'),('manual','Вручную')]
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='payments'); provider=models.CharField('Провайдер',max_length=32,choices=PROVIDERS,default='yookassa'); provider_payment_id=models.CharField('ID платежа у провайдера',max_length=255,blank=True,db_index=True); status=models.CharField('Статус платежа',max_length=64,blank=True); amount_rub=models.DecimalField('Сумма, ₽',max_digits=10,decimal_places=2,default=0); raw_payload=models.JSONField('Сырой payload',default=dict,blank=True); created_at=models.DateTimeField('Создано',auto_now_add=True); updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta: verbose_name='Платежная транзакция'; verbose_name_plural='Платежные транзакции'; ordering=['-created_at']
class Entitlement(models.Model):
    STATUS_CHOICES=[('active','Активно'),('expired','Истекло'),('revoked','Отозвано')]
    profile=models.ForeignKey(SteamProfile,on_delete=models.CASCADE,related_name='entitlements'); product=models.ForeignKey(Product,on_delete=models.PROTECT); order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,blank=True,related_name='entitlements'); status=models.CharField('Статус',max_length=32,choices=STATUS_CHOICES,default='active'); starts_at=models.DateTimeField('Начало'); expires_at=models.DateTimeField('Окончание',null=True,blank=True); server_payload=models.JSONField('Данные для выдачи на сервер',default=dict,blank=True); created_at=models.DateTimeField('Создано',auto_now_add=True); updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta: verbose_name='Выданное право/покупка'; verbose_name_plural='Выданные права/покупки'; ordering=['-created_at']
