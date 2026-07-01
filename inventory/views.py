from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import json
import hashlib

from .models import User, Product, Stock, Vendor, Order, AuditBlock, SalesLog
from .forms import RegisterForm, ProductForm, StockForm, VendorForm, OrderForm
from .decorators import manager_required, vendor_required
from .weather import get_weather_warnings
from .blockchain import add_order_to_ledger, verify_chain_integrity
from .predictor import get_product_forecast

# --- AUTHENTICATION VIEWS ---

def landing_view(request):
    return render(request, 'inventory/landing.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created successfully as {user.get_role_display()}!")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'inventory/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')


@login_required
def dashboard_redirect(request):
    if request.user.is_manager():
        return redirect('manager_dashboard')
    elif request.user.is_vendor():
        return redirect('vendor_dashboard')
    return redirect('login')


# --- STORE MANAGER VIEWS ---

@manager_required
def manager_dashboard(request):
    # Optimize ORM queries to select related fields instantly and avoid N+1 query problem
    products = Product.objects.all().select_related('stock')
    orders = Order.objects.all().select_related('product', 'vendor').order_by('-created_at')
    vendors = Vendor.objects.all()
    
    # Cryptographic ledger integrity check
    ledger_valid, ledger_errors = verify_chain_integrity()
    recent_blocks = AuditBlock.objects.order_by('-index')[:5]

    context = {
        'products_count': products.count(),
        'orders_count': orders.count(),
        'vendors_count': vendors.count(),
        'ledger_valid': ledger_valid,
        'ledger_errors': ledger_errors,
        'recent_blocks': recent_blocks,
        'orders': orders[:8]
    }
    return render(request, 'inventory/manager_dashboard.html', context)


def get_sparkline_coords(product):
    logs = SalesLog.objects.filter(product=product).order_by('month')[:6]
    if not logs.exists():
        vals = [10, 20, 15, 25, 20, 30]
    else:
        vals = [log.quantity_sold for log in logs]
        
    if len(vals) < 6:
        vals = [10]*(6-len(vals)) + vals
        
    max_val = max(vals) if max(vals) > 0 else 10
    min_val = min(vals)
    diff = max_val - min_val if max_val != min_val else 10
    
    points = []
    for i, val in enumerate(vals):
        x = i * 24
        y = 25 - ((val - min_val) / diff * 20)
        points.append(f"{x},{int(y)}")
    return "M " + " L ".join(points)


@manager_required
def product_list(request):
    # Optimize product query with select_related for stocks
    products = Product.objects.all().select_related('stock')
    product_data = []
    for product in products:
        forecast = get_product_forecast(product)
        sparkline = get_sparkline_coords(product)
        product_data.append({
            'product': product,
            'forecast': forecast,
            'sparkline': sparkline
        })
    return render(request, 'inventory/product_list.html', {'products': product_data})


@manager_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                product = form.save()
                Stock.objects.create(product=product, current_quantity=0, min_threshold=10)
                # Seed initial sales history to train the model immediately
                from .predictor import seed_sales_history
                seed_sales_history(product)
            messages.success(request, f"Product {product.name} created successfully.")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Create Product'})


@manager_required
def product_update(request):
    pass # Managed below


@manager_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product {product.name} updated successfully.")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})


@manager_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})


@manager_required
def stock_update(request, pk):
    stock = get_object_or_404(Stock, product_id=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, f"Stock updated for {stock.product.name}.")
            return redirect('product_list')
    else:
        form = StockForm(instance=stock)
    return render(request, 'inventory/stock_form.html', {'form': form, 'stock': stock})


@manager_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'inventory/vendor_list.html', {'vendors': vendors})


@manager_required
def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor profiles created successfully.")
            return redirect('vendor_list')
    else:
        form = VendorForm()
    return render(request, 'inventory/vendor_form.html', {'form': form, 'title': 'Create Vendor'})


@manager_required
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Vendor {vendor.name} updated successfully.")
            return redirect('vendor_list')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'inventory/vendor_form.html', {'form': form, 'title': 'Edit Vendor'})


@manager_required
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()
        messages.success(request, "Vendor profile deleted successfully.")
        return redirect('vendor_list')
    return render(request, 'inventory/vendor_confirm_delete.html', {'vendor': vendor})


@manager_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"Purchase Order PO-{order.id} placed successfully.")
            return redirect('manager_dashboard')
    else:
        form = OrderForm()
    return render(request, 'inventory/order_form.html', {'form': form})


# --- VENDOR VIEWS ---

@vendor_required
def vendor_dashboard(request):
    try:
        vendor = request.user.vendor_profile
    except Vendor.DoesNotExist:
        messages.error(request, "You do not have a vendor profile. Please contact the Store Manager.")
        logout(request)
        return redirect('login')
        
    orders = Order.objects.filter(vendor=vendor).order_by('-created_at')
    
    # Get weather warning for their own city
    weather_info = get_weather_warnings(vendor.city)
    
    context = {
        'vendor': vendor,
        'orders': orders,
        'weather_info': weather_info
    }
    return render(request, 'inventory/vendor_dashboard.html', context)


