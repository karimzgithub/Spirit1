from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import CrimeRecord
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json
from datetime import datetime, timedelta

# Create your views here.

class CrimeRecordListView(LoginRequiredMixin, ListView):
    model = CrimeRecord
    template_name = 'crime_records/crime_list.html'
    context_object_name = 'crime_records'
    ordering = ['-created_at']  # Order by most recent first
    paginate_by = 3  # Show only 3 records

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search_query')
        search_type = self.request.GET.get('search_type')

        if search_query and search_type:
            if search_type == 'case_number':
                queryset = queryset.filter(case_number__icontains=search_query)
            elif search_type == 'victim_name':
                queryset = queryset.filter(victim_name__icontains=search_query)

        # Always return the 3 most recent records
        return queryset[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic statistics
        context['total_records'] = CrimeRecord.objects.count()
        context['closed_cases'] = CrimeRecord.objects.filter(status='CLOSED').count()
        context['under_investigation'] = CrimeRecord.objects.filter(status='UNDER_INVESTIGATION').count()
        context['open_cases'] = CrimeRecord.objects.filter(status='OPEN').count()
        
        # Crime type distribution for pie chart
        crime_types = CrimeRecord.objects.values('crime_type').annotate(count=Count('id'))
        context['crime_type_data'] = json.dumps([{
            'type': dict(CrimeRecord.CRIME_TYPES)[item['crime_type']],
            'count': item['count']
        } for item in crime_types])
        
        # Monthly trend data for bar chart
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_trend = CrimeRecord.objects.filter(
            date_reported__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date_reported')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Get detailed records for each month
        monthly_records = {}
        for record in CrimeRecord.objects.filter(date_reported__gte=six_months_ago):
            month_key = record.date_reported.strftime('%Y-%m')
            if month_key not in monthly_records:
                monthly_records[month_key] = []
            monthly_records[month_key].append({
                'crime_type': dict(CrimeRecord.CRIME_TYPES)[record.crime_type],
                'location': record.location,
                'date_reported': record.date_reported.strftime('%B %d, %Y'),
                'case_number': record.case_number,
                'status': dict(CrimeRecord.STATUS_CHOICES)[record.status]
            })
        
        context['monthly_trend_data'] = json.dumps([{
            'month': item['month'].month,  # Just the month number
            'count': item['count'],
            'records': monthly_records.get(item['month'].strftime('%Y-%m'), [])
        } for item in monthly_trend])
        
        # Location data for heat map
        locations = CrimeRecord.objects.values('location').annotate(count=Count('id'))
        context['location_data'] = json.dumps([{
            'location': item['location'],
            'count': item['count']
        } for item in locations])
        
        return context

class CrimeRecordDetailView(LoginRequiredMixin, DetailView):
    model = CrimeRecord
    template_name = 'crime_records/crime_detail.html'
    context_object_name = 'crime'

class CrimeRecordCreateView(LoginRequiredMixin, CreateView):
    model = CrimeRecord
    template_name = 'crime_records/crime_form.html'
    fields = [
        # Basic Information
        'case_number', 'crime_type', 'description', 'location', 
        'date_occurred', 'status',
        
        # Case Registration Details
        'fir_number', 'fir_date', 'court_case_number',
        
        # Victim Details
        'victim_name', 'victim_age', 'victim_gender', 'victim_contact',
        'victim_address', 'victim_occupation', 'victim_marital_status',
        
        # Suspect Details
        'suspect_name', 'suspect_age', 'suspect_gender', 'suspect_contact',
        'suspect_address', 'suspect_occupation', 'suspect_status', 'suspect_image',
        
        # Evidence Details
        'evidence_type', 'evidence_collection_date', 'evidence_description',
        'evidence_location', 'evidence_chain_of_custody', 'evidence_image',
        
        # Officer Details
        'officer_name', 'officer_badge', 'officer_department', 'officer_contact',
        
        # Additional Information
        'evidence', 'notes'
    ]
    success_url = reverse_lazy('crime-list')

    def form_valid(self, form):
        # Set the date_reported to current time
        form.instance.date_reported = timezone.now()
        messages.success(self.request, 'Crime record created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class CrimeRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = CrimeRecord
    template_name = 'crime_records/crime_form.html'
    fields = [
        # Basic Information
        'case_number', 'crime_type', 'description', 'location', 
        'date_occurred', 'status',
        
        # Case Registration Details
        'fir_number', 'fir_date', 'court_case_number',
        
        # Victim Details
        'victim_name', 'victim_age', 'victim_gender', 'victim_contact',
        'victim_address', 'victim_occupation', 'victim_marital_status',
        
        # Suspect Details
        'suspect_name', 'suspect_age', 'suspect_gender', 'suspect_contact',
        'suspect_address', 'suspect_occupation', 'suspect_status', 'suspect_image',
        
        # Evidence Details
        'evidence_type', 'evidence_collection_date', 'evidence_description',
        'evidence_location', 'evidence_chain_of_custody', 'evidence_image',
        
        # Officer Details
        'officer_name', 'officer_badge', 'officer_department', 'officer_contact',
        
        # Additional Information
        'evidence', 'notes'
    ]
    success_url = reverse_lazy('crime-list')

    def form_valid(self, form):
        messages.success(self.request, 'Crime record updated successfully!')
        return super().form_valid(form)

class CrimeRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = CrimeRecord
    template_name = 'crime_records/crime_confirm_delete.html'
    success_url = reverse_lazy('crime-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Crime record deleted successfully!')
        return super().delete(request, *args, **kwargs)

class CrimeRecordUpdateListView(LoginRequiredMixin, ListView):
    model = CrimeRecord
    template_name = 'crime_records/crime_update_list.html'
    context_object_name = 'crimes'
    paginate_by = 10

class CrimeRecordDeleteListView(LoginRequiredMixin, ListView):
    model = CrimeRecord
    template_name = 'crime_records/crime_delete_list.html'
    context_object_name = 'crimes'
    paginate_by = 10

class CrimeRecordViewAllListView(LoginRequiredMixin, ListView):
    model = CrimeRecord
    template_name = 'crime_records/crime_view_all.html'
    context_object_name = 'crimes'
    paginate_by = 10

class CrimeRecordSearchView(LoginRequiredMixin, ListView):
    model = CrimeRecord
    template_name = 'crime_records/crime_search.html'
    context_object_name = 'crimes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search_query')
        search_type = self.request.GET.get('search_type')
        status = self.request.GET.get('status')

        if search_query and search_type:
            if search_type == 'case_number':
                queryset = queryset.filter(case_number__icontains=search_query)
            elif search_type == 'victim_name':
                queryset = queryset.filter(victim_name__icontains=search_query)

        if status:
            queryset = queryset.filter(status=status)

        return queryset
