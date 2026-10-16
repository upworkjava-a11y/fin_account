from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import translation
from django.views.decorators.http import require_POST


def home(request):
    return render(request, 'core/home.html')


def set_language(request, code):
    code = (code or 'uz')[:2].lower()
    allowed = {lang[0] for lang in settings.LANGUAGES}
    if code not in allowed:
        code = 'uz'
    translation.activate(code)
    request.session['django_language'] = code
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    response = redirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, code, max_age=365 * 24 * 60 * 60)
    return response


@require_POST
def set_language_post(request):
    code = request.POST.get('language', 'uz')
    return set_language(request, code)
