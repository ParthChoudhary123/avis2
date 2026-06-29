from django.contrib.auth.models import AbstractUser
from django.db import models
import json

class User(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'Store Manager'),
        ('vendor', 'Vendor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='manager')

    def is_manager(self):
        return self.role == 'manager'

    def is_vendor(self):
        return self.role == 'vendor'


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')
    current_quantity = models.IntegerField(default=0)
    min_threshold = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - Qty: {self.current_quantity}"


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO-{self.id}: {self.product.name} ({self.quantity}) - {self.status}"


class AuditBlock(models.Model):
    index = models.IntegerField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    order_data = models.TextField()  # JSON representation of order
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)

    def __str__(self):
        return f"Block #{self.index} [{self.hash[:8]}]"


class SalesLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_logs')
    month = models.DateField()  # Date representing the first day of the month
    quantity_sold = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.month.strftime('%Y-%m')}: {self.quantity_sold}"
