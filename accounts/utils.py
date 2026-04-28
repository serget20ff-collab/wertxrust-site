import re
from urllib.parse import urlencode
import requests
from django.conf import settings
STEAM_OPENID_URL='https://steamcommunity.com/openid/login'
STEAM_ID_RE=re.compile(r'https://steamcommunity.com/openid/id/(\d+)')
def get_client_ip(request):
    forwarded=request.META.get('HTTP_X_FORWARDED_FOR') if settings.TRUST_X_FORWARDED_FOR else ''
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')
def build_steam_login_url():
    params={'openid.ns':'http://specs.openid.net/auth/2.0','openid.mode':'checkid_setup','openid.return_to':settings.STEAM_RETURN_URL,'openid.realm':settings.STEAM_REALM,'openid.identity':'http://specs.openid.net/auth/2.0/identifier_select','openid.claimed_id':'http://specs.openid.net/auth/2.0/identifier_select'}
    return f'{STEAM_OPENID_URL}?{urlencode(params)}'
def verify_steam_response(querydict):
    data=querydict.copy(); data['openid.mode']='check_authentication'
    response=requests.post(STEAM_OPENID_URL,data=data,timeout=10); response.raise_for_status()
    response_values = dict(
        line.split(':', 1)
        for line in response.text.splitlines()
        if ':' in line
    )
    if response_values.get('is_valid') != 'true': return None
    match=STEAM_ID_RE.match(querydict.get('openid.claimed_id',''))
    return match.group(1) if match else None
def fetch_steam_player_summary(steam_id):
    if not settings.STEAM_API_KEY: return {}
    url='https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    response=requests.get(url,params={'key':settings.STEAM_API_KEY,'steamids':steam_id},timeout=10); response.raise_for_status()
    players=response.json().get('response',{}).get('players',[])
    return players[0] if players else {}
