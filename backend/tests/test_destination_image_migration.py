from io import BytesIO

from app.db.models import Category, Destination
from app.db.session import SessionLocal
from app.services.destination_images import DestinationImageMigrator
from app.services.destinations import DestinationService
from PIL import Image


def test_migrator_disabled_returns_original_urls():
    migrator = DestinationImageMigrator(
        enabled=False,
        cloud_name="",
        api_key="",
        api_secret="",
        upload_folder="travel/destinations",
        timeout_seconds=3.0,
        max_bytes=1024,
        max_concurrency=3,
    )

    migrated, stats = migrator.migrate_urls([
        "https://example.com/a.jpg",
        "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    ])

    assert migrated == [
        "https://example.com/a.jpg",
        "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    ]
    assert stats.processed == 2
    assert stats.skipped == 2
    assert stats.migrated == 0
    assert stats.fallback == 0


def test_migrator_fallback_when_transfer_fails(monkeypatch):
    migrator = DestinationImageMigrator(
        enabled=True,
        cloud_name="demo",
        api_key="key",
        api_secret="secret",
        upload_folder="travel/destinations",
        timeout_seconds=3.0,
        max_bytes=1024,
        max_concurrency=3,
    )

    def _boom(_: str) -> str:
        raise RuntimeError("upload_failed")

    monkeypatch.setattr(migrator, "_migrate_one_url", _boom)

    source = "https://example.com/a.jpg"
    migrated, stats = migrator.migrate_urls([source], destination_id=101)

    assert migrated == [source]
    assert stats.processed == 1
    assert stats.fallback == 1
    assert stats.migrated == 0


def test_migrator_converts_source_image_to_webp_before_upload(monkeypatch):
    migrator = DestinationImageMigrator(
        enabled=True,
        cloud_name="demo",
        api_key="key",
        api_secret="secret",
        upload_folder="travel/destinations",
        timeout_seconds=3.0,
        max_bytes=1024 * 1024,
        max_concurrency=1,
    )

    source_image = Image.new("RGB", (2, 2), color="red")
    source_buffer = BytesIO()
    source_image.save(source_buffer, format="PNG")

    captured = {}

    def _fake_download(_: str):
        return source_buffer.getvalue(), "image/png"

    def _fake_upload(binary: bytes, mime_type: str):
        captured["mime_type"] = mime_type
        captured["binary"] = binary
        return "https://res.cloudinary.com/demo/image/upload/sample.webp"

    monkeypatch.setattr(migrator, "_download_source_image", _fake_download)
    monkeypatch.setattr(migrator, "_upload_to_cloudinary", _fake_upload)

    result = migrator._migrate_one_url("https://example.com/a.png")

    assert result.endswith("sample.webp")
    assert captured["mime_type"] == "image/webp"
    assert Image.open(BytesIO(captured["binary"])).format == "WEBP"


def test_destination_service_create_migrates_images(monkeypatch):
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.slug == "image-migrate-cat").first()
        if not category:
            category = Category(name="Image Migrate", slug="image-migrate-cat", descriptions=None)
            db.add(category)
            db.flush()

        service = DestinationService(db)

        def _fake_migrate(urls, destination_id=None):
            return [f"https://res.cloudinary.com/demo/{idx}" for idx, _ in enumerate(urls, start=1)], type(
                "Stats",
                (),
                {"processed": len(urls), "migrated": len(urls), "skipped": 0, "fallback": 0},
            )()

        monkeypatch.setattr(service.image_migrator, "migrate_urls", _fake_migrate)

        destination = service.create(
            {
                "name": "Cloudinary Destination",
                "img_url": "https://example.com/original.jpg",
                "status": "active",
            },
            [int(category.id)],
        )
        db.commit()

        db.refresh(destination)
        assert destination.img_url == "https://res.cloudinary.com/demo/1"
        assert destination.img_urls == ["https://res.cloudinary.com/demo/1"]
    finally:
        db.close()


def test_destination_service_update_without_image_does_not_clear_existing(monkeypatch):
    db = SessionLocal()
    try:
        destination = Destination(
            name="Existing image",
            slug="existing-image-no-clear",
            status="active",
            img_url="https://res.cloudinary.com/demo/existing.jpg",
            img_urls=["https://res.cloudinary.com/demo/existing.jpg"],
        )
        db.add(destination)
        db.flush()

        service = DestinationService(db)
        called = {"value": False}

        def _fake_migrate(urls, destination_id=None):
            called["value"] = True
            return urls, type("Stats", (), {"processed": 0, "migrated": 0, "skipped": 0, "fallback": 0})()

        monkeypatch.setattr(service.image_migrator, "migrate_urls", _fake_migrate)

        updated = service.update(int(destination.id), {"description": "No image update"}, category_ids=None)
        db.commit()
        db.refresh(updated)

        assert called["value"] is False
        assert updated.img_url == "https://res.cloudinary.com/demo/existing.jpg"
        assert updated.img_urls == ["https://res.cloudinary.com/demo/existing.jpg"]
    finally:
        db.close()