@vendor_required
def vendor_order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk, vendor=request.user.vendor_profile)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Shipped', 'Delivered']:
            with transaction.atomic():
                order.status = new_status
                order.save()
                
                # If status is updated to Delivered, update active stock!
                if new_status == 'Delivered':
                    try:
                        stock = Stock.objects.get(product=order.product)
                        stock.current_quantity += order.quantity
                        stock.save()
                    except Stock.DoesNotExist:
                        Stock.objects.create(product=order.product, current_quantity=order.quantity)
                        
                # Force fresh block generation every time order status is updated (representing a state change)
                add_order_to_ledger(order)
                
            messages.success(request, f"Order status updated to {new_status}.")
            
            # Record historical sales log when order is delivered (for AI dataset growth)
            if new_status == 'Delivered':
                today_first = timezone.now().date().replace(day=1)
                log, created = SalesLog.objects.get_or_create(
                    product=order.product,
                    month=today_first,
                    defaults={'quantity_sold': 0}
                )
                log.quantity_sold += order.quantity
                log.save()
                
        return redirect('vendor_dashboard')
    return redirect('vendor_dashboard')


# --- CRYPTOGRAPHIC AUDITING & DEMO VIEWS ---

@manager_required
def blockchain_view(request):
    blocks = list(AuditBlock.objects.order_by('index'))
    is_valid, errors = verify_chain_integrity()
    
    # Annotate block validity for custom node styling
    previous_hash = "0" * 64
    for block in blocks:
        ts = int(block.timestamp.timestamp())
        block_string = json.dumps({
            "index": block.index,
            "timestamp": ts,
            "order_data": block.order_data,
            "previous_hash": block.previous_hash
        }, sort_keys=True)
        calculated_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
        
        block.is_valid = (block.hash == calculated_hash) and (block.previous_hash == previous_hash)
        previous_hash = block.hash
        
    return render(request, 'inventory/blockchain_view.html', {
        'blocks': blocks,
        'is_valid': is_valid,
        'errors': errors
    })


@manager_required
def blockchain_tamper(request, pk):
    """
    Intentionally tampers with a block's order_data string in the DB to demo verification failure.
    """
    block = get_object_or_404(AuditBlock, pk=pk)
    try:
        data = json.loads(block.order_data)
        # Modify a value
        data['quantity'] += 9999
        data['tampered'] = True
        block.order_data = json.dumps(data)
        block.save()
        messages.warning(request, f"Block #{block.index} payload has been intentionally modified in the database. Verify chain integrity to see it fail!")
    except Exception as e:
        messages.error(request, f"Failed to tamper: {str(e)}")
    return redirect('blockchain_view')


@manager_required
def blockchain_restore(request):
    """
    Clears blockchain and reconstructs it from existing database orders to repair the chain.
    """
    with transaction.atomic():
        AuditBlock.objects.all().delete()
        # Re-add blocks for all existing orders that have been Shipped or Delivered
        orders = Order.objects.all().order_by('created_at')
        for order in orders:
            add_order_to_ledger(order)
    messages.success(request, "Ledger chain cleared and successfully rebuilt from current order database tables.")
    return redirect('blockchain_view')


@manager_required
def api_weather_alerts(request):
    # Optimize ORM queries and fetch weather parameters asynchronously
    vendors = Vendor.objects.all()
    active_cities = set(vendors.values_list('city', flat=True))
    city_weather_cache = {}
    for city in active_cities:
        if city:
            city_weather_cache[city] = get_weather_warnings(city)
            
    orders = Order.objects.filter(status__in=['Pending', 'Shipped']).select_related('vendor', 'product')
    weather_alerts = []
    for order in orders:
        vendor_city = order.vendor.city
        weather_info = city_weather_cache.get(vendor_city, {'has_warning': False})
        if weather_info['has_warning']:
            weather_alerts.append({
                'order_id': order.id,
                'product_name': order.product.name,
                'vendor_name': order.vendor.name,
                'city': vendor_city,
                'condition': weather_info['condition'],
                'description': weather_info['description'],
                'source': weather_info['source']
            })
    return JsonResponse({'alerts': weather_alerts})


@manager_required
def api_reorder_alerts(request):
    # Asynchronously calculate forecasts without blocking UI
    products = Product.objects.all().select_related('stock')
    smart_alerts = []
    for product in products:
        forecast = get_product_forecast(product)
        if forecast['needs_reorder']:
            smart_alerts.append({
                'product_id': product.id,
                'product_name': product.name,
                'current_qty': product.stock.current_quantity,
                'projected_sales': forecast['projected_sales'],
                'reorder_point': forecast['reorder_point']
            })
    return JsonResponse({'alerts': smart_alerts})


@manager_required
def manager_quick_order(request, pk):
    # Auto-generate a purchase order using AI recommended reorder points
    product = get_object_or_404(Product, pk=pk)
    forecast = get_product_forecast(product)
    vendor = Vendor.objects.first()
    
    if not vendor:
        messages.error(request, "No suppliers/vendors found in database to fulfill order.")
        return redirect('manager_dashboard')
        
    with transaction.atomic():
        order = Order.objects.create(
            product=product,
            vendor=vendor,
            quantity=forecast['reorder_point'],
            status='Pending'
        )
    messages.success(request, f"Smart Reorder PO-{order.id} for {product.name} (Qty: {order.quantity}) successfully placed with vendor {vendor.name}.")
    return redirect('manager_dashboard')
