from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate
from orders.models import Order, OrderItem
from customers.models import Customer
from menu.models import Item

def dashboard_view(request):
    today = now().date()

   
    today_orders = Order.objects.filter(created_at__date=today).count()
    
 
    today_revenue = (
        OrderItem.objects.filter(order__created_at__date=today)
        .aggregate(total=Sum(F("price") * F("quantity")))["total"] or 0
    )

    total_customers = Customer.objects.count()
    menu_items = Item.objects.count()
    available_items = Item.objects.filter(is_available=True).count()

 
    recent_orders = (
        Order.objects.annotate(
            total_price=Sum(F("items__price") * F("items__quantity"))
        )
        .select_related("customer")
        .order_by("-created_at")[:10]
    )

   
    status_data = list(
        Order.objects.values("status").annotate(count=Count("id"))
    )


    sales_data = (
        OrderItem.objects.filter(order__created_at__date__gte=today.replace(day=max(1, today.day - 6)))
        .annotate(date=TruncDate("order__created_at"))
        .values("date")
        .annotate(total=Sum(F("price") * F("quantity")))
        .order_by("date")
    )

    context = {
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "total_customers": total_customers,
        "menu_items": menu_items,
        "available_items": available_items,
        "recent_orders": recent_orders,
        "status_data": status_data,
        "sales_data": list(sales_data),
    }
    return render(request, "dashboard.html", context)
