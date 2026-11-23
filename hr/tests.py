from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from .models import Department, Employee, HrOrder, Workplace, ensure_hr_seed
from .services import is_cyrillic_name, parse_stavka


class HrModuleTests(TestCase):
    def setUp(self):
        ensure_hr_seed()
        self.client = Client()

    def test_personnel_card_loads(self):
        response = self.client.get(reverse('hr_employees'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bo‘lim yaratish')

    def test_create_department_rejects_latin_russian_name(self):
        response = self.client.post(
            reverse('hr_department_new'),
            {
                'parent_id': 'none',
                'name_uz': 'Yangi bo‘lim',
                'name_ru': 'Technical',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'rus tilida')
        self.assertFalse(Department.objects.filter(name_uz='Yangi bo‘lim').exists())

    def test_create_workplace_with_staff_table(self):
        dept = Department.objects.filter(is_none=False).first()
        before = Workplace.objects.filter(department=dept, status=Workplace.STATUS_VACANT).count()
        response = self.client.post(
            reverse('hr_workplace_new'),
            {
                'department_id': str(dept.id),
                'classifier_title': 'Hamshira',
                'title_uz': 'Hamshira',
                'stavka_whole': '0',
                'stavka_frac': '50',
                'salary_staff': 'on',
                'salary_amount': '',
                'count': '2',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Workplace.objects.filter(department=dept, status=Workplace.STATUS_VACANT).count(),
            before + 2,
        )
        seat = Workplace.objects.filter(title_uz='Hamshira').first()
        self.assertEqual(seat.stavka, Decimal('0.50'))
        self.assertEqual(seat.salary_mode, Workplace.SALARY_STAFF)

    def test_paper_hire_flow(self):
        seat = Workplace.objects.filter(status=Workplace.STATUS_VACANT).first()
        start = self.client.post(
            reverse('hr_hire', args=[seat.id]),
            {
                'citizenship': 'uz',
                'passport_series': 'AA',
                'passport_number': '7654321',
                'pinfl': '30111223344556',
                'last_name': 'Karimova',
                'first_name': 'Dilnoza',
                'middle_name': 'Aziz qizi',
                'birth_date': '12.03.1992',
                'gender': 'female',
                'hire_mode': 'paper',
            },
        )
        self.assertEqual(start.status_code, 302)
        privacy = self.client.post(
            reverse('hr_hire_contract', args=[seat.id]),
            {'action': 'accept_privacy'},
        )
        self.assertEqual(privacy.status_code, 302)
        save = self.client.post(
            reverse('hr_hire_contract', args=[seat.id]),
            {
                'contract_number': '55',
                'contract_date': '10.11.2026',
                'indefinite': 'on',
                'end_date': '',
                'contract_type': 'main',
                'start_date': '10.11.2026',
                'stavka': '1.00',
                'order_number': '12-K',
                'order_date': '10.11.2026',
            },
        )
        self.assertEqual(save.status_code, 302)
        seat.refresh_from_db()
        self.assertEqual(seat.status, Workplace.STATUS_OCCUPIED)
        self.assertTrue(Employee.objects.filter(pinfl='30111223344556').exists())
        self.assertTrue(HrOrder.objects.filter(number='12-K').exists())

    def test_helpers(self):
        self.assertTrue(is_cyrillic_name('Технический отдел'))
        self.assertFalse(is_cyrillic_name('Technical'))
        self.assertEqual(parse_stavka('1', '25'), Decimal('1.25'))
        self.assertIsNone(parse_stavka('1', '75'))
