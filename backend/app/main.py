from app.app_factory import create_app
from app.routers import auth, public, activity_public, destinations, interaction, admin, analytics
from app.core.config import settings

routers = [
    auth.router,
    public.router,
    destinations.router,
    interaction.router,
    admin.router,
    analytics.router,
]

if settings.activity_recommendation_endpoint_enabled:
    routers.insert(2, activity_public.router)

app = create_app(routers)
