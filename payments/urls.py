from django.urls import path

from . import views

urlpatterns = [
    path('', views.payment_history, name='pay_home'),
    path('tax-payments/', views.payment_history, name='pay_history'),
    path('tax-payments/create/', views.payment_create, name='pay_create'),
    path('reconciliation/tax/', views.recon_tax, name='recon_tax'),
    path('reconciliation/counterparties/', views.recon_counterparties, name='recon_counterparties'),
]
