from django.shortcuts import render

DEMO_PAYMENTS = [
    {
        'number': 'TP-2026-0142',
        'code': '101010',
        'name': 'QQS',
        'date': '15.03.2026',
        'amount': '12 450 000',
        'status': 'Qabul qilingan',
    },
    {
        'number': 'TP-2026-0188',
        'code': '103010',
        'name': 'JShDS',
        'date': '05.04.2026',
        'amount': '3 200 000',
        'status': 'Jo‘natilgan',
    },
]

DEMO_COUNTERPARTIES = [
    {
        'name': '"SARDORBEK SERVIS" MChJ',
        'stir': '305556789',
        'contract': 'SH-45/26',
        'ehf': 'EHF-8891',
        'debit': '1 000 000',
        'credit': '0',
        'last_op': '12.04.2026',
        'status': 'Qarzdorlik yopildi',
    },
    {
        'name': '"ORIENT TRADE" MChJ',
        'stir': '301112233',
        'contract': 'SH-12/26',
        'ehf': 'EHF-9022',
        'debit': '0',
        'credit': '4 500 000',
        'last_op': '01.04.2026',
        'status': 'Kreditorka',
    },
]


def payment_history(request):
    return render(request, 'payments/history.html', {'payments': DEMO_PAYMENTS})


def payment_create(request):
    return render(request, 'payments/create.html')


def recon_tax(request):
    return render(
        request,
        'payments/recon_tax.html',
        {
            'debt': '2 150 000',
            'overpay': '0',
            'status': 'Hisob-kitob ochiq',
        },
    )


def recon_counterparties(request):
    return render(
        request,
        'payments/recon_counterparties.html',
        {'rows': DEMO_COUNTERPARTIES},
    )
