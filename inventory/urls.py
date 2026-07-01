from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Manager Routes
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/products/', views.product_list, name='product_list'),
    path('manager/products/create/', views.product_create, name='product_create'),
    path('manager/products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('manager/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('manager/products/<int:pk>/stock/', views.stock_update, name='stock_update'),
    
    path('manager/vendors/', views.vendor_list, name='vendor_list'),
    path('manager/vendors/create/', views.vendor_create, name='vendor_create'),
    path('manager/vendors/<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('manager/vendors/<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),
    
    path('manager/orders/create/', views.order_create, name='order_create'),
    
    # Vendor Routes
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/orders/<int:pk>/status/', views.vendor_order_status_update, name='vendor_order_status_update'),
    
    # Blockchain Audit Routes
    path('manager/blockchain/', views.blockchain_view, name='blockchain_view'),
    path('manager/blockchain/tamper/<int:pk>/', views.blockchain_tamper, name='blockchain_tamper'),
    path('manager/blockchain/restore/', views.blockchain_restore, name='blockchain_restore'),
    
    # Asynchronous Data API Routes
    path('api/weather-alerts/', views.api_weather_alerts, name='api_weather_alerts'),
    path('api/reorder-alerts/', views.api_reorder_alerts, name='api_reorder_alerts'),
]
