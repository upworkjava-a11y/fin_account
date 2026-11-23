from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .classifier import CLASSIFIER_TITLES, E_CONTRACT_FORMS
from .models import Department, Employee, HrOrder, LaborContract, Workplace, ensure_hr_seed
from .services import (
    format_date,
    is_cyrillic_name,
    parse_date,
    parse_money,
    parse_stavka,
    validate_uz_personal,
)

HIRE_SESSION_KEY = 'hr_hire'


def _seed(request):
    ensure_hr_seed()


def _hire_store(request, workplace_id, payload):
    data = request.session.get(HIRE_SESSION_KEY) or {}
    data[str(workplace_id)] = payload
    request.session[HIRE_SESSION_KEY] = data
    request.session.modified = True


def _hire_get(request, workplace_id):
    return (request.session.get(HIRE_SESSION_KEY) or {}).get(str(workplace_id))


def _hire_clear(request, workplace_id):
    data = request.session.get(HIRE_SESSION_KEY) or {}
    data.pop(str(workplace_id), None)
    request.session[HIRE_SESSION_KEY] = data
    request.session.modified = True


def personnel_card(request):
    _seed(request)
    departments = list(Department.objects.all())
    dept_id = request.GET.get('dept')
    selected = None
    if dept_id:
        selected = Department.objects.filter(pk=dept_id).first()
    if selected is None:
        with_seats = (
            Department.objects.filter(workplaces__isnull=False)
            .distinct()
            .order_by('sort_order', 'id')
            .first()
        )
        selected = with_seats or next(
            (d for d in departments if not d.is_none),
            departments[0] if departments else None,
        )

    workplaces = Workplace.objects.none()
    if selected:
        workplaces = (
            Workplace.objects.filter(department=selected)
            .select_related('employee')
            .order_by('status', 'id')
        )

    q_pinfl = (request.GET.get('pinfl') or '').strip()
    q_first = (request.GET.get('first_name') or '').strip()
    q_last = (request.GET.get('last_name') or '').strip()
    q_middle = (request.GET.get('middle_name') or '').strip()
    q_position = (request.GET.get('position') or '').strip()
    q_dept = (request.GET.get('filter_dept') or '').strip()

    if any([q_pinfl, q_first, q_last, q_middle, q_position, q_dept]):
        qs = Workplace.objects.select_related('employee', 'department')
        if q_dept:
            qs = qs.filter(department_id=q_dept)
        if q_position:
            qs = qs.filter(Q(title_uz__icontains=q_position) | Q(classifier_title__icontains=q_position))
        if q_pinfl:
            qs = qs.filter(employee__pinfl__icontains=q_pinfl)
        if q_first:
            qs = qs.filter(employee__first_name__icontains=q_first)
        if q_last:
            qs = qs.filter(employee__last_name__icontains=q_last)
        if q_middle:
            qs = qs.filter(employee__middle_name__icontains=q_middle)
        workplaces = qs.order_by('department_id', 'id')
        if q_dept:
            selected = Department.objects.filter(pk=q_dept).first() or selected

    positions = (
        Workplace.objects.order_by('title_uz')
        .values_list('title_uz', flat=True)
        .distinct()
    )

    return render(
        request,
        'hr/personnel_card.html',
        {
            'departments': departments,
            'selected_dept': selected,
            'workplaces': workplaces,
            'positions': positions,
            'filters': {
                'pinfl': q_pinfl,
                'first_name': q_first,
                'last_name': q_last,
                'middle_name': q_middle,
                'position': q_position,
                'filter_dept': q_dept,
            },
            'hr_mode': 'cards',
            'format_date': format_date,
        },
    )


