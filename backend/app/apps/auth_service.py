from app.app_factory import create_app
from app.routers import auth

app = create_app([auth.router])
