from app.app_factory import create_app
from app.routers import auth, public, destinations, interaction, admin

app = create_app([
    auth.router,
    public.router,
    destinations.router,
    interaction.router,
    admin.router,
])
