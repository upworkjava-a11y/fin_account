from django.contrib import admin

from .models import Department, Employee, HrOrder, LaborContract, Workplace


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'parent', 'is_none', 'sort_order')
    search_fields = ('name_uz', 'name_ru')


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'department', 'stavka', 'status', 'salary_mode')
    list_filter = ('status', 'salary_mode', 'department')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'pinfl', 'workplace')
    search_fields = ('last_name', 'first_name', 'pinfl')


@admin.register(LaborContract)
class LaborContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'employee', 'mode', 'contract_date', 'status')


@admin.register(HrOrder)
class HrOrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'employee_name', 'order_type', 'status')
