from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm
from customers.models import Customer
from menu.models import Item
import csv
from datetime import datetime, timedelta


class OrderListView(ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        queryset = Order.objects.select_related('customer').prefetch_related('items__item')
        
        # Get filter parameters
        status = self.request.GET.get('status')
        customer_query = self.request.GET.get('customer')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        # Apply filters
        if status:
            queryset = queryset.filter(status=status)
        
        if customer_query:
            queryset = queryset.filter(
                Q(customer__name__icontains=customer_query) |
                Q(customer__phone__icontains=customer_query)
            )
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to)
            except ValueError:
                pass
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.STATUS_CHOICES
        context['filter_params'] = self.request.GET
        return context


class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['order_items'] = order.items.select_related('item').all()
        context['total_price'] = order.total_price()
        context['can_add_items'] = order.status in ['pending', 'confirmed']
        return context


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'

    def get_success_url(self):
        return reverse('orders:add_items', kwargs={'order_id': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Order created successfully! Now add items to the order.')
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'

    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Order updated successfully!')
        return super().form_valid(form)


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Order deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Order Items Management
def add_items_to_order(request, order_id):
    """View to add items to an existing order"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.valid():
            order_item = form.save(commit=False)
            order_item.order = order
            order_item.price = order_item.item.price  # Set current price
            
            # Check if item already exists in order
            existing_item = OrderItem.objects.filter(
                order=order, item=order_item.item
            ).first()
            
            if existing_item:
                existing_item.quantity += order_item.quantity
                existing_item.save()
                messages.success(request, f'Updated quantity for {order_item.item.name}')
            else:
                order_item.save()
                messages.success(request, f'Added {order_item.item.name} to order')
            
            return redirect('orders:add_items', order_id=order.id)
    else:
        form = OrderItemForm()
    
    # Get current order items
    order_items = order.items.select_related('item').all()
    available_items = Item.objects.filter(is_available=True).order_by('category', 'name')
    
    context = {
        'order': order,
        'form': form,
        'order_items': order_items,
        'available_items': available_items,
        'total_price': order.total_price(),
        'total_items': order.total_items(),
    }
    
    return render(request, 'orders/add_items.html', context)


def update_order_item(request, order_id, item_id):
    """Update quantity of an order item"""
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, order=order, id=item_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            order_item.quantity = quantity
            order_item.save()
            messages.success(request, 'Item quantity updated successfully!')
        else:
            order_item.delete()
            messages.success(request, 'Item removed from order!')
    
    return redirect('orders:add_items', order_id=order.id)


def remove_order_item(request, order_id, item_id):
    """Remove an item from order"""
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, order=order, id=item_id)
    
    if request.method == 'POST':
        item_name = order_item.item.name
        order_item.delete()
        messages.success(request, f'Removed {item_name} from order!')
    
    return redirect('orders:add_items', order_id=order.id)


# Quick Order Creation
def quick_order_create(request):
    """Create order with customer selection in one step"""
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            order = Order.objects.create(
                customer=customer,
                status='pending'
            )
            messages.success(request, f'Order created for {customer.name}!')
            return redirect('orders:add_items', order_id=order.id)
        else:
            messages.error(request, 'Please select a customer.')
    
    customers = Customer.objects.order_by('name')
    context = {'customers': customers}
    return render(request, 'orders/quick_create.html', context)


# AJAX Views
def update_order_status(request, order_id):
    """AJAX view to update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return JsonResponse({
                'status': 'success',
                'new_status': new_status,
                'message': f'Order status updated to {order.get_status_display()}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def order_summary_ajax(request, order_id):
    """AJAX view to get order summary"""
    order = get_object_or_404(Order, id=order_id)
    
    items = [{
        'name': item.item.name,
        'quantity': item.quantity,
        'price': str(item.price),
        'total': str(item.get_total_price())
    } for item in order.items.all()]
    
    summary = {
        'items': items,
        'total_items': order.total_items(),
        'total_price': str(order.total_price()),
        'customer': order.customer.name,
        'status': order.get_status_display()
    }
    
    return JsonResponse(summary)


# Export and Reports
def export_orders_csv(request):
    """Export orders to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Order ID', 'Customer', 'Phone', 'Status', 'Total Items', 
        'Total Price', 'Created Date', 'Updated Date'
    ])

    orders = Order.objects.select_related('customer').prefetch_related('items')
    
    for order in orders:
        writer.writerow([
            order.id,
            order.customer.name,
            order.customer.phone,
            order.get_status_display(),
            order.total_items(),
            order.total_price(),
            order.created_at.strftime('%Y-%m-%d %H:%M'),
            order.updated_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response


def orders_report(request):
    """Generate orders report with statistics"""
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default to last 30 days
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).date()
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Filter orders
    orders = Order.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    )
    
    # Calculate statistics
    total_orders = orders.count()
    total_revenue = sum(order.total_price() for order in orders)
    
    # Orders by status
    orders_by_status = {}
    for status_code, status_name in Order.STATUS_CHOICES:
        count = orders.filter(status=status_code).count()
        orders_by_status[status_name] = count
    
    # Daily sales (last 7 days)
    daily_sales = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        daily_orders = orders.filter(created_at__date=date)
        daily_revenue = sum(order.total_price() for order in daily_orders)
        daily_sales.append({
            'date': date,
            'orders': daily_orders.count(),
            'revenue': daily_revenue
        })
    
    # Top customers
    top_customers = Customer.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__items__price')
    ).filter(
        orders__created_at__date__gte=date_from,
        orders__created_at__date__lte=date_to
    ).order_by('-total_spent')[:5]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': total_revenue / total_orders if total_orders > 0 else 0,
        'orders_by_status': orders_by_status,
        'daily_sales': daily_sales,
        'top_customers': top_customers,
    }
    
    return render(request, 'orders/report.html', context)


# Dashboard
def orders_dashboard(request):
    """Dashboard view with order statistics"""
    today = timezone.now().date()
    
    # Today's statistics
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = sum(order.total_price() for order in today_orders)
    
    # Overall statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]
    
    # Orders by status
    status_stats = {}
    for status_code, status_name in Order.STATUS_CHOICES:
        count = Order.objects.filter(status=status_code).count()
        status_stats[status_name] = count
    
    context = {
        'today_orders': today_orders.count(),
        'today_revenue': today_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'status_stats': status_stats,
    }
    
    return render(request, 'orders/dashboard.html', context)