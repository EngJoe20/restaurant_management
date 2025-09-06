from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order CRUD URLs
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order_edit'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    
    # Quick order creation
    path('quick-create/', views.quick_order_create, name='quick_create'),
    
    # Order items management
    path('<int:order_id>/add-items/', views.add_items_to_order, name='add_items'),
    path('<int:order_id>/item/<int:item_id>/update/', views.update_order_item, name='update_item'),
    path('<int:order_id>/item/<int:item_id>/remove/', views.remove_order_item, name='remove_item'),
    
    # AJAX URLs
    path('ajax/<int:order_id>/status/', views.update_order_status, name='ajax_update_status'),
    path('ajax/<int:order_id>/summary/', views.order_summary_ajax, name='ajax_order_summary'),
    
    # Export and Reports
    path('export/csv/', views.export_orders_csv, name='export_csv'),
    path('report/', views.orders_report, name='report'),
    path('dashboard/', views.orders_dashboard, name='dashboard'),
]