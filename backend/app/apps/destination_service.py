from app.app_factory import create_app
from app.routers import public, destinations

app = create_app([public.router, destinations.router])
