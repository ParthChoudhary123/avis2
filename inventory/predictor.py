import threading
import time
import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from .models import Product, Stock, SalesLog

# Global thread-safe cache for predictions
# format: {product_id: {"projected_sales": float, "reorder_point": float, "last_updated": float, "is_training": bool}}
PREDICTION_CACHE = {}
cache_lock = threading.Lock()

def seed_sales_history(product):
    """
    Seed 12 months of realistic sales history for a product if it has less than 6 logs.
    """
    count = SalesLog.objects.filter(product=product).count()
    if count >= 6:
        return
    
    today = datetime.date.today()
    for i in range(12, 0, -1):
        # Subtract months
        year = today.year - (1 if today.month <= i else 0)
        month = (today.month - i) % 12
        if month == 0:
            month = 12
        log_date = datetime.date(year, month, 1)
        
        # Make a seasonal pattern: higher sales in Nov/Dec, lower in Jan/Feb
        base_sales = 30
        if month in [11, 12]:
            seasonal_boost = 25
        elif month in [7, 8]:
            seasonal_boost = 15
        elif month in [1, 2]:
            seasonal_boost = -10
        else:
            seasonal_boost = 0
            
        quantity = max(10, int(base_sales + seasonal_boost + np.random.randint(-5, 6)))
        
        SalesLog.objects.get_or_create(
            product=product,
            month=log_date,
            defaults={'quantity_sold': quantity}
        )

def _train_and_predict(product_id):
    """
    Actual training logic run in a separate background thread.
    """
    try:
        product = Product.objects.get(id=product_id)
        seed_sales_history(product)
        
        logs = SalesLog.objects.filter(product=product).order_by('month')
        if not logs.exists():
            with cache_lock:
                PREDICTION_CACHE[product_id] = {
                    "projected_sales": 0.0,
                    "reorder_point": 10.0,
                    "last_updated": time.time(),
                    "is_training": False,
                    "error": "No sales logs available"
                }
            return

        # Load into pandas DataFrame
        data = {
            'month_date': [log.month for log in logs],
            'quantity_sold': [log.quantity_sold for log in logs]
        }
        df = pd.DataFrame(data)
        
        # Handle data preparation: clean, handle nulls/resample
        df.set_index('month_date', inplace=True)
        df = df.resample('MS').asfreq().fillna(0)
        df.reset_index(inplace=True)
        
        df['time_index'] = range(1, len(df) + 1)
        
        # Fit Linear Regression model
        X = df[['time_index']].values
        y = df['quantity_sold'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next month (time_index = len(df) + 1)
        next_month_index = len(df) + 1
        predicted_sales = float(model.predict([[next_month_index]])[0])
        predicted_sales = max(0.0, predicted_sales)
        
        # Calculate Smart Reorder Point
        # Smart Reorder Point math: Forecasted sales volume plus 20% safety margin
        smart_reorder_point = int(predicted_sales * 1.20)
        reorder_point = max(smart_reorder_point, 5)
        
        with cache_lock:
            PREDICTION_CACHE[product_id] = {
                "projected_sales": round(predicted_sales, 2),
                "reorder_point": reorder_point,
                "last_updated": time.time(),
                "is_training": False
            }
    except Exception as e:
        with cache_lock:
            PREDICTION_CACHE[product_id] = {
                "projected_sales": 0.0,
                "reorder_point": 10.0,
                "last_updated": time.time(),
                "is_training": False,
                "error": str(e)
            }

def get_product_forecast(product):
    """
    Get cached prediction or launch background thread if not cached or expired.
    Returns a dictionary of prediction results.
    """
    product_id = product.id
    now = time.time()
    
    with cache_lock:
        cache_entry = PREDICTION_CACHE.get(product_id)
        
    if not cache_entry or (now - cache_entry["last_updated"] > 3600 and not cache_entry.get("is_training")):
        with cache_lock:
            if not cache_entry:
                PREDICTION_CACHE[product_id] = {
                    "projected_sales": 0.0,
                    "reorder_point": 10.0,
                    "last_updated": now,
                    "is_training": True
                }
            else:
                cache_entry["is_training"] = True
                
        thread = threading.Thread(target=_train_and_predict, args=(product_id,))
        thread.daemon = True
        thread.start()
        
        if not cache_entry:
            return {
                "projected_sales": 0.0,
                "reorder_point": 10.0,
                "is_training": True,
                "needs_reorder": False
            }
            
    try:
        qty = product.stock.current_quantity
    except Stock.DoesNotExist:
        qty = 0
        
    reorder_threshold = cache_entry.get("reorder_point", 10.0)
    needs_reorder = qty < reorder_threshold
    
    return {
        "projected_sales": cache_entry.get("projected_sales", 0.0),
        "reorder_point": reorder_threshold,
        "is_training": cache_entry.get("is_training", False),
        "needs_reorder": needs_reorder
    }
