from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/add/', views.OrderCreateView.as_view(), name='order_add'),
    path('order/<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order_edit'),
    path('order/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('order/<int:order_id>/add-item/', views.OrderItemCreateView.as_view(), name='order_item_add'),
    path('order-item/<int:pk>/delete/', views.OrderItemDeleteView.as_view(), name='order_item_delete'),
]
