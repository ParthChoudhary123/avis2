from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
import json

from .models import Product, Stock, Vendor, Order, AuditBlock, SalesLog
from .blockchain import add_order_to_ledger, verify_chain_integrity
from .weather import get_weather_warnings
from .predictor import seed_sales_history, get_product_forecast

User = get_user_model()

class AVISSystemTestCase(TestCase):
    def setUp(self):
        # 1. Create Users
        self.manager_user = User.objects.create_user(
            username='manager_bob', password='password123', role='manager', email='manager@retail.com'
        )
        self.vendor_user = User.objects.create_user(
            username='vendor_acme', password='password123', role='vendor', email='acme@logistics.com'
        )

        # 2. Create Vendor Profile
        self.vendor = Vendor.objects.create(
            user=self.vendor_user,
            name='Acme Supplies',
            email='acme@logistics.com',
            city='Seattle',
            address='123 Rain Ave, Seattle, WA'
        )

        # 3. Create Product & Stock
        self.product = Product.objects.create(
            sku='PROD-XYZ-01',
            name='Super Widget',
            description='A widget of supreme quality',
            price=19.99
        )
        self.stock = Stock.objects.create(
            product=self.product,
            current_quantity=5,
            min_threshold=15
        )

    def test_role_based_isolation(self):
        """Verify role validation methods function correctly."""
        self.assertTrue(self.manager_user.is_manager())
        self.assertFalse(self.manager_user.is_vendor())
        self.assertTrue(self.vendor_user.is_vendor())
        self.assertFalse(self.vendor_user.is_manager())

    def test_order_creation_and_blockchain_ledger(self):
        """Verify order lifecycle and block chain recording on finalization."""
        # Check initial chain state
        self.assertEqual(AuditBlock.objects.count(), 0)
        is_valid, errors = verify_chain_integrity()
        self.assertTrue(is_valid)

        # Create Order
        order = Order.objects.create(
            product=self.product,
            vendor=self.vendor,
            quantity=50,
            status='Pending'
        )
        self.assertEqual(order.status, 'Pending')

        # Finalize order (Deliver it)
        order.status = 'Delivered'
        order.save()
        
        # Trigger block recording
        block = add_order_to_ledger(order)
        
        # Verify block matches
        self.assertEqual(AuditBlock.objects.count(), 1)
        db_block = AuditBlock.objects.first()
        self.assertEqual(db_block.index, 1)
        self.assertEqual(db_block.hash, block.hash)

        # Verify chain integrity passes
        is_valid, errors = verify_chain_integrity()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_tamper_detection(self):
        """Verify that altering historical blocks breaks blockchain verification."""
        order = Order.objects.create(product=self.product, vendor=self.vendor, quantity=10, status='Delivered')
        add_order_to_ledger(order)
        
        order2 = Order.objects.create(product=self.product, vendor=self.vendor, quantity=20, status='Delivered')
        add_order_to_ledger(order2)

        # Confirm chain is valid originally
        is_valid, errors = verify_chain_integrity()
        self.assertTrue(is_valid)

        # Tamper with block #1 data
        block1 = AuditBlock.objects.get(index=1)
        payload = json.loads(block1.order_data)
        payload['quantity'] = 9999 # modify quantity
        block1.order_data = json.dumps(payload)
        block1.save()

        # Check chain validity - should now fail
        is_valid, errors = verify_chain_integrity()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_weather_delay_engine_rules(self):
        """Test weather notifications for delay rules (mock and fallbacks)."""
        # Test mock Seattle warning (triggers Heavy Rain delay warning)
        seattle_check = get_weather_warnings('Seattle')
        self.assertTrue(seattle_check['has_warning'])
        self.assertEqual(seattle_check['condition'], 'Heavy Rain')

        # Test clear weather mock
        clear_check = get_weather_warnings('Los Angeles')
        self.assertFalse(clear_check['has_warning'])

    def test_predictive_sales_forecasting(self):
        """Test sales generation, Pandas cleaning, and Scikit-Learn forecasts."""
        # Seeding sales history
        seed_sales_history(self.product)
        self.assertEqual(SalesLog.objects.filter(product=self.product).count(), 12)

        # Verify predictive model training (waiting for the background thread to complete)
        import time
        for _ in range(50):
            forecast = get_product_forecast(self.product)
            if not forecast.get('is_training'):
                break
            time.sleep(0.1)
            
        self.assertIn('projected_sales', forecast)
        self.assertIn('reorder_point', forecast)
        
        # Confirm that current quantity (5) is less than reorder point (should be >10)
        # So item needs reorder
        self.assertTrue(forecast['needs_reorder'])
