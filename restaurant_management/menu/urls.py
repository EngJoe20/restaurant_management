from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.ItemListView.as_view(), name='item_list'),
    path('item/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('item/add/', views.ItemCreateView.as_view(), name='item_add'),
    path('item/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    path('search/', views.ItemSearchView.as_view(), name='item_search'),
]
