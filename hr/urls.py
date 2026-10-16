from django.urls import path

from . import views

urlpatterns = [
    path('', views.employees, name='hr_employees'),
    path('employees/', views.employees, name='hr_employees_alias'),
    path('payroll/', views.payroll, name='hr_payroll'),
    path('pit-social/', views.pit_social, name='hr_pit_social'),
    path('orders/', views.orders_archive, name='hr_orders'),
]
