from django.urls import path
from . import views

urlpatterns = [
    path('', views.CrimeRecordListView.as_view(), name='crime-list'),
    path('search/', views.CrimeRecordSearchView.as_view(), name='crime-search'),
    path('create/', views.CrimeRecordCreateView.as_view(), name='crime-create'),
    path('<int:pk>/', views.CrimeRecordDetailView.as_view(), name='crime-detail'),
    path('<int:pk>/update/', views.CrimeRecordUpdateView.as_view(), name='crime-update'),
    path('<int:pk>/delete/', views.CrimeRecordDeleteView.as_view(), name='crime-delete'),
    path('update-list/', views.CrimeRecordUpdateListView.as_view(), name='crime-update-list'),
    path('delete-list/', views.CrimeRecordDeleteListView.as_view(), name='crime-delete-list'),
    path('view-all/', views.CrimeRecordViewAllListView.as_view(), name='crime-view-all'),
] 