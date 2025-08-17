from rest_framework import permissions, serializers, views
from rest_framework.response import Response
from django.conf import settings
from .permissions import IsAdminOrReadOnly
from .s3 import s3_client

class PresignInSerializer(serializers.Serializer):
    object_key = serializers.CharField()
    mime = serializers.CharField(required=False, allow_blank=True)

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "role", "") == "admin")

class PresignUploadView(views.APIView):
    permission_classes = [IsAdmin]
    def post(self, request):
        ser = PresignInSerializer(data=request.data); ser.is_valid(raise_exception=True)
        client = s3_client()
        url = client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": settings.AWS_S3_BUCKET, "Key": ser.validated_data["object_key"], "ContentType": ser.validated_data.get("mime") or "application/octet-stream"},
            ExpiresIn=int(getattr(settings, "AWS_S3_PRESIGN_EXPIRES", 900)),
        )
        return Response({"put_url": url})
