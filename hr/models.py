from decimal import Decimal

from django.db import models


class Department(models.Model):
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, blank=True)
    is_none = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name_uz

    @property
    def employee_count(self):
        return self.workplaces.filter(status=Workplace.STATUS_OCCUPIED).count()


class Workplace(models.Model):
    STATUS_VACANT = 'vacant'
    STATUS_OCCUPIED = 'occupied'
    STATUS_CHOICES = [
        (STATUS_VACANT, 'Vakant'),
        (STATUS_OCCUPIED, 'Band'),
    ]
    SALARY_AMOUNT = 'amount'
    SALARY_STAFF = 'staff_table'
    SALARY_CHOICES = [
        (SALARY_AMOUNT, 'Oklad'),
        (SALARY_STAFF, 'Shtat jadvali'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='workplaces')
    classifier_title = models.CharField(max_length=255)
    title_uz = models.CharField(max_length=255)
    stavka = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
    salary_mode = models.CharField(max_length=20, choices=SALARY_CHOICES, default=SALARY_AMOUNT)
    salary_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_VACANT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.title_uz} ({self.get_status_display()})'

    @property
    def salary_display(self):
        if self.salary_mode == self.SALARY_STAFF:
            return 'Shtat jadvaliga muvofiq'
        if self.salary_amount is None:
            return '—'
        return f'{self.salary_amount:,.0f}'.replace(',', ' ')


class Employee(models.Model):
    CITIZEN_UZ = 'uz'
    CITIZEN_FOREIGN = 'foreign'
    CITIZEN_CHOICES = [
        (CITIZEN_UZ, "O'zbekiston Respublikasi fuqarosi"),
        (CITIZEN_FOREIGN, "Chet el fuqarosi / Fuqaroligi bo'lmagan shaxs"),
    ]
    GENDER_M = 'male'
    GENDER_F = 'female'
    GENDER_CHOICES = [
        (GENDER_M, 'Erkak'),
        (GENDER_F, 'Ayol'),
    ]

    workplace = models.OneToOneField(Workplace, on_delete=models.CASCADE, related_name='employee')
    citizenship = models.CharField(max_length=20, choices=CITIZEN_CHOICES, default=CITIZEN_UZ)
    passport_series = models.CharField(max_length=2, blank=True)
    passport_number = models.CharField(max_length=10, blank=True)
    pinfl = models.CharField(max_length=14, blank=True)
    last_name = models.CharField(max_length=120)
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    hired_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(p for p in parts if p).strip()

    @property
    def fio_short(self):
        return f'{self.last_name} {self.first_name}'.strip()


class LaborContract(models.Model):
    MODE_PAPER = 'paper'
    MODE_ELECTRONIC = 'electronic'
    MODE_CHOICES = [
        (MODE_PAPER, "Qog'oz"),
        (MODE_ELECTRONIC, 'Elektron'),
    ]
    TYPE_MAIN = 'main'
    TYPE_EXTERNAL = 'external'
    TYPE_CHOICES = [
        (TYPE_MAIN, 'Asosiy ish bo‘yicha'),
        (TYPE_EXTERNAL, 'Tashqi o‘rindoshlik bo‘yicha'),
    ]

    workplace = models.ForeignKey(Workplace, on_delete=models.CASCADE, related_name='contracts')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    form_type = models.PositiveSmallIntegerField(null=True, blank=True)
    contract_number = models.CharField(max_length=64, blank=True)
    contract_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    indefinite = models.BooleanField(default=False)
    contract_type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    start_date = models.DateField(null=True, blank=True)
    stavka = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    order_number = models.CharField(max_length=64, blank=True)
    order_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class HrOrder(models.Model):
    number = models.CharField(max_length=64)
    date = models.DateField()
    employee_name = models.CharField(max_length=255)
    order_type = models.CharField(max_length=120)
    status = models.CharField(max_length=64, default='Yuborilgan')
    workplace = models.ForeignKey(
        Workplace,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.number} — {self.employee_name}'


def _seat(department, *, title, stavka, salary_mode, salary_amount=None, status):
    existing = Workplace.objects.filter(department=department, title_uz=title).first()
    if existing:
        return existing
    return Workplace.objects.create(
        department=department,
        classifier_title=title,
        title_uz=title,
        stavka=Decimal(stavka),
        salary_mode=salary_mode,
        salary_amount=salary_amount,
        status=status,
    )


def _employee(workplace, **kwargs):
    existing = Employee.objects.filter(workplace=workplace).first()
    if existing:
        return existing
    return Employee.objects.create(workplace=workplace, **kwargs)


