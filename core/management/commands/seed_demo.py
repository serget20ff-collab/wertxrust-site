from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import NewsPost
from rules.models import RuleItem, RuleSection
from servers.models import RustServer
from shop.models import Product, ProductCategory
from core.models import LegalDocument
class Command(BaseCommand):
    help='Создает демо-наполнение WertxRust'
    def handle(self,*args,**options):
        RustServer.objects.get_or_create(slug='vanilla-plus-x2',defaults={'name':'WertxRust Vanilla+ x2','description':'Первый сервер проекта: честный Vanilla+ с x2 рейтами и минимумом лишних модов.','ip':'wertxrust.ru','port':28015,'connect_command':'connect wertxrust.ru:28015','server_type':'Vanilla+','rates':'x2','map_size':4000,'max_players':200,'wipe_schedule':'Расписание будет объявлено в Discord'})
        category,_=ProductCategory.objects.get_or_create(slug='privileges',defaults={'name':'Привилегии'})
        Product.objects.get_or_create(slug='starter-vip',defaults={'category':category,'name':'Starter VIP','product_type':'privilege','short_description':'Стартовая привилегия без pay-to-win. Название и бонусы можно изменить.','description':'Заготовка товара. Перед релизом нужно уточнить бонусы и юридические формулировки.','price_rub':Decimal('149.00'),'duration_days':30,'is_featured':True})
        NewsPost.objects.get_or_create(slug='soon-launch',defaults={'title':'Скоро открытие WertxRust','post_type':'update','excerpt':'Готовим сайт, Discord и первый сервер Vanilla+ x2.','body':'Следи за Discord. Там будут даты тестов, вайпа и публичного запуска.','is_published':True,'published_at':timezone.now()})
        section,_=RuleSection.objects.get_or_create(title='Основные правила сервера',defaults={'section_type':'server','description':'Базовые правила честной игры и общения.','sort_order':10})
        RuleItem.objects.get_or_create(section=section,code='1.1',defaults={'title':'Запрещены читы и сторонний софт','body':'Любые программы, макросы и обходы, дающие преимущество, запрещены.','punishment':'Перманентный бан','sort_order':10})
        RuleItem.objects.get_or_create(section=section,code='1.2',defaults={'title':'Запрещены оскорбления и токсичность','body':'Конфликты решаются через поддержку. Администрация может ограничить доступ к чату или серверу.','punishment':'Мут / бан','sort_order':20})
        LegalDocument.objects.get_or_create(doc_type='offer',defaults={'title':'Публичная оферта','body':'Черновик. Перед приемом платежей текст нужно проверить и доработать.'})
        LegalDocument.objects.get_or_create(doc_type='privacy',defaults={'title':'Политика конфиденциальности','body':'Черновик. Сайт хранит Steam ID, IP входов и данные покупок для работы проекта.'})
        LegalDocument.objects.get_or_create(doc_type='refund',defaults={'title':'Правила возврата','body':'Черновик. Условия возвратов нужно уточнить до запуска магазина.'})
        self.stdout.write(self.style.SUCCESS('Демо-данные созданы.'))
