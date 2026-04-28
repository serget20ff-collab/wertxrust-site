from django.contrib import admin
from .models import RuleItem, RuleSection
class RuleItemInline(admin.StackedInline): model=RuleItem; extra=0
@admin.register(RuleSection)
class RuleSectionAdmin(admin.ModelAdmin): list_display=('title','section_type','sort_order','is_public'); list_filter=('section_type','is_public'); inlines=[RuleItemInline]
@admin.register(RuleItem)
class RuleItemAdmin(admin.ModelAdmin): list_display=('code','title','section','punishment','sort_order','is_public'); search_fields=('code','title','body','note','punishment'); list_filter=('section','is_public')
