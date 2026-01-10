"""Utils."""

import os

import boto3
from botocore.config import Config


def get_s3_helper() -> dict:
    """Get the S3 helper with client and vars"""
    return {
        "endpoint": os.getenv("S3_ENDPOINT"),
        "bucket": os.getenv("S3_BUCKET"),
        "s3_client": boto3.client(
            "s3",
            endpoint_url="https://" + str(os.getenv("S3_ENDPOINT")),
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION", "us-east-1"),
            config=Config(
                signature_version="s3v4",
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        ),
    }


s3_helper = get_s3_helper() if os.getenv("S3_ENDPOINT") else None
