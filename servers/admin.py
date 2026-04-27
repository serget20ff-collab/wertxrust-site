from django.contrib import admin
from .models import PlayerServerStat, RustServer, ServerSnapshot
class ServerSnapshotInline(admin.TabularInline): model=ServerSnapshot; extra=0; readonly_fields=('online_players','queued_players','max_players','map_name','created_at'); can_delete=False
@admin.register(RustServer)
class RustServerAdmin(admin.ModelAdmin):
    list_display=('name','server_type','rates','ip','port','max_players','is_public','sort_order'); search_fields=('name','ip','description'); list_filter=('is_public','server_type','rates'); prepopulated_fields={'slug':('name',)}; inlines=[ServerSnapshotInline]
@admin.register(ServerSnapshot)
class ServerSnapshotAdmin(admin.ModelAdmin): list_display=('server','online_players','queued_players','max_players','created_at'); list_filter=('server','created_at')
@admin.register(PlayerServerStat)
class PlayerServerStatAdmin(admin.ModelAdmin): list_display=('profile','server','kills','deaths','playtime_minutes','last_seen_on_server'); search_fields=('profile__steam_id','profile__nickname','server__name'); list_filter=('server',)
