from django.contrib import admin
from django.urls import path, include
from .views import UserListCreateView, AdCampaignListCreateView, AdPerformanceListView, OptimizeBudgetAPI
urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='users'),
    path('campaigns/', AdCampaignListCreateView.as_view(), name='campaigns'),
    path('performance/', AdPerformanceListView.as_view(), name='performance'),
    path('optimize/', OptimizeBudgetAPI.as_view(), name='optimize-budget'),
]
