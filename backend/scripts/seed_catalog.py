"""Seed MVP demo catalog. Idempotent (by slug)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.models import Category, CategoryDestination, Destination, DestinationInsight
from app.db.session import SessionLocal

CATEGORIES = [
    ("Biển", "bien", "Bãi biển và hoạt động ven biển"),
    ("Núi", "nui", "Núi non và trekking"),
    ("Văn hóa", "van-hoa", "Di tích và văn hóa"),
]

DESTINATIONS = [
    {
        "name": "Bãi biển Mỹ Khê",
        "slug": "bai-bien-my-khe",
        "address": "Mỹ Khê, Đà Nẵng",
        "description": "Bãi biển đẹp nổi tiếng Đà Nẵng.",
        "price_level": "free",
        "open_hour": "05:00 đến 18:00",
        "categories": ["bien"],
        "insight": {"summary": "Điểm đến biển được yêu thích.", "highlights": ["Cát trắng", "Nước trong"]},
    },
    {
        "name": "Bà Nà Hills",
        "slug": "ba-na-hills",
        "address": "Hòa Ninh, Hòa Vang, Đà Nẵng",
        "description": "Khu du lịch trên núi với Cầu Vàng.",
        "price_level": "high",
        "open_hour": "08:00 đến 17:00",
        "categories": ["nui", "van-hoa"],
        "insight": {"summary": "Điểm đến núi nổi bật.", "highlights": ["Cầu Vàng", "Khí hậu mát"]},
    },
    {
        "name": "Phố cổ Hội An",
        "slug": "pho-co-hoi-an",
        "address": "Hội An, Quảng Nam",
        "description": "Di sản văn hóa thế giới.",
        "price_level": "low",
        "open_hour": "08:00 đến 21:00",
        "categories": ["van-hoa"],
        "insight": {"summary": "Phố cổ đèn lồng.", "highlights": ["Đèn lồng", "Ẩm thực"]},
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        cats = {}
        for name, slug, desc in CATEGORIES:
            c = db.query(Category).filter_by(slug=slug).first()
            if not c:
                c = Category(name=name, slug=slug, descriptions=desc)
                db.add(c)
                db.flush()
            cats[slug] = c
        for item in DESTINATIONS:
            d = db.query(Destination).filter_by(slug=item["slug"]).first()
            if not d:
                d = Destination(
                    name=item["name"],
                    slug=item["slug"],
                    address=item["address"],
                    description=item["description"],
                    price_level=item["price_level"],
                    open_hour=item["open_hour"],
                    status="active",
                )
                db.add(d)
                db.flush()
            for cslug in item["categories"]:
                exists = (
                    db.query(CategoryDestination)
                    .filter_by(category_id=cats[cslug].id, destination_id=d.id)
                    .first()
                )
                if not exists:
                    db.add(CategoryDestination(category_id=cats[cslug].id, destination_id=d.id))
            if not db.get(DestinationInsight, d.id):
                db.add(DestinationInsight(destination_id=d.id, final_data=item["insight"]))
        db.commit()
        print("seeded catalog")
    finally:
        db.close()


if __name__ == "__main__":
    main()
