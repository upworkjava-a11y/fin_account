from django.shortcuts import render

ORG_DATA = {
    'stir': '305556789',
    'oked': '62010',
    'soogu': '12345',
    'name': 'Demo Korxona MChJ',
    'tax_type': 'QQS to‘lovchisi',
    'director': 'Rahimov Aziz',
    'accountant': 'Karimova Dilnoza',
}

BANK_ACCOUNTS = [
    {
        'type': 'Asosiy hisob raqami',
        'number': '20208000486684884001',
        'mfo': '00580',
        'bank': 'Ipoteka bank, Tinchlik filiali',
    },
    {
        'type': 'Ikkilamchi hisob raqami',
        'number': '20208000999887766002',
        'mfo': '00014',
        'bank': 'Hamkorbank',
    },
]

DOCUMENTS = [
    {'name': 'Korxona guvohnomasi', 'file': 'guvohnoma.pdf', 'uploaded': '01.02.2026'},
    {'name': 'Korxona ustavi', 'file': 'ustav.pdf', 'uploaded': '01.02.2026'},
]


def org_main(request):
    return render(request, 'organization/main.html', {'org': ORG_DATA})


def org_documents(request):
    return render(request, 'organization/documents.html', {'documents': DOCUMENTS})


def org_banks(request):
    return render(request, 'organization/banks.html', {'accounts': BANK_ACCOUNTS})


def org_telegram(request):
    phones = ['+998 90 111 22 33', '+998 93 444 55 66']
    return render(request, 'organization/telegram.html', {'phones': phones})
