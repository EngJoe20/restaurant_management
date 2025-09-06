from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Customer
from .forms import CustomerForm, CustomerSearchForm
import csv


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Customer.objects.annotate(
            total_orders=Count('orders'),
            total_spent=Sum('orders__items__price')
        )
        
        # Get search parameter
        query = self.request.GET.get('query')
        
        # Apply search filter
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CustomerSearchForm(self.request.GET)
        return context


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Get customer's orders with pagination
        orders = customer.orders.select_related().prefetch_related('items__item').order_by('-created_at')
        paginator = Paginator(orders, 10)
        page_number = self.request.GET.get('page')
        page_orders = paginator.get_page(page_number)
        
        context['orders'] = page_orders
        context['total_orders'] = orders.count()
        context['total_spent'] = sum(order.total_price() for order in orders)
        
        # Recent orders (last 5)
        context['recent_orders'] = orders[:5]
        
        return context


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer created successfully!')
        return super().form_valid(form)


class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully!')
        return super().form_valid(form)


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Customer deleted successfully!')
        return super().delete(request, *args, **kwargs)


# AJAX Views
def customer_search_ajax(request):
    """AJAX view for customer search autocomplete"""
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(
        Q(name__icontains=query) |
        Q(phone__icontains=query)
    )[:10]
    
    results = [{
        'id': customer.id,
        'name': customer.name,
        'phone': customer.phone,
        'email': customer.email
    } for customer in customers]
    
    return JsonResponse({'customers': results})


def customer_stats_ajax(request, customer_id):
    """AJAX view to get customer statistics"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    stats = {
        'total_orders': customer.total_orders(),
        'total_spent': float(customer.total_spent()),
        'name': customer.name,
        'phone': customer.phone,
        'email': customer.email,
    }
    
    return JsonResponse(stats)


# Export Views
def export_customers_csv(request):
    """Export customers list to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Address', 'Total Orders', 'Total Spent', 'Created Date'])

    customers = Customer.objects.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__items__price')
    ).order_by('name')

    for customer in customers:
        writer.writerow([
            customer.name,
            customer.email,
            customer.phone,
            customer.address,
            customer.total_orders or 0,
            customer.total_spent or 0,
            customer.created_at.strftime('%Y-%m-%d')
        ])

    return response


# Dashboard view for customer statistics
def customers_dashboard(request):
    """Dashboard view with customer statistics"""
    total_customers = Customer.objects.count()
    customers_with_orders = Customer.objects.filter(orders__isnull=False).distinct().count()
    
    # Top customers by total spent
    top_customers = Customer.objects.annotate(
        total_spent=Sum('orders__items__price'),
        total_orders=Count('orders')
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:5]
    
    # Recent customers
    recent_customers = Customer.objects.order_by('-created_at')[:10]
    
    context = {
        'total_customers': total_customers,
        'customers_with_orders': customers_with_orders,
        'customers_without_orders': total_customers - customers_with_orders,
        'top_customers': top_customers,
        'recent_customers': recent_customers,
    }
    
    return render(request, 'customers/dashboard.html', context)