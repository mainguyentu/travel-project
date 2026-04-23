from app.app_factory import create_app
from app.routers import public, activity_public, destinations

app = create_app([public.router, activity_public.router, destinations.router])
