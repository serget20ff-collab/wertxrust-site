from django.contrib import admin

from .models import HelpCategory, HelpItem, LegalDocument


class HelpItemInline(admin.StackedInline):
    model = HelpItem
    extra = 0
    fields = (
        'title',
        'body',
        'sort_order',
        'is_public',
    )


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'title',
        'slug',
        'is_published',
        'updated_at',
    )
    list_filter = (
        'is_published',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'name',
        'title',
        'slug',
        'text',
    )

    prepopulated_fields = {
        'slug': ('name',),
    }

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            'Документ',
            {
                'fields': (
                    'name',
                    'slug',
                    'title',
                    'text',
                    'is_published',
                )
            },
        ),
        (
            'Системное',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'subtitle',
        'sort_order',
        'is_public',
    )
    list_filter = (
        'is_public',
    )
    search_fields = (
        'title',
        'subtitle',
    )
    inlines = [
        HelpItemInline,
    ]


@admin.register(HelpItem)
class HelpItemAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'sort_order',
        'is_public',
    )
    list_filter = (
        'category',
        'is_public',
    )
    search_fields = (
        'title',
        'body',
    )