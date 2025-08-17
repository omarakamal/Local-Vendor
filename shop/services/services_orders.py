from ..models import Order, OrderItem, Product
from django.utils.crypto import get_random_string

def generate_order_number() -> str:
    return get_random_string(10).upper()

def compute_totals(items, vat_rate: float, shipping_cents: int = 0):
    subtotal = sum(i["qty"] * i["unit_price_cents"] for i in items)
    vat_amount = round(subtotal * (vat_rate/100))
    total = subtotal + vat_amount + shipping_cents
    return subtotal, vat_amount, total


