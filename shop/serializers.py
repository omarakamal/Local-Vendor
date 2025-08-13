from rest_framework import serializers
from .models import Category, Product, ProductImage, User

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id","object_key","alt_en","alt_ar","sort_order"]

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ["id","parent","name_en","name_ar","slug","is_active","sort_order","children"]
    def get_children(self, obj):
        qs = obj.children.filter(is_active=True).order_by("sort_order","id")
        return CategorySerializer(qs, many=True).data

class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name_en", read_only=True)
    class Meta:
        model = Product
        fields = ["id","slug","name_en","name_ar","price_cents","currency","stock_qty","category","category_name","images"]

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ["id","slug","name_en","name_ar","description_en","description_ar",
                  "price_cents","currency","sku","stock_qty","is_active","avg_rating","rating_count",
                  "category","images"]
