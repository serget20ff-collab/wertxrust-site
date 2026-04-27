from django.contrib import admin
from .models import LegalDocument, SiteSetting
@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin): list_display=('key','description'); search_fields=('key','value','description')
@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin): list_display=('title','doc_type','updated_at'); search_fields=('title','body')
