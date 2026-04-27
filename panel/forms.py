from django import forms

from core.models import LegalDocument
from shop.models import Product, ProductCategory, ProductContentItem
from servers.models import RustServer, ServerApiToken


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
            'is_active',
            'is_featured',
        ]

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