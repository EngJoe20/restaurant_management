from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Item, Category
from .forms import ItemForm, CategoryForm, ItemSearchForm


class ItemListView(ListView):
    model = Item
    template_name = 'menu/item_list.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        queryset = Item.objects.select_related('category')
        
        # Get search parameters
        query = self.request.GET.get('query')
        category_id = self.request.GET.get('category')
        available_only = self.request.GET.get('available_only')

        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if available_only:
            queryset = queryset.filter(is_available=True)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ItemSearchForm(self.request.GET)
        context['categories'] = Category.objects.all()
        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = 'menu/item_detail.html'
    context_object_name = 'item'


class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'menu/item_form.html'
    success_url = reverse_lazy('menu:item_list')

    def form_valid(self, form):
        messages.success(self.request, 'Menu item created successfully!')
        return super().form_valid(form)


class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'menu/item_form.html'
    success_url = reverse_lazy('menu:item_list')

    def form_valid(self, form):
        messages.success(self.request, 'Menu item updated successfully!')
        return super().form_valid(form)


class ItemDeleteView(DeleteView):
    model = Item
    template_name = 'menu/item_confirm_delete.html'
    success_url = reverse_lazy('menu:item_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Menu item deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'menu/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.prefetch_related('items').order_by('name')


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'menu/category_confirm_delete.html'
    success_url = reverse_lazy('menu:category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)


# AJAX Views
def get_items_by_category(request, category_id):
    """AJAX view to get items by category"""
    items = Item.objects.filter(category_id=category_id, is_available=True)
    items_data = [{
        'id': item.id,
        'name': item.name,
        'price': str(item.price)
    } for item in items]
    return JsonResponse({'items': items_data})


def toggle_item_availability(request, item_id):
    """AJAX view to toggle item availability"""
    if request.method == 'POST':
        item = get_object_or_404(Item, id=item_id)
        item.is_available = not item.is_available
        item.save()
        return JsonResponse({
            'status': 'success',
            'is_available': item.is_available,
            'message': f'Item {"enabled" if item.is_available else "disabled"} successfully!'
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# Dashboard view for menu statistics
def menu_dashboard(request):
    """Dashboard view with menu statistics"""
    total_items = Item.objects.count()
    available_items = Item.objects.filter(is_available=True).count()
    categories_count = Category.objects.count()
    recent_items = Item.objects.order_by('-created_at')[:5]
    
    context = {
        'total_items': total_items,
        'available_items': available_items,
        'unavailable_items': total_items - available_items,
        'categories_count': categories_count,
        'recent_items': recent_items,
    }
    
    return render(request, 'menu/dashboard.html', context)