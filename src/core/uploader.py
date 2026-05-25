import boto3
import uuid
import datetime
import os
from botocore.config import Config

class R2Uploader:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._client = None

    def _get_client(self):
        if self._client is None:
            config = self.config_manager
            self._client = boto3.client(
                's3',
                endpoint_url=config.get("endpoint_url"),
                aws_access_key_id=config.get("access_key"),
                aws_secret_access_key=config.get("secret_key"),
                config=Config(signature_version='s3v4'),
                region_name='auto'  # Cloudflare R2 usually uses 'auto'
            )
        return self._client

    def upload_image(self, image_bytes: bytes, extension: str = "png") -> str:
        if not self.config_manager.is_valid():
            raise ValueError("R2 configuration is incomplete.")

        client = self._get_client()
        bucket = self.config_manager.get("bucket_name")
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.{extension}"
        
        # Determine target key (path in bucket)
        upload_path = self.config_manager.get("upload_path", "").strip()
        
        # Normalize path: ensure it doesn't start with / and ends with / if not empty
        if upload_path:
            upload_path = upload_path.lstrip("/")
            if not upload_path.endswith("/"):
                upload_path += "/"
        
        key = f"{upload_path}{filename}"

        # Upload
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=image_bytes,
            ContentType=f"image/{extension}"
        )

        # Construct return URL
        custom_domain = self.config_manager.get("custom_domain")
        if custom_domain:
            if not custom_domain.startswith(("http://", "https://")):
                custom_domain = f"https://{custom_domain}"
            if custom_domain.endswith("/"):
                custom_domain = custom_domain[:-1]
            return f"{custom_domain}/{key}"
        else:
            # Fallback to default R2 public URL format if no custom domain
            # Note: This might need adjustment based on R2's specific public bucket access format
            return f"{self.config_manager.get('endpoint_url')}/{bucket}/{key}"
