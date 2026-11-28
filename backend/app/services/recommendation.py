"""Recommendation engine (BE 1.3.0).

Nguyên tắc: mọi điểm số đọc từ `destination_insights.final_data`
(rating_avg/count/sum, favorite_count, view_count, categories, status).
Rating là dữ liệu tổng hợp từ nguồn chính thống (nhập tay qua admin bulk),
KHÔNG dùng rating cá nhân của user. Hồ sơ user suy từ favorites + user_views.
"""
from __future__ import annotations

import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Category, CategoryDestination, Destination, DestinationInsight, Favorite
from app.repositories.destinations import DestinationRepository

PRICE_ORDER = ["free", "low", "medium", "high"]

MATCHED_THRESHOLD = 60.0
EXPLORE_MIN = 40.0
EXPLORE_MAX_ITEMS = 10
EXPLORE_MAX_PER_CATEGORY = 2


def _blended_quality(rating_avg: float, rating_count: int) -> float:
    """Blended score 0..1 (baseline 50 theo insight_design.md)."""
    confidence = min(1.0, rating_count / 50.0)
    return (rating_avg / 5.0) * confidence + 0.5 * (1.0 - confidence)


def _price_score(pref: str | None, actual: str | None) -> float:
    if not pref or not actual or pref not in PRICE_ORDER or actual not in PRICE_ORDER:
        return 0.0
    d = abs(PRICE_ORDER.index(pref) - PRICE_ORDER.index(actual))
    if d == 0:
        return 10.0
    if d == 1:
        return 5.0
    return 0.0


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DestinationRepository(db)

    # -- profile ---------------------------------------------------------
    def profile(self, user_id: int) -> dict:
        signals = self.repo.user_profile_signals(user_id)
        fav_ids = set(signals["favorite_ids"])
        view_counts = signals["views"]

        cat_weight: dict[str, float] = {}
        price_votes: dict[str, float] = {}
        touched: set[int] = set()

        def _add(dest_id: int, w: float) -> None:
            touched.add(dest_id)
            dest = self.repo.get_detail(dest_id)
            if not dest or dest.status != "active":
                return
            for c in self.repo.categories_for(dest_id):
                cat_weight[c.slug] = cat_weight.get(c.slug, 0.0) + w
            if dest.price_level:
                price_votes[dest.price_level] = price_votes.get(dest.price_level, 0.0) + w

        for did in fav_ids:
            _add(did, 1.0)
        for did, n in view_counts.items():
            if did in fav_ids:
                continue
            _add(did, 0.6 if n >= 2 else 0.4)

        max_w = max(cat_weight.values()) if cat_weight else 0.0
        top_categories = (
            {k: round(v / max_w, 3) for k, v in sorted(cat_weight.items(), key=lambda kv: -kv[1])}
            if max_w > 0 else {}
        )
        preferred_price = max(price_votes, key=price_votes.get) if price_votes else None
        return {
            "top_categories": top_categories,
            "preferred_price": preferred_price,
            "favorite_ids": sorted(fav_ids),
            "viewed_ids": sorted(view_counts.keys()),
            "is_new": not touched,
        }

    # -- scoring ---------------------------------------------------------
    def _candidates(self) -> list:
        return list(
            self.db.scalars(
                select(Destination).where(Destination.status == "active").order_by(Destination.id.asc())
            ).all()
        )

    def _popularity_max(self) -> tuple[int, int]:
        dests = self._candidates()
        if not dests:
            return 1, 1
        ids = [d.id for d in dests]
        sub = (
            select(func.count(Favorite.destination_id).label("cnt"))
            .where(Favorite.destination_id.in_(ids))
            .group_by(Favorite.destination_id)
            .subquery()
        )
        fav_max = int(self.db.scalar(select(func.max(sub.c.cnt))) or 0)
        view_max = max((int(d.view_count or 0) for d in dests), default=0)
        return max(fav_max, 1), max(view_max, 1)

    def score_all(self, user_id: int) -> list[dict]:
        prof = self.profile(user_id)
        weights = prof["top_categories"]
        pref_price = prof["preferred_price"]
        excluded = set(prof["favorite_ids"])
        fav_max, view_max = self._popularity_max()
        out: list[dict] = []
        for dest in self._candidates():
            if dest.id in excluded:
                continue
            cats = [c.slug for c in self.repo.categories_for(dest.id)]
            insight_row = self.repo.insight_for(dest.id)
            ins = insight_row.final_data if insight_row else {}
            status = ins.get("status", "insufficient_data")
            rating_avg = float(ins.get("rating_avg", dest.rating_avg or 0))
            rating_count = int(ins.get("rating_count", 0))
            rating_source = ins.get("rating_source", "internal")
            fav_count = int(ins.get("favorite_count", self.repo.favorite_count(dest.id)))

            cat_score = min(45.0, sum(weights.get(s, 0.0) for s in cats) * 45.0)
            quality = round(_blended_quality(rating_avg, rating_count) * 35.0, 1)
            if status != "ok":
                quality = min(quality, 15.0)
            pop = round(
                (0.6 * min(fav_count / fav_max, 1.0) + 0.4 * min(int(dest.view_count or 0) / view_max, 1.0)) * 10.0, 1
            )
            price = _price_score(pref_price, dest.price_level)
            match = round(cat_score + quality + pop + price, 1)

            reasons: list[str] = []
            hit = [s for s in cats if s in weights]
            if hit:
                reasons.append(f"Hợp gu {', '.join(hit[:2])}")
            elif not weights:
                reasons.append("Được yêu thích nhất")
            if rating_count > 0:
                src = f" ({rating_source})" if rating_source != "internal" else ""
                reasons.append(f"★ {rating_avg} từ {rating_count} đánh giá{src}")
            if pref_price and dest.price_level == pref_price:
                reasons.append(f"Giá {dest.price_level} như bạn hay đi")
            if status != "ok":
                reasons.append("Ít dữ liệu — tham khảo thêm")
            out.append({
                "destination": dest,
                "categories": cats,
                "match": match,
                "reasons": reasons,
                "components": {
                    "category": round(cat_score, 1), "quality": quality,
                    "popularity": pop, "price": price,
                },
                "is_new_category": not any(s in weights for s in cats),
            })
        out.sort(key=lambda r: -r["match"])
        return out

    # -- public API ------------------------------------------------------
    def recommendations(self, user_id: int, limit: int = 10) -> dict:
        prof = self.profile(user_id)
        scored = self.score_all(user_id)
        if prof["is_new"]:
            # User mới: matched = hot toàn site, explore = phần còn lại.
            matched = [s for s in scored if s["match"] >= MATCHED_THRESHOLD][:limit]
            if not matched:
                matched = scored[:limit]
            used = {s["destination"].id for s in matched}
            explore = [s for s in scored if s["destination"].id not in used][:EXPLORE_MAX_ITEMS]
            return {"matched": matched, "explore": explore, "profile": prof}
        matched = [s for s in scored if s["match"] >= MATCHED_THRESHOLD][:limit]
        explore: list[dict] = []
        per_cat: dict[str, int] = {}
        for s in scored:
            if s["match"] >= MATCHED_THRESHOLD or s["match"] < EXPLORE_MIN:
                # Nhóm explore: 40–60, hoặc category hoàn toàn mới (khám phá).
                if not (s["is_new_category"] and s["match"] >= 30.0):
                    continue
            key = s["categories"][0] if s["categories"] else "_none"
            if per_cat.get(key, 0) >= EXPLORE_MAX_PER_CATEGORY:
                continue
            if len(explore) >= EXPLORE_MAX_ITEMS:
                break
            per_cat[key] = per_cat.get(key, 0) + 1
            explore.append(s)
        return {"matched": matched, "explore": explore, "profile": prof}

    def itinerary(self, user_id: int, limit: int = 5) -> dict:
        rec = self.recommendations(user_id, limit=max(limit * 2, limit))
        pool = list(rec["matched"]) or list(rec["explore"])
        picked: list[dict] = []
        prev_cats: set[str] = set()
        slots = ["sáng", "sáng", "chiều", "chiều", "tối"]
        rest = list(pool)
        while rest and len(picked) < limit:
            nxt = None
            for s in rest:
                if not (set(s["categories"]) & prev_cats):
                    nxt = s
                    break
            if nxt is None:
                nxt = rest[0]
            picked.append(nxt)
            rest.remove(nxt)
            prev_cats = set(nxt["categories"])
        items = []
        for i, s in enumerate(picked, start=1):
            items.append({
                "order": i,
                "destination": s["destination"],
                "match": s["match"],
                "reasons": s["reasons"],
                "slot": slots[i - 1] if i - 1 < len(slots) else "tự do",
            })
        avg = round(sum(s["match"] for s in picked) / len(picked), 1) if picked else 0.0
        return {"itinerary": items, "total_match": avg, "profile": rec["profile"]}
