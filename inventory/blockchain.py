import hashlib
import json
import time
from django.utils import timezone
from .models import AuditBlock

class OrderBlock:
    def __init__(self, index, previous_hash, order_payload, timestamp=None):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.previous_hash = previous_hash
        self.order_payload = order_payload
        self.hash = self.compute_block_hash()

    def compute_block_hash(self):
        # Normalize timestamp to integer UNIX timestamp to prevent string/timezone format mismatches across databases
        ts = self.timestamp
        if not isinstance(ts, (int, float)):
            ts = int(ts.timestamp())
        else:
            ts = int(ts)
            
        block_string = json.dumps({
            "index": self.index,
            "timestamp": ts,
            "previous_hash": self.previous_hash,
            "order_payload": self.order_payload
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

    new_block = OrderBlock(
        index=next_index,
        previous_hash=previous_hash,
        order_payload=payload_str,
        timestamp=timezone.now()
    )

    AuditBlock.objects.create(
        index=new_block.index,
        timestamp=new_block.timestamp,
        order_data=new_block.order_payload,
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
        # Reconstruct OrderBlock from DB record to check signature
        ob = OrderBlock(
            index=block.index,
            previous_hash=block.previous_hash,
            order_payload=block.order_data,
            timestamp=block.timestamp
        )

        if block.hash != ob.hash:
            errors.append(f"Block #{block.index} hash mismatch. Database hash: {block.hash}, calculated: {ob.hash}")
        
        if block.previous_hash != previous_hash:
            errors.append(f"Block #{block.index} link mismatch. Previous hash field: {block.previous_hash}, expected: {previous_hash}")

        previous_hash = block.hash

    return len(errors) == 0, errors

