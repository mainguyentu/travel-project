from app.app_factory import create_app
from app.routers import auth, public, activity_public, destinations, interaction, admin, analytics

app = create_app([
    auth.router,
    public.router,
    activity_public.router,
    destinations.router,
    interaction.router,
    admin.router,
    analytics.router,
])