def ensure_hr_seed():
    """Create baseline departments and 4–5 sample workplaces/employees."""
    from datetime import date

    none_dept, _ = Department.objects.get_or_create(
        is_none=True,
        defaults={'name_uz': "Bo‘linma mavjud emas", 'name_ru': '', 'sort_order': 0},
    )

    def dept(name_uz, name_ru, sort_order):
        obj, _ = Department.objects.get_or_create(
            name_uz=name_uz,
            defaults={'parent': none_dept, 'name_ru': name_ru, 'sort_order': sort_order},
        )
        return obj

    kasanachilik = dept('Kasanachilik', 'Надомничество', 1)
    doctors = dept("Doktorlar bo‘limi", 'Отдел врачей', 2)
    accounting = dept('Buxgalteriya', 'Бухгалтерия', 3)
    management = dept('Boshqaruv', 'Управление', 4)
    warehouse = dept('Ombor', 'Склад', 5)
    tech = dept('Texnik bo‘lim', 'Технический отдел', 6)

    vacant_micro = _seat(
        doctors,
        title='Bosh mikrobiolog',
        stavka='1.00',
        salary_mode=Workplace.SALARY_STAFF,
        status=Workplace.STATUS_VACANT,
    )
    occupied_doctor = _seat(
        doctors,
        title='Bosh vrach',
        stavka='1.00',
        salary_mode=Workplace.SALARY_STAFF,
        status=Workplace.STATUS_OCCUPIED,
    )
    vacant_nurse = _seat(
        doctors,
        title='Bosh hamshira',
        stavka='0.75',
        salary_mode=Workplace.SALARY_AMOUNT,
        salary_amount=Decimal('4500000'),
        status=Workplace.STATUS_VACANT,
    )
    occupied_accountant = _seat(
        accounting,
        title='Bosh buxgalter',
        stavka='1.00',
        salary_mode=Workplace.SALARY_AMOUNT,
        salary_amount=Decimal('8500000'),
        status=Workplace.STATUS_OCCUPIED,
    )
    vacant_accountant = _seat(
        accounting,
        title='Buxgalter',
        stavka='1.00',
        salary_mode=Workplace.SALARY_AMOUNT,
        salary_amount=Decimal('5500000'),
        status=Workplace.STATUS_VACANT,
    )
    occupied_director = _seat(
        management,
        title='Direktor',
        stavka='1.00',
        salary_mode=Workplace.SALARY_AMOUNT,
        salary_amount=Decimal('15000000'),
        status=Workplace.STATUS_OCCUPIED,
    )
    occupied_store = _seat(
        warehouse,
        title='Omborchi',
        stavka='1.00',
        salary_mode=Workplace.SALARY_AMOUNT,
        salary_amount=Decimal('4200000'),
        status=Workplace.STATUS_OCCUPIED,
    )
    vacant_dev = _seat(
        tech,
        title='Dasturchi',
        stavka='1.00',
        salary_mode=Workplace.SALARY_AMOUNT,
        salary_amount=Decimal('12000000'),
        status=Workplace.STATUS_VACANT,
    )
    vacant_home = _seat(
        kasanachilik,
        title='Uy ishchisi',
        stavka='0.50',
        salary_mode=Workplace.SALARY_STAFF,
        status=Workplace.STATUS_VACANT,
    )

    emp_doctor = _employee(
        occupied_doctor,
        citizenship=Employee.CITIZEN_UZ,
        passport_series='AA',
        passport_number='1234567',
        pinfl='42005933100054',
        last_name='Atajonova',
        first_name="Ma’muraxon",
        middle_name='Mansur qizi',
        birth_date=date(1990, 5, 12),
        gender=Employee.GENDER_F,
        phone='+998 90 111 22 33',
        hired_at=date(2021, 2, 1),
    )
    emp_acc = _employee(
        occupied_accountant,
        citizenship=Employee.CITIZEN_UZ,
        passport_series='AB',
        passport_number='7654321',
        pinfl='31234567890123',
        last_name='Karimova',
        first_name='Dilnoza',
        middle_name='Akmal qizi',
        birth_date=date(1992, 3, 12),
        gender=Employee.GENDER_F,
        phone='+998 93 222 33 44',
        hired_at=date(2021, 2, 1),
    )
    emp_dir = _employee(
        occupied_director,
        citizenship=Employee.CITIZEN_UZ,
        passport_series='AC',
        passport_number='1122334',
        pinfl='30111223344556',
        last_name='Rahimov',
        first_name='Aziz',
        middle_name='Karim o‘g‘li',
        birth_date=date(1988, 8, 5),
        gender=Employee.GENDER_M,
        phone='+998 97 555 66 77',
        hired_at=date(2019, 1, 15),
    )
    emp_store = _employee(
        occupied_store,
        citizenship=Employee.CITIZEN_UZ,
        passport_series='AD',
        passport_number='9988776',
        pinfl='30999887766554',
        last_name='Usmarov',
        first_name='Jasur',
        middle_name='Olim o‘g‘li',
        birth_date=date(1995, 11, 21),
        gender=Employee.GENDER_M,
        phone='+998 91 888 99 00',
        hired_at=date(2022, 6, 10),
    )

    # Drop temporary departments left by automated QA posts.
    Department.objects.filter(name_uz__startswith='QA Test').delete()

    samples = [
        ('BY-001', date(2021, 2, 1), emp_doctor.full_name, occupied_doctor),
        ('BY-014', date(2021, 2, 1), emp_acc.full_name, occupied_accountant),
        ('BY-002', date(2019, 1, 15), emp_dir.full_name, occupied_director),
        ('BY-088', date(2022, 6, 10), emp_store.full_name, occupied_store),
        ('BY-110', date(2026, 3, 1), 'Vakant — Bosh hamshira', vacant_nurse),
    ]
    for number, order_date, name, workplace in samples:
        HrOrder.objects.get_or_create(
            number=number,
            defaults={
                'date': order_date,
                'employee_name': name,
                'order_type': 'Ishga qabul qilish',
                'status': 'Yuborilgan',
                'workplace': workplace,
            },
        )

    _ = vacant_micro, vacant_accountant, vacant_dev, vacant_home
    return none_dept
