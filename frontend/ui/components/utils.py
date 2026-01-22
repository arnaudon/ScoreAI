"""Utils."""

import os

import boto3
import streamlit as st
from botocore.config import Config


class S3Helper:
    """S3 helper."""

    def __init__(self, endpoint=None, bucket=None):
        """Initialize the S3 helper."""
        self.endpoint = os.getenv("S3_ENDPOINT", endpoint)
        self.bucket = os.getenv("S3_BUCKET", endpoint)
        self.s3_client = self._init_client()

    def _init_client(self):
        """Initialize the S3 client."""
        return boto3.client(
            "s3",
            endpoint_url="https://" + str(self.endpoint),
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION", "us-east-1"),
            config=Config(
                signature_version="s3v4",
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        )

    def upload_pdf(self, key, file):
        """Upload a pdf file to S3."""
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file,
            ContentType="application/pdf",
            ContentDisposition="inline",
        )

    def delete_pdf(self, key):
        """Delete a pdf file from S3."""
        self.s3_client.delete_object(Bucket=self.bucket, Key=key)

    def download_pdf(self, key):
        """Download a pdf file from S3."""
        return self.s3_client.get_object(Bucket=self.bucket, Key=key)

    def get_pdf_url(self, key):
        """Get the url of a pdf file from S3."""
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
        )


@st.cache_resource
def get_s3_helper(endpoint=None, bucket=None):
    """Get the S3 helper with client and vars"""
    if os.getenv("S3_ENDPOINT"):
        return S3Helper(endpoint=endpoint, bucket=bucket)
    return None


s3_helper = get_s3_helper()
