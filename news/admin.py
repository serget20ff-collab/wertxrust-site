from django.contrib import admin
from .models import NewsPost
@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display=('title','post_type','is_published','published_at','created_at'); list_filter=('post_type','is_published'); search_fields=('title','excerpt','body'); prepopulated_fields={'slug':('title',)}
