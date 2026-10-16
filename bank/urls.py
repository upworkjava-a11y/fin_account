from django.urls import path

from . import views

urlpatterns = [
    path('', views.bank_turnover, name='bank_home'),
    path('turnover/', views.bank_turnover, name='bank_turnover'),
    path('auto-entries/', views.bank_auto, name='bank_auto'),
    path('archive/', views.bank_archive, name='bank_archive'),
]
