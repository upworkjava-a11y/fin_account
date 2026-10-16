from django.urls import path

from . import views

urlpatterns = [
    path('', views.asset_registry, name='asset_registry'),
    path('registry/', views.asset_registry, name='asset_registry_alias'),
    path('depreciation/', views.asset_depreciation, name='asset_depreciation'),
    path('inventory/', views.asset_inventory, name='asset_inventory'),
]
