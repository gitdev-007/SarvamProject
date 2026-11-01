import logging
import uuid
import boto3
from botocore.config import Config

from app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL_S3,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    NEON_STORAGE_BUCKET,
)

logger = logging.getLogger(__name__)

s3_config = Config(
    s3={"addressing_style": "path"},  # Path-style addressing required by Neon
    signature_version="s3v4",
    retries={"max_attempts": 3, "mode": "standard"},
)


def is_storage_configured() -> bool:
    return bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_ENDPOINT_URL_S3)


def get_s3_client():
    if not is_storage_configured():
        return None
    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL_S3,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        config=s3_config,
    )


def generate_object_key(tender_id: int | None, original_filename: str) -> str:
    """Generates a unique, non-colliding storage key."""
    clean_name = original_filename.replace(" ", "_")
    unique_id = uuid.uuid4().hex[:12]
    if tender_id:
        return f"tenders/{tender_id}/{unique_id}_{clean_name}"
    return f"vault/{unique_id}_{clean_name}"


def upload_file_to_neon(file_bytes: bytes, object_key: str, content_type: str = "application/pdf") -> str:
    """Uploads a file to the private Neon Object Storage bucket."""
    client = get_s3_client()
    if not client:
        raise ValueError("Neon Object Storage is not configured")
    try:
        client.put_object(
            Bucket=NEON_STORAGE_BUCKET,
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        return object_key
    except Exception as e:
        logger.error(f"Failed to upload object {object_key} to Neon Storage: {e}")
        raise e


def generate_presigned_download_url(object_key: str, expiration_seconds: int = 3600) -> str:
    """Generates a secure, temporary presigned download URL for a private object."""
    client = get_s3_client()
    if not client:
        raise ValueError("Neon Object Storage is not configured")
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": NEON_STORAGE_BUCKET, "Key": object_key},
        ExpiresIn=expiration_seconds,
    )


def download_file_bytes_from_neon(object_key: str) -> bytes:
    """Downloads an object from Neon Storage as bytes."""
    client = get_s3_client()
    if not client:
        raise ValueError("Neon Object Storage is not configured")
    response = client.get_object(Bucket=NEON_STORAGE_BUCKET, Key=object_key)
    return response["Body"].read()


def delete_file_from_neon(object_key: str) -> bool:
    """Deletes an object from Neon Storage."""
    client = get_s3_client()
    if not client:
        return False
    try:
        client.delete_object(Bucket=NEON_STORAGE_BUCKET, Key=object_key)
        return True
    except Exception as e:
        logger.warning(f"Error deleting object {object_key} from Neon Storage: {e}")
        return False
