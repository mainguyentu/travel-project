from app.db.models import Destination, Category, Favorite, Rating, User


def category_to_dict(category: Category) -> dict:
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "descriptions": category.descriptions,
    }


def destination_to_dict(destination: Destination) -> dict:
    categories = []
    for cd in destination.categories:
        if cd.category:
            categories.append(category_to_dict(cd.category))

    insight_data = None
    if destination.insight:
        insight_data = {
            "destination_id": destination.insight.destination_id,
            "human_override": destination.insight.human_override,
            "score_snapshot": destination.insight.score_snapshot,
            "final_data": destination.insight.final_data,
            "updated_at": destination.insight.updated_at.isoformat() if destination.insight.updated_at else None,
        }

    metrics_data = None
    if destination.metrics:
        metrics_data = {
            "destination_id": destination.metrics.destination_id,
            "favorite_count": int(destination.metrics.favorite_count or 0),
            "rating_count": int(destination.metrics.rating_count or 0),
            "rating_sum": int(destination.metrics.rating_sum or 0),
            "view_count": int(destination.metrics.view_count or 0),
            "updated_at": destination.metrics.updated_at.isoformat() if destination.metrics.updated_at else None,
        }

    return {
        "id": destination.id,
        "name": destination.name,
        "slug": destination.slug,
        "address": destination.address,
        "description": destination.description,
        "rating_avg": float(destination.rating_avg or 0),
        "lat": float(destination.lat) if destination.lat is not None else None,
        "lng": float(destination.lng) if destination.lng is not None else None,
        "price_level": destination.price_level,
        "open_hour": destination.open_hour,
        "img_url": destination.img_url,
        "url_map": destination.url_map,
        "view_count": int(destination.view_count or 0),
        "status": destination.status,
        "categories": categories,
        "insight": insight_data,
        "metrics": metrics_data,
    }


def favorite_to_dict(favorite: Favorite) -> dict:
    return {"destination_id": favorite.destination_id}


def rating_to_dict(rating: Rating) -> dict:
    return {
        "destination_id": rating.destination_id,
        "rating_score": rating.rating_score,
        "comment": rating.comment,
    }


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "status": user.status,
    }