@require_http_methods(['GET', 'POST'])
def department_form(request, pk=None):
    _seed(request)
    department = get_object_or_404(Department, pk=pk) if pk else None
    if department and department.is_none:
        messages.error(request, "Bu bo‘limni tahrirlash mumkin emas.")
        return redirect('hr_employees')

    parents = Department.objects.all()
    errors = []
    if department and department.parent_id:
        parent_value = (
            'none'
            if department.parent and department.parent.is_none
            else str(department.parent_id)
        )
    else:
        parent_value = 'none'
    form = {
        'parent_id': parent_value,
        'name_uz': department.name_uz if department else '',
        'name_ru': department.name_ru if department else '',
    }

    if request.method == 'POST':
        form['parent_id'] = request.POST.get('parent_id') or 'none'
        form['name_uz'] = (request.POST.get('name_uz') or '').strip()
        form['name_ru'] = (request.POST.get('name_ru') or '').strip()
        if not form['name_uz']:
            errors.append("Bo‘limning davlat tilidagi nomi majburiy.")
        if form['name_ru'] and not is_cyrillic_name(form['name_ru']):
            errors.append("Bo‘lim nomini rus tilida kiriting.")
        parent = Department.objects.filter(is_none=True).first()
        if form['parent_id'] not in ('', 'none'):
            chosen = Department.objects.filter(pk=form['parent_id']).first()
            if chosen and not chosen.is_none:
                parent = chosen
        if not errors:
            if department:
                department.parent = parent
                department.name_uz = form['name_uz']
                department.name_ru = form['name_ru']
                department.save()
                messages.success(request, "Bo‘lim yangilandi.")
            else:
                department = Department.objects.create(
                    parent=parent,
                    name_uz=form['name_uz'],
                    name_ru=form['name_ru'],
                    sort_order=Department.objects.count() + 1,
                )
                messages.success(request, "Bo‘lim saqlandi.")
            return redirect(f"{reverse('hr_employees')}?dept={department.pk}")

    return render(
        request,
        'hr/department_form.html',
        {
            'department': department,
            'parents': parents,
            'form': form,
            'errors': errors,
            'hr_mode': 'cards',
        },
    )


@require_http_methods(['GET', 'POST'])
def workplace_create(request):
    _seed(request)
    departments = Department.objects.all()
    dept_id = request.GET.get('dept') or request.POST.get('department_id')
    errors = []
    form = {
        'department_id': dept_id or '',
        'classifier_title': '',
        'title_uz': '',
        'stavka_whole': '1',
        'stavka_frac': '00',
        'salary_amount': '',
        'salary_staff': False,
        'count': '1',
    }

    if request.method == 'POST':
        form['department_id'] = request.POST.get('department_id') or ''
        form['classifier_title'] = (request.POST.get('classifier_title') or '').strip()
        form['title_uz'] = (request.POST.get('title_uz') or '').strip()
        form['stavka_whole'] = request.POST.get('stavka_whole') or '0'
        form['stavka_frac'] = request.POST.get('stavka_frac') or '00'
        form['salary_amount'] = request.POST.get('salary_amount') or ''
        form['salary_staff'] = request.POST.get('salary_staff') == 'on'
        form['count'] = request.POST.get('count') or '1'

        dept = Department.objects.filter(pk=form['department_id']).first()
        if not dept:
            errors.append("Bo‘linmani tanlang.")
        if not form['classifier_title']:
            errors.append('Lavozim / kasb nomi majburiy.')
        if not form['title_uz']:
            errors.append('Lavozimning to‘liq nomi majburiy.')
        stavka = parse_stavka(form['stavka_whole'], form['stavka_frac'])
        if stavka is None:
            errors.append('Stavka qiymati noto‘g‘ri.')
        salary_mode = Workplace.SALARY_STAFF if form['salary_staff'] else Workplace.SALARY_AMOUNT
        salary_amount = None
        if form['salary_staff'] and form['salary_amount'].strip():
            errors.append('Oklad va shtat jadvali birga tanlanmaydi.')
        if not form['salary_staff']:
            salary_amount = parse_money(form['salary_amount'])
            if salary_amount is None:
                errors.append('Oklad summasini kiriting yoki shtat jadvalini belgilang.')
        try:
            count = int(form['count'])
            if count < 1:
                raise ValueError
        except ValueError:
            errors.append("Ish o‘rinlari soni 1 yoki undan katta bo‘lishi kerak.")
            count = 1

        if not errors:
            created = []
            for _ in range(count):
                created.append(
                    Workplace.objects.create(
                        department=dept,
                        classifier_title=form['classifier_title'],
                        title_uz=form['title_uz'],
                        stavka=stavka,
                        salary_mode=salary_mode,
                        salary_amount=salary_amount,
                        status=Workplace.STATUS_VACANT,
                    )
                )
            messages.success(request, f"{len(created)} ta ish o‘rni yaratildi.")
            return redirect(f"{reverse('hr_employees')}?dept={dept.pk}")

    frac_options_0 = [f'{i:02d}' for i in range(0, 100)]
    frac_options_1 = [f'{i:02d}' for i in range(0, 51)]
    return render(
        request,
        'hr/workplace_form.html',
        {
            'departments': departments,
            'form': form,
            'errors': errors,
            'classifier_titles': CLASSIFIER_TITLES,
            'frac_options_0': frac_options_0,
            'frac_options_1': frac_options_1,
            'hr_mode': 'cards',
        },
    )


