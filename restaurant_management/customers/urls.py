from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('customer/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customer/add/', views.CustomerCreateView.as_view(), name='customer_add'),
    path('customer/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('customer/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    path('search/', views.CustomerSearchView.as_view(), name='customer_search'),
]
