from django.conf import settings
from django.urls import reverse

from .i18n_labels import get_labels


def _item(item_id, label, url_name, prefixes, icon, children=None, exact=False):
    kids = []
    for child in children or []:
        kids.append({
            'label': child[0],
            'url': reverse(child[1]),
            'name': child[1],
        })
    return {
        'id': item_id,
        'label': label,
        'url': reverse(url_name),
        'match_prefixes': prefixes,
        'exact': exact,
        'icon': icon,
        'children': kids,
    }


def site_context(request):
    lang = (
        request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        or request.session.get('django_language')
        or getattr(request, 'LANGUAGE_CODE', None)
        or settings.LANGUAGE_CODE
        or 'uz'
    )
    lang = lang[:2].lower()
    if lang not in {'uz', 'ru', 'en'}:
        lang = 'uz'
    t = get_labels(lang)

    is_guest = bool(request.session.get(settings.SESSION_GUEST_KEY))
    profile = request.session.get(settings.SESSION_PROFILE_KEY) or {
        'reg_date': '08.10.2026',
        'tariff': 'Standart',
        'tariff_until': '08.10.2027',
        'payment_due': '08.11.2026',
        'payment_phone': '+998 71 200 00 01',
        'telegram': 'https://t.me/finaccount_support',
        'company': "OOO \"Fin Trade\"",
    }

    sidebar = [
        _item('dashboard', t['dashboard'], 'app_dashboard', ['/app/'], '📊', exact=True),
        _item(
            'organization', t['mod_org'], 'org_main', ['/app/organization/'], '🏢',
            [
                (t['org_main'], 'org_main'),
                (t['org_docs'], 'org_documents'),
                (t['org_banks'], 'org_banks'),
                (t['org_tg'], 'org_telegram'),
            ],
        ),
        _item(
            'tax', t['mod_tax'], 'tax_journal', ['/app/tax/'], '📑',
            [
                (t['tax_forms'], 'tax_forms'),
                (t['tax_journal'], 'tax_journal'),
                (t['tax_forming'], 'tax_forming'),
            ],
        ),
        _item(
            'bank', t['mod_bank'], 'bank_turnover', ['/app/bank/'], '🏦',
            [
                (t['bank_turnover'], 'bank_turnover'),
                (t['bank_auto'], 'bank_auto'),
                (t['bank_archive'], 'bank_archive'),
            ],
        ),
        _item(
            'payments', t['mod_payments'], 'pay_history', ['/app/payments/'], '💳',
            [
                (t['pay_history'], 'pay_history'),
                (t['pay_create'], 'pay_create'),
                (t['recon_tax'], 'recon_tax'),
                (t['recon_cp'], 'recon_counterparties'),
            ],
        ),
        _item(
            'assets', t['mod_assets'], 'asset_registry', ['/app/assets/'], '🏗️',
            [
                (t['asset_registry'], 'asset_registry'),
                (t['asset_depr'], 'asset_depreciation'),
                (t['asset_inv'], 'asset_inventory'),
            ],
        ),
        _item(
            'inventory', t['mod_tmz'], 'tmz_registry', ['/app/inventory/'], '📦',
            [
                (t['tmz_registry'], 'tmz_registry'),
                (t['tmz_moves'], 'tmz_movements'),
                (t['tmz_wh'], 'tmz_warehouses'),
                (t['tmz_inv'], 'tmz_inventory'),
            ],
        ),
        _item(
            'ehf', t['mod_ehf'], 'ehf_incoming', ['/app/ehf/'], '📄',
            [
                (t['ehf_in'], 'ehf_incoming'),
                (t['ehf_out'], 'ehf_outgoing'),
                (t['ehf_drafts'], 'ehf_drafts'),
                (t['ehf_contracts'], 'ehf_contracts'),
                (t['ehf_archive'], 'ehf_archive'),
            ],
        ),
        _item(
            'hr', t['mod_hr'], 'hr_employees', ['/app/hr/'], '👥',
            [
                (t['hr_employees'], 'hr_employees'),
                (t['hr_payroll'], 'hr_payroll'),
                (t['hr_pit'], 'hr_pit_social'),
                (t['hr_orders'], 'hr_orders'),
            ],
        ),
    ]

    path = request.path
    module_tabs = []
    for item in sidebar:
        if item.get('exact'):
            item['active'] = path.rstrip('/') == '/app'
        else:
            item['active'] = any(path.startswith(p) for p in item['match_prefixes'])
        for child in item['children']:
            child['active'] = path.rstrip('/') == child['url'].rstrip('/')
        if item['active'] and item['children']:
            module_tabs = item['children']

    return {
        't': t,
        'current_lang': lang,
        'languages': settings.LANGUAGES,
        'is_guest': is_guest,
        'profile': profile,
        'sidebar_modules': sidebar,
        'module_tabs': module_tabs,
    }
