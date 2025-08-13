from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Category, Product, ProductImage

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username","email","role","is_active","is_staff")

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id","name_en","sku","category","price_cents","stock_qty","is_active")
    list_filter = ("category","is_active")
    search_fields = ("name_en","sku")
    inlines = [ProductImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","name_en","parent","is_active","sort_order")
    list_editable = ("is_active","sort_order")
    prepopulated_fields = {"slug": ("name_en",)}
