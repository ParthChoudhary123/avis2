import hashlib
import json
from django.utils import timezone
from .models import AuditBlock

class Block:
    def __init__(self, index, timestamp, order_data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.order_data = order_data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Normalize timestamp to integer UNIX timestamp to prevent string/timezone format mismatches across databases
        ts = self.timestamp
        if not isinstance(ts, (int, float)):
            ts = int(ts.timestamp())
            
        block_string = json.dumps({
            "index": self.index,
            "timestamp": ts,
            "order_data": self.order_data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()


def add_order_to_ledger(order):
    """
    Creates and saves a new block in the database for the given finalized order.
    """
    payload = {
        "order_id": order.id,
        "product_sku": order.product.sku,
        "product_name": order.product.name,
        "vendor_name": order.vendor.name,
        "quantity": order.quantity,
        "status": order.status,
        "timestamp": str(timezone.now())
    }
    payload_str = json.dumps(payload, sort_keys=True)

    last_block = AuditBlock.objects.order_by('-index').first()
    if last_block:
        next_index = last_block.index + 1
        previous_hash = last_block.hash
    else:
        next_index = 1
        previous_hash = "0" * 64

    new_block = Block(
        index=next_index,
        timestamp=timezone.now(),
        order_data=payload_str,
        previous_hash=previous_hash
    )

    AuditBlock.objects.create(
        index=new_block.index,
        timestamp=new_block.timestamp,
        order_data=new_block.order_data,
        previous_hash=new_block.previous_hash,
        hash=new_block.hash
    )
    return new_block


def verify_chain_integrity():
    """
    Validates the entire blockchain stored in the database.
    Returns (is_valid, list_of_errors).
    """
    blocks = AuditBlock.objects.order_by('index')
    errors = []
    
    previous_hash = "0" * 64
    for block in blocks:
        ts = block.timestamp
        if not isinstance(ts, (int, float)):
            ts = int(ts.timestamp())
            
        block_string = json.dumps({
            "index": block.index,
            "timestamp": ts,
            "order_data": block.order_data,
            "previous_hash": block.previous_hash
        }, sort_keys=True)
        calculated_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()

        if block.hash != calculated_hash:
            errors.append(f"Block #{block.index} hash mismatch. Database hash: {block.hash}, calculated: {calculated_hash}")
        
        if block.previous_hash != previous_hash:
            errors.append(f"Block #{block.index} link mismatch. Previous hash field: {block.previous_hash}, expected: {previous_hash}")

        previous_hash = block.hash

    return len(errors) == 0, errors
