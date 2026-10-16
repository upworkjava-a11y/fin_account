from django.shortcuts import render

JOURNAL_TABS = [
    'checking',
    'error',
    'accepted',
    'sent',
    'rejected',
    'draft',
    'auto',
]

# Demo: taxpayer type QQS → show related report cards
FORMING_REPORTS = [
    {'title': 'QQS hisoboti', 'period': '1-chorak 2026', 'status': 'Tayyorlash mumkin'},
    {'title': 'Buxgalteriya balansi', 'period': '2025', 'status': 'Shakllanmoqda'},
    {'title': 'Moliyaviy natijalar to‘g‘risidagi hisobot', 'period': '2025', 'status': 'Tayyorlash mumkin'},
    {'title': 'JShDS va ijtimoiy soliq hisob-kitobi', 'period': 'Mart 2026', 'status': 'Tayyorlash mumkin'},
    {'title': 'INPS reyestri', 'period': 'Mart 2026', 'status': 'Tayyorlash mumkin'},
    {'title': 'Mol-mulk, yer va suv soliqlari', 'period': '2026', 'status': 'Kutilmoqda'},
]


def tax_forms(request):
    forms = [
        {'code': '10001', 'name': 'QQS hisoboti', 'period': 'Choraklik'},
        {'code': '10002', 'name': 'Aylanmadan olinadigan soliq', 'period': 'Oylik'},
        {'code': '10003', 'name': 'JShDS va ijtimoiy soliq', 'period': 'Oylik'},
    ]
    return render(request, 'tax/forms.html', {'forms': forms})


def tax_journal(request):
    tab = request.GET.get('tab', 'accepted')
    if tab not in JOURNAL_TABS:
        tab = 'accepted'
    year = request.GET.get('year', '')
    packet = request.GET.get('packet', '')
    rows = []
    if year:
        rows = [
            {
                'name': 'QQS hisoboti',
                'period': f'1-chorak {year}',
                'packet': packet or 'P-10021',
                'sent': f'15.04.{year}',
                'status': 'Qabul qilingan',
                'updated': f'16.04.{year}',
            },
            {
                'name': 'JShDS',
                'period': f'Mart {year}',
                'packet': packet or 'P-10045',
                'sent': f'10.04.{year}',
                'status': 'Qabul qilingan',
                'updated': f'11.04.{year}',
            },
        ]
    return render(
        request,
        'tax/journal.html',
        {
            'active_tab': tab,
            'selected_year': year,
            'packet': packet,
            'show_rows': bool(year),
            'rows': rows,
        },
    )


def tax_forming(request):
    return render(
        request,
        'tax/forming.html',
        {
            'tax_type': 'QQS to‘lovchisi',
            'reports': FORMING_REPORTS,
        },
    )
