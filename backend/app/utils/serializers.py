from app.db.models import Category, Destination


def category_to_dict(c: Category, count: int | None = None) -> dict:
    data = {
        "id": c.id,
        "name": c.name,
        "slug": c.slug,
        "descriptions": c.descriptions,
    }
    if count is not None:
        data["destination_count"] = count
    return data


def destination_to_dict(
    d: Destination,
    categories: list | None = None,
    insight: dict | None = None,
    favorite_count: int | None = None,
    rating_count: int | None = None,
    rating_sum: int | None = None,
) -> dict:
    data = {
        "id": d.id,
        "name": d.name,
        "slug": d.slug,
        "address": d.address,
        "description": d.description,
        "rating_avg": float(d.rating_avg or 0),
        "lat": float(d.lat) if d.lat is not None else None,
        "lng": float(d.lng) if d.lng is not None else None,
        "price_level": d.price_level,
        "open_hour": d.open_hour,
        "img_url": d.img_url,
        "url_map": d.url_map,
        "view_count": d.view_count,
        "status": d.status,
    }
    if categories is not None:
        data["categories"] = [{"id": c.id, "name": c.name, "slug": c.slug} for c in categories]
    if insight is not None:
        data["insight"] = insight
    metrics = {}
    if favorite_count is not None:
        metrics["favorite_count"] = favorite_count
    if rating_count is not None:
        metrics["rating_count"] = rating_count
    if rating_sum is not None:
        metrics["rating_sum"] = rating_sum
    if metrics:
        metrics["view_count"] = d.view_count
        data["metrics"] = metrics
    return data
