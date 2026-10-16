from django.urls import path

from . import views

urlpatterns = [
    path('', views.tmz_registry, name='tmz_registry'),
    path('registry/', views.tmz_registry, name='tmz_registry_alias'),
    path('movements/', views.tmz_movements, name='tmz_movements'),
    path('warehouses/', views.tmz_warehouses, name='tmz_warehouses'),
    path('inventory-check/', views.tmz_inventory, name='tmz_inventory'),
]
