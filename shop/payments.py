from dataclasses import dataclass

@dataclass
class PaymentInitResult:
    provider: str
    intent_id: str
    redirect_url: str

class PaymentProvider:
    name = "stub"
    def init(self, order, method: str) -> PaymentInitResult:
        # In real impl: call Tap/Checkout.com and return redirect URL
        return PaymentInitResult(self.name, f"intent_{order.order_number}", f"https://example.com/pay/{order.order_number}")

    def handle_webhook(self, payload: dict) -> dict:
        # parse payload and return {"order_number": "...", "status": "captured"|"failed", "payment_ref": "..."}
        return {}
