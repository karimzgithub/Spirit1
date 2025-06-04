from django.contrib import admin
from .models import CrimeRecord

@admin.register(CrimeRecord)
class CrimeRecordAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'crime_type', 'location', 'date_reported', 'status', 'victim_name')
    list_filter = ('crime_type', 'status', 'date_reported')
    search_fields = ('case_number', 'victim_name', 'suspect_name', 'location')
    date_hierarchy = 'date_reported'
    ordering = ('-date_reported',)
