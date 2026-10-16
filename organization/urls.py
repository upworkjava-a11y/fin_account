from django.urls import path

from . import views

urlpatterns = [
    path('', views.org_main, name='org_main'),
    path('documents/', views.org_documents, name='org_documents'),
    path('bank-accounts/', views.org_banks, name='org_banks'),
    path('telegram-phones/', views.org_telegram, name='org_telegram'),
]
