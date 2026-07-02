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
    product = models.OneToOneField(Product, on_delete=models.PROTECT, related_name='stock')
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
        ('Accepted', 'Accepted'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='orders')
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO-{self.id}: {self.product.name} ({self.quantity}) - {self.status}"


class AuditBlock(models.Model):
    index = models.IntegerField(unique=True)
    timestamp = models.DateTimeField()
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


class Company(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    display_name = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=100)
    street_address = models.TextField(blank=True, null=True)
    base_currency = models.CharField(max_length=3, default='INR')
    show_currency_on_orders = models.BooleanField(default=False)
    default_delivery_sales_days = models.IntegerField(default=14)
    default_lead_purchase_days = models.IntegerField(default=14)
    current_plan_tier = models.CharField(max_length=20, default='Free')

    def __str__(self):
        return self.display_name


class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=150)
    email_address = models.EmailField(blank=True, null=True)
    currency = models.CharField(max_length=3, default='INR')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    reference_id = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SubscriptionSimulation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='simulations')
    estimated_monthly_sales = models.IntegerField(default=1000)
    has_manufacturing_mgmt = models.BooleanField(default=False)
    has_shop_floor_app = models.BooleanField(default=False)
    has_traceability = models.BooleanField(default=False)
    has_warehouse_mgmt = models.BooleanField(default=True)
    calculated_total_due = models.DecimalField(max_digits=10, decimal_places=2, default=746.00)

    def __str__(self):
        return f"Sim {self.id}: {self.calculated_total_due}"

