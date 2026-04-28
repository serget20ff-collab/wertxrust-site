from django import forms

from core.models import LegalDocument
from news.models import NewsPost
from rules.models import RuleItem, RuleSection
from shop.models import Product, ProductCategory, ProductContentItem
from servers.models import RustServer, ServerApiToken, ServerShopCategory


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = [
            'name',
            'slug',
            'description',
            'icon',
            'is_active',
        ]


class ProductForm(forms.ModelForm):
    content_items_text = forms.CharField(
        required=False,
        label='Состав кита',
        help_text='Только для типа “Кит”. Каждый предмет с новой строки. Пример: Камень x1000',
        widget=forms.Textarea(attrs={'rows': 5}),
    )

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'product_type',
            'short_description',
            'description',
            'detail_lines',
            'how_to_get',
            'image',
            'display_amount',
            'price_rub',
            'old_price_rub',
            'duration_days',
            'promo_duration_days',
            'server_scope',
            'servers',
            'server_categories',
            'is_active',
            'is_featured',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and not self.initial.get('content_items_text'):
            self.initial['content_items_text'] = '\n'.join(
                f'{item.name} x{item.amount}'
                for item in self.instance.content_items.all()
            )

    def clean(self):
        cleaned_data = super().clean()
        product_type = cleaned_data.get('product_type')
        content_items_text = cleaned_data.get('content_items_text', '').strip()

        if product_type != Product.PRODUCT_KIT and content_items_text:
            self.add_error(
                'content_items_text',
                'Состав предметов используется только для типа “Кит”.',
            )

        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=commit)

        if commit:
            text = self.cleaned_data.get('content_items_text', '').strip()

            ProductContentItem.objects.filter(product=product).delete()

            if product.product_type == Product.PRODUCT_KIT and text:
                for line in text.splitlines():
                    line = line.strip()

                    if not line:
                        continue

                    amount = 1
                    name = line

                    if ' x' in line.lower():
                        parts = line.rsplit('x', 1)
                        name = parts[0].strip()

                        try:
                            amount = int(parts[1].strip())
                        except ValueError:
                            amount = 1

                    ProductContentItem.objects.create(
                        product=product,
                        name=name,
                        amount=amount,
                    )

        return product


class RustServerForm(forms.ModelForm):
    class Meta:
        model = RustServer
        fields = [
            'name',
            'slug',
            'description',
            'shop_category',
            'ip',
            'port',
            'server_type',
            'rates',
            'map_size',
            'max_players',
            'is_public',
            'show_on_home',
            'sort_order',
        ]


class ServerShopCategoryForm(forms.ModelForm):
    class Meta:
        model = ServerShopCategory
        fields = [
            'name',
            'slug',
            'description',
            'sort_order',
            'is_active',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ServerApiTokenForm(forms.ModelForm):
    class Meta:
        model = ServerApiToken
        fields = [
            'name',
            'server',
            'allowed_ip',
            'is_active',
        ]


class LegalDocumentForm(forms.ModelForm):
    class Meta:
        model = LegalDocument
        fields = [
            'name',
            'slug',
            'title',
            'text',
            'is_published',
        ]

        widgets = {
            'text': forms.Textarea(
                attrs={
                    'rows': 14,
                    'placeholder': 'Введите текст документа...',
                }
            ),
        }


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = [
            'title',
            'slug',
            'post_type',
            'excerpt',
            'body',
            'cover',
            'is_published',
            'published_at',
        ]

        widgets = {
            'body': forms.Textarea(attrs={'rows': 10}),
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class RuleSectionForm(forms.ModelForm):
    class Meta:
        model = RuleSection
        fields = [
            'title',
            'section_type',
            'description',
            'sort_order',
            'is_public',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class RuleItemForm(forms.ModelForm):
    class Meta:
        model = RuleItem
        fields = [
            'section',
            'code',
            'title',
            'body',
            'note',
            'punishment',
            'sort_order',
            'is_public',
        ]

        widgets = {
            'body': forms.Textarea(attrs={'rows': 6}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }