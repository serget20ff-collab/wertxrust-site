from django.contrib import admin

from .models import (
    PlayerServerStat,
    RustServer,
    ServerApiToken,
    ServerPlayerConnection,
    ServerSnapshot,
)


@admin.register(RustServer)
class RustServerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'ip',
        'port',
        'server_type',
        'rates',
        'map_size',
        'max_players',
        'is_public',
        'show_on_home',
        'sort_order',
    )
    list_filter = (
        'is_public',
        'show_on_home',
        'server_type',
        'rates',
    )
    search_fields = (
        'name',
        'slug',
        'ip',
    )
    prepopulated_fields = {
        'slug': ('name',),
    }


@admin.register(ServerSnapshot)
class ServerSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'server',
        'online_players',
        'queued_players',
        'max_players',
        'map_name',
        'created_at',
    )
    list_filter = (
        'server',
        'created_at',
    )
    search_fields = (
        'server__name',
        'map_name',
    )
    readonly_fields = (
        'created_at',
    )


@admin.register(PlayerServerStat)
class PlayerServerStatAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'server',
        'kills',
        'deaths',
        'playtime_minutes',
        'last_seen_on_server',
        'updated_at',
    )
    list_filter = (
        'server',
        'updated_at',
    )
    search_fields = (
        'profile__steam_id',
        'profile__nickname',
        'server__name',
    )


@admin.register(ServerPlayerConnection)
class ServerPlayerConnectionAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'server_ip',
        'server',
        'nickname_at_moment',
        'connections_count',
        'first_seen_at',
        'last_seen_at',
    )
    list_filter = (
        'server',
        'last_seen_at',
        'created_at',
    )
    search_fields = (
        'profile__steam_id',
        'profile__nickname',
        'server_ip',
        'nickname_at_moment',
        'server__name',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(ServerApiToken)
class ServerApiTokenAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'server',
        'is_active',
        'allowed_ip',
        'last_used_at',
        'created_at',
    )
    list_filter = (
        'is_active',
        'server',
        'created_at',
    )
    search_fields = (
        'name',
        'token',
        'server__name',
        'allowed_ip',
    )
    readonly_fields = (
        'token',
        'last_used_at',
        'created_at',
    )