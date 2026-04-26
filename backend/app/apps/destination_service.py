from app.app_factory import create_app
from app.routers import public, activity_public, destinations, internal_destination, internal_destination_admin
from app.core.config import settings

routers = [public.router, destinations.router, internal_destination.router, internal_destination_admin.router]

if settings.activity_recommendation_endpoint_enabled:
	routers.insert(1, activity_public.router)

app = create_app(routers)
