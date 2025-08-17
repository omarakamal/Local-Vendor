from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)) 
]

from shop.view_orders import MyCartView, AddToCartView, CheckoutView, MyOrdersView
urlpatterns += [
    path("me/cart/", MyCartView.as_view()),
    path("me/cart/items/", AddToCartView.as_view()),
    path("checkout/session/", CheckoutView.as_view()),  # creates pending order (no payment yet)
    path("me/orders/", MyOrdersView.as_view()),
]


from shop.view_reviews import CreateRatingView, ComplaintCreateView, MyComplaintsView
urlpatterns += [
    path("ratings/", CreateRatingView.as_view()),
    path("complaints/", ComplaintCreateView.as_view()),
    path("me/complaints/", MyComplaintsView.as_view()),
]
