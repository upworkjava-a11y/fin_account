from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('app/organization/', include('organization.urls')),
    path('app/tax/', include('tax.urls')),
    path('app/bank/', include('bank.urls')),
    path('app/payments/', include('payments.urls')),
    path('app/assets/', include('assets.urls')),
    path('app/inventory/', include('inventory.urls')),
    path('app/ehf/', include('ehf.urls')),
    path('app/hr/', include('hr.urls')),
]
