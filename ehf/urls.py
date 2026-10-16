from django.urls import path

from . import views

urlpatterns = [
    path('', views.incoming, name='ehf_incoming'),
    path('incoming/', views.incoming, name='ehf_incoming_alias'),
    path('outgoing/', views.outgoing, name='ehf_outgoing'),
    path('drafts/', views.drafts, name='ehf_drafts'),
    path('contracts/', views.contracts, name='ehf_contracts'),
    path('archive/', views.archive, name='ehf_archive'),
]