@require_http_methods(['GET', 'POST'])
def hire_start(request, workplace_id):
    _seed(request)
    workplace = get_object_or_404(Workplace.objects.select_related('department'), pk=workplace_id)
    if workplace.status != Workplace.STATUS_VACANT:
        messages.error(request, "Bu ish o‘rni band.")
        return redirect(f"{reverse('hr_employees')}?dept={workplace.department_id}")

    stored = _hire_get(request, workplace_id) or {}
    form = {
        'citizenship': stored.get('citizenship', Employee.CITIZEN_UZ),
        'passport_series': stored.get('passport_series', ''),
        'passport_number': stored.get('passport_number', ''),
        'pinfl': stored.get('pinfl', ''),
        'last_name': stored.get('last_name', ''),
        'first_name': stored.get('first_name', ''),
        'middle_name': stored.get('middle_name', ''),
        'birth_date': stored.get('birth_date', ''),
        'gender': stored.get('gender', ''),
        'hire_mode': stored.get('hire_mode', LaborContract.MODE_PAPER),
    }
    errors = []
    foreign_blocked = False

    if request.method == 'POST':
        for key in form:
            if key == 'hire_mode':
                form[key] = request.POST.get('hire_mode') or LaborContract.MODE_PAPER
            elif key == 'citizenship':
                form[key] = request.POST.get('citizenship') or Employee.CITIZEN_UZ
            else:
                form[key] = (request.POST.get(key) or '').strip()
        form['passport_series'] = form['passport_series'].upper()

        if form['citizenship'] == Employee.CITIZEN_FOREIGN:
            foreign_blocked = True
            errors.append("Chet el fuqarolari uchun rasmiylashtirish keyingi bosqichda qo‘shiladi.")
        else:
            errors.extend(validate_uz_personal(form))
            if form['hire_mode'] not in (LaborContract.MODE_PAPER, LaborContract.MODE_ELECTRONIC):
                errors.append('Rasmiylashtirish usulini tanlang.')

        if not errors:
            payload = dict(form)
            payload['privacy_accepted'] = False
            _hire_store(request, workplace_id, payload)
            if form['hire_mode'] == LaborContract.MODE_ELECTRONIC:
                return redirect('hr_hire_eform', workplace_id=workplace_id)
            return redirect('hr_hire_contract', workplace_id=workplace_id)

    return render(
        request,
        'hr/hire_start.html',
        {
            'workplace': workplace,
            'form': form,
            'errors': errors,
            'foreign_blocked': foreign_blocked,
            'hr_mode': 'cards',
            'show_privacy_modal': False,
        },
    )


