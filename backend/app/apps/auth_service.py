from app.app_factory import create_app
from app.routers import auth, internal_auth_admin

app = create_app([auth.router, internal_auth_admin.router])
