from django.contrib import admin

from .models import EriLogin


@admin.register(EriLogin)
class EriLoginAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'cn', 'stir', 'pinfl', 'verified_by')
    search_fields = ('cn', 'stir', 'pinfl', 'serial')
