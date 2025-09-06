from django.db import models
from django.urls import reverse

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('customers:customer_detail', kwargs={'pk': self.pk})

    def total_orders(self):
        return self.orders.count()

    def total_spent(self):
        return sum(order.total_price() for order in self.orders.all())