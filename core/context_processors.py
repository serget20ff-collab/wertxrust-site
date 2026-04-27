from django.conf import settings
def site_context(request): return {'SITE_NAME':settings.SITE_NAME,'SITE_URL':settings.SITE_URL,'DISCORD_URL':'https://discord.gg/wertxrust'}
