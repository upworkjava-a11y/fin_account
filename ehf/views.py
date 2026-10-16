from django.shortcuts import render

INCOMING_TABS = [
    ('all', 'Barchasi'),
    ('pending', 'Imzolanishi kutilmoqda'),
    ('signed', 'Imzolangan'),
    ('rejected', 'Rad etilgan'),
    ('cancelled', 'Bekor qilingan'),
]

DEMO_DOCS = [
    {
        'status': 'Imzolangan',
        'type': 'EHF',
        'counterparty': '"ORIENT TRADE" MChJ',
        'stir': '301112233',
        'number': 'EHF-9022',
        'contract': 'SH-12/26',
        'without_vat': '3 750 000',
        'vat': '750 000',
        'with_vat': '4 500 000',
        'created': '01.04.2026',
        'tab': 'signed',
    },
    {
        'status': 'Imzolanishi kutilmoqda',
        'type': 'Akt',
        'counterparty': '"SARDORBEK SERVIS" MChJ',
        'stir': '305556789',
        'number': 'AKT-77',
        'contract': 'SH-45/26',
        'without_vat': '1 000 000',
        'vat': '0',
        'with_vat': '1 000 000',
        'created': '10.04.2026',
        'tab': 'pending',
    },
]


def incoming(request):
    tab = request.GET.get('tab', 'all')
    rows = DEMO_DOCS if tab == 'all' else [d for d in DEMO_DOCS if d['tab'] == tab]
    return render(
        request,
        'ehf/incoming.html',
        {'rows': rows, 'tabs': INCOMING_TABS, 'active_tab': tab},
    )


def outgoing(request):
    return render(request, 'ehf/outgoing.html', {'rows': DEMO_DOCS})


def drafts(request):
    drafts_rows = [
        {'type': 'Faktura', 'counterparty': 'Demo LLC', 'number': 'DRAFT-01', 'status': 'Loyiha'},
        {'type': 'Shartnoma', 'counterparty': 'Demo LLC', 'number': 'DRAFT-02', 'status': 'Loyiha'},
    ]
    return render(request, 'ehf/drafts.html', {'rows': drafts_rows})


def contracts(request):
    status = request.GET.get('status', 'active')
    rows = [
        {'number': 'SH-12/26', 'party': '"ORIENT TRADE" MChJ', 'status': 'Faol', 'key': 'active'},
        {'number': 'SH-01/25', 'party': '"OLD PARTNER" MChJ', 'status': 'Tugagan', 'key': 'ended'},
    ]
    filtered = [r for r in rows if r['key'] == status] if status != 'all' else rows
    return render(
        request,
        'ehf/contracts.html',
        {'rows': filtered, 'active_status': status},
    )


def archive(request):
    return render(request, 'ehf/archive.html', {'rows': DEMO_DOCS})
