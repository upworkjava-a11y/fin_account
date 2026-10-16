from django.shortcuts import render

GROUPS = [
    ('building', '🏢 Bino va inshootlar'),
    ('transport', '🚗 Transport vositalari'),
    ('it', '💻 Kompyuter va ofis texnikasi'),
    ('equipment', '🏭 Uskunalar va jihozlar'),
    ('furniture', '🪑 Mebel va inventarlar'),
    ('other', '⚙️ Boshqa asosiy vositalar'),
]

DEMO_ASSETS = [
    {
        'inv': 'AV-001',
        'name': 'Ofis binosi',
        'type': 'building',
        'type_label': '🏢 Bino va inshootlar',
        'buy_date': '01.01.2020',
        'initial': '1 200 000 000',
        'rate': '5%',
        'residual': '840 000 000',
        'place': 'Toshkent, Yakkasaroy',
        'responsible': 'Rahimov A.',
        'status': 'Aktiv',
        'source': 'my.soliq.uz',
    },
    {
        'inv': 'AV-014',
        'name': 'Chevrolet Cobalt',
        'type': 'transport',
        'type_label': '🚗 Transport vositalari',
        'buy_date': '15.06.2023',
        'initial': '145 000 000',
        'rate': '20%',
        'residual': '87 000 000',
        'place': 'Asosiy ofis',
        'responsible': 'Karimov B.',
        'status': 'Aktiv',
        'source': 'manual',
    },
    {
        'inv': 'AV-088',
        'name': 'Dell OptiPlex',
        'type': 'it',
        'type_label': '💻 Kompyuter va ofis texnikasi',
        'buy_date': '10.02.2025',
        'initial': '8 500 000',
        'rate': '40%',
        'residual': '5 100 000',
        'place': 'Buxgalteriya',
        'responsible': 'Usmonova D.',
        'status': 'Aktiv',
        'source': 'manual',
    },
]


def asset_registry(request):
    group = request.GET.get('group', '')
    assets = DEMO_ASSETS
    if group:
        assets = [a for a in DEMO_ASSETS if a['type'] == group]
    return render(
        request,
        'assets/registry.html',
        {'assets': assets, 'groups': GROUPS, 'active_group': group},
    )


def asset_depreciation(request):
    return render(request, 'assets/depreciation.html', {'assets': DEMO_ASSETS})


def asset_inventory(request):
    return render(request, 'assets/inventory.html', {'assets': DEMO_ASSETS})
