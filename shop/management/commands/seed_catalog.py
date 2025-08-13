from django.core.management.base import BaseCommand
from shop.models import Category, Product, ProductImage
from django.db import transaction

class Command(BaseCommand):
    help = "Seed sample categories/products"

    @transaction.atomic
    def handle(self, *args, **opts):
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        food = Category.objects.create(name_en="Food", name_ar="أغذية", sort_order=1)
        drinks = Category.objects.create(name_en="Drinks", name_ar="مشروبات", sort_order=2)

        p1 = Product.objects.create(category=food, name_en="Local Honey", name_ar="عسل محلي",
                                    sku="HON-001", price_cents=4500, stock_qty=25)
        p2 = Product.objects.create(category=drinks, name_en="Arabic Coffee", name_ar="قهوة عربية",
                                    sku="CAF-001", price_cents=3000, stock_qty=40)

        ProductImage.objects.create(product=p1, object_key="seed/honey.jpg", alt_en="Honey jar")
        ProductImage.objects.create(product=p2, object_key="seed/coffee.jpg", alt_en="Coffee pack")

        self.stdout.write(self.style.SUCCESS("Seeded categories/products."))
