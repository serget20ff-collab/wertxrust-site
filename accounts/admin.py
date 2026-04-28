from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import (
    PlayerAdminNote,
    SteamLoginEvent,
    SteamProfile,
    WalletTransaction,
)


class SteamLoginEventInline(admin.TabularInline):
    model = SteamLoginEvent
    extra = 0
    readonly_fields = (
        'steam_id',
        'ip_address',
        'user_agent',
        'success',
        'reason',
        'created_at',
    )
    can_delete = False


class PlayerAdminNoteInline(admin.TabularInline):
    model = PlayerAdminNote
    extra = 0


@admin.register(SteamProfile)
class SteamProfileAdmin(admin.ModelAdmin):
    list_display = (
        'steam_id',
        'nickname',
        'project_role',
        'balance_rub',
        'last_known_ip',
        'last_seen_at',
        'is_project_staff',
        'is_banned_on_site',
    )
    search_fields = (
        'steam_id',
        'nickname',
        'last_known_ip',
        'profile_url',
    )
    list_filter = (
        'project_role',
        'is_project_staff',
        'is_banned_on_site',
        'country_code',
    )
    readonly_fields = (
        'first_seen_at',
        'last_seen_at',
    )
    fieldsets = (
        (
            'Главное',
            {
                'fields': (
                    'steam_id',
                    'user',
                    'nickname',
                    'profile_url',
                )
            },
        ),
        (
            'Роль и баланс',
            {
                'fields': (
                    'project_role',
                    'balance_rub',
                    'is_project_staff',
                )
            },
        ),
        (
            'Steam',
            {
                'fields': (
                    'avatar_small',
                    'avatar_medium',
                    'avatar_full',
                    'real_name',
                    'country_code',
                    'persona_state',
                )
            },
        ),
        (
            'Активность',
            {
                'fields': (
                    'first_seen_at',
                    'last_seen_at',
                    'last_known_ip',
                    'last_user_agent',
                )
            },
        ),
        (
            'Ограничения',
            {
                'fields': (
                    'is_banned_on_site',
                    'ban_reason',
                    'notes',
                )
            },
        ),
    )
    inlines = [
        SteamLoginEventInline,
        PlayerAdminNoteInline,
    ]


@admin.register(SteamLoginEvent)
class SteamLoginEventAdmin(admin.ModelAdmin):
    list_display = (
        'steam_id',
        'profile',
        'ip_address',
        'success',
        'reason',
        'created_at',
    )
    search_fields = (
        'steam_id',
        'ip_address',
        'reason',
        'profile__nickname',
    )
    list_filter = (
        'success',
        'created_at',
    )


@admin.register(PlayerAdminNote)
class PlayerAdminNoteAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'profile',
        'author',
        'created_at',
    )
    search_fields = (
        'title',
        'body',
        'profile__steam_id',
        'profile__nickname',
    )


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'profile',
        'tx_type',
        'amount_rub',
        'balance_after_rub',
        'counterparty_profile',
        'reference_code',
    )
    list_filter = (
        'tx_type',
        'created_at',
    )
    search_fields = (
        'profile__steam_id',
        'profile__nickname',
        'counterparty_profile__steam_id',
        'reference_code',
        'description',
    )



try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass