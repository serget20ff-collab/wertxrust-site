from django.contrib import admin
from .models import PlayerAdminNote, SteamLoginEvent, SteamProfile
class SteamLoginEventInline(admin.TabularInline):
    model=SteamLoginEvent; extra=0; readonly_fields=('steam_id','ip_address','user_agent','success','reason','created_at'); can_delete=False
class PlayerAdminNoteInline(admin.TabularInline):
    model=PlayerAdminNote; extra=0
@admin.register(SteamProfile)
class SteamProfileAdmin(admin.ModelAdmin):
    list_display=('steam_id','nickname','last_known_ip','last_seen_at','is_project_staff','is_banned_on_site')
    search_fields=('steam_id','nickname','last_known_ip'); list_filter=('is_project_staff','is_banned_on_site','country_code')
    readonly_fields=('first_seen_at','last_seen_at'); inlines=[SteamLoginEventInline,PlayerAdminNoteInline]
@admin.register(SteamLoginEvent)
class SteamLoginEventAdmin(admin.ModelAdmin):
    list_display=('steam_id','profile','ip_address','success','reason','created_at'); search_fields=('steam_id','ip_address','reason'); list_filter=('success','created_at')
@admin.register(PlayerAdminNote)
class PlayerAdminNoteAdmin(admin.ModelAdmin):
    list_display=('title','profile','author','created_at'); search_fields=('title','body','profile__steam_id','profile__nickname')
