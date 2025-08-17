import boto3
from django.conf import settings

def s3_client():
    return boto3.client(
        "s3",
        region_name=getattr(settings, "AWS_S3_REGION", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
    )
