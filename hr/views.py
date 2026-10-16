from django.shortcuts import render

DEMO_EMPLOYEES = [
    {
        'fio': 'Karimova Dilnoza',
        'pinfl': '31234567890123',
        'birth': '12.03.1992',
        'phone': '+998 90 111 22 33',
        'position': 'Bosh buxgalter',
        'dept': 'Buxgalteriya',
        'hired': '01.02.2021',
        'salary': '8 500 000',
        'status': 'Aktiv',
    },
    {
        'fio': 'Rahimov Aziz',
        'pinfl': '30111223344556',
        'birth': '05.08.1988',
        'phone': '+998 93 444 55 66',
        'position': 'Direktor',
        'dept': 'Boshqaruv',
        'hired': '15.01.2019',
        'salary': '15 000 000',
        'status': 'Aktiv',
    },
    {
        'fio': 'Usmarov Jasur',
        'pinfl': '30999887766554',
        'birth': '21.11.1995',
        'phone': '+998 97 777 88 99',
        'position': 'Omborchi',
        'dept': 'Ombor',
        'hired': '10.06.2022',
        'salary': '4 200 000',
        'status': 'Bo‘shagan',
    },
]

DEMO_ORDERS = [
    {
        'number': 'BY-001',
        'date': '01.02.2021',
        'employee': 'Karimova Dilnoza',
        'type': 'Ishga qabul qilish',
        'status': 'Yuborilgan',
    },
    {
        'number': 'BY-088',
        'date': '01.03.2026',
        'employee': 'Usmarov Jasur',
        'type': 'Ishdan bo‘shatish',
        'status': 'Yuborilgan',
    },
]


def employees(request):
    return render(request, 'hr/employees.html', {'employees': DEMO_EMPLOYEES})


def payroll(request):
    return render(request, 'hr/payroll.html', {'employees': DEMO_EMPLOYEES})


def pit_social(request):
    return render(request, 'hr/pit_social.html', {'employees': DEMO_EMPLOYEES})


def orders_archive(request):
    return render(request, 'hr/orders.html', {'orders': DEMO_ORDERS})
