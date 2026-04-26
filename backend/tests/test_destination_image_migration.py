from io import BytesIO
from uuid import uuid4

from app.db.models import Category, Destination
from app.db.session import SessionLocal
from app.services.destination_images import DestinationImageMigrator
from app.services.destinations import DestinationService
from app.worker.handlers import dispatch_event
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


def test_destination_service_create_many_defers_image_migration(monkeypatch):
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.slug == "image-migrate-bulk-cat").first()
        if not category:
            category = Category(name="Image Migrate Bulk", slug="image-migrate-bulk-cat", descriptions=None)
            db.add(category)
            db.flush()

        service = DestinationService(db)
        called = {"value": False}

        def _fake_migrate(urls, destination_id=None):
            called["value"] = True
            return urls, type("Stats", (), {"processed": 0, "migrated": 0, "skipped": 0, "fallback": 0})()

        monkeypatch.setattr(service.image_migrator, "migrate_urls", _fake_migrate)

        destinations = service.create_many(
            [
                {
                    "name": "Bulk Image Destination",
                    "img_url": "https://example.com/bulk-original.jpg",
                    "status": "active",
                    "category_ids": [int(category.id)],
                }
            ]
        )

        db.commit()

        assert called["value"] is False
        assert destinations[0].img_url == "https://example.com/bulk-original.jpg"
        assert destinations[0].img_urls == ["https://example.com/bulk-original.jpg"]
    finally:
        db.close()


def test_destination_service_create_many_preserves_d_in_category_slug():
    db = SessionLocal()
    try:
        suffix = uuid4().hex[:8]
        service = DestinationService(db)

        destinations = service.create_many(
            [
                {
                    "name": f"Bulk Slug Destination {suffix}",
                    "status": "active",
                    "category": [f"Đà Nẵng {suffix}"],
                }
            ]
        )

        db.commit()

        created = destinations[0]
        category = db.query(Category).filter(Category.name == f"Đà Nẵng {suffix}").first()

        assert created.slug.startswith(f"bulk-slug-destination-{suffix}")
        assert category is not None
        assert category.slug == f"da-nang-{suffix}"
    finally:
        db.close()


def test_worker_handles_bulk_destination_created_events(monkeypatch):
    db = SessionLocal()
    try:
        suffix = uuid4().hex[:8]
        category = Category(name=f"Bulk Worker {suffix}", slug=f"bulk-worker-{suffix}", descriptions="bulk worker")
        db.add(category)
        db.flush()

        first = Destination(
            name=f"Bulk Worker Place 1 {suffix}",
            slug=f"bulk-worker-place-1-{suffix}",
            address="Hue",
            description="First destination for bulk worker test",
            img_url="https://example.com/worker-1.jpg",
            img_urls=["https://example.com/worker-1.jpg"],
            price_level="medium",
            open_hour="All day",
            status="active",
            rating_avg=0,
            view_count=0,
        )
        second = Destination(
            name=f"Bulk Worker Place 2 {suffix}",
            slug=f"bulk-worker-place-2-{suffix}",
            address="Hoi An",
            description="Second destination for bulk worker test",
            img_url="https://example.com/worker-2.jpg",
            img_urls=["https://example.com/worker-2.jpg"],
            price_level="medium",
            open_hour="All day",
            status="active",
            rating_avg=0,
            view_count=0,
        )
        db.add_all([first, second])
        db.commit()

        monkeypatch.setattr("app.worker.handlers.index_destination_document", lambda *_args, **_kwargs: None)

        class _FakeMigrator:
            enabled = True
            configured = True

            def migrate_urls(self, urls, destination_id=None):
                migrated = [f"https://res.cloudinary.com/demo/{destination_id}/{idx}" for idx, _ in enumerate(urls, start=1)]
                return migrated, type(
                    "Stats",
                    (),
                    {"processed": len(urls), "migrated": len(urls), "skipped": 0, "fallback": 0},
                )()

        monkeypatch.setattr("app.worker.handlers.get_destination_image_migrator", lambda: _FakeMigrator())

        event = {
            "event_type": "destination.created",
            "payload": {
                "destinations": [
                    {
                        "id": int(first.id),
                        "name": first.name,
                        "slug": first.slug,
                        "img_url": first.img_url,
                        "img_urls": first.img_urls,
                    },
                    {
                        "id": int(second.id),
                        "name": second.name,
                        "slug": second.slug,
                        "img_url": second.img_url,
                        "img_urls": second.img_urls,
                    },
                ]
            },
        }

        dispatch_event(event)

        db.refresh(first)
        db.refresh(second)
        assert first.img_url == f"https://res.cloudinary.com/demo/{int(first.id)}/1"
        assert first.img_urls == [f"https://res.cloudinary.com/demo/{int(first.id)}/1"]
        assert second.img_url == f"https://res.cloudinary.com/demo/{int(second.id)}/1"
        assert second.img_urls == [f"https://res.cloudinary.com/demo/{int(second.id)}/1"]
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
