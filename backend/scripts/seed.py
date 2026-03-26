import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.db.models import User, Category, Destination, CategoryDestination
from app.core.security import hash_password


def upsert_user(db, name, email, password, role):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(name=name, email=email, password_hash=hash_password(password), role=role, status="active")
    db.add(user)
    db.flush()
    return user


def upsert_category(db, name, slug, descriptions=None):
    category = db.query(Category).filter(Category.slug == slug).first()
    if category:
        return category
    category = Category(name=name, slug=slug, descriptions=descriptions)
    db.add(category)
    db.flush()
    return category


def upsert_destination(db, data, category_ids):
    destination = db.query(Destination).filter(Destination.slug == data["slug"]).first()
    if not destination:
        destination = Destination(**data)
        db.add(destination)
        db.flush()
    existing = {cd.category_id for cd in destination.categories}
    for cid in category_ids:
        if cid not in existing:
            destination.categories.append(CategoryDestination(category_id=cid, destination_id=destination.id))
    db.flush()
    return destination


def run():
    db = SessionLocal()
    try:
        admin = upsert_user(db, "Admin", "admin@alats.vn", "Admin@123", "admin")
        user = upsert_user(db, "User", "user@alats.vn", "User@123", "user")

        c_beach = upsert_category(db, "Bai bien", "beach", "Cac bai bien dep")
        c_food = upsert_category(db, "Am thuc", "food", "Quan an, mon ngon")
        c_culture = upsert_category(db, "Van hoa", "culture", "Dia diem van hoa")
        c_nature = upsert_category(db, "Thien nhien", "nature", "Canh quan thien nhien")
        c_adventure = upsert_category(db, "Kham pha", "adventure", "Trai nghiem mao hiem")
        c_shopping = upsert_category(db, "Mua sam", "shopping", "Cho, trung tam mua sam")

        destinations = [
            {
                "name": "My Khe Beach",
                "slug": "my-khe-beach",
                "address": "Vo Nguyen Giap, Da Nang",
                "description": "Bai bien noi tieng nhat Da Nang",
                "price_level": "free",
                "open_hour": "All day",
                "img_url": "https://example.com/mykhe.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.0595,
                "lng": 108.2466,
                "status": "active",
            },
            {
                "name": "Son Tra Peninsula",
                "slug": "son-tra-peninsula",
                "address": "Son Tra, Da Nang",
                "description": "Ban dao Son Tra voi canh dep",
                "price_level": "free",
                "open_hour": "All day",
                "img_url": "https://example.com/sontra.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.1180,
                "lng": 108.3022,
                "status": "active",
            },
            {
                "name": "Ba Na Hills",
                "slug": "ba-na-hills",
                "address": "Hoa Ninh, Hoa Vang",
                "description": "Khu du lich Ba Na Hills",
                "price_level": "high",
                "open_hour": "08:00-22:00",
                "img_url": "https://example.com/banahills.jpg",
                "url_map": "https://maps.google.com",
                "lat": 15.9955,
                "lng": 107.9967,
                "status": "active",
            },
            {
                "name": "Dragon Bridge",
                "slug": "dragon-bridge",
                "address": "Nguyen Van Linh, Da Nang",
                "description": "Cau Rong noi tieng phun lua",
                "price_level": "free",
                "open_hour": "All day",
                "img_url": "https://example.com/dragonbridge.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.0608,
                "lng": 108.2286,
                "status": "active",
            },
            {
                "name": "Han Market",
                "slug": "han-market",
                "address": "Tran Phu, Da Nang",
                "description": "Cho Han mua sam dac san",
                "price_level": "low",
                "open_hour": "06:00-19:00",
                "img_url": "https://example.com/hanmarket.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.0687,
                "lng": 108.2248,
                "status": "active",
            },
            {
                "name": "Hoi An Ancient Town",
                "slug": "hoi-an-ancient-town",
                "address": "Hoi An, Quang Nam",
                "description": "Pho co Hoi An gan Da Nang",
                "price_level": "medium",
                "open_hour": "08:00-21:00",
                "img_url": "https://example.com/hoian.jpg",
                "url_map": "https://maps.google.com",
                "lat": 15.8801,
                "lng": 108.3380,
                "status": "active",
            },
            {
                "name": "Asia Park",
                "slug": "asia-park",
                "address": "2/9 Street, Da Nang",
                "description": "Cong vien vui choi Asia Park",
                "price_level": "medium",
                "open_hour": "15:00-22:00",
                "img_url": "https://example.com/asiapark.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.0308,
                "lng": 108.2168,
                "status": "active",
            },
            {
                "name": "Marble Mountains",
                "slug": "marble-mountains",
                "address": "Ngu Hanh Son, Da Nang",
                "description": "Nui Ngu Hanh Son",
                "price_level": "low",
                "open_hour": "07:00-17:00",
                "img_url": "https://example.com/marble.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.0013,
                "lng": 108.2645,
                "status": "active",
            },
            {
                "name": "Con Market",
                "slug": "con-market",
                "address": "Hung Vuong, Da Nang",
                "description": "Cho Con am thuc va mua sam",
                "price_level": "low",
                "open_hour": "06:00-18:00",
                "img_url": "https://example.com/conmarket.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.0602,
                "lng": 108.2118,
                "status": "active",
            },
            {
                "name": "Hai Van Pass",
                "slug": "hai-van-pass",
                "address": "Hai Van, Da Nang",
                "description": "Deo Hai Van noi tieng",
                "price_level": "free",
                "open_hour": "All day",
                "img_url": "https://example.com/haivan.jpg",
                "url_map": "https://maps.google.com",
                "lat": 16.1905,
                "lng": 108.1027,
                "status": "active",
            },
        ]

        mapping = {
            "my-khe-beach": [c_beach.id, c_nature.id],
            "son-tra-peninsula": [c_nature.id, c_adventure.id],
            "ba-na-hills": [c_adventure.id, c_culture.id],
            "dragon-bridge": [c_culture.id],
            "han-market": [c_shopping.id, c_food.id],
            "hoi-an-ancient-town": [c_culture.id],
            "asia-park": [c_adventure.id],
            "marble-mountains": [c_nature.id, c_culture.id],
            "con-market": [c_food.id, c_shopping.id],
            "hai-van-pass": [c_nature.id, c_adventure.id],
        }

        for d in destinations:
            upsert_destination(db, d, mapping.get(d["slug"], []))

        db.commit()
        print("Seed done")
        print(f"Admin: {admin.email} / Admin@123")
        print(f"User: {user.email} / User@123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
