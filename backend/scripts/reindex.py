"""Reindex all active destinations into Elasticsearch (Pha B).

Run inside backend container:
    python scripts/reindex.py
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from sqlalchemy import select  # noqa: E402

from app.db.models import Destination  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.repositories.destinations import DestinationRepository  # noqa: E402
from app.services import search as search_svc  # noqa: E402

if __name__ == "__main__":
    db = SessionLocal()
    try:
        ok = search_svc.ensure_index()
        print(f"index ready: {ok}")
        repo = DestinationRepository(db)
        ids = list(db.scalars(select(Destination.id).where(Destination.status == "active")).all())
        n = 0
        for did in ids:
            dest = repo.get_detail(int(did))
            cats = [c.slug for c in repo.categories_for(int(did))]
            if search_svc.index_destination({
                "id": dest.id, "name": dest.name, "slug": dest.slug,
                "address": dest.address or "", "description": dest.description or "",
                "price_level": dest.price_level, "category_slugs": cats,
                "rating_avg": float(dest.rating_avg or 0), "status": dest.status,
            }):
                n += 1
        print(f"indexed {n}/{len(ids)}")
    finally:
        db.close()
