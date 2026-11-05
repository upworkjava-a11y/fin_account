import json
import time
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .eri import EriError, issue_challenge, verify_login
from .models import EriLogin


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        # TODO: STIR lookup via my.soliq.uz, password validation, oferta, SMS verify
        messages.info(
            request,
            "Ro'yxatdan o'tish keyingi bosqichda ulanadi (STIR / my.soliq.uz).",
        )
        return redirect('register')
    return render(request, 'accounts/register.html')


def guest_enter(request):
    request.session[settings.SESSION_GUEST_KEY] = True
    request.session[settings.SESSION_PROFILE_KEY] = {
        'reg_date': '—',
        'tariff': 'Guest / Demo',
        'tariff_until': '—',
        'payment_due': '—',
        'payment_phone': '+998 71 000 00 00',
        'telegram': 'https://t.me/finaccount_support',
        'company': 'Mehmon (Demo)',
    }
    return redirect('app_dashboard')


def guest_exit(request):
    for key in (
        settings.SESSION_GUEST_KEY,
        settings.SESSION_PROFILE_KEY,
        settings.SESSION_ERI_KEY,
        'eri_challenge',
        'eri_challenge_at',
    ):
        request.session.pop(key, None)
    return redirect('home')


def eri_login(request):
    return render(
        request,
        'accounts/eri_login.html',
        {
            'eimzo_ws': settings.EIMZO_WS_URL,
            'eimzo_api_keys': settings.EIMZO_API_KEYS,
        },
    )


@require_GET
def eri_challenge(request):
    try:
        challenge = issue_challenge()
    except EriError as exc:
        return JsonResponse({'ok': False, 'error': exc.code}, status=503)
    request.session['eri_challenge'] = challenge
    request.session['eri_challenge_at'] = time.time()
    return JsonResponse({'ok': True, 'challenge': challenge, 'ttl': settings.EIMZO_CHALLENGE_TTL})


@require_POST
def eri_verify(request):
    challenge = request.session.get('eri_challenge')
    issued_at = request.session.get('eri_challenge_at') or 0
    if not challenge or time.time() - float(issued_at) > settings.EIMZO_CHALLENGE_TTL:
        return JsonResponse({'ok': False, 'error': 'challenge_expired'}, status=400)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        pkcs7 = str(payload.get('pkcs7') or '').strip()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'bad_pkcs7'}, status=400)
    if not pkcs7:
        return JsonResponse({'ok': False, 'error': 'bad_pkcs7'}, status=400)
    try:
        info = verify_login(pkcs7, challenge, request)
    except EriError as exc:
        return JsonResponse({'ok': False, 'error': exc.code}, status=400)
    request.session.pop('eri_challenge', None)
    request.session.pop('eri_challenge_at', None)
    request.session[settings.SESSION_GUEST_KEY] = False
    request.session[settings.SESSION_ERI_KEY] = True
    company = info['cn'] or info['stir'] or 'ERI'
    request.session[settings.SESSION_PROFILE_KEY] = {
        'reg_date': date.today().strftime('%d.%m.%Y'),
        'tariff': 'ERI',
        'tariff_until': info['valid_to'],
        'payment_due': '—',
        'payment_phone': '+998 71 200 00 01',
        'telegram': 'https://t.me/finaccount_support',
        'company': company,
        'stir': info['stir'] or '—',
        'pinfl': info['pinfl'],
    }
    EriLogin.objects.create(
        cn=info['cn'][:255],
        stir=info['stir'],
        pinfl=info['pinfl'],
        serial=info['serial'][:128],
        verified_by=info['verified_by'],
    )
    return JsonResponse({'ok': True, 'redirect': '/app/'})


def app_dashboard(request):
    return render(request, 'accounts/dashboard.html')
