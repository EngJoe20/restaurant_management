from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Item URLs
    path('', views.ItemListView.as_view(), name='item_list'),
    path('item/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('item/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('item/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # AJAX URLs
    path('ajax/category/<int:category_id>/items/', views.get_items_by_category, name='ajax_items_by_category'),
    path('ajax/item/<int:item_id>/toggle/', views.toggle_item_availability, name='ajax_toggle_availability'),
    
    # Dashboard
    path('dashboard/', views.menu_dashboard, name='dashboard'),
]