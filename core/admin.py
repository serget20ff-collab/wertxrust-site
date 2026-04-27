from django.contrib import admin

from .models import LegalDocument


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