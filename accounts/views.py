from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


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
    request.session.pop(settings.SESSION_GUEST_KEY, None)
    request.session.pop(settings.SESSION_PROFILE_KEY, None)
    return redirect('home')


def app_dashboard(request):
    return render(request, 'accounts/dashboard.html')
