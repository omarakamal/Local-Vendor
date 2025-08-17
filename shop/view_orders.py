from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Cart, CartItem, Order
from .serializers import CartSerializer, AddToCartSerializer, CheckoutSerializer, OrderSerializer

class MyCartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.CreateAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        item = serializer.save(self.request.user)
        self.instance = item.cart  # for response

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(CartSerializer(self.instance).data)

class CheckoutView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data); ser.is_valid(raise_exception=True)
        order = ser.save(request.user)
        return Response(OrderSerializer(order).data)

class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-id")
