from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('guest/', views.guest_enter, name='guest_enter'),
    path('guest/exit/', views.guest_exit, name='guest_exit'),
    path('app/', views.app_dashboard, name='app_dashboard'),
]
