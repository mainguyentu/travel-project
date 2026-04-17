from __future__ import annotations

from io import BytesIO
from dataclasses import dataclass
from hashlib import sha1
from time import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

import httpx
from PIL import Image, UnidentifiedImageError

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ImageMigrationStats:
    processed: int = 0
    migrated: int = 0
    skipped: int = 0
    fallback: int = 0


class DestinationImageMigrator:
    def __init__(
        self,
        *,
        enabled: bool,
        cloud_name: str,
        api_key: str,
        api_secret: str,
        upload_folder: str,
        timeout_seconds: float,
        max_bytes: int,
        max_concurrency: int,
    ):
        self.enabled = enabled
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.upload_folder = upload_folder
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self.max_concurrency = max(1, max_concurrency)

    @property
    def configured(self) -> bool:
        return bool(self.cloud_name and self.api_key and self.api_secret)

    def is_cloudinary_url(self, url: str) -> bool:
        if not url:
            return False
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        return "res.cloudinary.com" in host

    def _is_valid_remote_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def migrate_urls(
        self,
        urls: list[str],
        *,
        destination_id: int | None = None,
    ) -> tuple[list[str], ImageMigrationStats]:
        stats = ImageMigrationStats()
        cleaned = [str(item).strip() for item in urls if str(item).strip()]
        if not cleaned:
            return [], stats

        if not self.enabled:
            stats.processed = len(cleaned)
            stats.skipped = len(cleaned)
            return cleaned, stats

        migrated_urls: list[str | None] = [None] * len(cleaned)
        pending: list[tuple[int, str]] = []

        for index, source_url in enumerate(cleaned):
            stats.processed += 1
            if self.is_cloudinary_url(source_url):
                stats.skipped += 1
                migrated_urls[index] = source_url
                continue

            if not self.configured:
                stats.fallback += 1
                logger.warning(
                    "destination_image_migrate_failed stage=config destination_id=%s source_url=%s reason=missing_credentials",
                    destination_id,
                    source_url,
                )
                migrated_urls[index] = source_url
                continue

            pending.append((index, source_url))

        if not pending:
            return [item for item in migrated_urls if item], stats

        if self.max_concurrency <= 1 or len(pending) == 1:
            for index, source_url in pending:
                try:
                    secure_url = self._migrate_one_url(source_url)
                except Exception as exc:  # noqa: BLE001
                    stats.fallback += 1
                    logger.warning(
                        "destination_image_migrate_failed stage=transfer destination_id=%s source_url=%s reason=%s",
                        destination_id,
                        source_url,
                        str(exc),
                    )
                    migrated_urls[index] = source_url
                    continue

                stats.migrated += 1
                migrated_urls[index] = secure_url

            return [item for item in migrated_urls if item], stats

        with ThreadPoolExecutor(max_workers=min(self.max_concurrency, len(pending))) as executor:
            future_map = {executor.submit(self._migrate_one_url, source_url): (index, source_url) for index, source_url in pending}
            for future in as_completed(future_map):
                index, source_url = future_map[future]
                try:
                    secure_url = future.result()
                except Exception as exc:  # noqa: BLE001
                    stats.fallback += 1
                    logger.warning(
                        "destination_image_migrate_failed stage=transfer destination_id=%s source_url=%s reason=%s",
                        destination_id,
                        source_url,
                        str(exc),
                    )
                    migrated_urls[index] = source_url
                    continue

                stats.migrated += 1
                migrated_urls[index] = secure_url

        return [item for item in migrated_urls if item], stats

    def _migrate_one_url(self, source_url: str) -> str:
        binary, mime_type = self._download_source_image(source_url)
        webp_binary = self._convert_to_webp(binary, source_url=source_url)
        return self._upload_to_cloudinary(webp_binary, "image/webp")

    def _convert_to_webp(self, binary: bytes, *, source_url: str) -> bytes:
        try:
            with Image.open(BytesIO(binary)) as image:
                if image.mode not in {"RGB", "RGBA"}:
                    target_mode = "RGBA" if "A" in image.getbands() else "RGB"
                    image = image.convert(target_mode)

                output = BytesIO()
                image.save(output, format="WEBP", quality=85, method=6)
                return output.getvalue()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            logger.warning(
                "destination_image_convert_failed stage=convert source_url=%s reason=%s",
                source_url,
                str(exc),
            )
            raise

    def _download_source_image(self, source_url: str) -> tuple[bytes, str]:
        if not self._is_valid_remote_url(source_url):
            raise ValueError("invalid_source_url")

        timeout = httpx.Timeout(self.timeout_seconds)
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(source_url)
            response.raise_for_status()

            content_length_raw = response.headers.get("content-length")
            if content_length_raw:
                try:
                    content_length = int(content_length_raw)
                    if content_length > self.max_bytes:
                        raise ValueError("source_too_large")
                except ValueError as exc:
                    if str(exc) == "source_too_large":
                        raise

            body = response.content
            if len(body) > self.max_bytes:
                raise ValueError("source_too_large")

            mime_type = response.headers.get("content-type") or "application/octet-stream"
            return body, mime_type

    def _build_signature(self, *, timestamp: int) -> str:
        params = f"folder={self.upload_folder}&timestamp={timestamp}{self.api_secret}"
        return sha1(params.encode("utf-8")).hexdigest()

    def _upload_to_cloudinary(self, binary: bytes, mime_type: str) -> str:
        timestamp = int(time())
        signature = self._build_signature(timestamp=timestamp)
        endpoint = f"https://api.cloudinary.com/v1_1/{self.cloud_name}/image/upload"

        files = {"file": ("destination-image", binary, mime_type)}
        data = {
            "api_key": self.api_key,
            "timestamp": timestamp,
            "signature": signature,
            "folder": self.upload_folder,
        }
        timeout = httpx.Timeout(self.timeout_seconds)
        with httpx.Client(timeout=timeout) as client:
            response = client.post(endpoint, files=files, data=data)
            response.raise_for_status()
            payload = response.json()

        secure_url = payload.get("secure_url")
        if not isinstance(secure_url, str) or not secure_url.strip():
            raise ValueError("missing_secure_url")
        return secure_url.strip()


_destination_image_migrator: DestinationImageMigrator | None = None


def get_destination_image_migrator() -> DestinationImageMigrator:
    global _destination_image_migrator
    if _destination_image_migrator is None:
        _destination_image_migrator = DestinationImageMigrator(
            enabled=settings.destination_image_cloudinary_enabled,
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            upload_folder=settings.cloudinary_upload_folder,
            timeout_seconds=settings.destination_image_timeout_seconds,
            max_bytes=settings.destination_image_max_bytes,
            max_concurrency=settings.destination_image_upload_concurrency,
        )
    return _destination_image_migrator
