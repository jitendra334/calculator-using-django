from django.contrib import admin
from .models import Calculation

@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ('user', 'expression', 'result', 'operation', 'created_at')
    list_filter = ('operation', 'created_at')
    search_fields = ('expression', 'result')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)