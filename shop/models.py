from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Create your models here.

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True


class User(AbstractUser):
    ROLE_CHOICES = (("admin","Admin"),("customer","Customer"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")



class Category(TimeStamped):
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    name_en = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True, default="")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)[:210]
        super().save(*args, **kwargs)

    def __str__(self): return self.name_en


class Product(TimeStamped):
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)[:230]
        super().save(*args, **kwargs)

    def __str__(self): return self.name_en

class ProductImage(TimeStamped):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    object_key = models.CharField(max_length=512)  # S3 object key, not a public URL
    alt_en = models.CharField(max_length=200, blank=True, default="")
    alt_ar = models.CharField(max_length=200, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
