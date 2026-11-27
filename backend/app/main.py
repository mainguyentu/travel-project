from app.app_factory import create_app
from app.routers import activities, admin, analytics, auth, destinations, interaction, internal, observability, public

app = create_app([
    auth.router,
    public.router,
    activities.router,
    destinations.router,
    interaction.router,
    admin.router,
    analytics.router,
    internal.router,
    observability.router,
])
