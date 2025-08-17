from rest_framework import viewsets
from django.db.models import Q
from .models import Category, Product
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer
)
from .permissions import IsAdminOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True).order_by("sort_order","id")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images").order_by("-id")
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action in ["retrieve","create","update","partial_update"] else ProductListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        cat = self.request.query_params.get("category")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        in_stock = self.request.query_params.get("in_stock")
        sort = self.request.query_params.get("sort")

        if q:
            qs = qs.filter(
                Q(name_en__icontains=q) | Q(description_en__icontains=q) |
                Q(name_ar__icontains=q) | Q(description_ar__icontains=q)
            )
        if cat:
            qs = qs.filter(category__slug=cat)
        if min_price:
            qs = qs.filter(price_cents__gte=int(min_price))
        if max_price:
            qs = qs.filter(price_cents__lte=int(max_price))
        if in_stock == "1":
            qs = qs.filter(stock_qty__gt=0)

        if sort == "price_asc": qs = qs.order_by("price_cents")
        elif sort == "price_desc": qs = qs.order_by("-price_cents")
        elif sort == "newest": qs = qs.order_by("-id")
        return qs
