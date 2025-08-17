from django.db import models
from django.utils.text import slugify
from django.db import models
from django.conf import settings


class Category(models.Model):  # flat categories (no parent)
    name_en = models.CharField(max_length=200, unique=True)
    name_ar = models.CharField(max_length=200, blank=True, default="")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)[:210]
        super().save(*args, **kwargs)

    def __str__(self): return self.name_en

    class Meta:
        db_table = "category"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name_en = models.CharField(max_length=220)
    name_ar = models.CharField(max_length=220, blank=True, default="")
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    description_en = models.TextField(blank=True, default="")
    description_ar = models.TextField(blank=True, default="")
    price_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="BHD")
    sku = models.CharField(max_length=64, unique=True)
    stock_qty = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    avg_rating = models.FloatField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)[:230]
        super().save(*args, **kwargs)

    def __str__(self): return self.name_en

    class Meta:
        db_table = "product"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    object_key = models.CharField(max_length=512)  # S3 object key only
    alt_en = models.CharField(max_length=200, blank=True, default="")
    alt_ar = models.CharField(max_length=200, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "product_image"



class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    unit_price_cents = models.PositiveIntegerField()  # snapshot at add-time

    class Meta:
        db_table = "cart_item"

class Order(models.Model):
    STATUS = (("pending","pending"),("paid","paid"),("shipped","shipped"),("cancelled","cancelled"),("refunded","refunded"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=24, unique=True)
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    subtotal_cents = models.PositiveIntegerField(default=0)
    vat_rate = models.FloatField(default=10.0)  # percent
    vat_amount_cents = models.PositiveIntegerField(default=0)
    shipping_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="BHD")
    payment_status = models.CharField(max_length=16, default="init")
    payment_provider = models.CharField(max_length=32, blank=True, default="")
    payment_ref = models.CharField(max_length=64, blank=True, default="")
    placed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "orders"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    name_snapshot = models.CharField(max_length=220)
    qty = models.PositiveIntegerField()
    unit_price_cents = models.PositiveIntegerField()
    total_cents = models.PositiveIntegerField()

    class Meta:
        db_table = "order_item"

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user","product")
        db_table = "ratings"

class Complaint(models.Model):
    TYPE = (("product","product"),("delivery","delivery"),("payment","payment"),("other","other"))
    STATUS = (("new","new"),("in_progress","in_progress"),("resolved","resolved"),("closed","closed"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.OneToOneField(Order,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    type = models.CharField(max_length=20, choices=TYPE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="new")
    admin_note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "complaints"
