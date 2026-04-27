from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET
from .models import SteamLoginEvent, SteamProfile
from .utils import build_steam_login_url, fetch_steam_player_summary, get_client_ip, verify_steam_response

@require_GET
def steam_login(request): return redirect(build_steam_login_url())

@require_GET
def steam_callback(request):
    ip=get_client_ip(request); user_agent=request.META.get('HTTP_USER_AGENT','')
    try: steam_id=verify_steam_response(request.GET)
    except Exception as exc:
        SteamLoginEvent.objects.create(ip_address=ip,user_agent=user_agent,success=False,reason=f'OpenID error: {exc}')
        messages.error(request,'Steam не подтвердил вход. Попробуй еще раз.'); return redirect('core:home')
    if not steam_id:
        SteamLoginEvent.objects.create(ip_address=ip,user_agent=user_agent,success=False,reason='Invalid OpenID response')
        messages.error(request,'Не удалось получить Steam ID.'); return redirect('core:home')
    summary={}
    try: summary=fetch_steam_player_summary(steam_id)
    except Exception as exc: SteamLoginEvent.objects.create(steam_id=steam_id,ip_address=ip,user_agent=user_agent,success=False,reason=f'Steam API profile fetch failed: {exc}')
    user,_=User.objects.get_or_create(username=f'steam_{steam_id}',defaults={'first_name':summary.get('personaname','')[:150]})
    if not user.has_usable_password(): user.set_unusable_password(); user.save(update_fields=['password'])
    profile,_=SteamProfile.objects.get_or_create(steam_id=steam_id,defaults={'user':user})
    profile.user=user; profile.nickname=summary.get('personaname',profile.nickname); profile.profile_url=summary.get('profileurl',profile.profile_url)
    profile.avatar_small=summary.get('avatar',profile.avatar_small); profile.avatar_medium=summary.get('avatarmedium',profile.avatar_medium); profile.avatar_full=summary.get('avatarfull',profile.avatar_full)
    profile.real_name=summary.get('realname',profile.real_name); profile.country_code=summary.get('loccountrycode',profile.country_code); profile.persona_state=summary.get('personastate',profile.persona_state or 0)
    profile.save(); profile.touch_login(ip=ip,user_agent=user_agent)
    SteamLoginEvent.objects.create(profile=profile,steam_id=steam_id,ip_address=ip,user_agent=user_agent,success=True,reason='OK')
    login(request,user); messages.success(request,f'Вход выполнен: {profile.nickname or steam_id}'); return redirect('core:home')

def logout_view(request): logout(request); messages.info(request,'Ты вышел из аккаунта.'); return redirect('core:home')
def profile_view(request):
    if not request.user.is_authenticated: return redirect('accounts:steam_login')
    return render(request,'accounts/profile.html')
