from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # Customer CRUD URLs
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    
    # AJAX URLs
    path('ajax/search/', views.customer_search_ajax, name='ajax_search'),
    path('ajax/<int:customer_id>/stats/', views.customer_stats_ajax, name='ajax_stats'),
    
    # Export and Reports
    path('export/csv/', views.export_customers_csv, name='export_csv'),
    path('dashboard/', views.customers_dashboard, name='dashboard'),
]