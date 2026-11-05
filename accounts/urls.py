from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('eri/', views.eri_login, name='eri_login'),
    path('eri/challenge/', views.eri_challenge, name='eri_challenge'),
    path('eri/verify/', views.eri_verify, name='eri_verify'),
    path('guest/', views.guest_enter, name='guest_enter'),
    path('guest/exit/', views.guest_exit, name='guest_exit'),
    path('app/', views.app_dashboard, name='app_dashboard'),
]
