import os
import django
from django.utils import timezone
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avis_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Product, Stock, Vendor, Order, SalesLog
from inventory.blockchain import add_order_to_ledger

User = get_user_model()

# Clear existing tables (except manager user Parth)
Product.objects.all().delete()
Vendor.objects.all().delete()
Order.objects.all().delete()
SalesLog.objects.all().delete()
from inventory.models import AuditBlock
AuditBlock.objects.all().delete()

# Create vendor users and profiles
u1, _ = User.objects.get_or_create(username='nexus_wholesale', defaults={'email': 'nexus@wholesale.com', 'role': 'vendor'})
u1.set_password('nexus123')
u1.save()
v1, _ = Vendor.objects.get_or_create(user=u1, defaults={'name': 'Nexus Wholesale', 'email': 'nexus@wholesale.com', 'city': 'Seattle', 'address': '100 Industrial Way, Seattle, WA'})

u2, _ = User.objects.get_or_create(username='apex_logistics', defaults={'email': 'apex@logistics.com', 'role': 'vendor'})
u2.set_password('apex123')
u2.save()
v2, _ = Vendor.objects.get_or_create(user=u2, defaults={'name': 'Apex Logistics', 'email': 'apex@logistics.com', 'city': 'Buffalo', 'address': '200 Logistics Blvd, Buffalo, NY'})

# Create products and stocks
p1 = Product.objects.create(sku='PROD-0812', name='Super Widget', description='Premium manufacturing widget with high durability', price=19.99)
Stock.objects.create(product=p1, current_quantity=12, min_threshold=18)

p2 = Product.objects.create(sku='PROD-0943', name='Quantum Gear', description='Advanced synchronization gear for high speed assembly', price=49.99)
Stock.objects.create(product=p2, current_quantity=85, min_threshold=30)

# Seed sales history to make ROP predictions work
today = datetime.date.today()
for i in range(12, 0, -1):
    year = today.year - (1 if today.month <= i else 0)
    month = (today.month - i) % 12
    if month == 0:
        month = 12
    log_date = datetime.date(year, month, 1)
    
    # PROD-0812: stable sales around 15 units
    SalesLog.objects.create(product=p1, month=log_date, quantity_sold=15)
    # PROD-0943: sales around 25 units
    SalesLog.objects.create(product=p2, month=log_date, quantity_sold=25)

# Create historical and active orders
# 1. Active order for PROD-0812 (status Pending)
o1 = Order.objects.create(product=p1, vendor=v1, quantity=18, status='Pending')
add_order_to_ledger(o1)

# 2. Historical order for PROD-0943 (status Delivered)
o2 = Order.objects.create(product=p2, vendor=v2, quantity=50, status='Delivered')
add_order_to_ledger(o2)

print("Database successfully seeded with mock data conforming to specifications!")
