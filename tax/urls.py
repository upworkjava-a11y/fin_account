from django.urls import path

from . import views

urlpatterns = [
    path('', views.tax_journal, name='tax_home'),
    path('electronic-forms/', views.tax_forms, name='tax_forms'),
    path('journal/', views.tax_journal, name='tax_journal'),
    path('forming-reports/', views.tax_forming, name='tax_forming'),
]
