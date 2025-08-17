from rest_framework import generics, permissions
from django.db.models import F
from .serializers import RatingCreateSerializer, ComplaintSerializer
from .models import Rating, Complaint
from .models import Product

class CreateRatingView(generics.CreateAPIView):
    serializer_class = RatingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        rating = serializer.save(user=self.request.user)
        # update aggregates
        p = rating.product
        p.rating_count = Rating.objects.filter(product=p).count()
        p.avg_rating = Rating.objects.filter(product=p).aggregate(avg=models.Avg("stars"))["avg"] or 0
        p.save(update_fields=["avg_rating","rating_count"])

class ComplaintCreateView(generics.CreateAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyComplaintsView(generics.ListAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user).order_by("-id")
