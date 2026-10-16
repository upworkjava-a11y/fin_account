from django.shortcuts import render

DEMO_ACCOUNTS = [
    {
        'title': 'Asosiy hisob raqami',
        'number': '20208000486684884001',
        'mfo': '00580',
        'bank': 'Ipoteka bank, Tinchlik filiali',
        'balance': '125 450 000',
        'last_period': '01.01.2026 - 31.03.2026',
        'last_end': '2026-03-31',
    },
    {
        'title': '2-hisob raqami',
        'number': '20208000999887766002',
        'mfo': '00014',
        'bank': 'Hamkorbank',
        'balance': '42 100 000',
        'last_period': '01.01.2026 - 31.03.2026',
        'last_end': '2026-03-31',
    },
    {
        'title': 'Valyuta hisob raqami',
        'number': '20208800111222333003',
        'mfo': '00445',
        'bank': 'Kapitalbank',
        'balance': '12 500 USD',
        'last_period': '01.01.2026 - 31.03.2026',
        'last_end': '2026-03-31',
    },
]

ARCHIVE_ROWS = [
    {
        'type': 'Asosiy',
        'account': '20208000486684884001',
        'bank': 'Ipoteka bank',
        'period': '01.01.2026 – 31.03.2026',
        'uploaded': '01.04.2026',
        'file': 'oborotka_Q1.xlsx',
        'ops': 128,
    },
    {
        'type': 'Asosiy',
        'account': '20208000486684884001',
        'bank': 'Ipoteka bank',
        'period': '01.04.2026 – 30.06.2026',
        'uploaded': '01.07.2026',
        'file': 'oborotka_Q2.xlsx',
        'ops': 154,
    },
    {
        'type': 'Ikkilamchi',
        'account': '20208000999887766002',
        'bank': 'Hamkorbank',
        'period': '01.01.2026 – 31.03.2026',
        'uploaded': '01.04.2026',
        'file': 'hamkor_Q1.xlsx',
        'ops': 64,
    },
]


def bank_turnover(request):
    return render(request, 'bank/turnover.html', {'accounts': DEMO_ACCOUNTS})


def bank_auto(request):
    year = request.GET.get('year', '2026')
    month = request.GET.get('month', '1')
    return render(
        request,
        'bank/auto_entries.html',
        {'selected_year': year, 'selected_month': month},
    )


def bank_archive(request):
    return render(request, 'bank/archive.html', {'rows': ARCHIVE_ROWS})