@require_http_methods(['GET', 'POST'])
def hire_contract(request, workplace_id):
    _seed(request)
    workplace = get_object_or_404(Workplace.objects.select_related('department'), pk=workplace_id)
    stored = _hire_get(request, workplace_id)
    if not stored or stored.get('hire_mode') != LaborContract.MODE_PAPER:
        return redirect('hr_hire', workplace_id=workplace_id)
    if workplace.status != Workplace.STATUS_VACANT:
        messages.error(request, "Bu ish o‘rni band.")
        return redirect('hr_employees')

    show_privacy = not stored.get('privacy_accepted')
    errors = []
    today = date.today().strftime('%d.%m.%Y')
    form = {
        'contract_number': '1',
        'contract_date': today,
        'end_date': '',
        'indefinite': True,
        'contract_type': LaborContract.TYPE_MAIN,
        'start_date': today,
        'stavka': f'{workplace.stavka:.2f}',
        'order_number': '',
        'order_date': today,
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept_privacy':
            stored['privacy_accepted'] = True
            _hire_store(request, workplace_id, stored)
            return redirect('hr_hire_contract', workplace_id=workplace_id)

        if not stored.get('privacy_accepted'):
            messages.error(request, "Avval shaxsiy ma’lumotlar shartlari bilan tanishing.")
            return redirect('hr_hire_contract', workplace_id=workplace_id)

        for key in form:
            if key == 'indefinite':
                form[key] = request.POST.get('indefinite') == 'on'
            else:
                form[key] = (request.POST.get(key) or '').strip()

        contract_date = parse_date(form['contract_date'])
        end_date = None if form['indefinite'] else parse_date(form['end_date'])
        start_date = parse_date(form['start_date'])
        order_date = parse_date(form['order_date'])
        try:
            stavka = Decimal(form['stavka'].replace(',', '.'))
        except Exception:
            stavka = None

        if not form['contract_number']:
            errors.append('Shartnoma raqami majburiy.')
        if not contract_date:
            errors.append('Shartnoma sanasi noto‘g‘ri.')
        if not form['indefinite'] and not end_date:
            errors.append('Tugash sanasini kiriting yoki Muddatsiz ni belgilang.')
        if form['contract_type'] not in (LaborContract.TYPE_MAIN, LaborContract.TYPE_EXTERNAL):
            errors.append('Shartnoma turini tanlang.')
        if not start_date:
            errors.append('Ish boshlangan sana noto‘g‘ri.')
        if stavka is None:
            errors.append('Stavka noto‘g‘ri.')
        if not form['order_number']:
            errors.append('Buyruq raqami majburiy.')
        if not order_date:
            errors.append('Buyruq sanasi noto‘g‘ri.')
        if contract_date and order_date and order_date < contract_date:
            errors.append('Buyruq sanasi mehnat shartnomasi tuzilgan sanadan oldin bo‘lishi mumkin emas.')

        if not errors:
            employee = Employee.objects.create(
                workplace=workplace,
                citizenship=stored['citizenship'],
                passport_series=stored['passport_series'].upper(),
                passport_number=stored['passport_number'],
                pinfl=stored['pinfl'],
                last_name=stored['last_name'],
                first_name=stored['first_name'],
                middle_name=stored.get('middle_name') or '',
                birth_date=parse_date(stored.get('birth_date') or ''),
                gender=stored['gender'],
                hired_at=start_date,
            )
            LaborContract.objects.create(
                workplace=workplace,
                employee=employee,
                mode=LaborContract.MODE_PAPER,
                contract_number=form['contract_number'],
                contract_date=contract_date,
                end_date=end_date,
                indefinite=form['indefinite'],
                contract_type=form['contract_type'],
                start_date=start_date,
                stavka=stavka,
                order_number=form['order_number'],
                order_date=order_date,
                status='active',
            )
            workplace.status = Workplace.STATUS_OCCUPIED
            workplace.stavka = stavka
            workplace.save(update_fields=['status', 'stavka'])
            HrOrder.objects.create(
                number=form['order_number'],
                date=order_date,
                employee_name=employee.full_name,
                order_type='Ishga qabul qilish',
                status='Yuborilgan',
                workplace=workplace,
            )
            _hire_clear(request, workplace_id)
            messages.success(request, 'Xodim rasmiylashtirildi.')
            return redirect(f"{reverse('hr_employees')}?dept={workplace.department_id}")

    candidate = f"{stored.get('last_name', '')} {stored.get('first_name', '')} {stored.get('middle_name', '')}".strip()
    return render(
        request,
        'hr/hire_contract.html',
        {
            'workplace': workplace,
            'stored': stored,
            'candidate': candidate,
            'form': form,
            'errors': errors,
            'show_privacy_modal': show_privacy,
            'hr_mode': 'cards',
        },
    )


@require_http_methods(['GET', 'POST'])
def hire_eform(request, workplace_id):
    _seed(request)
    workplace = get_object_or_404(Workplace.objects.select_related('department'), pk=workplace_id)
    stored = _hire_get(request, workplace_id)
    if not stored or stored.get('hire_mode') != LaborContract.MODE_ELECTRONIC:
        return redirect('hr_hire', workplace_id=workplace_id)
    if workplace.status != Workplace.STATUS_VACANT:
        messages.error(request, "Bu ish o‘rni band.")
        return redirect('hr_employees')

    if request.method == 'POST':
        try:
            form_type = int(request.POST.get('form_type') or 0)
        except ValueError:
            form_type = 0
        titles = dict(E_CONTRACT_FORMS)
        if form_type not in titles:
            messages.error(request, 'Shartnoma shaklini tanlang.')
        else:
            candidate = f"{stored.get('last_name', '')} {stored.get('first_name', '')} {stored.get('middle_name', '')}".strip()
            today = date.today()
            employee = Employee.objects.create(
                workplace=workplace,
                citizenship=stored['citizenship'],
                passport_series=(stored.get('passport_series') or '').upper(),
                passport_number=stored.get('passport_number') or '',
                pinfl=stored.get('pinfl') or '',
                last_name=stored['last_name'],
                first_name=stored['first_name'],
                middle_name=stored.get('middle_name') or '',
                birth_date=parse_date(stored.get('birth_date') or ''),
                gender=stored.get('gender') or '',
                hired_at=today,
            )
            LaborContract.objects.create(
                workplace=workplace,
                employee=employee,
                mode=LaborContract.MODE_ELECTRONIC,
                form_type=form_type,
                contract_type=LaborContract.TYPE_MAIN,
                start_date=today,
                stavka=workplace.stavka,
                status='draft',
            )
            workplace.status = Workplace.STATUS_OCCUPIED
            workplace.save(update_fields=['status'])
            HrOrder.objects.create(
                number=f'EL-{workplace.pk}-{form_type}',
                date=today,
                employee_name=candidate or employee.full_name,
                order_type=f'Elektron shartnoma (shakl {form_type})',
                status='Loyiha',
                workplace=workplace,
            )
            _hire_clear(request, workplace_id)
            messages.success(
                request,
                "Elektron shartnoma shakli tanlandi. my.mehnat.uz ga yuborish keyingi bosqichda ulanadi.",
            )
            return redirect(f"{reverse('hr_employees')}?dept={workplace.department_id}")

    candidate = f"{stored.get('last_name', '')} {stored.get('first_name', '')} {stored.get('middle_name', '')}".strip()
    return render(
        request,
        'hr/hire_eform.html',
        {
            'workplace': workplace,
            'candidate': candidate,
            'forms': E_CONTRACT_FORMS,
            'hr_mode': 'cards',
        },
    )


def workplace_detail(request, workplace_id):
    _seed(request)
    workplace = get_object_or_404(
        Workplace.objects.select_related('department', 'employee'),
        pk=workplace_id,
    )
    contracts = LaborContract.objects.filter(workplace=workplace).order_by('-created_at')
    return render(
        request,
        'hr/workplace_detail.html',
        {
            'workplace': workplace,
            'contracts': contracts,
            'hr_mode': 'cards',
            'format_date': format_date,
        },
    )


@require_http_methods(['POST'])
def workplace_delete(request, workplace_id):
    workplace = get_object_or_404(Workplace, pk=workplace_id)
    dept_id = workplace.department_id
    if workplace.status == Workplace.STATUS_OCCUPIED:
        messages.error(request, "Band ish o‘rnini o‘chirish mumkin emas.")
    else:
        workplace.delete()
        messages.success(request, "Ish o‘rni o‘chirildi.")
    return redirect(f"{reverse('hr_employees')}?dept={dept_id}")


def payroll(request):
    _seed(request)
    employees = Employee.objects.select_related('workplace').filter(
        workplace__status=Workplace.STATUS_OCCUPIED
    )
    rows = []
    for emp in employees:
        salary = emp.workplace.salary_display
        rows.append(
            {
                'fio': emp.full_name,
                'salary': salary,
                'status': 'Aktiv',
            }
        )
    return render(request, 'hr/payroll.html', {'employees': rows, 'hr_mode': 'payroll'})


def pit_social(request):
    _seed(request)
    employees = Employee.objects.select_related('workplace').filter(
        workplace__status=Workplace.STATUS_OCCUPIED
    )
    rows = [
        {
            'fio': e.full_name,
            'salary': e.workplace.salary_display,
            'status': 'Aktiv',
        }
        for e in employees
    ]
    return render(request, 'hr/pit_social.html', {'employees': rows, 'hr_mode': 'payroll'})


def orders_archive(request):
    _seed(request)
    orders = [
        {
            'number': o.number,
            'date': format_date(o.date),
            'employee': o.employee_name,
            'type': o.order_type,
            'status': o.status,
        }
        for o in HrOrder.objects.all()
    ]
    return render(request, 'hr/orders.html', {'orders': orders, 'hr_mode': 'orders'})
