from rest_framework import serializers
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem

from rest_framework import serializers
from .models import Product
from .services import compute_totals, generate_order_number

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name_en","name_ar","slug","is_active","sort_order"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id","object_key","alt_en","alt_ar","sort_order"]

class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name_en", read_only=True)
    class Meta:
        model = Product
        fields = ["id","slug","name_en","name_ar","price_cents","currency","stock_qty",
                  "category","category_name","images","is_active","created_at"]

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ["id","slug","name_en","name_ar","description_en","description_ar",
                  "price_cents","currency","sku","stock_qty","is_active","avg_rating","rating_count",
                  "category","images","created_at"]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id","product","qty","unit_price_cents"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ["id","items","created_at","updated_at"]

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1, default=1)

    def save(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        product = Product.objects.get(id=self.validated_data["product_id"])
        item = CartItem.objects.create(
            cart=cart,
            product=product,
            qty=self.validated_data["qty"],
            unit_price_cents=product.price_cents,
        )
        return item

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id","product","name_snapshot","qty","unit_price_cents","total_cents"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id","order_number","status","subtotal_cents","vat_rate","vat_amount_cents",
                  "shipping_cents","total_cents","currency","payment_status","payment_provider",
                  "payment_ref","placed_at","items"]

class CheckoutSerializer(serializers.Serializer):
    vat_rate = serializers.FloatField(default=10.0)
    shipping_cents = serializers.IntegerField(default=0)

    def save(self, user):
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.select_related("product")
        items = [{"qty":ci.qty, "unit_price_cents":ci.unit_price_cents} for ci in cart_items]
        subtotal, vat_amount, total = compute_totals(items, self.validated_data["vat_rate"], self.validated_data["shipping_cents"])
        order = Order.objects.create(
            user=user,
            order_number=generate_order_number(),
            subtotal_cents=subtotal,
            vat_rate=self.validated_data["vat_rate"],
            vat_amount_cents=vat_amount,
            shipping_cents=self.validated_data["shipping_cents"],
            total_cents=total,
        )
        # snapshot items
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                product=ci.product,
                name_snapshot=ci.product.name_en,
                qty=ci.qty,
                unit_price_cents=ci.unit_price_cents,
                total_cents=ci.qty * ci.unit_price_cents,
            )
        cart.items.all().delete()
        return order



from rest_framework import serializers
from .models import Rating, Complaint

class RatingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["stars","comment","product","order_item"]
    def validate(self, attrs):
        oi = attrs["order_item"]
        if oi.product_id != attrs["product"].id or oi.order.user_id != self.context["request"].user.id:
            raise serializers.ValidationError("Verified purchase required.")
        return attrs

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["id","order_id","type","message","status","admin_note","created_at"]
        read_only_fields = ["status","admin_note","created_at"]
