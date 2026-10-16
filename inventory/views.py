from django.shortcuts import render

DEMO_ITEMS = [
    {
        'code': 'TMZ-001',
        'name': 'Shakar',
        'unit': 'kg',
        'warehouse': 'Asosiy ombor',
        'qty': '100',
        'avg_cost': '12 000',
        'total': '1 200 000',
    },
    {
        'code': 'TMZ-002',
        'name': "Yog'",
        'unit': 'dona',
        'warehouse': 'Savdo ombori',
        'qty': '50',
        'avg_cost': '45 000',
        'total': '2 250 000',
    },
]

DEMO_MOVEMENTS = [
    {
        'date': '02.04.2026',
        'type': 'Kirim',
        'doc': 'EHF-8891',
        'product': 'Shakar',
        'qty': '100',
    },
    {
        'date': '03.04.2026',
        'type': 'Chiqim',
        'doc': 'AKT-12',
        'product': "Yog'",
        'qty': '5',
    },
]


def tmz_registry(request):
    return render(request, 'inventory/registry.html', {'items': DEMO_ITEMS})


def tmz_movements(request):
    return render(request, 'inventory/movements.html', {'rows': DEMO_MOVEMENTS})


def tmz_warehouses(request):
    warehouses = [
        {'name': 'Asosiy ombor', 'items': 42},
        {'name': 'Savdo ombori', 'items': 18},
        {'name': 'Ishlab chiqarish ombori', 'items': 7},
    ]
    return render(request, 'inventory/warehouses.html', {'warehouses': warehouses})


def tmz_inventory(request):
    return render(request, 'inventory/inventory_check.html', {'items': DEMO_ITEMS})
