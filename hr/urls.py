from django.urls import path

from . import views

urlpatterns = [
    path('', views.personnel_card, name='hr_employees'),
    path('employees/', views.personnel_card, name='hr_employees_alias'),
    path('departments/new/', views.department_form, name='hr_department_new'),
    path('departments/<int:pk>/edit/', views.department_form, name='hr_department_edit'),
    path('workplaces/new/', views.workplace_create, name='hr_workplace_new'),
    path('workplaces/<int:workplace_id>/', views.workplace_detail, name='hr_workplace_detail'),
    path('workplaces/<int:workplace_id>/delete/', views.workplace_delete, name='hr_workplace_delete'),
    path('hire/<int:workplace_id>/', views.hire_start, name='hr_hire'),
    path('hire/<int:workplace_id>/contract/', views.hire_contract, name='hr_hire_contract'),
    path('hire/<int:workplace_id>/e-form/', views.hire_eform, name='hr_hire_eform'),
    path('payroll/', views.payroll, name='hr_payroll'),
    path('pit-social/', views.pit_social, name='hr_pit_social'),
    path('orders/', views.orders_archive, name='hr_orders'),
]
